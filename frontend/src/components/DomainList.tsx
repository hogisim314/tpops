import React from "react";
import type { Summary } from "../types";

interface DomainListProps {
  summary: Summary;
}

export const DomainList: React.FC<DomainListProps> = ({ summary }) => {
  return (
    <div className="entity-list">
      <div className="info-card">
        <h3 style={{ marginBottom: "15px", fontSize: "1.4em" }}>
          도메인 기본 정보
        </h3>
        <div className="info-row">
          <span className="info-label">도메인 ID:</span>
          <span className="info-value">{summary.domain_id}</span>
        </div>
        <div className="info-row">
          <span className="info-label">도메인 이름:</span>
          <span className="info-value">{summary.domain_name}</span>
        </div>
        {summary.domain_shmkey && (
          <div className="info-row">
            <span className="info-label">Shared Memory Key:</span>
            <span className="info-value">{summary.domain_shmkey}</span>
          </div>
        )}
        {summary.domain_tportno && (
          <div className="info-row">
            <span className="info-label">Tmax 포트:</span>
            <span className="info-value">{summary.domain_tportno}</span>
          </div>
        )}
        {summary.domain_racport && (
          <div className="info-row">
            <span className="info-label">RAC 포트:</span>
            <span className="info-value">{summary.domain_racport}</span>
          </div>
        )}
        {summary.domain_security && (
          <div className="info-row">
            <span className="info-label">보안 설정:</span>
            <span className="info-value">{summary.domain_security}</span>
          </div>
        )}
        {summary.domain_loglvl && (
          <div className="info-row">
            <span className="info-label">로그 레벨:</span>
            <span className="info-value">{summary.domain_loglvl}</span>
          </div>
        )}
      </div>

      <div className="info-card" style={{ marginTop: "20px" }}>
        <h3 style={{ marginBottom: "15px", fontSize: "1.4em" }}>리소스 제한</h3>
        {summary.domain_maxuser && (
          <div className="info-row">
            <span className="info-label">최대 사용자:</span>
            <span className="info-value">{summary.domain_maxuser}</span>
          </div>
        )}
        {summary.domain_maxnode && (
          <div className="info-row">
            <span className="info-label">최대 노드:</span>
            <span className="info-value">{summary.domain_maxnode}</span>
          </div>
        )}
        {summary.domain_maxsvg && (
          <div className="info-row">
            <span className="info-label">최대 서버 그룹:</span>
            <span className="info-value">{summary.domain_maxsvg}</span>
          </div>
        )}
        {summary.domain_maxsvr && (
          <div className="info-row">
            <span className="info-label">최대 서버:</span>
            <span className="info-value">{summary.domain_maxsvr}</span>
          </div>
        )}
        {summary.domain_maxsvc && (
          <div className="info-row">
            <span className="info-label">최대 서비스:</span>
            <span className="info-value">{summary.domain_maxsvc}</span>
          </div>
        )}
        {summary.domain_maxgw && (
          <div className="info-row">
            <span className="info-label">최대 게이트웨이:</span>
            <span className="info-value">{summary.domain_maxgw}</span>
          </div>
        )}
        {summary.domain_maxsession && (
          <div className="info-row">
            <span className="info-label">최대 세션:</span>
            <span className="info-value">{summary.domain_maxsession}</span>
          </div>
        )}
      </div>

      <div className="info-card" style={{ marginTop: "20px" }}>
        <h3 style={{ marginBottom: "15px", fontSize: "1.4em" }}>현재 상태</h3>
        <div className="info-row">
          <span className="info-label">총 노드 수:</span>
          <span className="info-value">{summary.total_nodes}개</span>
        </div>
        <div className="info-row">
          <span className="info-label">총 서버 그룹 수:</span>
          <span className="info-value">{summary.total_server_groups}개</span>
        </div>
        <div className="info-row">
          <span className="info-label">총 서버 수:</span>
          <span className="info-value">{summary.total_servers}개</span>
        </div>
        <div className="info-row">
          <span className="info-label">총 서비스 수:</span>
          <span className="info-value">{summary.total_services}개</span>
        </div>
        <div className="info-row">
          <span className="info-label">총 게이트웨이 수:</span>
          <span className="info-value">{summary.total_gateways}개</span>
        </div>
      </div>
    </div>
  );
};
