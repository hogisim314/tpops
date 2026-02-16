import React, { useState } from "react";
import "../App.css";

interface PerformanceData {
  avgTime: number;
  minTime: number;
  maxTime: number;
  medianTime: number;
  count: number;
  slowTransactions: {
    timestamp: string;
    duration: number;
    status: string;
  }[];
  timeSeriesData: {
    timestamp: string;
    avgDuration: number;
    count: number;
  }[];
}

interface ServicePerformanceProps {
  serviceName: string;
  onClose?: () => void;
  isEmbedded?: boolean;
}

const ServicePerformance: React.FC<ServicePerformanceProps> = ({
  serviceName,
  onClose,
  isEmbedded = false,
}) => {
  const [startDate, setStartDate] = useState(() => {
    const date = new Date();
    date.setHours(date.getHours() - 24);
    return date.toISOString().slice(0, 16);
  });

  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().slice(0, 16);
  });

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<PerformanceData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/performance/${serviceName}?start=${startDate}&end=${endDate}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        },
      );

      if (!response.ok) {
        throw new Error("데이터를 가져오는데 실패했습니다");
      }

      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다",
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms.toFixed(2)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const formatDateTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString("ko-KR", {
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  };

  const content = (
    <>
      {!isEmbedded && (
        <div className="modal-header">
          <h2>성능 분석 - {serviceName}</h2>
        </div>
      )}

      <div className={isEmbedded ? "tab-content-body" : "modal-body"}>
        {/* 검색 조건 */}
        <div className="search-section">
          <div className="date-range-picker">
            <div className="date-input-group">
              <label>시작 시간</label>
              <input
                type="datetime-local"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                max={endDate}
              />
            </div>
            <span className="date-separator">~</span>
            <div className="date-input-group">
              <label>종료 시간</label>
              <input
                type="datetime-local"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                min={startDate}
                max={new Date().toISOString().slice(0, 16)}
              />
            </div>
          </div>

          <div className="quick-select-buttons">
            <button
              onClick={() => {
                const end = new Date();
                const start = new Date(end.getTime() - 60 * 60 * 1000);
                setStartDate(start.toISOString().slice(0, 16));
                setEndDate(end.toISOString().slice(0, 16));
              }}
            >
              최근 1시간
            </button>
            <button
              onClick={() => {
                const end = new Date();
                const start = new Date(end.getTime() - 24 * 60 * 60 * 1000);
                setStartDate(start.toISOString().slice(0, 16));
                setEndDate(end.toISOString().slice(0, 16));
              }}
            >
              최근 24시간
            </button>
            <button
              onClick={() => {
                const end = new Date();
                const start = new Date(end.getTime() - 7 * 24 * 60 * 60 * 1000);
                setStartDate(start.toISOString().slice(0, 16));
                setEndDate(end.toISOString().slice(0, 16));
              }}
            >
              최근 7일
            </button>
          </div>

          <button
            className="search-button"
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "조회 중..." : "조회"}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {data && (
          <>
            {/* 통계 카드 */}
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">총 호출 수</div>
                <div className="stat-value">{data.count.toLocaleString()}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">평균 처리시간</div>
                <div className="stat-value highlight">
                  {formatDuration(data.avgTime)}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">최소 처리시간</div>
                <div className="stat-value success">
                  {formatDuration(data.minTime)}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">최대 처리시간</div>
                <div className="stat-value warning">
                  {formatDuration(data.maxTime)}
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-label">중앙값</div>
                <div className="stat-value">
                  {formatDuration(data.medianTime)}
                </div>
              </div>
            </div>

            {/* 시계열 그래프 */}
            <div className="chart-section">
              <h3>시간대별 평균 처리시간</h3>
              <div className="simple-chart">
                {data.timeSeriesData.length > 0 ? (
                  <div className="bar-chart">
                    {data.timeSeriesData.map((item, index) => {
                      const maxDuration = Math.max(
                        ...data.timeSeriesData.map((d) => d.avgDuration),
                      );
                      const heightPercent =
                        (item.avgDuration / maxDuration) * 100;

                      return (
                        <div key={index} className="bar-item">
                          <div className="bar-wrapper">
                            <div
                              className="bar"
                              style={{
                                height: `${heightPercent}%`,
                                backgroundColor:
                                  item.avgDuration > data.avgTime * 1.5
                                    ? "#e74c3c"
                                    : "#3498db",
                              }}
                              title={`${formatDateTime(item.timestamp)}\n평균: ${formatDuration(item.avgDuration)}\n호출수: ${item.count}`}
                            >
                              <span className="bar-value">
                                {formatDuration(item.avgDuration)}
                              </span>
                            </div>
                          </div>
                          <div className="bar-label">
                            {formatDateTime(item.timestamp).split(" ")[1]}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="no-data">데이터가 없습니다</div>
                )}
              </div>
            </div>

            {/* 느린 트랜잭션 목록 */}
            <div className="slow-transactions-section">
              <h3>느린 트랜잭션 Top 10</h3>
              {data.slowTransactions.length > 0 ? (
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>순위</th>
                      <th>발생 시간</th>
                      <th>처리시간</th>
                      <th>상태</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.slowTransactions.map((tx, index) => (
                      <tr key={index}>
                        <td>{index + 1}</td>
                        <td>{formatDateTime(tx.timestamp)}</td>
                        <td className="duration-cell">
                          <span
                            className={
                              tx.duration > data.avgTime * 2
                                ? "critical"
                                : "warning"
                            }
                          >
                            {formatDuration(tx.duration)}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`status-badge ${tx.status === "success" ? "success" : "error"}`}
                          >
                            {tx.status === "success" ? "성공" : "실패"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="no-data">느린 트랜잭션이 없습니다</div>
              )}
            </div>
          </>
        )}

        {!data && !loading && !error && (
          <div className="empty-state">
            <p>기간을 선택하고 조회 버튼을 클릭하세요</p>
          </div>
        )}
      </div>
    </>
  );

  if (isEmbedded) {
    return content;
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content performance-modal"
        onClick={(e) => e.stopPropagation()}
      >
        {content}
      </div>
    </div>
  );
};

export default ServicePerformance;
