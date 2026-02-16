import React from "react";

interface SvrGroupListProps {
  serverGroups: string[];
  onSvrGroupClick: (svgName: string) => void;
}

export const SvrGroupList: React.FC<SvrGroupListProps> = ({
  serverGroups,
  onSvrGroupClick,
}) => {
  if (serverGroups.length === 0) {
    return <p>서버 그룹이 없습니다.</p>;
  }

  return (
    <ul className="item-list">
      {serverGroups.map((svg) => (
        <li
          key={svg}
          className="list-item"
          onClick={() => onSvrGroupClick(svg)}
        >
          <div className="item-name">
            {svg}
            <span className="status-badge status-active">실행 중</span>
          </div>
          <div className="item-info">클릭하여 상세 정보 보기</div>
        </li>
      ))}
    </ul>
  );
};
