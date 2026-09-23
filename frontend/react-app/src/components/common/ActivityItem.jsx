import React from 'react';
import { AlertCircle, CheckCircle, Info, TrendingUp, Activity } from 'lucide-react';
import { getRelativeTime } from '../../utils/helpers';
import './ActivityItem.css';

/**
 * Activity Item - Display recent events and activities
 */
const ActivityItem = ({ 
    type = 'info',
    title, 
    description,
    timestamp,
    metadata,
    onClick
}) => {
    const getIcon = () => {
        switch(type) {
            case 'success': return <CheckCircle size={16} />;
            case 'warning': return <AlertCircle size={16} />;
            case 'error': return <AlertCircle size={16} />;
            case 'trend': return <TrendingUp size={16} />;
            case 'activity': return <Activity size={16} />;
            default: return <Info size={16} />;
        }
    };

    return (
        <div 
            className={`activity-item activity-item-${type}`}
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            <div className={`activity-icon activity-icon-${type}`}>
                {getIcon()}
            </div>
            <div className="activity-content">
                <div className="activity-header">
                    <span className="activity-title">{title}</span>
                    <span className="activity-time">{getRelativeTime(timestamp)}</span>
                </div>
                {description && (
                    <p className="activity-description">{description}</p>
                )}
                {metadata && (
                    <div className="activity-metadata">
                        {metadata}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ActivityItem;
