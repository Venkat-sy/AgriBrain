import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';
import Button from '../common/Button';
import { formatArea } from '../../utils/helpers';

const FarmDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { farms, fields, crops } = useApp();
    
    const farm = farms.find(f => f.id === parseInt(id));
    const farmFields = fields.filter(f => f.farmId === parseInt(id));

    if (!farm) {
        return (
            <div className="page-container">
                <Card>
                    <h2>Farm not found</h2>
                    <Button onClick={() => navigate('/farms')}>Back to Farms</Button>
                </Card>
            </div>
        );
    }

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <div>
                    <Button variant="outline" size="small" onClick={() => navigate('/farms')}>
                        ← Back
                    </Button>
                    <h1 className="page-title" style={{ marginTop: '0.5rem' }}>{farm.name}</h1>
                    <p className="page-subtitle">📍 {farm.location}</p>
                </div>
                <Button icon="+">Add Field</Button>
            </div>

            <div className="grid grid-4 mb-3">
                <Card>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                        Total Area
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: '700' }}>
                        {formatArea(farm.area)}
                    </div>
                </Card>
                <Card>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                        Fields
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: '700' }}>
                        {farmFields.length}
                    </div>
                </Card>
                <Card>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                        Soil Type
                    </div>
                    <div style={{ fontSize: '1.75rem', fontWeight: '700' }}>
                        {farm.soilType}
                    </div>
                </Card>
                <Card>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                        Status
                    </div>
                    <span className={`badge badge-${farm.status === 'active' ? 'success' : 'warning'}`}>
                        {farm.status}
                    </span>
                </Card>
            </div>

            <Card>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>Fields</h2>
                {farmFields.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                        No fields added yet
                    </div>
                ) : (
                    <div className="grid grid-3">
                        {farmFields.map(field => {
                            const crop = crops.find(c => c.id === field.cropId);
                            return (
                                <div 
                                    key={field.id}
                                    style={{
                                        padding: '1rem',
                                        background: 'var(--bg-secondary)',
                                        borderRadius: 'var(--radius-md)',
                                        borderLeft: `4px solid ${field.status === 'healthy' ? 'var(--agri-green)' : 'var(--agri-amber)'}`
                                    }}
                                >
                                    <h3 style={{ fontSize: '1.1rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                        {field.name}
                                    </h3>
                                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                                        🌾 {crop?.name || 'No crop'}
                                    </div>
                                    <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                                        Area: {formatArea(field.area)}
                                    </div>
                                    <div style={{ fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                                        Soil Health: <span style={{ fontWeight: '600', color: 'var(--agri-green)' }}>
                                            {field.soilHealth}%
                                        </span>
                                    </div>
                                    <span className={`badge badge-${field.status === 'healthy' ? 'success' : 'warning'}`}>
                                        {field.status}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}
            </Card>
        </div>
    );
};

export default FarmDetail;
