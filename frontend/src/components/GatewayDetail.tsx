import React from "react";

interface GatewayInfo {
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

interface GatewayDetailProps {
  gateway: GatewayInfo;
  onClose: () => void;
}

export const GatewayDetail: React.FC<GatewayDetailProps> = ({
  gateway,
  onClose,
}) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>게이트웨이 상세 정보: {gateway.name}</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>
        <div className="modal-body">
          <table className="detail-table">
            <tbody>
              <tr>
                <th>속성</th>
                <th>값</th>
              </tr>
              <tr>
                <td>게이트웨이명</td>
                <td>{gateway.name}</td>
              </tr>
              <tr>
                <td>노드명</td>
                <td>{gateway.node || "N/A"}</td>
              </tr>
              <tr>
                <td>포트</td>
                <td>{gateway.port || "N/A"}</td>
              </tr>
              <tr>
                <td>원격 주소</td>
                <td>{gateway.remote_addr || "N/A"}</td>
              </tr>
              <tr>
                <td>원격 포트</td>
                <td>{gateway.remote_port || "N/A"}</td>
              </tr>
              {gateway.backup_addr && (
                <tr>
                  <td>백업 주소</td>
                  <td>{gateway.backup_addr}</td>
                </tr>
              )}
              {gateway.backup_port && (
                <tr>
                  <td>백업 포트</td>
                  <td>{gateway.backup_port}</td>
                </tr>
              )}
              {gateway.backup_rgwaddr && (
                <tr>
                  <td>백업 원격 게이트웨이 주소</td>
                  <td>{gateway.backup_rgwaddr}</td>
                </tr>
              )}
              {gateway.backup_rgwportno && (
                <tr>
                  <td>백업 원격 게이트웨이 포트</td>
                  <td>{gateway.backup_rgwportno}</td>
                </tr>
              )}
              <tr>
                <td>방향</td>
                <td>{gateway.direction || "N/A"}</td>
              </tr>
              <tr>
                <td>게이트웨이 타입</td>
                <td>{gateway.gw_type || "N/A"}</td>
              </tr>
              {gateway.cpc && (
                <tr>
                  <td>CPC</td>
                  <td>{gateway.cpc}</td>
                </tr>
              )}
              {gateway.restart && (
                <tr>
                  <td>재시작</td>
                  <td>{gateway.restart}</td>
                </tr>
              )}
              {gateway.clopt && (
                <tr>
                  <td>클라이언트 옵션</td>
                  <td style={{ wordBreak: "break-all" }}>{gateway.clopt}</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
