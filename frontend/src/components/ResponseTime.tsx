import React, { useState, useEffect } from "react";
import "../App.css";
import { api } from "../api";
import type { ServicePerformanceSummary } from "../types";

interface ResponseTimeProps {
  onServiceClick?: (serviceName: string) => void;
}

export const ResponseTime: React.FC<ResponseTimeProps> = ({
  onServiceClick,
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [performanceData, setPerformanceData] = useState<
    ServicePerformanceSummary[]
  >([]);
  const [sortBy, setSortBy] = useState<"avgTime" | "maxTime" | "count">(
    "avgTime",
  );
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadPerformanceData();
  }, []);

  const loadPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getServicesPerformance();
      setPerformanceData(data);
    } catch (err) {
      console.error("Error loading performance data:", err);
      setError("응답시간 데이터를 불러오는 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (ms: number | null) => {
    if (ms === null || ms === undefined) return "N/A";
    if (ms < 1) return `${(ms * 1000).toFixed(0)}μs`;
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getPerformanceColor = (avgTime: number | null) => {
    if (avgTime === null) return "#999";
    if (avgTime < 100) return "#10b981"; // 녹색 - 빠름
    if (avgTime < 500) return "#f59e0b"; // 주황 - 보통
    return "#ef4444"; // 빨강 - 느림
  };

  const handleSort = (field: "avgTime" | "maxTime" | "count") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
  };

  const filteredAndSortedData = performanceData
    .filter((item) =>
      item.serviceName.toLowerCase().includes(searchTerm.toLowerCase()),
    )
    .sort((a, b) => {
      const aVal = a[sortBy] ?? 0;
      const bVal = b[sortBy] ?? 0;
      const diff = sortOrder === "asc" ? aVal - bVal : bVal - aVal;
      return diff;
    });

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>응답시간 데이터를 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="response-time-container">
      <div className="response-time-header">
        <h2>서비스 응답시간 모니터링</h2>
        <div className="response-time-controls">
          <input
            type="text"
            placeholder="서비스 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <button onClick={loadPerformanceData} className="refresh-btn">
            새로고침
          </button>
        </div>
      </div>

      <div className="performance-summary-grid">
        <div className="summary-card">
          <div className="summary-card-label">총 서비스</div>
          <div className="summary-card-value">{performanceData.length}</div>
        </div>
        <div className="summary-card">
          <div className="summary-card-label">평균 응답시간</div>
          <div className="summary-card-value">
            {formatDuration(
              performanceData.reduce(
                (sum, item) => sum + (item.avgTime ?? 0),
                0,
              ) / performanceData.length,
            )}
          </div>
        </div>
        <div className="summary-card">
          <div className="summary-card-label">총 요청 수</div>
          <div className="summary-card-value">
            {performanceData
              .reduce((sum, item) => sum + (item.count ?? 0), 0)
              .toLocaleString()}
          </div>
        </div>
      </div>

      <div className="response-time-table-container">
        <table className="response-time-table">
          <thead>
            <tr>
              <th>서비스명</th>
              <th
                onClick={() => handleSort("avgTime")}
                className="sortable"
                style={{ cursor: "pointer" }}
              >
                평균 응답시간{" "}
                {sortBy === "avgTime" && (sortOrder === "asc" ? "↑" : "↓")}
              </th>
              <th>최소</th>
              <th
                onClick={() => handleSort("maxTime")}
                className="sortable"
                style={{ cursor: "pointer" }}
              >
                최대 {sortBy === "maxTime" && (sortOrder === "asc" ? "↑" : "↓")}
              </th>
              <th
                onClick={() => handleSort("count")}
                className="sortable"
                style={{ cursor: "pointer" }}
              >
                요청 수{" "}
                {sortBy === "count" && (sortOrder === "asc" ? "↑" : "↓")}
              </th>
              <th>상태</th>
            </tr>
          </thead>
          <tbody>
            {filteredAndSortedData.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  style={{ textAlign: "center", padding: "2rem" }}
                >
                  {searchTerm
                    ? "검색 결과가 없습니다."
                    : "응답시간 데이터가 없습니다."}
                </td>
              </tr>
            ) : (
              filteredAndSortedData.map((item) => (
                <tr
                  key={item.serviceName}
                  onClick={() => onServiceClick?.(item.serviceName)}
                  className="clickable"
                >
                  <td>
                    <strong>{item.serviceName}</strong>
                  </td>
                  <td>
                    <span
                      style={{
                        color: getPerformanceColor(item.avgTime),
                        fontWeight: "bold",
                      }}
                    >
                      {formatDuration(item.avgTime)}
                    </span>
                  </td>
                  <td>{formatDuration(item.minTime)}</td>
                  <td>{formatDuration(item.maxTime)}</td>
                  <td>{item.count?.toLocaleString() ?? "0"}</td>
                  <td>
                    {item.avgTime !== null && item.avgTime < 100 && (
                      <span className="status-badge status-good">양호</span>
                    )}
                    {item.avgTime !== null &&
                      item.avgTime >= 100 &&
                      item.avgTime < 500 && (
                        <span className="status-badge status-warning">
                          주의
                        </span>
                      )}
                    {item.avgTime !== null && item.avgTime >= 500 && (
                      <span className="status-badge status-critical">느림</span>
                    )}
                    {item.avgTime === null && (
                      <span className="status-badge">데이터 없음</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <style>{`
        .response-time-container {
          padding: 1rem;
        }

        .response-time-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
        }

        .response-time-header h2 {
          margin: 0;
          font-size: 1.5rem;
          color: #1f2937;
        }

        .response-time-controls {
          display: flex;
          gap: 0.5rem;
        }

        .search-input {
          padding: 0.5rem 1rem;
          border: 1px solid #d1d5db;
          border-radius: 6px;
          font-size: 0.875rem;
          min-width: 200px;
        }

        .search-input:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        .performance-summary-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .summary-card {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          text-align: center;
        }

        .summary-card-label {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .summary-card-value {
          font-size: 1.875rem;
          font-weight: bold;
          color: #1f2937;
        }

        .response-time-table-container {
          background: white;
          border-radius: 8px;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }

        .response-time-table {
          width: 100%;
          border-collapse: collapse;
        }

        .response-time-table thead {
          background: #f9fafb;
          border-bottom: 2px solid #e5e7eb;
        }

        .response-time-table th {
          padding: 0.75rem 1rem;
          text-align: left;
          font-size: 0.875rem;
          font-weight: 600;
          color: #374151;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .response-time-table th.sortable:hover {
          background: #f3f4f6;
        }

        .response-time-table tbody tr {
          border-bottom: 1px solid #e5e7eb;
          transition: background-color 0.2s;
        }

        .response-time-table tbody tr:hover {
          background: #f9fafb;
        }

        .response-time-table tbody tr.clickable {
          cursor: pointer;
        }

        .response-time-table td {
          padding: 1rem;
          font-size: 0.875rem;
          color: #1f2937;
        }

        .status-badge {
          display: inline-block;
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 600;
          background: #e5e7eb;
          color: #6b7280;
        }

        .status-good {
          background: #d1fae5;
          color: #065f46;
        }

        .status-warning {
          background: #fef3c7;
          color: #92400e;
        }

        .status-critical {
          background: #fee2e2;
          color: #991b1b;
        }
      `}</style>
    </div>
  );
};
