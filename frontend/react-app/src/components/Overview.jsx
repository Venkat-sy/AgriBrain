import React, { useState } from 'react';

const Overview = () => {
    const [activeTab, setActiveTab] = useState('dashboard');

    const metrics = [
        { icon: '🌡️', color: 'cyan', label: 'Temperature', value: '28.4°C', sub: 'Optimal' },
        { icon: '💧', color: 'green', label: 'Moisture', value: '67%', sub: 'Good' },
        { icon: '🌱', color: 'purple', label: 'NPK Index', value: '8.2', sub: 'High' },
        { icon: '📈', color: 'pink', label: 'Yield Score', value: '94%', sub: 'Excellent' },
    ];

    const barData = [
        { label: 'N', value: 85, color: '#39ff14' },
        { label: 'P', value: 62, color: '#00ffff' },
        { label: 'K', value: 78, color: '#bf00ff' },
        { label: 'pH', value: 91, color: '#ff0080' },
        { label: 'Rain', value: 45, color: '#ffff00' },
        { label: 'Temp', value: 73, color: '#ff6b00' },
    ];

    const timeline = [
        { marker: '✅', status: 'completed', title: 'Data Collection', period: 'Phase 1 • Complete', desc: '10,000-row synthetic dataset generated with Digital Twin logic.' },
        { marker: '✅', status: 'completed', title: 'Model Training', period: 'Phase 2 • Complete', desc: 'RF + XGBoost models trained with GridSearchCV hyperparameter tuning.' },
        { marker: '🔄', status: 'active', title: 'SHAP Explainability', period: 'Phase 3 • In Progress', desc: 'Generating feature importance plots and waterfall charts for XAI.' },
        { marker: '⏳', status: 'upcoming', title: 'Frontend Deployment', period: 'Phase 4 • Upcoming', desc: 'React dashboard with component-based architecture and CI/CD.' },
        { marker: '⏳', status: 'upcoming', title: 'Field Testing', period: 'Phase 5 • Upcoming', desc: 'Deploy to Indian smallholder farms with pilot program.' },
    ];

    return (
        <div className="fade-in">
            <div className="panel top-panel">
                <div className="panel-header">
                    <div>
                        <h2>🌾 Crop Health Overview</h2>
                        <p className="subtitle">Real-time agricultural intelligence dashboard</p>
                    </div>
                    <button className="pill-btn">Live Data</button>
                </div>

                <div className="metrics-row">
                    {metrics.map((m, i) => (
                        <React.Fragment key={i}>
                            <div className="metric-item">
                                <div className={`metric-icon ${m.color}`}>{m.icon}</div>
                                <div className="metric-info">
                                    <span className="metric-label">{m.label}</span>
                                    <span className={`metric-value ${m.color === 'green' ? 'green' : ''}`}>{m.value}</span>
                                </div>
                            </div>
                            {i < metrics.length - 1 && <div className="metric-divider" />}
                        </React.Fragment>
                    ))}
                </div>
            </div>

            <div className="dashboard-grid" style={{ marginTop: '1.5rem' }}>
                <div className="panel inputs-panel">
                    <div className="panel-header">
                        <h2>📊 Soil Analysis</h2>
                    </div>
                    <div className="bar-chart-container">
                        <div className="y-axis">
                            <span>100</span><span>80</span><span>60</span><span>40</span><span>20</span><span>0</span>
                        </div>
                        <div className="chart-bars">
                            {barData.map((bar, i) => (
                                <div key={i} className="bar-column">
                                    <span className="bar-value">{bar.value}%</span>
                                    <div className="bar-track">
                                        <div className="bar-fill" style={{ height: `${bar.value}%` }} />
                                    </div>
                                    <span className="bar-label">{bar.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="panel yield-panel">
                    <div className="panel-header">
                        <h2>📋 Project Roadmap</h2>
                    </div>
                    <div className="roadmap-timeline">
                        {timeline.map((item, i) => (
                            <div key={i} className={`timeline-item ${item.status}`}>
                                <div className={`timeline-marker ${item.status === 'active' ? 'pulse-marker' : ''}`}>
                                    {item.marker}
                                </div>
                                <div className="timeline-content">
                                    <h3>{item.title}</h3>
                                    <span className="timeline-period">{item.period}</span>
                                    <p>{item.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Overview;