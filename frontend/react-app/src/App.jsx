import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Farms from './components/farms/Farms';
import FarmDetail from './components/farms/FarmDetail';
import Crops from './components/crops/Crops';
import Weather from './components/weather/Weather';
import Alerts from './components/alerts/Alerts';
import Recommendations from './components/recommendations/Recommendations';
import Chat from './components/chat/AIChat';
import Analytics from './components/AIAnalytics';

import Settings from './components/Settings';
import './styles/main.css';

function App() {
    return (
        <AppProvider>
            <div className="app">
                <Sidebar />
                <div className="main-wrapper">
                    <Header />
                    <div className="main-content">
                        <Routes>
                            <Route path="/" element={<Dashboard />} />
                            <Route path="/farms" element={<Farms />} />
                            <Route path="/farms/:id" element={<FarmDetail />} />
                            <Route path="/crops" element={<Crops />} />
                            <Route path="/weather" element={<Weather />} />
                            <Route path="/alerts" element={<Alerts />} />
                            <Route path="/recommendations" element={<Recommendations />} />
                            <Route path="/chat" element={<Chat />} />

                            <Route path="/analytics" element={<Analytics />} />
                            <Route path="/settings" element={<Settings />} />
                        </Routes>
                    </div>
                </div>
            </div>
        </AppProvider>
    );
}

export default App;
