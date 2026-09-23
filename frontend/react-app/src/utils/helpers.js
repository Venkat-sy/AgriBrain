// Date formatting utilities
export const formatDate = (date) => {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' });
};

export const formatDateTime = (date) => {
    if (!date) return 'N/A';
    const d = new Date(date);
    return d.toLocaleString('en-IN', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

export const getRelativeTime = (date) => {
    if (!date) return 'N/A';
    const now = new Date();
    const d = new Date(date);
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    return formatDate(date);
};

export const getDaysUntil = (date) => {
    if (!date) return null;
    const now = new Date();
    const target = new Date(date);
    const diffMs = target - now;
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    return diffDays;
};

// Status helpers
export const getStatusColor = (status) => {
    const colors = {
        healthy: '#10b981',
        active: '#10b981',
        monitoring: '#f59e0b',
        warning: '#f59e0b',
        alert: '#ef4444',
        critical: '#dc2626',
        info: '#3b82f6',
        inactive: '#6b7280'
    };
    return colors[status?.toLowerCase()] || '#6b7280';
};

export const getHealthColor = (health) => {
    if (health >= 80) return '#10b981';
    if (health >= 60) return '#84cc16';
    if (health >= 40) return '#f59e0b';
    return '#ef4444';
};

// Number formatting
export const formatNumber = (num, decimals = 1) => {
    if (num === null || num === undefined) return 'N/A';
    return Number(num).toFixed(decimals);
};

export const formatArea = (area) => {
    if (!area) return 'N/A';
    return `${formatNumber(area, 1)} ha`;
};

export const formatYield = (yieldValue) => {
    if (!yieldValue) return 'N/A';
    return `${formatNumber(yieldValue, 2)} t/ha`;
};

// Weather helpers
export const getWeatherIcon = (condition) => {
    const icons = {
        'sunny': '☀️',
        'partly cloudy': '⛅',
        'cloudy': '☁️',
        'rainy': '🌧️',
        'stormy': '⛈️',
        'foggy': '🌫️'
    };
    return icons[condition?.toLowerCase()] || '🌤️';
};

// Crop growth stage helpers
export const getGrowthStageProgress = (stage) => {
    const stages = {
        'germination': 10,
        'seedling': 25,
        'vegetative': 40,
        'flowering': 60,
        'fruiting': 75,
        'maturation': 90,
        'harvest ready': 100
    };
    return stages[stage?.toLowerCase()] || 0;
};

export const getCropHealthIcon = (status) => {
    const icons = {
        'healthy': '✅',
        'monitoring': '⚠️',
        'alert': '🚨',
        'critical': '❌'
    };
    return icons[status?.toLowerCase()] || '❓';
};

// Validation helpers
export const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

export const validatePhone = (phone) => {
    const re = /^[6-9]\d{9}$/;
    return re.test(phone);
};

// Search and filter helpers
export const searchItems = (items, searchTerm, fields) => {
    if (!searchTerm) return items;
    const term = searchTerm.toLowerCase();
    return items.filter(item => 
        fields.some(field => 
            String(item[field] || '').toLowerCase().includes(term)
        )
    );
};

export const sortItems = (items, field, direction = 'asc') => {
    return [...items].sort((a, b) => {
        const aVal = a[field];
        const bVal = b[field];
        if (aVal === bVal) return 0;
        const comparison = aVal > bVal ? 1 : -1;
        return direction === 'asc' ? comparison : -comparison;
    });
};
