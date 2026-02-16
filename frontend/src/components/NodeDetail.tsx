import React from "react";
import type { NodeInfo } from "../types";

interface NodeDetailProps {
  nodeInfo: NodeInfo;
}

export const NodeDetail: React.FC<NodeDetailProps> = ({ nodeInfo }) => {
  return (
    <div>
      <h2>노드 상세 정보: {nodeInfo.node_name}</h2>
      <table className="detail-table">
        <tbody>
          <tr>
            <th>속성</th>
            <th>값</th>
          </tr>
          <tr>
            <td>호스트명</td>
            <td>{nodeInfo.hostname || "N/A"}</td>
          </tr>
          <tr>
            <td>포트</td>
            <td>{nodeInfo.port || "N/A"}</td>
          </tr>
          <tr>
            <td>최대 서버</td>
            <td>{nodeInfo.max_servers || "N/A"}</td>
          </tr>
          <tr>
            <td>최대 사용자</td>
            <td>{nodeInfo.max_users || "N/A"}</td>
          </tr>
          <tr>
            <td>Tmax Home</td>
            <td>{nodeInfo.tmax_home || "N/A"}</td>
          </tr>
          <tr>
            <td>서버 그룹 수</td>
            <td>
              {nodeInfo.server_groups ? nodeInfo.server_groups.length : 0}
            </td>
          </tr>
        </tbody>
      </table>
      {nodeInfo.server_groups && nodeInfo.server_groups.length > 0 && (
        <>
          <h3 style={{ marginTop: "20px" }}>서버 그룹 목록</h3>
          <ul style={{ listStyle: "none", padding: "10px" }}>
            {nodeInfo.server_groups.map((svg) => (
              <li
                key={svg}
                style={{
                  padding: "8px",
                  margin: "5px 0",
                  background: "#f8f9fa",
                  borderRadius: "5px",
                }}
              >
                {svg}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};
