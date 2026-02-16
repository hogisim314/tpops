// API 타입 정의
export interface Summary {
  domain_id: string;
  domain_name: string;
  domain_shmkey?: string;
  domain_tportno?: string;
  domain_racport?: string;
  domain_maxuser?: string;
  domain_maxnode?: string;
  domain_maxsvg?: string;
  domain_maxsvr?: string;
  domain_maxsvc?: string;
  domain_maxgw?: string;
  domain_maxsession?: string;
  domain_security?: string;
  domain_loglvl?: string;
  total_domains: number;
  total_nodes: number;
  total_server_groups: number;
  total_servers: number;
  total_services: number;
  total_gateways: number;
  nodes: string[];
  server_groups: string[];
}

export interface ConfigResponse {
  success: boolean;
  summary: Summary;
  last_update: string;
}

export interface NodeInfo {
  node_name: string;
  hostname: string;
  port: string;
  server_groups: string[];
  max_servers: string;
  max_users: string;
  tmax_home: string;
}

export interface ServerInfo {
  name: string;
  min: string;
  max: string;
  restart: string;
}

export interface SvrGroupInfo {
  svg_name: string;
  node: string;
  backup: string;
  cousin: string;
  restart: string;
  autobackup: string;
  servers: ServerInfo[];
}

// 인증 관련 타입
export interface User {
  id: number;
  username: string;
  role: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// 서버 검색 타입
export interface ServerListItem {
  name: string;
  svg: string;
  min: string;
  max: string;
  restart: string;
  node: string;
  maxqcount?: string; // INFRASTRUCTURE 이상만
  asqcount?: string; // INFRASTRUCTURE 이상만
  db_info?: string; // INFRASTRUCTURE 이상만
}

export interface ServerDetail {
  name: string;
  svg_name: string;
  node_name: string;
  min_proc: string;
  max_proc: string;
  restart: string;
  maxqcount?: string; // INFRASTRUCTURE 이상만
  asqcount?: string; // INFRASTRUCTURE 이상만
  db_info?: string; // INFRASTRUCTURE 이상만
  services: ServiceListItem[];
}

// 서비스 검색 타입
export interface ServiceListItem {
  name: string;
  server: string;
  timeout: string;
  autotran: string;
  export: string;
}

export interface ServiceDetail {
  name: string;
  server_name: string;
  timeout: string;
  autotran: string;
  export: string;

  server_info?: {
    svg_name: string;
    node_name: string;
    min_proc: string;
    max_proc: string;
  };
}

export interface Gateway {
  name: string;
  node: string;
  port?: string;
  remote_addr?: string;
  remote_port?: string;
  direction?: string;
  gw_type?: string;
  backup_addr?: string;
  backup_port?: string;
  backup_rgwaddr?: string;
  backup_rgwportno?: string;
  cpc?: string;
  restart?: string;
  clopt?: string;
}

// 서비스 응답시간 요약 타입
export interface ServicePerformanceSummary {
  serviceName: string;
  avgTime: number | null;
  minTime: number | null;
  maxTime: number | null;
  count: number | null;
}
