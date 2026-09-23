import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
    Home, 
    MapPin, 
    Wheat, 
    CloudSun, 
    Bell, 
    Lightbulb, 
    BarChart3, 
    Settings,
    Sparkles
} from 'lucide-react';

const Sidebar = () => {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo">
                    <Sparkles size={24} strokeWidth={2.5} />
                </div>
                <div className="sidebar-brand">
                    <span className="sidebar-brand-name">AgriBrain</span>
                    <span className="sidebar-brand-tag">AI AgriTech</span>
                </div>
            </div>

            <nav className="sidebar-nav">
                <div className="sidebar-nav-section">
                    <div className="sidebar-nav-label">Main</div>
                    <NavLink to="/" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Home size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Dashboard</span>
                    </NavLink>
                    <NavLink to="/farms" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <MapPin size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Farms</span>
                    </NavLink>
                    <NavLink to="/crops" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Wheat size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Crops</span>
                    </NavLink>
                </div>

                <div className="sidebar-nav-section">
                    <div className="sidebar-nav-label">Intelligence</div>
                    <NavLink to="/chat" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Sparkles size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">AI Assistant</span>
                    </NavLink>

                    <NavLink to="/recommendations" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Lightbulb size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">AI Insights</span>
                    </NavLink>
                    <NavLink to="/analytics" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <BarChart3 size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Analytics</span>
                    </NavLink>
                </div>

                <div className="sidebar-nav-section">
                    <div className="sidebar-nav-label">Monitoring</div>
                    <NavLink to="/weather" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <CloudSun size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Weather</span>
                    </NavLink>
                    <NavLink to="/alerts" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Bell size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Alerts</span>
                        <span className="sidebar-badge">3</span>
                    </NavLink>
                </div>

                <div className="sidebar-nav-section">
                    <div className="sidebar-nav-label">System</div>
                    <NavLink to="/settings" className={({ isActive }) => `sidebar-nav-item ${isActive ? 'active' : ''}`}>
                        <span className="sidebar-nav-icon">
                            <Settings size={20} strokeWidth={2} />
                        </span>
                        <span className="sidebar-nav-text">Settings</span>
                    </NavLink>
                </div>
            </nav>
        </aside>
    );
};

export default Sidebar;
