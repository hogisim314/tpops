import React from "react";

interface StatCardProps {
  icon: string;
  label: string;
  value: string;
}

export const StatCard: React.FC<StatCardProps> = ({ icon, label, value }) => {
  return (
    <div className="stat-card">
      <div className="icon">{icon}</div>
      <div className="label">{label}</div>
      <div className="value">{value}</div>
    </div>
  );
};
