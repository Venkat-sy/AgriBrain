import React from 'react';

const Settings = () => {
    const settings = [
        { category: 'Data', items: ['Dataset Source', 'Preprocessing Options', 'Feature Selection'] },
        { category: 'Models', items: ['Model Selection', 'Hyperparameters', 'Validation Strategy'] },
        { category: 'Notifications', items: ['Alert Thresholds', 'Email Notifications', 'Dashboard Refresh Rate'] },
        { category: 'System', items: ['API Keys', 'Storage Path', 'Log Level'] },
    ];

    return (
        <div className="fade-in">
            <div className="panel top-panel">
                <div className="panel-header">
                    <div>
                        <h2>⚙️ Settings</h2>
                        <p className="subtitle">Configure your AgriBrain dashboard preferences</p>
                    </div>
                    <button className="pill-btn">Save Changes</button>
                </div>
            </div>

            <div className="dashboard-grid" style={{ marginTop: '1.5rem' }}>
                {settings.map((group, gi) => (
                    <div key={gi} className="panel">
                        <div className="panel-header">
                            <h2>{group.category}</h2>
                        </div>
                        <div className="action-list">
                            {group.items.map((item, ii) => (
                                <div key={ii} className="action-item">
                                    <div className="action-icon">⚙️</div>
                                    <div className="action-text">
                                        <span className="action-title">{item}</span>
                                        <span className="action-sub">Configure {item.toLowerCase()}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <div className="panel" style={{ marginTop: '1.5rem' }}>
                <div className="panel-header">
                    <h2>📊 System Health</h2>
                </div>
                <div className="metrics-row">
                    <div className="metric-item">
                        <div className="metric-icon green">🧠</div>
                        <div className="metric-info">
                            <span className="metric-label">GPU Usage</span>
                            <span className="metric-value green">34%</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon cyan">💾</div>
                        <div className="metric-info">
                            <span className="metric-label">Storage</span>
                            <span className="metric-value">67GB / 128GB</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon purple">🌐</div>
                        <div className="metric-info">
                            <span className="metric-label">API Calls</span>
                            <span className="metric-value">1.2K/day</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Settings;