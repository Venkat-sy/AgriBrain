import React, { useState } from 'react';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';

const Recommendations = () => {
    const { recommendations, addRecommendation, crops } = useApp();
    const [selectedCrop, setSelectedCrop] = useState('');
    const [loading, setLoading] = useState(false);

    const handleGetRecommendation = () => {
        if (!selectedCrop) return;
        setLoading(true);
        
        setTimeout(() => {
            const crop = crops.find(c => c.id === parseInt(selectedCrop));
            addRecommendation({
                crop: crop.name,
                recommendation: 'Apply NPK fertilizer at ratio 20:10:10',
                reasoning: `Based on soil analysis for ${crop.growthStage} stage.`,
                priority: 'Medium',
                action: 'Apply 50kg NPK per hectare within 7 days',
                confidence: 0.92
            });
            setLoading(false);
        }, 1500);
    };

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <h1 className="page-title">AI Recommendations</h1>
                <p className="page-subtitle">Get intelligent farming insights powered by AI</p>
            </div>

            <Card className="mb-3">
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
                    Generate Recommendation
                </h2>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                    <div style={{ flex: 1 }}>
                        <label className="form-label">Select Crop</label>
                        <select
                            className="form-input form-select"
                            value={selectedCrop}
                            onChange={(e) => setSelectedCrop(e.target.value)}
                        >
                            <option value="">Choose a crop...</option>
                            {crops.map(crop => (
                                <option key={crop.id} value={crop.id}>
                                    {crop.name} ({crop.variety})
                                </option>
                            ))}
                        </select>
                    </div>
                    <Button onClick={handleGetRecommendation} disabled={!selectedCrop || loading}>
                        {loading ? 'Analyzing...' : 'Get Recommendations'}
                    </Button>
                </div>
            </Card>

            {loading && <Card><LoadingSpinner text="Analyzing crop data..." /></Card>}

            {!loading && recommendations.length > 0 && (
                <Card>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>
                        Recent Recommendations
                    </h2>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {recommendations.map(rec => (
                            <div 
                                key={rec.id}
                                style={{
                                    padding: '1.5rem',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--radius-md)',
                                    borderLeft: `4px solid var(--agri-green)`
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                                    <div>
                                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                            {rec.crop}
                                        </div>
                                        <h3 style={{ fontSize: '1.1rem', fontWeight: '600' }}>
                                            {rec.recommendation}
                                        </h3>
                                    </div>
                                    <span className={`badge badge-${rec.priority === 'High' ? 'danger' : 'warning'}`}>
                                        {rec.priority}
                                    </span>
                                </div>
                                <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                                    <strong>Reasoning:</strong> {rec.reasoning}
                                </div>
                                <div style={{ marginBottom: '1rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
                                    <strong>Action:</strong> {rec.action}
                                </div>
                                <div style={{ fontSize: '0.875rem', color: 'var(--agri-green)', fontWeight: '600' }}>
                                    AI Confidence: {Math.round(rec.confidence * 100)}%
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {!loading && recommendations.length === 0 && (
                <Card>
                    <div style={{ textAlign: 'center', padding: '4rem' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🤖</div>
                        <h2>No Recommendations Yet</h2>
                        <p style={{ color: 'var(--text-muted)' }}>
                            Select a crop and get AI-powered insights
                        </p>
                    </div>
                </Card>
            )}
        </div>
    );
};

export default Recommendations;
