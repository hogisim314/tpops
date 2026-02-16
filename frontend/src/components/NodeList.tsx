import React from "react";

interface NodeListProps {
  nodes: string[];
  onNodeClick: (nodeName: string) => void;
}

export const NodeList: React.FC<NodeListProps> = ({ nodes, onNodeClick }) => {
  if (nodes.length === 0) {
    return <p>노드가 없습니다.</p>;
  }

  return (
    <ul className="item-list">
      {nodes.map((node) => (
        <li key={node} className="list-item" onClick={() => onNodeClick(node)}>
          <div className="item-name">
            {node}
            <span className="status-badge status-active">활성</span>
          </div>
          <div className="item-info">클릭하여 상세 정보 보기</div>
        </li>
      ))}
    </ul>
  );
};
