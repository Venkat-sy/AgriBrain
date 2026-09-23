import React, { useState } from 'react';

const FieldStatus = () => {
    const [sliders, setSliders] = useState({
        nitrogen: 65,
        phosphorus: 50,
        potassium: 70,
        ph: 6.8,
        rainfall: 45,
        temperature: 28,
        humidity: 60,
    });

    const handleChange = (key, value) => {
        setSliders(prev => ({ ...prev, [key]: value }));
    };

    const fields = [
        { name: 'Field A — Wheat', status: 'Healthy', color: '#39ff14', health: 92 },
        { name: 'Field B — Rice', status: 'Monitoring', color: '#00ffff', health: 78 },
        { name: 'Field C — Sugarcane', status: 'Alert', color: '#ff4757', health: 45 },
        { name: 'Field D — Cotton', status: 'Optimal', color: '#bf00ff', health: 96 },
    ];

    return (
        <div className="fade-in">
            <div className="panel top-panel">
                <div className="panel-header">
                    <div>
                        <h2>🌾 Field Status Monitor</h2>
                        <p className="subtitle">Real-time soil and weather conditions across all fields</p>
                    </div>
                    <button className="pill-btn">Refresh</button>
                </div>

                <div className="metrics-row">
                    <div className="metric-item">
                        <div className="metric-icon green">📡</div>
                        <div className="metric-info">
                            <span className="metric-label">Active Sensors</span>
                            <span className="metric-value green">24/24</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon cyan">⚡</div>
                        <div className="metric-info">
                            <span className="metric-label">Power Level</span>
                            <span className="metric-value">87%</span>
                        </div>
                    </div>
                    <div className="metric-divider" />
                    <div className="metric-item">
                        <div className="metric-icon purple">📶</div>
                        <div className="metric-info">
                            <span className="metric-label">Connectivity</span>
                            <span className="metric-value">99.2%</span>
                        </div>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid" style={{ marginTop: '1.5rem' }}>
                <div className="panel inputs-panel">
                    <div className="panel-header">
                        <h2>🎛️ Sensor Controls</h2>
                    </div>
                    <div className="sliders-container">
                        {[
                            { key: 'nitrogen', label: 'Nitrogen (N)', unit: 'ppm', min: 0, max: 100 },
                            { key: 'phosphorus', label: 'Phosphorus (P)', unit: 'ppm', min: 0, max: 100 },
                            { key: 'potassium', label: 'Potassium (K)', unit: 'ppm', min: 0, max: 100 },
                            { key: 'ph', label: 'Soil pH', unit: '', min: 0, max: 14, step: 0.1 },
                            { key: 'rainfall', label: 'Rainfall', unit: 'mm', min: 0, max: 100 },
                            { key: 'temperature', label: 'Temperature', unit: '°C', min: 0, max: 50 },
                            { key: 'humidity', label: 'Humidity', unit: '%', min: 0, max: 100 },
                        ].map(slider => (
                            <div key={slider.key}>
                                <div className="slider-labels">
                                    {slider.label} <span className="unit">{sliders[slider.key]}{slider.unit}</span>
                                </div>
                                <input
                                    type="range"
                                    className="styled-slider"
                                    min={slider.min}
                                    max={slider.max}
                                    step={slider.step || 1}
                                    value={sliders[slider.key]}
                                    onChange={(e) => handleChange(slider.key, parseFloat(e.target.value))}
                                    style={{ '--slider-fill': `${(sliders[slider.key] / slider.max) * 100}%` }}
                                />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="panel yield-panel">
                    <div className="panel-header">
                        <h2>📡 Field Sensors</h2>
                    </div>
                    <div className="action-list">
                        {fields.map((field, i) => (
                            <div key={i} className="action-item" style={{ borderLeft: `3px solid ${field.color}` }}>
                                <div className="action-icon" style={{ borderColor: field.color, color: field.color, boxShadow: `0 0 12px ${field.color}40` }}>
                                    🌾
                                </div>
                                <div className="action-text">
                                    <span className="action-title">{field.name}</span>
                                    <span className="action-sub">Status: {field.status} • Health: {field.health}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FieldStatus;