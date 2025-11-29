import { useState, useEffect } from 'react';
import {
    ArrowLeft,
    Download,
    Filter,
    Calendar,
    TrendingUp,
    TrendingDown,
    Activity,
    BarChart as BarChartIcon,
    ChevronDown,
    Search
} from 'lucide-react';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';
import './DataVisualization.css';
import './EmptyState.css';

const API_BASE = 'http://localhost:5000/api';

const DataVisualization = ({ operation, onBack }) => {
    const [selectedSymbol, setSelectedSymbol] = useState('XU100');
    const [timeRange, setTimeRange] = useState('1Y');
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const [symbols, setSymbols] = useState([]);
    const [chartType, setChartType] = useState('area');

    const timeRanges = ['1W', '1M', '3M', '6M', '1Y', '5Y', 'ALL'];
    const chartTypes = [
        { id: 'line', label: 'Line Chart' },
        { id: 'area', label: 'Area Chart' },
        { id: 'bar', label: 'Bar Chart' }
    ];

    const [inputSymbol, setInputSymbol] = useState(selectedSymbol);
    const [showSuggestions, setShowSuggestions] = useState(false);

    const filteredSymbols = symbols.filter(s =>
        s.toUpperCase().includes(inputSymbol.toUpperCase())
    );

    useEffect(() => {
        setInputSymbol(selectedSymbol);
    }, [selectedSymbol]);

    const handleSymbolSubmit = (e) => {
        e.preventDefault();
        if (inputSymbol.trim()) {
            setSelectedSymbol(inputSymbol.toUpperCase());
        }
    };

    // Fetch available symbols
    useEffect(() => {
        fetch(`${API_BASE}/symbols`)
            .then(res => res.json())
            .then(data => setSymbols(data.slice(0, 20))) // First 20 symbols
            .catch(err => console.error('Error fetching symbols:', err));
    }, []);

    // Fetch data when symbol or time range changes
    useEffect(() => {
        if (selectedSymbol) {
            fetchData(selectedSymbol, timeRange);
        }
    }, [selectedSymbol, timeRange]);

    const fetchData = async (symbol, range) => {
        setLoading(true);
        try {
            const response = await fetch(`${API_BASE}/time-range/${symbol}?range=${range}`);
            const result = await response.json();

            if (result.data && result.data.length > 0) {
                setData(result.data);

                // Calculate stats
                const closes = result.data.map(d => d.close);
                const currentValue = closes[closes.length - 1];
                const previousValue = closes[closes.length - 2] || currentValue;
                const change = currentValue - previousValue;
                const changePercent = (change / previousValue) * 100;

                // Calculate volume stats
                const volumes = result.data.map(d => d.volume || 0);
                const avgVolume = volumes.reduce((a, b) => a + b, 0) / volumes.length;

                // Calculate volatility
                const returns = closes.map((close, i) =>
                    i > 0 ? (close - closes[i - 1]) / closes[i - 1] : 0
                );
                const volatility = Math.sqrt(
                    returns.reduce((sum, r) => sum + r * r, 0) / returns.length
                ) * 100;

                setStats({
                    currentValue: currentValue.toFixed(2),
                    change: change.toFixed(2),
                    changePercent: changePercent.toFixed(2),
                    trend: change >= 0 ? 'up' : 'down',
                    volume: avgVolume.toFixed(0),
                    volatility: volatility.toFixed(2),
                    dataPoints: result.data.length
                });
            } else {
                setData([]);
                setStats(null);
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            setData([]);
            setStats(null);
        } finally {
            setLoading(false);
        }
    };

    const handleTimeRangeChange = (range) => {
        setTimeRange(range);
    };

    const renderChart = () => {
        if (!data || data.length === 0) {
            return (
                <div className="empty-state">
                    <div className="empty-icon">
                        <BarChartIcon size={64} />
                    </div>
                    <h3 className="empty-title">No Data Available</h3>
                    <p className="empty-description">
                        We couldn't find any data for the selected symbol and time range.
                        Try selecting a different symbol or adjusting the time range.
                    </p>
                    <div className="empty-suggestions">
                        <button className="suggestion-tag" onClick={() => setSelectedSymbol('XU100')}>Try: XU100</button>
                        <button className="suggestion-tag" onClick={() => setSelectedSymbol('THYAO')}>Try: THYAO</button>
                        <button className="suggestion-tag" onClick={() => setSelectedSymbol('AKBNK')}>Try: AKBNK</button>
                    </div>
                </div>
            );
        }

        const commonProps = {
            data,
            margin: { top: 10, right: 30, left: 0, bottom: 0 }
        };

        switch (chartType) {
            case 'area':
                return (
                    <AreaChart {...commonProps}>
                        <defs>
                            <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                        <XAxis dataKey="date" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e2538',
                                border: '1px solid #2d3748',
                                borderRadius: '8px'
                            }}
                        />
                        <Legend />
                        <Area
                            type="monotone"
                            dataKey="close"
                            stroke="#6366f1"
                            fillOpacity={1}
                            fill="url(#colorClose)"
                            name="Close Price"
                        />
                    </AreaChart>
                );
            case 'bar':
                return (
                    <BarChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                        <XAxis dataKey="date" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e2538',
                                border: '1px solid #2d3748',
                                borderRadius: '8px'
                            }}
                        />
                        <Legend />
                        <Bar dataKey="close" fill="#6366f1" name="Close Price" />
                    </BarChart>
                );
            default:
                return (
                    <LineChart {...commonProps}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                        <XAxis dataKey="date" stroke="#64748b" />
                        <YAxis stroke="#64748b" />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: '#1e2538',
                                border: '1px solid #2d3748',
                                borderRadius: '8px'
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="close"
                            stroke="#6366f1"
                            strokeWidth={2}
                            dot={false}
                            name="Close Price"
                        />
                        {data[0]?.sp500 && (
                            <Line
                                type="monotone"
                                dataKey="sp500"
                                stroke="#10b981"
                                strokeWidth={2}
                                dot={false}
                                name="S&P 500"
                            />
                        )}
                    </LineChart>
                );
        }
    };

    return (
        <div className="data-visualization animate-fade-in">
            {/* Header */}
            <div className="viz-header">

                <div className="header-info">
                    <div
                        className="operation-icon-large"
                        style={{ background: operation.color }}
                    >
                        {operation.icon}
                    </div>
                    <div>
                        <h1 className="viz-title">{operation.title}</h1>
                        <p className="viz-description">{operation.description}</p>
                    </div>
                </div>
            </div>

            {/* Symbol Selector */}
            <div className="symbol-selector card">
                <label className="control-label">
                    <Activity size={16} />
                    Enter Symbol
                </label>
                <form onSubmit={handleSymbolSubmit} className="symbol-select-wrapper" style={{ position: 'relative' }}>
                    <input
                        type="text"
                        className="symbol-select"
                        value={inputSymbol}
                        onChange={(e) => {
                            setInputSymbol(e.target.value.toUpperCase());
                            setShowSuggestions(true);
                        }}
                        onFocus={() => setShowSuggestions(true)}
                        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                        placeholder="Enter symbol (e.g. THYAO)"
                    />
                    <button type="submit" className="select-arrow" style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'inherit' }}>
                        <Search size={20} />
                    </button>

                    {showSuggestions && inputSymbol && filteredSymbols.length > 0 && (
                        <div className="symbol-suggestions" style={{
                            position: 'absolute',
                            top: '100%',
                            left: 0,
                            right: 0,
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            marginTop: '4px',
                            maxHeight: '200px',
                            overflowY: 'auto',
                            zIndex: 1000,
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                        }}>
                            {filteredSymbols.map(sym => (
                                <div
                                    key={sym}
                                    onClick={() => {
                                        setInputSymbol(sym);
                                        setSelectedSymbol(sym);
                                        setShowSuggestions(false);
                                    }}
                                    style={{
                                        padding: '0.75rem 1rem',
                                        cursor: 'pointer',
                                        borderBottom: '1px solid #334155',
                                        color: '#e2e8f0',
                                        transition: 'background 0.2s'
                                    }}
                                    onMouseEnter={(e) => e.target.style.background = '#334155'}
                                    onMouseLeave={(e) => e.target.style.background = 'transparent'}
                                >
                                    {sym}
                                </div>
                            ))}
                        </div>
                    )}
                </form>
            </div>

            {/* Stats Cards */}
            {stats && (
                <div className="stats-row">
                    <div className="stat-card-viz card">
                        <div className="stat-card-header">
                            <span className="stat-card-label">Current Value</span>
                            {stats.trend === 'up' ? (
                                <TrendingUp size={20} style={{ color: '#10b981' }} />
                            ) : (
                                <TrendingDown size={20} style={{ color: '#ef4444' }} />
                            )}
                        </div>
                        <div className="stat-card-value" style={{ color: stats.trend === 'up' ? '#10b981' : '#ef4444' }}>
                            {stats.currentValue}
                        </div>
                        <div
                            className={`stat-card-change ${stats.trend}`}
                            style={{ color: stats.trend === 'up' ? '#10b981' : '#ef4444' }}
                        >
                            {stats.trend === 'up' ? '+' : ''}{stats.changePercent}%
                        </div>
                    </div>

                    <div className="stat-card-viz card">
                        <div className="stat-card-header">
                            <span className="stat-card-label">Daily Change</span>
                            <Activity size={20} style={{ color: '#3b82f6' }} />
                        </div>
                        <div className="stat-card-value" style={{ color: '#3b82f6' }}>
                            {stats.change}
                        </div>
                        <div className="stat-card-change" style={{ color: '#3b82f6' }}>
                            {stats.trend === 'up' ? '+' : ''}{stats.changePercent}%
                        </div>
                    </div>

                    <div className="stat-card-viz card">
                        <div className="stat-card-header">
                            <span className="stat-card-label">Avg Volume</span>
                            <BarChartIcon size={20} style={{ color: '#8b5cf6' }} />
                        </div>
                        <div className="stat-card-value" style={{ color: '#8b5cf6' }}>
                            {stats.volume}
                        </div>
                        <div className="stat-card-change" style={{ color: '#8b5cf6' }}>
                            {stats.dataPoints} points
                        </div>
                    </div>

                    <div className="stat-card-viz card">
                        <div className="stat-card-header">
                            <span className="stat-card-label">Volatility</span>
                            <Activity size={20} style={{ color: '#f59e0b' }} />
                        </div>
                        <div className="stat-card-value" style={{ color: '#f59e0b' }}>
                            {stats.volatility}%
                        </div>
                        <div className="stat-card-change" style={{ color: '#f59e0b' }}>
                            {timeRange}
                        </div>
                    </div>
                </div>
            )
            }

            {/* Controls */}
            <div className="viz-controls card">
                <div className="control-group">
                    <label className="control-label">
                        <Calendar size={16} />
                        Time Range
                    </label>
                    <div className="time-range-buttons">
                        {timeRanges.map(range => (
                            <button
                                key={range}
                                className={`time-btn ${timeRange === range ? 'active' : ''}`}
                                onClick={() => handleTimeRangeChange(range)}
                            >
                                {range}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="control-group">
                    <label className="control-label">
                        <Activity size={16} />
                        Chart Type
                    </label>
                    <div className="chart-type-buttons">
                        {chartTypes.map(type => (
                            <button
                                key={type.id}
                                className={`chart-type-btn ${chartType === type.id ? 'active' : ''}`}
                                onClick={() => setChartType(type.id)}
                            >
                                {type.label}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="control-actions">
                    <button className="btn btn-secondary">
                        <Filter size={16} />
                        Filters
                    </button>
                    <button className="btn btn-primary">
                        <Download size={16} />
                        Export
                    </button>
                </div>
            </div>

            {/* Chart */}
            <div className="chart-container card">
                <div className="chart-header">
                    <h2 className="chart-title">
                        {selectedSymbol} - {operation.title}
                    </h2>
                    <div className="chart-legend">
                        <div className="legend-item">
                            <span className="legend-dot" style={{ background: '#6366f1' }}></span>
                            <span>{selectedSymbol}</span>
                        </div>
                    </div>
                </div>
                <div className="chart-wrapper">
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '4rem' }}>
                            <Activity className="spin" size={48} />
                            <p>Loading data...</p>
                        </div>
                    ) : (
                        <ResponsiveContainer width="100%" height={400}>
                            {renderChart()}
                        </ResponsiveContainer>
                    )}
                </div>
            </div>

            {/* Additional Info */}
            <div className="info-grid grid grid-2">
                <div className="info-card card">
                    <h3 className="info-title">Analysis Summary</h3>
                    <div className="info-content">
                        <div className="info-item">
                            <span className="info-label">Symbol:</span>
                            <span className="info-value">{selectedSymbol}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Time Range:</span>
                            <span className="info-value">{timeRange}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Data Points:</span>
                            <span className="info-value">{stats?.dataPoints || 0}</span>
                        </div>
                        <div className="info-item">
                            <span className="info-label">Chart Type:</span>
                            <span className="info-value">{chartType.toUpperCase()}</span>
                        </div>
                    </div>
                </div>
                <div className="info-card card">
                    <h3 className="info-title">Key Insights</h3>
                    <div className="info-content">
                        <div className="insight-item">
                            <span className="insight-icon">📈</span>
                            <span>Real-time data from 1997-2025</span>
                        </div>
                        <div className="insight-item">
                            <span className="insight-icon">⚡</span>
                            <span>Using {stats?.dataPoints || 0} data points</span>
                        </div>
                        <div className="insight-item">
                            <span className="insight-icon">💡</span>
                            <span>Volatility: {stats?.volatility || 0}%</span>
                        </div>
                    </div>
                </div>
            </div>
        </div >
    );
};

export default DataVisualization;
