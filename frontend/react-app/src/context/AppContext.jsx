import React, { createContext, useContext, useState, useEffect } from 'react';

const AppContext = createContext();

export const useApp = () => {
    const context = useContext(AppContext);
    if (!context) {
        throw new Error('useApp must be used within AppProvider');
    }
    return context;
};

export const AppProvider = ({ children }) => {
    const [farms, setFarms] = useState([]);
    const [fields, setFields] = useState([]);
    const [crops, setCrops] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [recommendations, setRecommendations] = useState([]);
    const [weather, setWeather] = useState(null);
    const [loading, setLoading] = useState(false);

    // Initialize with sample data
    useEffect(() => {
        initializeSampleData();
    }, []);

    const initializeSampleData = () => {
        // Sample farms
        const sampleFarms = [
            {
                id: 1,
                name: 'Green Valley Farm',
                location: 'Karnataka, India',
                area: 25,
                status: 'active',
                coordinates: { lat: 12.9716, lng: 77.5946 },
                soilType: 'Loamy',
                createdAt: new Date('2024-01-15')
            },
            {
                id: 2,
                name: 'Sunrise Agriculture',
                location: 'Maharashtra, India',
                area: 40,
                status: 'active',
                coordinates: { lat: 19.0760, lng: 72.8777 },
                soilType: 'Clay',
                createdAt: new Date('2023-08-20')
            },
            {
                id: 3,
                name: 'River Bend Fields',
                location: 'Punjab, India',
                area: 60,
                status: 'monitoring',
                coordinates: { lat: 30.7333, lng: 76.7794 },
                soilType: 'Sandy Loam',
                createdAt: new Date('2023-05-10')
            }
        ];

        // Sample fields - continued in next chunk
        const sampleFields = [
            {
                id: 1,
                farmId: 1,
                name: 'Field A-1',
                area: 10,
                status: 'healthy',
                cropId: 1,
                plantingDate: new Date('2024-06-01'),
                expectedHarvest: new Date('2024-10-15'),
                soilHealth: 92
            },
            {
                id: 2,
                farmId: 1,
                name: 'Field A-2',
                area: 15,
                status: 'monitoring',
                cropId: 2,
                plantingDate: new Date('2024-05-15'),
                expectedHarvest: new Date('2024-11-01'),
                soilHealth: 78
            },
            {
                id: 3,
                farmId: 2,
                name: 'Field B-1',
                area: 20,
                status: 'alert',
                cropId: 3,
                plantingDate: new Date('2024-07-01'),
                expectedHarvest: new Date('2024-12-15'),
                soilHealth: 45
            },
            {
                id: 4,
                farmId: 2,
                name: 'Field B-2',
                area: 20,
                status: 'healthy',
                cropId: 4,
                plantingDate: new Date('2024-06-20'),
                expectedHarvest: new Date('2024-10-30'),
                soilHealth: 96
            }
        ];

        // Sample crops
        const sampleCrops = [
            {
                id: 1,
                name: 'Wheat',
                variety: 'HD-2967',
                growthStage: 'vegetative',
                healthStatus: 'healthy',
                daysPlanted: 95,
                expectedYield: 4.2,
                currentConditions: {
                    nitrogen: 85,
                    phosphorus: 62,
                    potassium: 78,
                    ph: 6.8,
                    temperature: 28,
                    humidity: 67,
                    rainfall: 45
                }
            },
            {
                id: 2,
                name: 'Rice',
                variety: 'Basmati-370',
                growthStage: 'flowering',
                healthStatus: 'monitoring',
                daysPlanted: 110,
                expectedYield: 3.8,
                currentConditions: {
                    nitrogen: 72,
                    phosphorus: 58,
                    potassium: 65,
                    ph: 6.5,
                    temperature: 32,
                    humidity: 78,
                    rainfall: 120
                }
            },
            {
                id: 3,
                name: 'Sugarcane',
                variety: 'Co-86032',
                growthStage: 'tillering',
                healthStatus: 'alert',
                daysPlanted: 60,
                expectedYield: 2.5
            },
            {
                id: 4,
                name: 'Cotton',
                variety: 'BT-Cotton',
                growthStage: 'boll formation',
                healthStatus: 'healthy',
                daysPlanted: 85,
                expectedYield: 5.1
            }
        ];

        // Sample alerts
        const sampleAlerts = [
            {
                id: 1,
                type: 'critical',
                title: 'Low Soil Health Detected',
                message: 'Field B-1 showing significant nutrient deficiency. Immediate fertilization recommended.',
                farmId: 2,
                fieldId: 3,
                timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
                read: false,
                actionRequired: true
            },
            {
                id: 2,
                type: 'warning',
                title: 'Pest Risk Alert',
                message: 'Weather conditions favorable for pest activity in the next 48 hours.',
                farmId: 1,
                fieldId: 2,
                timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000),
                read: false,
                actionRequired: true
            },
            {
                id: 3,
                type: 'info',
                title: 'Optimal Harvesting Window',
                message: 'Field A-1 wheat crop will reach optimal harvest stage in 7-10 days.',
                farmId: 1,
                fieldId: 1,
                timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000),
                read: true,
                actionRequired: false
            }
        ];

        // Sample weather
        const sampleWeather = {
            current: {
                temperature: 28,
                feelsLike: 30,
                humidity: 67,
                windSpeed: 12,
                windDirection: 'NE',
                condition: 'Partly Cloudy'
            },
            forecast: [
                { day: 'Today', temp: 28, condition: 'Partly Cloudy', rain: 10, humidity: 67 },
                { day: 'Tomorrow', temp: 30, condition: 'Sunny', rain: 5, humidity: 60 },
                { day: 'Wed', temp: 27, condition: 'Rainy', rain: 80, humidity: 85 },
                { day: 'Thu', temp: 26, condition: 'Cloudy', rain: 40, humidity: 75 }
            ]
        };

        setFarms(sampleFarms);
        setFields(sampleFields);
        setCrops(sampleCrops);
        setAlerts(sampleAlerts);
        setWeather(sampleWeather);
    };

    // Farm operations
    const addFarm = (farm) => {
        const newFarm = { ...farm, id: Date.now(), createdAt: new Date(), status: 'active' };
        setFarms([...farms, newFarm]);
        return newFarm;
    };

    const updateFarm = (id, updates) => {
        setFarms(farms.map(farm => farm.id === id ? { ...farm, ...updates } : farm));
    };

    const deleteFarm = (id) => {
        setFarms(farms.filter(farm => farm.id !== id));
        setFields(fields.filter(field => field.farmId !== id));
    };

    // Field operations
    const addField = (field) => {
        const newField = { ...field, id: Date.now(), status: 'healthy', soilHealth: 80 };
        setFields([...fields, newField]);
        return newField;
    };

    const updateField = (id, updates) => {
        setFields(fields.map(field => field.id === id ? { ...field, ...updates } : field));
    };

    const deleteField = (id) => {
        setFields(fields.filter(field => field.id !== id));
    };

    // Alert operations
    const markAlertAsRead = (id) => {
        setAlerts(alerts.map(alert => alert.id === id ? { ...alert, read: true } : alert));
    };

    const dismissAlert = (id) => {
        setAlerts(alerts.filter(alert => alert.id !== id));
    };

    const addAlert = (alert) => {
        const newAlert = { ...alert, id: Date.now(), timestamp: new Date(), read: false };
        setAlerts([newAlert, ...alerts]);
    };

    // Recommendation operations
    const addRecommendation = (recommendation) => {
        const newRec = { ...recommendation, id: Date.now(), timestamp: new Date() };
        setRecommendations([newRec, ...recommendations]);
        return newRec;
    };

    const value = {
        farms,
        fields,
        crops,
        alerts,
        recommendations,
        weather,
        loading,
        setLoading,
        addFarm,
        updateFarm,
        deleteFarm,
        addField,
        updateField,
        deleteField,
        markAlertAsRead,
        dismissAlert,
        addAlert,
        addRecommendation
    };

    return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
