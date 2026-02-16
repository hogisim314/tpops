import React, { useState, useEffect } from "react";
import { api } from "../api";
import type { ServerListItem, ServiceListItem, User } from "../types";

interface SearchProps {
  onServerClick: (serverName: string) => void;
  onServiceClick: (serviceName: string) => void;
  currentUser: User | null;
  initialTab?: "server" | "service";
}

export const Search: React.FC<SearchProps> = ({
  onServerClick,
  onServiceClick,
  currentUser,
  initialTab = "server",
}) => {
  const [searchType, setSearchType] = useState<"server" | "service">(
    initialTab,
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [servers, setServers] = useState<ServerListItem[]>([]);
  const [services, setServices] = useState<ServiceListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);

  // initialTab이 변경되면 searchType 업데이트
  useEffect(() => {
    setSearchType(initialTab);
    setSearchQuery(""); // 검색어도 초기화
  }, [initialTab]);

  // INFRASTRUCTURE 이상만 export 가능
  const canExport =
    currentUser?.role === "infrastructure" || currentUser?.role === "admin";

  const handleExport = async () => {
    if (!canExport) return;

    if (
      !window.confirm(
        "서버에 부하가 갈 수 있습니다.\n전체 데이터를 엑셀로 다운로드하시겠습니까?",
      )
    ) {
      return;
    }

    setExporting(true);
    try {
      if (searchType === "server") {
        await api.exportServers();
      } else {
        await api.exportServices();
      }
    } catch (err: any) {
      console.error("Export error:", err);
      alert(
        err.response?.data?.detail || "엑셀 다운로드 중 오류가 발생했습니다.",
      );
    } finally {
      setExporting(false);
    }
  };

  useEffect(() => {
    // 검색어가 없으면 결과 초기화
    if (searchQuery.trim() === "") {
      setServers([]);
      setServices([]);
      setLoading(false);
      setError(null);
      return;
    }

    const searchData = async () => {
      setLoading(true);
      setError(null);
      try {
        if (searchType === "server") {
          const results = await api.searchServers(searchQuery.trim());
          console.log("Server search results:", results);
          setServers(results);
          setServices([]);
        } else {
          const results = await api.searchServices(searchQuery.trim());
          console.log("Service search results:", results);
          setServices(results);
          setServers([]);
        }
      } catch (err: any) {
        console.error("Search error:", err);
        setError(err.response?.data?.detail || "검색 중 오류가 발생했습니다.");
        setServers([]);
        setServices([]);
      } finally {
        setLoading(false);
      }
    };

    const debounce = setTimeout(searchData, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery, searchType]);

  return (
    <div className="search-container">
      <div className="search-header">
        <h2>
          {searchType === "server" ? "서버 프로세스 검색" : "서비스(TR) 검색"}
        </h2>
        {canExport && (
          <button
            className="export-btn"
            onClick={handleExport}
            disabled={exporting}
          >
            {exporting ? "다운로드 중..." : "엑셀 다운로드 (전체)"}
          </button>
        )}
      </div>

      <div className="search-input-wrapper">
        <input
          type="text"
          className="search-input"
          placeholder={`${searchType === "server" ? "서버 프로세스" : "서비스(TR)"} 이름을 검색하세요...`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        {loading && <span className="search-loading">검색 중...</span>}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="search-results">
        {searchType === "server" && servers.length > 0 && (
          <div className="results-list">
            <div className="results-count">
              {servers.length}개의 서버 프로세스를 찾았습니다
            </div>
            {servers.map((server, index) => (
              <div
                key={`${server.name}-${server.svg}-${index}`}
                className="result-item"
                onClick={() => onServerClick(server.name)}
              >
                <div className="result-name">{server.name}</div>
                <div className="result-details">
                  <span>그룹: {server.svg}</span>
                  <span>노드: {server.node || "N/A"}</span>
                  <span>
                    프로세스: {server.min}-{server.max}
                  </span>
                  {server.maxqcount && (
                    <span>MAXQCOUNT: {server.maxqcount}</span>
                  )}
                  {server.asqcount && <span>ASQCOUNT: {server.asqcount}</span>}
                  {server.db_info && <span>DB: {server.db_info}</span>}
                </div>
              </div>
            ))}
          </div>
        )}

        {searchType === "service" && services.length > 0 && (
          <div className="results-list">
            <div className="results-count">
              {services.length}개의 서비스(TR)를 찾았습니다
            </div>
            {services.map((service, index) => (
              <div
                key={`${service.name}-${service.server}-${index}`}
                className="result-item"
                onClick={() => onServiceClick(service.name)}
              >
                <div className="result-name">{service.name}</div>
                <div className="result-details">
                  <span>서버 프로세스: {service.server}</span>
                  <span>타임아웃: {service.timeout}</span>
                  <span>Export: {service.export}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading &&
          !error &&
          searchQuery.trim() !== "" &&
          servers.length === 0 &&
          services.length === 0 && (
            <div className="no-results">검색 결과가 없습니다.</div>
          )}

        {searchQuery.trim() === "" && (
          <div className="no-results">
            {searchType === "server" ? "서버 프로세스" : "서비스(TR)"} 이름을
            입력하여 검색하세요
          </div>
        )}
      </div>
    </div>
  );
};
