import React from "react";
import type { ServerDetail } from "../types";

interface ServerDetailModalProps {
  serverInfo: ServerDetail;
}

export const ServerDetailModal: React.FC<ServerDetailModalProps> = ({
  serverInfo,
}) => {
  return (
    <div className="detail-content">
      <h3>서버 정보</h3>

      <div className="info-grid">
        <div className="info-item">
          <strong>서버 이름:</strong>
          <span>{serverInfo.name}</span>
        </div>
        <div className="info-item">
          <strong>서버 그룹:</strong>
          <span>{serverInfo.svg_name}</span>
        </div>
        <div className="info-item">
          <strong>노드:</strong>
          <span>{serverInfo.node_name}</span>
        </div>
        <div className="info-item">
          <strong>최소 프로세스:</strong>
          <span>{serverInfo.min_proc}</span>
        </div>
        <div className="info-item">
          <strong>최대 프로세스:</strong>
          <span>{serverInfo.max_proc}</span>
        </div>
        <div className="info-item">
          <strong>재시작 정책:</strong>
          <span>{serverInfo.restart}</span>
        </div>
        {serverInfo.maxqcount && (
          <div className="info-item">
            <strong>MAXQCOUNT:</strong>
            <span>{serverInfo.maxqcount}</span>
          </div>
        )}
        {serverInfo.asqcount && (
          <div className="info-item">
            <strong>ASQCOUNT:</strong>
            <span>{serverInfo.asqcount}</span>
          </div>
        )}
        {serverInfo.db_info && (
          <div className="info-item">
            <strong>DB 연결:</strong>
            <span>{serverInfo.db_info}</span>
          </div>
        )}
      </div>

      {serverInfo.services && serverInfo.services.length > 0 && (
        <>
          <h4>연결된 서비스 ({serverInfo.services.length}개)</h4>
          <div className="service-list">
            {serverInfo.services.map((service, index) => (
              <div key={index} className="service-item">
                <div className="service-name">{service.name}</div>
                <div className="service-details">
                  <span>타임아웃: {service.timeout}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
