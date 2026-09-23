import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { 
    Tractor, 
    Wheat, 
    Droplets, 
    AlertTriangle,
    TrendingUp,
    Calendar,
    MapPin,
    ArrowUpRight,
    Sparkles,
    ThermometerSun,
    Cloud,
    Wind
} from 'lucide-react';
import { 
    LineChart, Line, AreaChart, Area, 
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend 
} from 'recharts';
import KPICard from './common/KPICard';
import ChartCard from './common/ChartCard';
import ActivityItem from './common/ActivityItem';
import DataTable from './common/DataTable';
import { formatArea } from '../utils/helpers';
import './Dashboard.css';

const Dashboard = () => {
    const navigate = useNavigate();
    const { farms, fields, alerts, weather } = useApp();

    // Calculate KPIs
    const totalFarms = farms.length;
    const totalFields = fields.length;
    const totalArea = farms.reduce((sum, farm) => sum + farm.area, 0);
    const healthyFields = fields.filter(f => f.status === 'healthy').length;
    const unreadAlerts = alerts.filter(a => !a.read).length;
    const criticalAlerts = alerts.filter(a => a.type === 'critical' && !a.read).length;
    const avgFieldHealth = fields.length > 0 
        ? Math.round(fields.reduce((sum, f) => sum + f.soilHealth, 0) / fields.length)
        : 0;

    // Sample chart data
    const yieldTrendData = [
        { month: 'Jan', yield: 4.2, target: 4.5 },
        { month: 'Feb', yield: 4.5, target: 4.5 },
        { month: 'Mar', yield: 4.8, target: 4.7 },
        { month: 'Apr', yield: 5.1, target: 4.8 },
        { month: 'May', yield: 5.3, target: 5.0 },
        { month: 'Jun', yield: 5.6, target: 5.2 }
    ];

    // Activity data
    const recentActivities = [
        {
            type: 'success',
            title: 'Irrigation completed',
            description: 'Field A-1 irrigation cycle finished successfully',
            timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
        },
        {
            type: 'warning',
            title: 'Soil moisture low',
            description: 'Field B-1 requires irrigation within 24 hours',
            timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000)
        },
        {
            type: 'info',
            title: 'Weather alert',
            description: 'Light rain expected tomorrow afternoon',
            timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000)
        },
        {
            type: 'success',
            title: 'Fertilizer applied',
            description: 'Field A-2 received scheduled fertilizer treatment',
            timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000)
        }
    ];

    // Field performance table data
    const fieldTableColumns = [
        { header: 'Field', key: 'name', width: '30%' },
        { 
            header: 'Crop', 
            key: 'crop',
            render: (value) => (
                <span style={{ 
                    display: 'inline-flex', 
                    alignItems: 'center', 
                    gap: '6px',
                    padding: '4px 10px',
                    background: 'rgba(132, 204, 22, 0.1)',
                    borderRadius: '6px',
                    fontSize: '0.8125rem',
                    fontWeight: '500',
                    color: 'var(--lime-600)'
                }}>
                    <Wheat size={14} />
                    {value}
                </span>
            )
        },
        { 
            header: 'Health', 
            key: 'health',
            align: 'center',
            render: (value) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
                    <div style={{ 
                        flex: '1',
                        maxWidth: '80px',
                        height: '6px', 
                        background: 'var(--neutral-200)', 
                        borderRadius: '3px',
                        overflow: 'hidden'
                    }}>
                        <div style={{ 
                            width: `${value}%`, 
                            height: '100%', 
                            background: value >= 80 ? 'var(--forest-500)' : value >= 60 ? 'var(--lime-500)' : 'var(--amber-500)',
                            borderRadius: '3px'
                        }} />
                    </div>
                    <span style={{ 
                        fontSize: '0.8125rem', 
                        fontWeight: '600',
                        color: value >= 80 ? 'var(--forest-600)' : value >= 60 ? 'var(--lime-600)' : 'var(--amber-600)'
                    }}>
                        {value}%
                    </span>
                </div>
            )
        },
        { 
            header: 'Status', 
            key: 'status',
            align: 'center',
            render: (value) => {
                const colors = {
                    healthy: { bg: 'rgba(16, 185, 129, 0.1)', text: 'var(--forest-600)', label: 'Healthy' },
                    monitoring: { bg: 'rgba(245, 158, 11, 0.1)', text: 'var(--amber-600)', label: 'Monitoring' },
                    alert: { bg: 'rgba(239, 68, 68, 0.1)', text: 'var(--error)', label: 'Alert' }
                };
                const config = colors[value] || colors.healthy;
                return (
                    <span style={{ 
                        display: 'inline-block',
                        padding: '4px 10px',
                        background: config.bg,
                        color: config.text,
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: '600'
                    }}>
                        {config.label}
                    </span>
                );
            }
        },
        { 
            header: 'Area', 
            key: 'area',
            align: 'right',
            render: (value) => formatArea(value)
        }
    ];

    const fieldTableData = fields.map(field => ({
        name: field.name,
        crop: 'Wheat',
        health: field.soilHealth,
        status: field.status,
        area: field.area
    }));

    return (
        <div className="dashboard-container">
            {/* KPI Cards Grid */}
            <div className="dashboard-kpi-grid">
                <KPICard
                    icon={Tractor}
                    label="Total Farms"
                    value={totalFarms}
                    trend="up"
                    trendValue="+12%"
                    subtitle={formatArea(totalArea)}
                    color="forest"
                    onClick={() => navigate('/farms')}
                />
                <KPICard
                    icon={Wheat}
                    label="Active Fields"
                    value={totalFields}
                    trend="up"
                    trendValue="+5%"
                    subtitle={`${healthyFields} healthy`}
                    color="leaf"
                    onClick={() => navigate('/farms')}
                />
                <KPICard
                    icon={Droplets}
                    label="Avg Soil Health"
                    value={`${avgFieldHealth}%`}
                    trend={avgFieldHealth >= 80 ? 'up' : 'neutral'}
                    trendValue={avgFieldHealth >= 80 ? '+3%' : '0%'}
                    subtitle={avgFieldHealth >= 80 ? 'Excellent' : 'Good'}
                    color={avgFieldHealth >= 80 ? 'sky' : 'lime'}
                />
                <KPICard
                    icon={AlertTriangle}
                    label="Active Alerts"
                    value={unreadAlerts}
                    trend={criticalAlerts > 0 ? 'down' : 'neutral'}
                    trendValue={criticalAlerts > 0 ? `${criticalAlerts} critical` : 'All clear'}
                    subtitle={criticalAlerts > 0 ? 'Needs attention' : 'No issues'}
                    color={criticalAlerts > 0 ? 'error' : 'forest'}
                    onClick={() => navigate('/alerts')}
                />
            </div>

            {/* Main Content Grid - Charts and Weather */}
            <div className="dashboard-main-grid">
                <div className="dashboard-col-large">
                    <ChartCard 
                        title="Yield Performance Trend"
                        subtitle="Monthly yield vs target (t/ha)"
                    >
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={yieldTrendData}>
                                <defs>
                                    <linearGradient id="yieldGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e7e5e4" />
                                <XAxis 
                                    dataKey="month" 
                                    tick={{ fill: '#78716c', fontSize: 12 }}
                                />
                                <YAxis 
                                    tick={{ fill: '#78716c', fontSize: 12 }}
                                />
                                <Tooltip />
                                <Legend />
                                <Area 
                                    type="monotone" 
                                    dataKey="yield" 
                                    stroke="#10b981" 
                                    strokeWidth={3}
                                    fill="url(#yieldGradient)" 
                                    name="Actual Yield"
                                />
                                <Line 
                                    type="monotone" 
                                    dataKey="target" 
                                    stroke="#84cc16" 
                                    strokeWidth={2}
                                    strokeDasharray="5 5"
                                    name="Target"
                                    dot={false}
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </ChartCard>

                    <ChartCard 
                        title="Field Performance"
                        subtitle={`${fields.length} fields monitored`}
                        className="mt-6"
                    >
                        <DataTable 
                            columns={fieldTableColumns}
                            data={fieldTableData}
                            onRowClick={() => navigate('/farms')}
                            hoverable={true}
                        />
                    </ChartCard>
                </div>

                <div className="dashboard-col-medium">
                    <ChartCard title="Current Weather" subtitle="Real-time conditions">
                        {weather && (
                            <div className="weather-display">
                                <div className="weather-main">
                                    <div className="weather-icon-large">
                                        <ThermometerSun size={48} strokeWidth={1.5} />
                                    </div>
                                    <div className="weather-temp">
                                        <span className="weather-temp-value">{weather.current.temperature}</span>
                                        <span className="weather-temp-unit">°C</span>
                                    </div>
                                    <div className="weather-condition">{weather.current.condition}</div>
                                </div>
                                <div className="weather-metrics">
                                    <div className="weather-metric">
                                        <Droplets size={16} />
                                        <span className="weather-metric-label">Humidity</span>
                                        <span className="weather-metric-value">{weather.current.humidity}%</span>
                                    </div>
                                    <div className="weather-metric">
                                        <Wind size={16} />
                                        <span className="weather-metric-label">Wind</span>
                                        <span className="weather-metric-value">{weather.current.windSpeed} km/h</span>
                                    </div>
                                    <div className="weather-metric">
                                        <Cloud size={16} />
                                        <span className="weather-metric-label">Feels Like</span>
                                        <span className="weather-metric-value">{weather.current.feelsLike}°C</span>
                                    </div>
                                </div>
                                <button 
                                    className="weather-forecast-btn"
                                    onClick={() => navigate('/weather')}
                                >
                                    View 7-Day Forecast
                                </button>
                            </div>
                        )}
                    </ChartCard>

                    <ChartCard 
                        title="AI Insights"
                        subtitle="Powered by machine learning"
                        className="mt-6"
                    >
                        <div className="ai-insights-list">
                            <div className="ai-insight-item">
                                <div className="ai-insight-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--forest-600)' }}>
                                    <TrendingUp size={18} />
                                </div>
                                <div className="ai-insight-content">
                                    <div className="ai-insight-title">Optimal Harvest Window</div>
                                    <div className="ai-insight-text">Field A-1 wheat will reach peak yield in 7-10 days.</div>
                                </div>
                            </div>
                            <div className="ai-insight-item">
                                <div className="ai-insight-icon" style={{ background: 'rgba(14, 165, 233, 0.1)', color: 'var(--sky-600)' }}>
                                    <Droplets size={18} />
                                </div>
                                <div className="ai-insight-content">
                                    <div className="ai-insight-title">Irrigation Optimization</div>
                                    <div className="ai-insight-text">Reduce water usage by 15% in Field B-2.</div>
                                </div>
                            </div>
                            <div className="ai-insight-item">
                                <div className="ai-insight-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--amber-600)' }}>
                                    <Calendar size={18} />
                                </div>
                                <div className="ai-insight-content">
                                    <div className="ai-insight-title">Fertilizer Schedule</div>
                                    <div className="ai-insight-text">Apply nitrogen fertilizer to Field C-1 within 3 days.</div>
                                </div>
                            </div>
                        </div>
                        <button 
                            className="ai-insights-cta"
                            onClick={() => navigate('/recommendations')}
                        >
                            View All AI Recommendations
                        </button>
                    </ChartCard>

                    <ChartCard 
                        title="Recent Activity"
                        subtitle="Latest farm updates"
                        className="mt-6"
                    >
                        <div className="activity-list">
                            {recentActivities.map((activity, idx) => (
                                <ActivityItem 
                                    key={idx}
                                    type={activity.type}
                                    title={activity.title}
                                    description={activity.description}
                                    timestamp={activity.timestamp}
                                />
                            ))}
                        </div>
                    </ChartCard>
                </div>
            </div>

            {/* Farm Quick Access */}
            <ChartCard 
                title="Your Farms"
                subtitle={`${farms.length} properties managed`}
                className="mt-6"
                action={
                    <button className="chart-action-btn" onClick={() => navigate('/farms')}>
                        View All <ArrowUpRight size={14} />
                    </button>
                }
            >
                <div className="farm-grid">
                    {farms.map(farm => (
                        <div 
                            key={farm.id}
                            className="farm-card"
                            onClick={() => navigate(`/farms/${farm.id}`)}
                        >
                            <div className="farm-card-header">
                                <div className="farm-card-icon">
                                    <MapPin size={20} />
                                </div>
                                <div className="farm-card-badge">{formatArea(farm.area)}</div>
                            </div>
                            <div className="farm-card-body">
                                <h3 className="farm-card-title">{farm.name}</h3>
                                <p className="farm-card-location">{farm.location}</p>
                                <div className="farm-card-meta">
                                    <span className="farm-card-meta-item">
                                        <Wheat size={14} />
                                        {fields.filter(f => f.farmId === farm.id).length} fields
                                    </span>
                                    <span className="farm-card-meta-item">
                                        <Calendar size={14} />
                                        Active
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </ChartCard>
        </div>
    );
};

export default Dashboard;

