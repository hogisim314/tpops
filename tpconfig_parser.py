#!/usr/bin/env python3
"""
Tmax Configuration Parser
tp_config 파일을 파싱하여 JSON 형식으로 변환하는 모듈
"""

import re
import json
from typing import Dict, List, Any
from collections import defaultdict


class TpConfigParser:
    """Tmax tp_config 파일 파서"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config_data = {
            'DOMAIN': {},
            'NODE': {},
            'SVRGROUP': {},
            'SERVER': defaultdict(list),
            'SERVICE': {},
            'GATEWAY': {}
        }
        
    def parse(self) -> Dict[str, Any]:
        """설정 파일 전체를 파싱"""
        current_section = None
        current_entry_name = None
        current_entry_lines = []
        
        with open(self.config_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                stripped = line.strip()
                
                # 섹션 헤더 감지 (*로 시작)
                if stripped.startswith('*'):
                    # 이전 엔트리 저장
                    if current_entry_name and current_entry_lines:
                        self._save_entry(current_section, current_entry_name, current_entry_lines)
                    
                    current_section = stripped[1:].strip()
                    current_entry_name = None
                    current_entry_lines = []
                    continue
                
                # 빈 줄이나 주석 무시
                if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                    continue
                
                # 새로운 엔트리인지 확인 (탭으로 시작하지 않음)
                if not line.startswith('\t') and not line.startswith(' ' * 4) and line[0] not in ' \t':
                    # 이전 엔트리 저장
                    if current_entry_name and current_entry_lines:
                        self._save_entry(current_section, current_entry_name, current_entry_lines)
                    
                    # 새 엔트리 시작 - 첫 단어가 엔트리 이름
                    parts = stripped.split(maxsplit=1)
                    if parts:
                        current_entry_name = parts[0]
                        current_entry_lines = [stripped]
                else:
                    # 현재 엔트리에 줄 추가 (들여쓰기된 줄)
                    if current_entry_name:
                        current_entry_lines.append(stripped)
            
            # 마지막 엔트리 저장
            if current_entry_name and current_entry_lines:
                self._save_entry(current_section, current_entry_name, current_entry_lines)
        
        return self.config_data
    
    def _save_entry(self, section: str, name: str, lines: List[str]):
        """엔트리를 파싱하고 저장"""
        if not section or not name:
            return
        
        # 모든 줄을 하나로 합치기
        full_text = ' '.join(line.strip() for line in lines)
        
        # 키-값 쌍 파싱
        attrs = {}
        
        # 이름 추출 (첫 번째 단어)
        name_match = re.match(r'^(\S+)', full_text)
        if name_match:
            entry_name = name_match.group(1)
            attrs['name'] = entry_name
        else:
            return
        
        # 속성 파싱 (KEY = VALUE 패턴)
        # 쉼표로 구분되고, = 로 키-값이 나뉨
        pattern = r'(\w+)\s*=\s*([^,]+?)(?=\s*,\s*\w+\s*=|\s*$)'
        matches = re.findall(pattern, full_text)
        
        for key, value in matches:
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            attrs[key] = value
        
        # 데이터 저장 - 섹션 타입에 따라
        if section == 'DOMAIN':
            # DOMAIN은 하나만 있음
            if not self.config_data['DOMAIN']:
                self.config_data['DOMAIN'] = attrs
        elif section == 'NODE':
            # NODE는 이름으로 구분
            self.config_data['NODE'][entry_name] = attrs
        elif section == 'SVRGROUP':
            self.config_data['SVRGROUP'][entry_name] = attrs
        elif section == 'SERVER':
            # SERVER는 같은 이름이 여러 노드에 있을 수 있음
            self.config_data['SERVER'][entry_name].append(attrs)
        elif section == 'SERVICE':
            self.config_data['SERVICE'][entry_name] = attrs
        elif section == 'GATEWAY':
            self.config_data['GATEWAY'][entry_name] = attrs
    
    def get_summary(self) -> Dict[str, Any]:
        """설정 요약 정보 반환"""
        domain_name = self.config_data['DOMAIN'].get('name', 'N/A')
        return {
            'domain_id': self.config_data['DOMAIN'].get('DOMAINID', 'N/A'),
            'domain_name': domain_name,
            'total_nodes': len(self.config_data['NODE']),
            'total_server_groups': len(self.config_data['SVRGROUP']),
            'total_servers': sum(len(v) for v in self.config_data['SERVER'].values()),
            'total_services': len(self.config_data['SERVICE']),
            'total_gateways': len(self.config_data['GATEWAY']),
            'nodes': list(self.config_data['NODE'].keys()),
            'server_groups': list(self.config_data['SVRGROUP'].keys())[:20],  # 처음 20개만
        }
    
    def get_node_info(self, node_name: str) -> Dict[str, Any]:
        """특정 노드 정보 반환"""
        node_data = self.config_data['NODE'].get(node_name, {})
        
        # 이 노드에 속한 서버 그룹 찾기
        node_svgroups = []
        for svg_name, svg_data in self.config_data['SVRGROUP'].items():
            if svg_data.get('NODENAME', '').strip('"') == node_name:
                node_svgroups.append(svg_name)
        
        return {
            'node_name': node_name,
            'hostname': node_data.get('HOSTNAME', 'N/A'),
            'port': node_data.get('TmaxPort', 'N/A'),
            'server_groups': node_svgroups,
            'max_servers': node_data.get('MAXSVR', 'N/A'),
            'max_users': node_data.get('MAXUSER', 'N/A'),
            'tmax_home': node_data.get('TMAXHOME', 'N/A'),
        }
    
    def get_server_group_info(self, svg_name: str) -> Dict[str, Any]:
        """특정 서버 그룹 정보 반환"""
        svg_data = self.config_data['SVRGROUP'].get(svg_name, {})
        
        # 이 서버 그룹에 속한 서버들 찾기
        servers = []
        for srv_name, srv_list in self.config_data['SERVER'].items():
            for srv_data in srv_list:
                if srv_data.get('SVGNAME', '').strip('"') == svg_name:
                    servers.append({
                        'name': srv_name,
                        'min': srv_data.get('MIN', 'N/A'),
                        'max': srv_data.get('MAX', 'N/A'),
                        'restart': srv_data.get('RESTART', 'N/A')
                    })
        
        return {
            'svg_name': svg_name,
            'node': svg_data.get('NODENAME', 'N/A').strip('"'),
            'backup': svg_data.get('BACKUP', 'N/A').strip('"'),
            'cousin': svg_data.get('COUSIN', 'N/A').strip('"'),
            'restart': svg_data.get('RESTART', 'N/A'),
            'autobackup': svg_data.get('AUTOBACKUP', 'N/A'),
            'servers': servers
        }


def main():
    """테스트용 메인 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tpconfig_parser.py <tp_config_file>")
        sys.exit(1)
    
    parser = TpConfigParser(sys.argv[1])
    config_data = parser.parse()
    
    print("=== Tmax Configuration Summary ===")
    summary = parser.get_summary()
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
