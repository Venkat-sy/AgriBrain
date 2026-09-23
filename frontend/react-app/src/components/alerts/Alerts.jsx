import React from 'react';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';
import Button from '../common/Button';
import { getRelativeTime, getStatusColor } from '../../utils/helpers';

const Alerts = () => {
    const { alerts, markAlertAsRead, dismissAlert } = useApp();
    const unreadAlerts = alerts.filter(a => !a.read);
    const readAlerts = alerts.filter(a => a.read);

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <h1 className="page-title">Alerts</h1>
                <p className="page-subtitle">{unreadAlerts.length} unread notification{unreadAlerts.length !== 1 ? 's' : ''}</p>
            </div>

            {unreadAlerts.length > 0 && (
                <Card className="mb-3">
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Unread Alerts</h2>
                    {unreadAlerts.map(alert => (
                        <div 
                            key={alert.id}
                            style={{
                                padding: '1.25rem',
                                marginBottom: '0.75rem',
                                background: 'white',
                                border: `2px solid ${getStatusColor(alert.type)}`,
                                borderLeft: `6px solid ${getStatusColor(alert.type)}`,
                                borderRadius: 'var(--radius-md)'
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span className={`badge badge-${alert.type === 'critical' ? 'danger' : 
                                                                 alert.type === 'warning' ? 'warning' : 'info'}`}>
                                    {alert.type}
                                </span>
                                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                    {getRelativeTime(alert.timestamp)}
                                </div>
                            </div>
                            <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                {alert.title}
                            </h3>
                            <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                                {alert.message}
                            </p>
                            <div style={{ display: 'flex', gap: '0.75rem' }}>
                                <Button size="small" onClick={() => markAlertAsRead(alert.id)}>
                                    Mark as Read
                                </Button>
                                {!alert.actionRequired && (
                                    <Button size="small" variant="outline" onClick={() => dismissAlert(alert.id)}>
                                        Dismiss
                                    </Button>
                                )}
                            </div>
                        </div>
                    ))}
                </Card>
            )}

            {readAlerts.length > 0 && (
                <Card>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>Read Alerts</h2>
                    {readAlerts.map(alert => (
                        <div 
                            key={alert.id}
                            style={{
                                padding: '1rem',
                                marginBottom: '0.75rem',
                                background: 'var(--bg-secondary)',
                                borderLeft: `4px solid ${getStatusColor(alert.type)}`,
                                borderRadius: 'var(--radius-md)',
                                opacity: 0.7
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                                <h3 style={{ fontSize: '1rem', fontWeight: '600' }}>{alert.title}</h3>
                                <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                                    {getRelativeTime(alert.timestamp)}
                                </div>
                            </div>
                            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                {alert.message}
                            </p>
                        </div>
                    ))}
                </Card>
            )}

            {alerts.length === 0 && (
                <Card>
                    <div style={{ textAlign: 'center', padding: '4rem' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🔔</div>
                        <h2>No Alerts</h2>
                        <p style={{ color: 'var(--text-muted)' }}>You're all caught up!</p>
                    </div>
                </Card>
            )}
        </div>
    );
};

export default Alerts;
