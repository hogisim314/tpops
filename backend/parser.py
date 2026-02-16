"""
TpConfig 파서 모듈
Tmax tp_config 설정 파일을 파싱하는 Python 모듈
"""

import re
from typing import Dict, List, Any, Optional


class TpConfigParser:
    """tp_config 파서 클래스"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
    
    def parse(self) -> Dict[str, Any]:
        """설정 파일 파싱"""
        config_data = {
            "domain": {},
            "node": {},
            "svrgroup": {},
            "server": {},
            "service": {},
            "gateway": {}
        }
        
        current_section = ""
        current_entry_name = ""
        current_entry_lines = []
        
        with open(self.config_file, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                stripped = line.strip()
                
                # 섹션 헤더 감지
                if stripped.startswith("*"):
                    # 이전 엔트리 저장
                    if current_entry_name and current_entry_lines:
                        self._save_entry(
                            config_data,
                            current_section,
                            current_entry_name,
                            current_entry_lines
                        )
                    
                    current_section = stripped[1:]  # Remove *
                    current_entry_name = ""
                    current_entry_lines = []
                    continue
                
                # 빈 줄이나 주석 무시
                if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                    continue
                
                # 새로운 엔트리인지 확인 (들여쓰기 없음)
                if line and not line[0].isspace():
                    # 이전 엔트리 저장
                    if current_entry_name and current_entry_lines:
                        self._save_entry(
                            config_data,
                            current_section,
                            current_entry_name,
                            current_entry_lines
                        )
                    
                    # 새 엔트리 시작
                    parts = stripped.split()
                    if parts:
                        current_entry_name = parts[0]
                        current_entry_lines = [stripped]
                else:
                    # 현재 엔트리에 줄 추가
                    if current_entry_name:
                        current_entry_lines.append(stripped)
        
        # 마지막 엔트리 저장
        if current_entry_name and current_entry_lines:
            self._save_entry(
                config_data,
                current_section,
                current_entry_name,
                current_entry_lines
            )
        
        return config_data
    
    def _save_entry(
        self,
        config_data: Dict[str, Any],
        section: str,
        name: str,
        lines: List[str]
    ):
        """엔트리 저장"""
        if not section or not name:
            return
        
        # 모든 줄을 하나로 합치기
        full_text = " ".join(lines)
        
        # 속성 파싱
        attrs = {"name": name}
        
        # KEY = VALUE 패턴 파싱
        pattern = r'(\w+)\s*=\s*([^,]+?)(?:\s*,|\s*$)'
        matches = re.findall(pattern, full_text)
        
        for key, value in matches:
            key = key.strip()
            value = value.strip().strip('"\'')
            if value:
                attrs[key] = value
        
        # 섹션별 저장
        section_lower = section.lower()
        
        if section_lower == "domain":
            if not config_data["domain"]:
                config_data["domain"] = attrs
        elif section_lower == "node":
            config_data["node"][name] = attrs
        elif section_lower == "svrgroup":
            config_data["svrgroup"][name] = attrs
        elif section_lower == "server":
            if name not in config_data["server"]:
                config_data["server"][name] = []
            config_data["server"][name].append(attrs)
        elif section_lower == "service":
            config_data["service"][name] = attrs
        elif section_lower == "gateway":
            config_data["gateway"][name] = attrs
    
    def get_summary(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """설정 요약 정보 반환"""
        # 노드 목록
        nodes = list(config_data["node"].keys())
        
        # 서버 그룹 목록 (처음 20개만)
        server_groups = list(config_data["svrgroup"].keys())[:20]
        
        # 총 서버 수 계산
        total_servers = sum(len(srv_list) for srv_list in config_data["server"].values())
        
        domain_name = config_data["domain"].get("name", "N/A")
        
        return {
            "domain_id": config_data["domain"].get("DOMAINID", ""),
            "domain_name": domain_name,
            "total_nodes": len(config_data["node"]),
            "total_server_groups": len(config_data["svrgroup"]),
            "total_servers": total_servers,
            "total_services": len(config_data["service"]),
            "total_gateways": len(config_data["gateway"]),
            "nodes": nodes,
            "server_groups": server_groups
        }
    
    def get_node_info(self, config_data: Dict[str, Any], node_name: str) -> Optional[Dict[str, Any]]:
        """특정 노드 정보 반환"""
        node_data = config_data["node"].get(node_name)
        if not node_data:
            return None
        
        # 이 노드에 속한 서버 그룹 찾기
        server_groups = []
        for svg_name, svg_data in config_data["svrgroup"].items():
            node_name_in_svg = svg_data.get("NODENAME", "").strip('"')
            if node_name_in_svg == node_name:
                server_groups.append(svg_name)
        
        return {
            "node_name": node_name,
            "hostname": node_data.get("HOSTNAME", ""),
            "port": node_data.get("TmaxPort", ""),
            "server_groups": server_groups,
            "max_servers": node_data.get("MAXSVR", ""),
            "max_users": node_data.get("MAXUSER", ""),
            "tmax_home": node_data.get("TMAXHOME", "")
        }
    
    def get_svrgroup_info(self, config_data: Dict[str, Any], svg_name: str) -> Optional[Dict[str, Any]]:
        """특정 서버 그룹 정보 반환"""
        svg_data = config_data["svrgroup"].get(svg_name)
        if not svg_data:
            return None
        
        # 이 서버 그룹에 속한 서버들 찾기
        servers = []
        for srv_name, srv_list in config_data["server"].items():
            for srv_data in srv_list:
                srv_svg_name = srv_data.get("SVGNAME", "").strip('"')
                if srv_svg_name == svg_name:
                    servers.append({
                        "name": srv_name,
                        "min": srv_data.get("MIN", ""),
                        "max": srv_data.get("MAX", ""),
                        "restart": srv_data.get("RESTART", "")
                    })
        
        backup = svg_data.get("BACKUP", "N/A")
        if not backup:
            backup = "N/A"
        
        cousin = svg_data.get("COUSIN", "N/A")
        if not cousin:
            cousin = "N/A"
        
        return {
            "svg_name": svg_name,
            "node": svg_data.get("NODENAME", "").strip('"'),
            "backup": backup.strip('"'),
            "cousin": cousin.strip('"'),
            "restart": svg_data.get("RESTART", ""),
            "autobackup": svg_data.get("AUTOBACKUP", ""),
            "servers": servers
        }
