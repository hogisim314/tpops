import React, { useState } from "react";
import type { ServiceDetail } from "../types";
import ServicePerformance from "./ServicePerformance";

interface ServiceDetailModalProps {
  serviceInfo: ServiceDetail;
  onServerClick?: (serverName: string) => void;
}

export const ServiceDetailModal: React.FC<ServiceDetailModalProps> = ({
  serviceInfo,
  onServerClick,
}) => {
  const [activeTab, setActiveTab] = useState<"info" | "performance">("info");

  return (
    <div className="detail-content">
      {/* 탭 헤더 */}
      <div className="detail-tabs">
        <button
          className={`tab-button ${activeTab === "info" ? "active" : ""}`}
          onClick={() => setActiveTab("info")}
        >
          서비스(TR) 정보
        </button>
        <button
          className={`tab-button ${activeTab === "performance" ? "active" : ""}`}
          onClick={() => setActiveTab("performance")}
        >
          응답시간
        </button>
      </div>

      {/* 탭 컨텐츠 */}
      {activeTab === "info" ? (
        <>
          <div className="info-grid">
            <div className="info-item">
              <strong>서비스 이름:</strong>
              <span>{serviceInfo.name}</span>
            </div>
            <div className="info-item">
              <strong>타임아웃:</strong>
              <span>{serviceInfo.timeout}</span>
            </div>
          </div>

          {serviceInfo.server_info && (
            <>
              <h4>소속 서버 프로세스</h4>
              <div className="info-grid">
                <div className="info-item">
                  <strong>서버 프로세스 이름:</strong>
                  {onServerClick ? (
                    <span
                      style={{
                        color: "#3a7bd5",
                        cursor: "pointer",
                        textDecoration: "underline",
                      }}
                      onClick={() => onServerClick(serviceInfo.server_name)}
                    >
                      {serviceInfo.server_name}
                    </span>
                  ) : (
                    <span>{serviceInfo.server_name}</span>
                  )}
                </div>
                <div className="info-item">
                  <strong>서버 그룹:</strong>
                  <span>{serviceInfo.server_info.svg_name}</span>
                </div>
                <div className="info-item">
                  <strong>노드:</strong>
                  <span>{serviceInfo.server_info.node_name}</span>
                </div>
                <div className="info-item">
                  <strong>프로세스 MIN:</strong>
                  <span>{serviceInfo.server_info.min_proc}</span>
                </div>
                <div className="info-item">
                  <strong>프로세스 MAX:</strong>
                  <span>{serviceInfo.server_info.max_proc}</span>
                </div>
              </div>
            </>
          )}
        </>
      ) : (
        <ServicePerformance serviceName={serviceInfo.name} isEmbedded={true} />
      )}
    </div>
  );
};
