import React, { useState, useEffect } from 'react';

/**
 * DigitalTwin component – Phase 6 implementation.
 *
 * Features added in this phase:
 *   • Dropdowns for district and crop populated from the backend API.
 *   • Full simulation request matching the FastAPI `SimulationRequest` schema.
 *   • Run‑simulation button with loading indicator and error handling.
 *   • Expanded result display (cost breakdown, profit, ROI, risk).
 *   • Basic UI styling retained from previous phases.
 */

const DigitalTwin = () => {
  // ---- Simulation input state ------------------------------------------------
  const [districtId, setDistrictId] = useState('');
  const [selectedCrop, setSelectedCrop] = useState('');
  const [landArea, setLandArea] = useState('');
  const [budget, setBudget] = useState('');
  const [rainfallOverride, setRainfallOverride] = useState('');
  // confirmed soil type is required; for now we default to an empty string.
  const [confirmedSoilType] = useState('');

  const [loadingSim, setLoadingSim] = useState(false);
  const [simResult, setSimResult] = useState(null);

  // ---- UI helper state -------------------------------------------------------
  const [districts, setDistricts] = useState([]);
  const [crops, setCrops] = useState([]);
  const [progress, setProgress] = useState(75);
  const [scenario, setScenario] = useState('normal');

  // ---- Load dropdown data only once ------------------------------------------
  useEffect(() => {
    // District list
    fetch('/api/v1/map/districts')
      .then(r => r.json())
      .then(data => setDistricts(data))
      .catch(() => setDistricts([]));

    // Crop list
    fetch('/api/v1/crop/profiles')
      .then(r => r.json())
      .then(data => setCrops(data))
      .catch(() => setCrops([]));
  }, []);

  // Simple progress animation (kept from earlier UI)
  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => (prev >= 100 ? 0 : prev + 1));
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const scenarios = [
    { name: 'Normal', color: '#39ff14', risk: 'Low' },
    { name: 'Drought', color: '#ff4757', risk: 'High' },
    { name: 'Flood', color: '#00ffff', risk: 'Medium' },
    { name: 'Optimal', color: '#bf00ff', risk: 'Very Low' },
  ];

  const twinMetrics = [
    { icon: '🌡️', label: 'Soil Temp', value: simResult?.soil_temp ?? '28.4°C', color: '#ff6b00' },
    { icon: '💧', label: 'Moisture', value: simResult?.moisture ?? '67%', color: '#00ffff' },
    { icon: '🌱', label: 'N Level', value: simResult?.nitrogen_level ?? '85ppm', color: '#39ff14' },
    {
      icon: '📊',
      label: 'Yield Est.',
      value: simResult?.estimated_yield_tons_per_ha
        ? `${simResult.estimated_yield_tons_per_ha.toFixed(2)}t/ha`
        : '4.2t/ha',
      color: '#bf00ff',
    },
  ];

  // ---------------------------------------------------------------------------
  const runSimulation = async () => {
    if (!districtId || !selectedCrop || !landArea || !budget) {
      alert('Please fill out all required simulation parameters.');
      return;
    }
    const payload = {
      district_id: parseInt(districtId),
      selected_crop: selectedCrop,
      land_area_ha: parseFloat(landArea),
      budget_inr: parseFloat(budget),
      confirmed_soil_type: confirmedSoilType || 'unknown',
      rainfall_override_mm: rainfallOverride ? parseFloat(rainfallOverride) : undefined,
    };
    setLoadingSim(true);
    try {
      const resp = await fetch('/api/v1/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) throw new Error('Simulation request failed');
      const data = await resp.json();
      setSimResult(data);
    } catch (e) {
      console.error(e);
      alert('Failed to run simulation. See console for details.');
    } finally {
      setLoadingSim(false);
    }
  };

  return (
    <div className="fade-in">
      <div className="panel top-panel">
        <div className="panel-header">
          <div>
            <h2>🔄 Digital Twin Simulation</h2>
            <p className="subtitle">Real-time crop environment simulation and what‑if analysis</p>
          </div>
          <div className="shap-task-selector">
            {scenarios.map(s => (
              <button
                key={s.name}
                className={`pill-btn ${scenario === s.name ? 'active-shap' : ''}`}
                onClick={() => setScenario(s.name)}
                style={{
                  borderColor: s.color,
                  color: s.color,
                  ...(scenario === s.name ? { background: `${s.color}20`, boxShadow: `0 0 15px ${s.color}40` } : {}),
                }}
              >
                {s.name}
              </button>
            ))}
          </div>
        </div>
        {/* Simulation Parameters Form */}
        <div className="panel" style={{ padding: '1rem', marginTop: '1rem' }}>
          <h3 className="section-title">Simulation Parameters</h3>
          <div className="grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
            <select className="form-input" value={districtId} onChange={e => setDistrictId(e.target.value)}>
              <option value="">Select District</option>
              {districts.map(d => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.state})
                </option>
              ))}
            </select>
            <select className="form-input" value={selectedCrop} onChange={e => setSelectedCrop(e.target.value)}>
              <option value="">Select Crop</option>
              {crops.map(c => (
                <option key={c.id} value={c.name}>
                  {c.name}
                </option>
              ))}
            </select>
            <input className="form-input" type="number" placeholder="Land Area (ha)" value={landArea} onChange={e => setLandArea(e.target.value)} />
            <input className="form-input" type="number" placeholder="Budget (INR)" value={budget} onChange={e => setBudget(e.target.value)} />
            <input className="form-input" type="number" placeholder="Rainfall Override (mm)" value={rainfallOverride} onChange={e => setRainfallOverride(e.target.value)} />
          </div>
          <button className="form-input" style={{ marginTop: '1rem' }} disabled={loadingSim} onClick={runSimulation}>
            {loadingSim ? 'Running…' : 'Run Simulation'}
          </button>
        </div>
        {/* Metrics Display */}
        <div className="metric-grid" style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          {twinMetrics.map(m => (
            <div key={m.label} style={{ flex: '1 1 150px', background: m.color + '10', padding: '0.5rem', borderRadius: '4px' }}>
              <span>{m.icon}</span> <strong>{m.label}:</strong> {m.value}
            </div>
          ))}
        </div>
        {/* Additional Result Details when available */}
        {simResult && (
          <div className="panel" style={{ marginTop: '1rem', padding: '1rem' }}>
            <h3 className="section-title">Simulation Output</h3>
            <p><strong>Total Cost (INR):</strong> {simResult.total_cost_inr?.toLocaleString()}</p>
            <p><strong>Estimated Yield (t):</strong> {simResult.estimated_yield_tons?.toFixed(2)}</p>
            <p><strong>Market Value (INR):</strong> {simResult.market_value_inr?.toLocaleString()}</p>
            <p><strong>Net Profit (INR):</strong> {simResult.net_profit_inr?.toLocaleString()}</p>
            <p><strong>ROI (%):</strong> {simResult.roi_percentage?.toFixed(2)}</p>
            <p><strong>Risk Level:</strong> {simResult.risk_level}</p>
            {simResult.cost_breakdown && (
              <details style={{ marginTop: '0.5rem' }}>
                <summary>Cost Breakdown</summary>
                <ul>
                  {simResult.cost_breakdown.map((item, idx) => (
                    <li key={idx}>
                      {item.activity}: {item.quantity} {item.unit} × {item.unit_cost} = {item.total_cost}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DigitalTwin;