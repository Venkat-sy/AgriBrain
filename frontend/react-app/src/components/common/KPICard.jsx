import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import './KPICard.css';

/**
 * Compact KPI Card for displaying key metrics with trends
 * Premium SaaS style with subtle animations
 */
const KPICard = ({ 
    icon: Icon, 
    label, 
    value, 
    trend, 
    trendValue, 
    subtitle,
    color = 'forest',
    onClick 
}) => {
    const getTrendIcon = () => {
        if (trend === 'up') return <TrendingUp size={14} />;
        if (trend === 'down') return <TrendingDown size={14} />;
        return <Minus size={14} />;
    };

    const getTrendClass = () => {
        if (trend === 'up') return 'kpi-trend-up';
        if (trend === 'down') return 'kpi-trend-down';
        return 'kpi-trend-neutral';
    };

    return (
        <div 
            className={`kpi-card kpi-card-${color}`}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            <div className="kpi-header">
                <div className={`kpi-icon kpi-icon-${color}`}>
                    {Icon && <Icon size={20} strokeWidth={2} />}
                </div>
                {trendValue && (
                    <div className={`kpi-trend ${getTrendClass()}`}>
                        {getTrendIcon()}
                        <span>{trendValue}</span>
                    </div>
                )}
            </div>
            
            <div className="kpi-body">
                <div className="kpi-value">{value}</div>
                <div className="kpi-label">{label}</div>
                {subtitle && <div className="kpi-subtitle">{subtitle}</div>}
            </div>
        </div>
    );
};

export default KPICard;
