import React from 'react';
import './ChartCard.css';

/**
 * Chart Card - Container for data visualizations
 * Provides consistent styling for charts with headers, actions, and legends
 */
const ChartCard = ({ 
    title, 
    subtitle,
    action,
    children,
    className = '',
    size = 'default',
    noPadding = false
}) => {
    return (
        <div className={`chart-card chart-card-${size} ${className}`}>
            {(title || subtitle || action) && (
                <div className="chart-card-header">
                    <div className="chart-card-header-content">
                        {title && <h3 className="chart-card-title">{title}</h3>}
                        {subtitle && <p className="chart-card-subtitle">{subtitle}</p>}
                    </div>
                    {action && (
                        <div className="chart-card-action">
                            {action}
                        </div>
                    )}
                </div>
            )}
            <div className={`chart-card-body ${noPadding ? 'no-padding' : ''}`}>
                {children}
            </div>
        </div>
    );
};

export default ChartCard;
