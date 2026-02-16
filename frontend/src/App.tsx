import React, { useState, useEffect } from "react";
import "./App.css";
import { api, auth } from "./api";
import type {
  Summary,
  NodeInfo,
  User,
  ServerDetail,
  ServiceDetail,
  Gateway,
} from "./types";
import { Modal } from "./components/Modal";
import { NodeDetail } from "./components/NodeDetail";
import { Login } from "./components/Login";
import { Search } from "./components/Search";
import { ServerDetailModal } from "./components/ServerDetailModal";
import { ServiceDetailModal } from "./components/ServiceDetailModal";
import { DomainList } from "./components/DomainList";
import { GatewayList } from "./components/GatewayList";
import { ResponseTime } from "./components/ResponseTime";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [loginError, setLoginError] = useState<string | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<string>("");
  const [activeTab, setActiveTab] = useState<string>("");
  const [gateways, setGateways] = useState<Gateway[]>([]);

  // 모달 상태
  const [modalOpen, setModalOpen] = useState(false);
  const [modalContent, setModalContent] = useState<React.ReactNode>(null);

  // 인증 확인
  useEffect(() => {
    const token = auth.getToken();
    const user = auth.getUser();
    if (token && user) {
      setIsAuthenticated(true);
      setCurrentUser(user);
      // 권한에 따라 초기 탭 설정
      if (user.role === "infrastructure" || user.role === "admin") {
        setActiveTab("domain");
      } else if (user.role === "monitoring") {
        setActiveTab("nodes");
      } else {
        setActiveTab("servers");
      }
    } else {
      setIsAuthenticated(false);
      setLoading(false);
    }
  }, []);

  const handleLogin = async (username: string, password: string) => {
    try {
      setLoginError(null);
      const response = await api.login(username, password);
      auth.setToken(response.access_token);
      auth.setUser(response.user);
      setCurrentUser(response.user);
      setIsAuthenticated(true);
    } catch (err: any) {
      console.error("Login error:", err);
      setLoginError(
        err.response?.data?.detail ||
          "로그인에 실패했습니다. 사용자 이름과 비밀번호를 확인하세요.",
      );
    }
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    setCurrentUser(null);
    setSummary(null);
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getConfig();
      setSummary(data.summary);
      setLastUpdate(new Date(data.last_update).toLocaleString("ko-KR"));

      // 게이트웨이 데이터 로드
      const gatewayData = await api.getGateways();
      setGateways(gatewayData);
    } catch (err) {
      setError("데이터를 불러오는 중 오류가 발생했습니다.");
      console.error("Error loading data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      loadData();

      // 30초마다 자동 새로고침
      const interval = setInterval(loadData, 30000);

      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const handleNodeClick = async (nodeName: string) => {
    try {
      const nodeInfo: NodeInfo = await api.getNode(nodeName);
      setModalContent(<NodeDetail nodeInfo={nodeInfo} />);
      setModalOpen(true);
    } catch (err) {
      alert("노드 정보를 불러올 수 없습니다.");
      console.error("Error loading node:", err);
    }
  };

  const handleServerClick = async (serverName: string) => {
    try {
      const serverInfo: ServerDetail = await api.getServer(serverName);
      setModalContent(<ServerDetailModal serverInfo={serverInfo} />);
      setModalOpen(true);
    } catch (err) {
      alert("서버 정보를 불러올 수 없습니다.");
      console.error("Error loading server:", err);
    }
  };

  const handleServiceClick = async (serviceName: string) => {
    try {
      const serviceInfo: ServiceDetail = await api.getService(serviceName);

      const handleServerClickFromModal = async (serverName: string) => {
        setModalOpen(false);
        // 탭 전환 후 서버 상세 정보 자동으로 표시
        setTimeout(async () => {
          setActiveTab("servers");
          // 서버 상세 정보 자동으로 열기
          await handleServerClick(serverName);
        }, 100);
      };

      setModalContent(
        <ServiceDetailModal
          serviceInfo={serviceInfo}
          onServerClick={handleServerClickFromModal}
        />,
      );
      setModalOpen(true);
    } catch (err) {
      alert("서비스 정보를 불러올 수 없습니다.");
      console.error("Error loading service:", err);
    }
  };

  // 권한 체크 함수
  const canViewInfrastructure = () => {
    return (
      currentUser?.role === "infrastructure" || currentUser?.role === "admin"
    );
  };

  // 탭 구성 (권한별)
  const getTabs = () => {
    const tabs = [
      { id: "nodes", label: "노드" },
      { id: "servers", label: "서버 프로세스" },
      { id: "services", label: "서비스(TR)" },
      { id: "response-time", label: "응답시간" },
    ];

    if (canViewInfrastructure()) {
      tabs.unshift(
        { id: "domain", label: "도메인" },
        { id: "gateways", label: "게이트웨이" },
      );
    }

    return tabs;
  };

  // 탭 렌더링 함수
  const renderTabContent = () => {
    if (!summary) return null;

    switch (activeTab) {
      case "domain":
        return <DomainList summary={summary} />;

      case "nodes":
        return (
          <div className="entity-list">
            {summary.nodes.map((nodeName) => (
              <div
                key={nodeName}
                className="list-item clickable"
                onClick={() => handleNodeClick(nodeName)}
              >
                <div className="item-header">
                  <h3>{nodeName}</h3>
                </div>
              </div>
            ))}
          </div>
        );

      case "gateways":
        return <GatewayList gateways={gateways} />;

      case "servers":
        return (
          <Search
            onServerClick={handleServerClick}
            onServiceClick={handleServiceClick}
            currentUser={currentUser}
            initialTab="server"
          />
        );

      case "services":
        return (
          <Search
            onServerClick={handleServerClick}
            onServiceClick={handleServiceClick}
            currentUser={currentUser}
            initialTab="service"
          />
        );
      case "response-time":
        return <ResponseTime onServiceClick={handleServiceClick} />;

      default:
        return null;
    }
  };

  return (
    <>
      {!isAuthenticated ? (
        <Login onLogin={handleLogin} error={loginError} />
      ) : (
        <>
          <div className="header">
            <div className="header-top">
              <div className="header-brand">
                <h1>
                  TPOps Dashboard
                  <span className="status-indicator"></span>
                </h1>
                <p className="subtitle">Tmax 시스템 실시간 모니터링</p>
              </div>
              <div className="user-info">
                <span>{currentUser?.username}</span>
                <span className="role-badge">{currentUser?.role}</span>
                <button onClick={handleLogout} className="logout-btn">
                  로그아웃
                </button>
              </div>
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          {loading && !summary ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>데이터를 불러오는 중...</p>
            </div>
          ) : (
            summary && (
              <>
                <div className="main-container">
                  <div className="content-wrapper">
                    {/* 탭 네비게이션 */}
                    <div className="tabs-container">
                      <div className="tabs">
                        {getTabs().map((tab) => (
                          <button
                            key={tab.id}
                            className={`tab ${activeTab === tab.id ? "active" : ""}`}
                            onClick={() => setActiveTab(tab.id)}
                          >
                            {tab.label}
                          </button>
                        ))}
                      </div>

                      <div className="tab-actions">
                        <div className="stats-summary">
                          <span className="stat-badge">
                            도메인: {summary.total_domains}
                          </span>
                          <span className="stat-badge">
                            노드: {summary.total_nodes}
                          </span>
                          <span className="stat-badge">
                            서버: {summary.total_servers}
                          </span>
                          <span className="stat-badge">
                            서비스: {summary.total_services}
                          </span>
                          <span className="stat-badge">
                            게이트웨이: {summary.total_gateways}
                          </span>
                        </div>

                        <button className="refresh-btn" onClick={loadData}>
                          새로고침
                        </button>
                      </div>
                    </div>

                    {/* 탭 컨텐츠 */}
                    <div className="tab-content">{renderTabContent()}</div>

                    <div className="timestamp">
                      마지막 업데이트: {lastUpdate}
                    </div>
                  </div>
                </div>
              </>
            )
          )}

          {modalOpen && (
            <Modal onClose={() => setModalOpen(false)}>{modalContent}</Modal>
          )}
        </>
      )}
    </>
  );
}

export default App;
