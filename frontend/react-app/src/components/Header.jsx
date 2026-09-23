import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { useApp } from '../context/AppContext';
import { Search, Bell, HelpCircle, ChevronDown } from 'lucide-react';

const Header = () => {
    const location = useLocation();
    const { alerts } = useApp();
    const [searchQuery, setSearchQuery] = useState('');

    const unreadCount = alerts.filter(a => !a.read).length;

    const getPageInfo = () => {
        const path = location.pathname;
        if (path === '/') return { title: 'Dashboard', subtitle: 'Overview of your farming operations' };
        if (path === '/farms') return { title: 'Farms', subtitle: 'Manage your farm properties' };
        if (path.startsWith('/farms/')) return { title: 'Farm Details', subtitle: 'View and manage farm information' };
        if (path === '/crops') return { title: 'Crops', subtitle: 'Monitor crop health and growth' };
        if (path === '/weather') return { title: 'Weather', subtitle: 'Real-time weather insights' };
        if (path === '/alerts') return { title: 'Alerts', subtitle: 'Important notifications and warnings' };
        if (path === '/recommendations') return { title: 'AI Insights', subtitle: 'Intelligent recommendations powered by AI' };
        if (path === '/analytics') return { title: 'Analytics', subtitle: 'Data-driven farming insights' };
        if (path === '/settings') return { title: 'Settings', subtitle: 'Configure your preferences' };
        if (path === '/chat') return { title: 'AI Assistant', subtitle: 'Ask questions and get intelligent farming insights' };

        return { title: 'AgriBrain', subtitle: '' };
    };

    const pageInfo = getPageInfo();

    return (
        <header className="header">
            <div className="header-left">
                <div className="header-page-info">
                    <h1 className="header-title">{pageInfo.title}</h1>
                    {pageInfo.subtitle && <p className="header-subtitle">{pageInfo.subtitle}</p>}
                </div>
            </div>
            
            <div className="header-right">
                <div className="header-search">
                    <Search className="header-search-icon" size={18} strokeWidth={2} />
                    <input
                        type="text"
                        placeholder="Search farms, fields, crops..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>
                
                <button className="header-icon-btn" title="Notifications">
                    {unreadCount > 0 && <span className="header-badge">{unreadCount}</span>}
                    <Bell size={20} strokeWidth={2} />
                </button>

                <button className="header-icon-btn" title="Help & Support">
                    <HelpCircle size={20} strokeWidth={2} />
                </button>

                <div className="header-divider"></div>

                <div className="header-profile">
                    <div className="header-avatar">
                        <span>AB</span>
                    </div>
                    <div className="header-profile-info">
                        <div className="header-profile-name">Alex Brown</div>
                        <div className="header-profile-role">Farm Manager</div>
                    </div>
                    <ChevronDown size={16} strokeWidth={2} className="header-profile-chevron" />
                </div>
            </div>
        </header>
    );
};

export default Header;

