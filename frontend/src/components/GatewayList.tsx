import React, { useState } from "react";
import { GatewayDetail } from "./GatewayDetail";

interface Gateway {
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

interface GatewayListProps {
  gateways: Gateway[];
}

export const GatewayList: React.FC<GatewayListProps> = ({ gateways }) => {
  const [selectedGateway, setSelectedGateway] = useState<Gateway | null>(null);

  if (!gateways || gateways.length === 0) {
    return <div className="empty-message">등록된 게이트웨이가 없습니다.</div>;
  }

  return (
    <>
      <div className="entity-list">
        {gateways.map((gateway) => (
          <div
            key={gateway.name}
            className="list-item clickable"
            onClick={() => setSelectedGateway(gateway)}
          >
            <div className="item-header">
              <h3>{gateway.name}</h3>
            </div>
            <div className="item-details">
              <span>노드: {gateway.node}</span>
              {gateway.remote_addr && gateway.remote_port && (
                <span>
                  원격: {gateway.remote_addr}:{gateway.remote_port}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {selectedGateway && (
        <GatewayDetail
          gateway={selectedGateway}
          onClose={() => setSelectedGateway(null)}
        />
      )}
    </>
  );
};
