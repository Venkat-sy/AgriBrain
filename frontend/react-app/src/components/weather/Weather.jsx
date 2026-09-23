import React from 'react';
import { useApp } from '../../context/AppContext';
import Card from '../common/Card';

const Weather = () => {
    const { weather } = useApp();

    if (!weather) {
        return (
            <div className="page-container fade-in">
                <Card>
                    <div style={{ textAlign: 'center', padding: '3rem' }}>
                        <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>🌤️</div>
                        <h2>Weather data unavailable</h2>
                    </div>
                </Card>
            </div>
        );
    }

    const getWeatherIcon = (condition) => {
        const icons = {
            'Sunny': '☀️',
            'Partly Cloudy': '⛅',
            'Cloudy': '☁️',
            'Rainy': '🌧️'
        };
        return icons[condition] || '🌤️';
    };

    return (
        <div className="page-container fade-in">
            <div className="page-header">
                <h1 className="page-title">Weather</h1>
                <p className="page-subtitle">Current conditions and forecast</p>
            </div>

            <Card className="mb-3">
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>Current Conditions</h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', marginBottom: '2rem' }}>
                    <div style={{ fontSize: '6rem' }}>
                        {getWeatherIcon(weather.current.condition)}
                    </div>
                    <div>
                        <div style={{ fontSize: '4rem', fontWeight: '700', lineHeight: 1 }}>
                            {weather.current.temperature}°C
                        </div>
                        <div style={{ fontSize: '1.25rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                            {weather.current.condition}
                        </div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                            Feels like {weather.current.feelsLike}°C
                        </div>
                    </div>
                </div>

                <div className="grid grid-4">
                    <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💧</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{weather.current.humidity}%</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Humidity</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>💨</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{weather.current.windSpeed}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Wind (km/h)</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🧭</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>{weather.current.windDirection}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Direction</div>
                    </div>
                    <div style={{ textAlign: 'center', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
                        <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🌧️</div>
                        <div style={{ fontSize: '1.5rem', fontWeight: '700' }}>0mm</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Rainfall</div>
                    </div>
                </div>
            </Card>

            <Card>
                <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1.5rem' }}>7-Day Forecast</h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '1rem' }}>
                    {weather.forecast.map((day, index) => (
                        <div 
                            key={index}
                            style={{
                                textAlign: 'center',
                                padding: '1rem',
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius-md)'
                            }}
                        >
                            <div style={{ fontSize: '0.875rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                                {day.day}
                            </div>
                            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>
                                {getWeatherIcon(day.condition)}
                            </div>
                            <div style={{ fontSize: '1.25rem', fontWeight: '700', marginBottom: '0.25rem' }}>
                                {day.temp}°C
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                💧 {day.rain}%
                            </div>
                        </div>
                    ))}
                </div>
            </Card>
        </div>
    );
};

export default Weather;
