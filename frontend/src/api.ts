import axios from "axios";
import type {
  ConfigResponse,
  NodeInfo,
  SvrGroupInfo,
  AuthResponse,
  User,
  ServerListItem,
  ServerDetail,
  ServiceListItem,
  ServiceDetail,
  Gateway,
  ServicePerformanceSummary,
} from "./types";

const API_BASE_URL = "/api";

// 토큰 관리 함수
export const auth = {
  getToken: (): string | null => {
    return localStorage.getItem("access_token");
  },

  setToken: (token: string): void => {
    localStorage.setItem("access_token", token);
  },

  removeToken: (): void => {
    localStorage.removeItem("access_token");
  },

  getUser: (): User | null => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  },

  setUser: (user: User): void => {
    localStorage.setItem("user", JSON.stringify(user));
  },

  removeUser: (): void => {
    localStorage.removeItem("user");
  },
};

// axios 인터셉터 설정
axios.interceptors.request.use(
  (config) => {
    const token = auth.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// 401 에러 처리
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      auth.removeToken();
      auth.removeUser();
      window.location.href = "/";
    }
    return Promise.reject(error);
  },
);

export const api = {
  // 로그인
  login: async (username: string, password: string): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await axios.post<AuthResponse>(
      `${API_BASE_URL}/auth/login`,
      formData,
      {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      },
    );
    return response.data;
  },

  // 로그아웃
  logout: (): void => {
    auth.removeToken();
    auth.removeUser();
  },

  // 현재 사용자 정보
  getCurrentUser: async (): Promise<User> => {
    const response = await axios.get<User>(`${API_BASE_URL}/auth/me`);
    return response.data;
  },

  // 전체 설정 요약
  getConfig: async (): Promise<ConfigResponse> => {
    const response = await axios.get<ConfigResponse>(`${API_BASE_URL}/config`);
    return response.data;
  },

  // 특정 노드 정보
  getNode: async (nodeName: string): Promise<NodeInfo> => {
    const response = await axios.get<NodeInfo>(
      `${API_BASE_URL}/node/${nodeName}`,
    );
    return response.data;
  },

  // 특정 서버 그룹 정보
  getSvrGroup: async (svgName: string): Promise<SvrGroupInfo> => {
    const response = await axios.get<SvrGroupInfo>(
      `${API_BASE_URL}/svrgroup/${svgName}`,
    );
    return response.data;
  },

  // 헬스 체크
  healthCheck: async () => {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  },

  // 설정 재로드
  reloadConfig: async () => {
    const response = await axios.get(`${API_BASE_URL}/reload`);
    return response.data;
  },

  // 서버 검색
  searchServers: async (search?: string): Promise<ServerListItem[]> => {
    const params = search ? { search } : {};
    const response = await axios.get(`${API_BASE_URL}/servers`, { params });
    return response.data.servers;
  },

  // 서버 상세 정보
  getServer: async (serverName: string): Promise<ServerDetail> => {
    const response = await axios.get(`${API_BASE_URL}/server/${serverName}`);
    return response.data.server;
  },

  // 서비스 검색
  searchServices: async (search?: string): Promise<ServiceListItem[]> => {
    const params = search ? { search } : {};
    const response = await axios.get(`${API_BASE_URL}/services`, { params });
    return response.data.services;
  },

  // 서비스 상세 정보
  getService: async (serviceName: string): Promise<ServiceDetail> => {
    const response = await axios.get(`${API_BASE_URL}/service/${serviceName}`);
    return response.data.service;
  },

  // 서버 목록 엑셀 export
  exportServers: async (): Promise<void> => {
    const response = await axios.get(`${API_BASE_URL}/export/servers`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    const filename =
      response.headers["content-disposition"]?.split("filename=")[1] ||
      "servers.xlsx";
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // 서비스 목록 엑셀 export
  exportServices: async (): Promise<void> => {
    const response = await axios.get(`${API_BASE_URL}/export/services`, {
      responseType: "blob",
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    const filename =
      response.headers["content-disposition"]?.split("filename=")[1] ||
      "services.xlsx";
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },

  // 게이트웨이 목록
  getGateways: async (): Promise<Gateway[]> => {
    const response = await axios.get(`${API_BASE_URL}/gateways`);
    return response.data.gateways;
  },

  // 서비스 응답시간 요약 정보
  getServicesPerformance: async (): Promise<ServicePerformanceSummary[]> => {
    const response = await axios.get(`${API_BASE_URL}/services/performance`);
    return response.data.services || [];
  },
};
