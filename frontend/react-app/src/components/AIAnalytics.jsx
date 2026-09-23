import React, { useState } from 'react';

import {
    BarChart,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    Legend,
} from 'recharts';
import './AIAnalytics.css';


const AIAnalytics = () => {
    const [activeShap, setActiveShap] = useState('crop');

    const modelData = {
        crop: { rf: { acc: '94.2%', f1: '0.93' }, xgb: { acc: '96.8%', f1: '0.96' } },
        fertilizer: { rf: { acc: '89.1%', f1: '0.88' }, xgb: { acc: '92.3%', f1: '0.92' } },
        yield: { rf: { r2: '0.87' }, xgb: { r2: '0.91' } },
    };

    const shapFeatures = [
        { name: 'Nitrogen', importance: 0.85 },
        { name: 'Phosphorus', importance: 0.72 },
        { name: 'Potassium', importance: 0.68 },
        { name: 'Rainfall', importance: 0.55 },
        { name: 'Temperature', importance: 0.48 },
        { name: 'pH Level', importance: 0.41 },
        { name: 'Humidity', importance: 0.33 },
        { name: 'Area', importance: 0.28 },
    ];

    const shapWaterfall = [
        { name: 'Base', value: 3.2, positive: false },
        { name: 'N', value: 1.8, positive: true },
        { name: 'P', value: 1.2, positive: true },
        { name: 'K', value: 0.9, positive: true },
        { name: 'pH', value: -0.3, positive: false },
        { name: 'Temp', value: 0.7, positive: true },
        { name: 'Final', value: 5.7, positive: true },
    ];

    return (
        <div className="fade-in">
            <div className="panel top-panel">
                <div className="panel-header">
                    <div>
                        <h2>🧠 AI Analytics Dashboard</h2>
                        <p className="subtitle">Model performance metrics and SHAP explainability</p>
                    </div>
                    <div className="pipeline-status-badge">
                        <span className="pulse-dot" />
                        Pipeline Active
                    </div>
                </div>

                <div className="metrics-row">
                    <div className="metric-item">
                        <div className="metric-icon green">🤖</div>
                        <div className="metric-info">
                            <span className="metric-label">Models Trained</span>
                            <span className="metric-value green">8</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon cyan">📊</div>
                        <div className="metric-info">
                            <span className="metric-label">Best Accuracy</span>
                            <span className="metric-value">96.8%</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon purple">✨</div>
                        <div className="metric-info">
                            <span className="metric-label">SHAP Score</span>
                            <span className="metric-value">0.91</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid" style={{ marginTop: '1.5rem' }}>
                <div className="panel inputs-panel">
                    <div className="panel-header">
                        <h2>📊 Model Comparison</h2>
                    </div>
                    <div className="model-table-wrapper">
                        <table className="model-table">
                            <thead>
                                <tr>
                                    <th>Task</th>
                                    <th>Model</th>
                                    <th>Accuracy</th>
                                    <th>F1 Score</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(modelData).map(([task, models]) => (
                                    <React.Fragment key={task}>
                                        {Object.entries(models).map(([model, metrics]) => (
                                            <tr key={`${task}-${model}`} className={model === 'xgb' ? 'best-row' : ''}>
                                                <td><strong>{task.replace('_', ' ')}</strong></td>
                                                <td><span className={`model-badge ${model}`}>{model.toUpperCase()}</span></td>
                                                <td className="metric-cell">{metrics.acc || metrics.r2}</td>
                                                <td className="metric-cell">{metrics.f1 || '—'}</td>
                                                <td>{model === 'xgb' ? <span className="status-best">⭐ Best</span> : <span className="status-alt">Good</span>}</td>
                                            </tr>
                                        ))}
                {/* Radar Chart for Feature Comparison */}
                <div className="panel radar-panel" style={{ marginTop: '2rem' }}>
                    <div className="panel-header">
                        <h2>🛰️ Feature Importance Radar</h2>
                    </div>
                    <div className="radar-chart-wrapper" style={{ width: '100%', height: '350px' }}>
                        <ResponsiveContainer>
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={shapFeatures.map(f => ({
                                feature: f.name,
                                importance: f.importance * 100,
                            }))}>
                                <PolarGrid />
                                <PolarAngleAxis dataKey="feature" />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tickCount={5} />
                                <Radar name="Importance" dataKey="importance" stroke="var(--forest-500)" fill="var(--forest-200)" fillOpacity={0.6} />
                                <Legend />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                                        <tr className="table-spacer"><td colSpan="5"></td></tr>
                                    </React.Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div className="panel yield-panel">
                    <div className="panel-header">
                        <h2>🔍 SHAP Explainability</h2>
                    </div>
                    <div className="shap-task-selector">
                        {['crop', 'fertilizer', 'yield'].map(task => (
                            <button
                                key={task}
                                className={`pill-btn shap-btn ${activeShap === task ? 'active-shap' : ''}`}
                                onClick={() => setActiveShap(task)}
                            >
                                {task.charAt(0).toUpperCase() + task.slice(1)}
                            </button>
                        ))}
                    </div>

                    <div className="shap-content">
                        <div>
                            <h3 className="shap-section-title">Feature Importance</h3>
                            <div className="shap-bar-chart">
                                {shapFeatures.map((feat, i) => (
                                    <div key={i} className="shap-bar-row">
                                        <span className="shap-feature-name">{feat.name}</span>
                                        <div className="shap-bar-track">
                                            <div
                                                className="shap-bar-fill"
                                                style={{
                                                    width: `${feat.importance * 100}%`,
                                                    background: `linear-gradient(90deg, var(--neon-green), var(--neon-cyan))`,
                                                    boxShadow: `0 0 8px rgba(57, 255, 20, 0.4)`,
                                                }}
                                            />
                                        </div>
                                        <span className="shap-bar-value">{feat.importance.toFixed(2)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <h3 className="shap-section-title">Prediction Waterfall</h3>
                            <div className="shap-explain-card">
                                <div className="explain-header">
                                    <div className="explain-icon">🧠</div>
                                    <div>
                                        <span className="explain-title">Crop Recommendation</span>
                                        <span className="explain-sub">Wheat — Confidence: 94.2%</span>
                                    </div>
                                </div>
                                <div className="explain-body">
                                    <div className="explain-insight">
                                        <span className="insight-label">Key Driver</span>
                                        <span className="insight-value">Nitrogen levels are the strongest predictor for wheat yield</span>
                                    </div>
                                    <div className="explain-insight">
                                        <span className="insight-label">Risk Factor</span>
                                        <span className="insight-value">Soil pH slightly below optimal range — monitor closely</span>
                                    </div>
                                    <div className="waterfall-preview">
                                        <h4 className="shap-section-title" style={{ marginTop: '1rem' }}>Contribution Breakdown</h4>
                                        <div className="waterfall-bars">
                                            {shapWaterfall.map((step, i) => (
                                                <div key={i} className="waterfall-row">
                                                    <span className="wf-name">{step.name}</span>
                                                    <div className="wf-bar-area">
                                                        <div
                                                            className="wf-bar"
                                                            style={{
                                                                width: `${Math.abs(step.value) * 20}%`,
                                                                background: step.positive ? 'var(--neon-green)' : 'var(--neon-red)',
                                                                boxShadow: step.positive ? '0 0 8px var(--neon-green)' : '0 0 8px var(--neon-red)',
                                                            }}
                                                        />
                                                    </div>
                                                    <span className="wf-value" style={{ color: step.positive ? 'var(--neon-green)' : 'var(--neon-red)' }}>
                                                        {step.value > 0 ? '+' : ''}{step.value}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                        <div className="waterfall-legend">
                                            <span><span className="legend-dot positive" /> Positive contribution</span>
                                            <span><span className="legend-dot negative" /> Negative contribution</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AIAnalytics;