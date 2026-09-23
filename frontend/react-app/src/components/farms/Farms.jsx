import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';
import Button from '../common/Button';
import EmptyState from '../common/EmptyState';
import { formatArea, formatDate } from '../../utils/helpers';

const Farms = () => {
    const navigate = useNavigate();
    const { farms, fields } = useApp();

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Farms</h1>
                    <p className="page-subtitle">Manage all your farms and properties</p>
                </div>
                <Button icon="+">Add Farm</Button>
            </div>

            {farms.length === 0 ? (
                <Card>
                    <EmptyState
                        icon="🏞️"
                        title="No Farms Yet"
                        message="Start by adding your first farm to begin managing your agricultural operations"
                        action={<Button>Add Your First Farm</Button>}
                    />
                </Card>
            ) : (
                <div className="grid grid-3">
                    {farms.map(farm => {
                        const farmFields = fields.filter(f => f.farmId === farm.id);
                        const healthyCount = farmFields.filter(f => f.status === 'healthy').length;
                        
                        return (
                            <Card 
                                key={farm.id} 
                                hover 
                                onClick={() => navigate(`/farms/${farm.id}`)}
                            >
                                <div style={{ fontSize: '3rem', marginBottom: '1rem', textAlign: 'center' }}>
                                    🏞️
                                </div>
                                <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                    {farm.name}
                                </h3>
                                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                                    📍 {farm.location}
                                </div>
                                
                                <div style={{ 
                                    display: 'grid', 
                                    gridTemplateColumns: '1fr 1fr', 
                                    gap: '0.75rem',
                                    padding: '1rem',
                                    background: 'var(--bg-secondary)',
                                    borderRadius: 'var(--radius-md)',
                                    marginBottom: '1rem'
                                }}>
                                    <div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Area</div>
                                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{formatArea(farm.area)}</div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Fields</div>
                                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{farmFields.length}</div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Soil Type</div>
                                        <div style={{ fontSize: '1rem', fontWeight: '600' }}>{farm.soilType}</div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Healthy</div>
                                        <div style={{ fontSize: '1rem', fontWeight: '600', color: 'var(--agri-green)' }}>
                                            {healthyCount}/{farmFields.length}
                                        </div>
                                    </div>
                                </div>
                                
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span className={`badge badge-${farm.status === 'active' ? 'success' : 'warning'}`}>
                                        {farm.status}
                                    </span>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                        Added {formatDate(farm.createdAt)}
                                    </div>
                                </div>
                            </Card>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Farms;
