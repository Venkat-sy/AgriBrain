import React from 'react';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';
import { formatYield } from '../../utils/helpers';

const Crops = () => {
    const { crops, fields } = useApp();

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <h1 className="page-title">Crops</h1>
                <p className="page-subtitle">Monitor all your crop health and growth stages</p>
            </div>

            <div className="grid grid-3">
                {crops.map(crop => {
                    const cropFields = fields.filter(f => f.cropId === crop.id);
                    
                    return (
                        <Card key={crop.id} hover>
                            <div style={{ fontSize: '3rem', textAlign: 'center', marginBottom: '1rem' }}>
                                🌾
                            </div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem', textAlign: 'center' }}>
                                {crop.name}
                            </h3>
                            <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textAlign: 'center', marginBottom: '1rem' }}>
                                Variety: {crop.variety}
                            </div>

                            <div style={{ 
                                padding: '1rem', 
                                background: 'var(--bg-secondary)', 
                                borderRadius: 'var(--radius-md)',
                                marginBottom: '1rem'
                            }}>
                                <div style={{ marginBottom: '0.75rem' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Growth Stage</div>
                                    <div style={{ fontSize: '1rem', fontWeight: '600', textTransform: 'capitalize' }}>
                                        {crop.growthStage}
                                    </div>
                                </div>
                                <div style={{ marginBottom: '0.75rem' }}>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Days Planted</div>
                                    <div style={{ fontSize: '1rem', fontWeight: '600' }}>
                                        {crop.daysPlanted} days
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Expected Yield</div>
                                    <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--agri-green)' }}>
                                        {formatYield(crop.expectedYield)}
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span className={`badge badge-${crop.healthStatus === 'healthy' ? 'success' : 
                                                              crop.healthStatus === 'monitoring' ? 'warning' : 'danger'}`}>
                                    {crop.healthStatus}
                                </span>
                                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                                    {cropFields.length} field{cropFields.length !== 1 ? 's' : ''}
                                </div>
                            </div>
                        </Card>
                    );
                })}
            </div>
        </div>
    );
};

export default Crops;
