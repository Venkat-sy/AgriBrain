import React from 'react';
import './StatCard.css';

const StatCard = ({ icon, label, value, subtitle, color = 'primary', trend, onClick }) => {
    return (
        <div 
            className={`stat-card stat-card-${color}`}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            <div className="stat-icon">{icon}</div>
            <div className="stat-content">
                <div className="stat-label">{label}</div>
                <div className="stat-value">{value}</div>
                {subtitle && <div className="stat-subtitle">{subtitle}</div>}
                {trend && (
                    <div className={`stat-trend ${trend.direction}`}>
                        {trend.direction === 'up' ? '↑' : '↓'} {trend.value}
                    </div>
                )}
            </div>
        </div>
    );
};

export default StatCard;
