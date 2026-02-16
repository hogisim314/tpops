#!/usr/bin/env python3
"""
Tmax Monitoring Dashboard Backend
Flask 웹 서버를 통한 Tmax 설정 모니터링 API
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
from tpconfig_parser import TpConfigParser
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 설정 파일 경로
CONFIG_FILE = 'tp_config_20260126'

# 파서 인스턴스 (캐시)
parser = None
config_data = None
last_update = None


def get_parser():
    """파서 인스턴스 가져오기 (캐시 포함)"""
    global parser, config_data, last_update
    
    if parser is None or config_data is None:
        print(f"Loading config file: {CONFIG_FILE}")
        parser = TpConfigParser(CONFIG_FILE)
        config_data = parser.parse()
        last_update = datetime.now()
        print(f"Config loaded successfully at {last_update}")
    
    return parser


@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/api/config')
def get_config():
    """전체 설정 정보 API"""
    try:
        p = get_parser()
        summary = p.get_summary()
        
        return jsonify({
            'success': True,
            'summary': summary,
            'last_update': last_update.isoformat() if last_update else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/full')
def get_full_config():
    """전체 설정 데이터 API (대용량)"""
    try:
        p = get_parser()
        
        return jsonify({
            'success': True,
            'data': config_data,
            'last_update': last_update.isoformat() if last_update else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/node/<node_name>')
def get_node_info(node_name):
    """특정 노드 정보 API"""
    try:
        p = get_parser()
        node_info = p.get_node_info(node_name)
        
        if not node_info or not node_info.get('hostname'):
            return jsonify({
                'success': False,
                'error': f'Node {node_name} not found'
            }), 404
        
        return jsonify({
            'success': True,
            **node_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/svrgroup/<svg_name>')
def get_svrgroup_info(svg_name):
    """특정 서버 그룹 정보 API"""
    try:
        p = get_parser()
        svg_info = p.get_server_group_info(svg_name)
        
        if not svg_info or not svg_info.get('node'):
            return jsonify({
                'success': False,
                'error': f'Server group {svg_name} not found'
            }), 404
        
        return jsonify({
            'success': True,
            **svg_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/nodes')
def get_all_nodes():
    """모든 노드 목록 API"""
    try:
        p = get_parser()
        nodes = []
        
        for node_name in config_data['NODE'].keys():
            node_info = p.get_node_info(node_name)
            nodes.append(node_info)
        
        return jsonify({
            'success': True,
            'nodes': nodes,
            'total': len(nodes)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/svrgroups')
def get_all_svrgroups():
    """모든 서버 그룹 목록 API"""
    try:
        p = get_parser()
        svgs = []
        
        for svg_name in config_data['SVRGROUP'].keys():
            svg_info = p.get_server_group_info(svg_name)
            svgs.append(svg_info)
        
        return jsonify({
            'success': True,
            'server_groups': svgs,
            'total': len(svgs)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/servers')
def get_all_servers():
    """모든 서버 목록 API"""
    try:
        servers = []
        
        for srv_name, srv_list in config_data['SERVER'].items():
            for srv_data in srv_list:
                servers.append({
                    'name': srv_name,
                    'svg': srv_data.get('SVGNAME', '').strip('"'),
                    'min': srv_data.get('MIN', 'N/A'),
                    'max': srv_data.get('MAX', 'N/A'),
                    'restart': srv_data.get('RESTART', 'N/A'),
                    'node': srv_data.get('NODENAME', '').strip('"') or 'N/A'
                })
        
        return jsonify({
            'success': True,
            'servers': servers,
            'total': len(servers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/services')
def get_all_services():
    """모든 서비스 목록 API"""
    try:
        services = []
        
        for svc_name, svc_data in config_data['SERVICE'].items():
            services.append({
                'name': svc_name,
                'server': svc_data.get('SVRNAME', '').strip('"'),
                'timeout': svc_data.get('SVCTIME', 'N/A'),
                'autotran': svc_data.get('AUTOTRAN', 'N/A'),
                'export': svc_data.get('EXPORT', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'services': services,
            'total': len(services)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/gateways')
def get_all_gateways():
    """모든 게이트웨이 목록 API"""
    try:
        gateways = []
        
        for gw_name, gw_data in config_data['GATEWAY'].items():
            gateways.append({
                'name': gw_name,
                'node': gw_data.get('NODENAME', '').strip('"'),
                'port': gw_data.get('PORTNO', 'N/A'),
                'remote_addr': gw_data.get('RGWADDR', '').strip('"'),
                'remote_port': gw_data.get('RGWPORTNO', 'N/A'),
                'direction': gw_data.get('DIRECTION', 'N/A'),
                'type': gw_data.get('GWTYPE', 'N/A')
            })
        
        return jsonify({
            'success': True,
            'gateways': gateways,
            'total': len(gateways)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/reload')
def reload_config():
    """설정 다시 로드 API"""
    global parser, config_data, last_update
    
    try:
        parser = None
        config_data = None
        get_parser()  # 다시 로드
        
        return jsonify({
            'success': True,
            'message': 'Configuration reloaded successfully',
            'last_update': last_update.isoformat() if last_update else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health')
def health_check():
    """헬스 체크 API"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    # 설정 파일 존재 확인
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Config file '{CONFIG_FILE}' not found!")
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        exit(1)
    
    # 초기 설정 로드
    try:
        get_parser()
        print("Configuration loaded successfully!")
        print(f"Total nodes: {len(config_data['NODE'])}")
        print(f"Total server groups: {len(config_data['SVRGROUP'])}")
        print(f"Total servers: {sum(len(v) for v in config_data['SERVER'].values())}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        exit(1)
    
    print("\n" + "="*50)
    print("🚀 Tmax Monitoring Dashboard Starting...")
    print("="*50)
    print(f"📁 Config file: {CONFIG_FILE}")
    print(f"🌐 Dashboard URL: http://localhost:5001")
    print(f"🔧 API URL: http://localhost:5001/api/config")
    print("="*50 + "\n")
    
    # Flask 서버 시작
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        threaded=True
    )
