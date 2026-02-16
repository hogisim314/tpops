import React from "react";
import type { SvrGroupInfo } from "../types";

interface SvrGroupDetailProps {
  svgInfo: SvrGroupInfo;
}

export const SvrGroupDetail: React.FC<SvrGroupDetailProps> = ({ svgInfo }) => {
  return (
    <div>
      <h2>서버 그룹 상세 정보: {svgInfo.svg_name}</h2>
      <table className="detail-table">
        <tbody>
          <tr>
            <th>속성</th>
            <th>값</th>
          </tr>
          <tr>
            <td>노드</td>
            <td>{svgInfo.node || "N/A"}</td>
          </tr>
          <tr>
            <td>백업</td>
            <td>{svgInfo.backup || "None"}</td>
          </tr>
          <tr>
            <td>Cousin</td>
            <td>{svgInfo.cousin || "None"}</td>
          </tr>
          <tr>
            <td>재시작</td>
            <td>{svgInfo.restart || "N/A"}</td>
          </tr>
          <tr>
            <td>자동 백업</td>
            <td>{svgInfo.autobackup || "N/A"}</td>
          </tr>
        </tbody>
      </table>
      {svgInfo.servers && svgInfo.servers.length > 0 ? (
        <>
          <h3 style={{ marginTop: "20px" }}>서버 목록</h3>
          <table className="detail-table">
            <thead>
              <tr>
                <th>서버명</th>
                <th>최소</th>
                <th>최대</th>
                <th>재시작</th>
              </tr>
            </thead>
            <tbody>
              {svgInfo.servers.map((srv, index) => (
                <tr key={index}>
                  <td>{srv.name}</td>
                  <td>{srv.min}</td>
                  <td>{srv.max}</td>
                  <td>{srv.restart}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      ) : (
        <p style={{ marginTop: "20px" }}>서버가 없습니다.</p>
      )}
    </div>
  );
};
