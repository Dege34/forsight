import { useState, useEffect } from 'react';
import {
    Search,
    TrendingUp,
    TrendingDown,
    Calendar,
    Download,
    RefreshCw,
    BarChart3,
    Activity,
    Target,
    Zap,
    AlertCircle,
    CheckCircle,
    ArrowLeft
} from 'lucide-react';
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine
} from 'recharts';
import './SymbolAnalysis.css';
import './ModelComparison.css';
import './EmptyState.css';

const API_BASE = 'http://localhost:5000/api';

const SymbolAnalysis = ({ onBack }) => {
    const [symbols, setSymbols] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState('');
    const [searchTerm, setSearchTerm] = useState('');
    const [timeRange, setTimeRange] = useState('1Y');
    const [loading, setLoading] = useState(false);
    const [symbolData, setSymbolData] = useState(null);
    const [compareSymbols, setCompareSymbols] = useState([]);
    const [comparisonData, setComparisonData] = useState(null);

    const timeRanges = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y', '10Y', 'ALL'];

    // Fetch available symbols
    useEffect(() => {
        fetch(`${API_BASE}/symbols`)
            .then(res => res.json())
            .then(data => setSymbols(data))
            .catch(err => console.error('Error fetching symbols:', err));
    }, []);

    // Fetch symbol data
    const fetchSymbolData = async (symbol, range) => {
        console.log('Fetching data for:', symbol, 'Range:', range);
        setLoading(true);
        try {
            console.log('Fetching range data from:', `${API_BASE}/time-range/${symbol}?range=${range}`);
            const response = await fetch(`${API_BASE}/time-range/${symbol}?range=${range}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const rangeData = await response.json();
            console.log('Range data received:', rangeData);

            console.log('Fetching detail data from:', `${API_BASE}/symbol/${symbol}`);
            const detailResponse = await fetch(`${API_BASE}/symbol/${symbol}`);

            if (!detailResponse.ok) {
                throw new Error(`HTTP error! status: ${detailResponse.status}`);
            }

            const detailData = await detailResponse.json();
            console.log('Detail data received:', detailData);

            setSymbolData({
                ...detailData,
                rangeData: rangeData.data
            });

            console.log('Symbol data set successfully');
        } catch (error) {
            console.error('Error fetching symbol data:', error);
            alert(`Error loading data: ${error.message}. Please check if the API is running on port 5000.`);
        } finally {
            setLoading(false);
        }
    };

    // Handle symbol selection
    const handleSymbolSelect = (symbol) => {
        setSelectedSymbol(symbol);
        setSearchTerm(symbol);
        fetchSymbolData(symbol, timeRange);
    };

    // Handle time range change
    const handleTimeRangeChange = (range) => {
        setTimeRange(range);
        if (selectedSymbol) {
            fetchSymbolData(selectedSymbol, range);
        }
    };

    // Handle comparison
    const handleCompare = async () => {
        if (compareSymbols.length < 2) return;

        try {
            const response = await fetch(`${API_BASE}/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbols: compareSymbols })
            });
            const data = await response.json();
            setComparisonData(data);
        } catch (error) {
            console.error('Error comparing symbols:', error);
        }
    };

    const filteredSymbols = symbols.filter(s =>
        s.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="symbol-analysis">
            {/* Back Button */}


            {/* Search Section */}
            <div className="search-section card">
                <div className="search-header">
                    <h2>Symbol Search & Analysis</h2>
                    <p>Search for any symbol from our database (1997-2025)</p>
                </div>

                <div className="search-input-wrapper">
                    <Search size={20} />
                    <input
                        type="text"
                        placeholder="Search symbol (e.g., THYAO, AKBNK, GARAN...)"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </div>

                {searchTerm && filteredSymbols.length > 0 && !selectedSymbol && (
                    <div className="search-results">
                        {filteredSymbols.slice(0, 10).map(symbol => (
                            <div
                                key={symbol}
                                className="search-result-item"
                                onClick={() => handleSymbolSelect(symbol)}
                            >
                                <BarChart3 size={16} />
                                <span>{symbol}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Time Range Selector */}
            {selectedSymbol && (
                <div className="time-range-section card">
                    <div className="time-range-header">
                        <Calendar size={20} />
                        <span>Select Time Range</span>
                    </div>
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
            )}

            {/* Loading State */}
            {loading && (
                <div className="loading-state card">
                    <RefreshCw className="spin" size={32} />
                    <p>Loading data...</p>
                </div>
            )}

            {/* Empty/Error State */}
            {selectedSymbol && !loading && !symbolData && (
                <div className="empty-state card">
                    <div className="empty-icon">
                        <BarChart3 size={64} />
                    </div>
                    <h3 className="empty-title">No Data Available</h3>
                    <p className="empty-description">
                        We couldn't find any data for <strong>{selectedSymbol}</strong>.
                        Please check the symbol or try another one.
                    </p>
                    <div className="empty-suggestions">
                        <button className="btn btn-secondary" onClick={() => handleSymbolSelect('XU100')}>Try XU100</button>
                        <button className="btn btn-secondary" onClick={() => handleSymbolSelect('THYAO')}>Try THYAO</button>
                    </div>
                </div>
            )}

            {/* Symbol Data Display */}
            {!loading && symbolData && (
                <>
                    {/* Statistics Cards */}
                    <div className="stats-grid">
                        <div className="stat-card card">
                            <div className="stat-icon" style={{ background: '#6366f1' }}>
                                <TrendingUp size={24} />
                            </div>
                            <div className="stat-content">
                                <span className="stat-label">Current Price</span>
                                <span className="stat-value">
                                    {symbolData.statistics.price_stats.current.toFixed(2)}
                                </span>
                                <span className={`stat-change ${symbolData.statistics.returns_stats.total_return >= 0 ? 'positive' : 'negative'}`}>
                                    {symbolData.statistics.returns_stats.total_return >= 0 ? '+' : ''}
                                    {symbolData.statistics.returns_stats.total_return.toFixed(2)}%
                                </span>
                            </div>
                        </div>

                        <div className="stat-card card">
                            <div className="stat-icon" style={{ background: '#10b981' }}>
                                <Activity size={24} />
                            </div>
                            <div className="stat-content">
                                <span className="stat-label">Avg Daily Return</span>
                                <span className="stat-value">
                                    {symbolData.statistics.returns_stats.avg_daily_return.toFixed(3)}%
                                </span>
                                <span className="stat-sublabel">
                                    Sharpe: {symbolData.statistics.returns_stats.sharpe_ratio.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        <div className="stat-card card">
                            <div className="stat-icon" style={{ background: '#f59e0b' }}>
                                <Zap size={24} />
                            </div>
                            <div className="stat-content">
                                <span className="stat-label">Volatility</span>
                                <span className="stat-value">
                                    {symbolData.statistics.returns_stats.volatility.toFixed(2)}%
                                </span>
                                <span className="stat-sublabel">
                                    Std Dev: {symbolData.statistics.price_stats.std.toFixed(2)}
                                </span>
                            </div>
                        </div>

                        <div className="stat-card card">
                            <div className="stat-icon" style={{ background: '#3b82f6' }}>
                                <BarChart3 size={24} />
                            </div>
                            <div className="stat-content">
                                <span className="stat-label">Data Points</span>
                                <span className="stat-value">
                                    {symbolData.statistics.total_records.toLocaleString()}
                                </span>
                                <span className="stat-sublabel">
                                    {symbolData.statistics.date_range.start} - {symbolData.statistics.date_range.end}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Prediction Section */}
                    {symbolData.prediction && (
                        <div className="prediction-section card">
                            <div className="prediction-header">
                                <Target size={24} />
                                <h3>AI-Powered Multi-Model Prediction</h3>
                                <span className={`confidence-badge ${symbolData.prediction.confidence.toLowerCase()}`}>
                                    {symbolData.prediction.confidence} Confidence
                                </span>
                            </div>

                            <div className="prediction-grid">
                                <div className="prediction-item">
                                    <span className="prediction-label">Current Price</span>
                                    <span className="prediction-value">
                                        {symbolData.prediction.current_price.toFixed(2)}
                                    </span>
                                </div>
                                <div className="prediction-item">
                                    <span className="prediction-label">Predicted Price ({symbolData.prediction.days_ahead}d)</span>
                                    <span className="prediction-value highlight">
                                        {symbolData.prediction.predicted_price.toFixed(2)}
                                    </span>
                                </div>
                                <div className="prediction-item">
                                    <span className="prediction-label">Expected Change</span>
                                    <span className={`prediction-value ${symbolData.prediction.predicted_change_percent >= 0 ? 'positive' : 'negative'}`}>
                                        {symbolData.prediction.predicted_change_percent >= 0 ? '+' : ''}
                                        {symbolData.prediction.predicted_change_percent.toFixed(2)}%
                                    </span>
                                </div>
                                <div className="prediction-item">
                                    <span className="prediction-label">Best Model Accuracy</span>
                                    <span className="prediction-value">
                                        {symbolData.prediction.accuracy.toFixed(1)}%
                                    </span>
                                </div>
                            </div>

                            {/* Model Comparison */}
                            {symbolData.prediction.all_models && (
                                <div className="model-comparison">
                                    <h4>Model Performance Comparison</h4>
                                    <div className="models-grid">
                                        {Object.entries(symbolData.prediction.all_models).map(([modelName, metrics]) => (
                                            <div key={modelName} className={`model-card ${modelName === symbolData.prediction.best_model ? 'best-model' : ''}`}>
                                                <div className="model-header">
                                                    <span className="model-name">{modelName}</span>
                                                    {modelName === symbolData.prediction.best_model && (
                                                        <span className="best-badge">BEST</span>
                                                    )}
                                                </div>
                                                <div className="model-metrics">
                                                    <div className="metric">
                                                        <span className="metric-label">Accuracy:</span>
                                                        <span className="metric-value">{metrics.accuracy.toFixed(1)}%</span>
                                                    </div>
                                                    <div className="metric">
                                                        <span className="metric-label">Test R²:</span>
                                                        <span className="metric-value">{metrics.test_r2.toFixed(3)}</span>
                                                    </div>
                                                    <div className="metric">
                                                        <span className="metric-label">CV R²:</span>
                                                        <span className="metric-value">{metrics.cv_r2.toFixed(3)}</span>
                                                    </div>
                                                    <div className="metric">
                                                        <span className="metric-label">RMSE:</span>
                                                        <span className="metric-value">{metrics.rmse.toFixed(2)}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="prediction-details">
                                <h4>Prediction Methodology</h4>
                                <div className="methodology-grid">
                                    <div className="methodology-item">
                                        <CheckCircle size={16} />
                                        <span>Best Model: {symbolData.prediction.best_model}</span>
                                    </div>
                                    <div className="methodology-item">
                                        <CheckCircle size={16} />
                                        <span>Features Used: {symbolData.prediction.prediction_basis.features_used}</span>
                                    </div>
                                    <div className="methodology-item">
                                        <CheckCircle size={16} />
                                        <span>Training Samples: {symbolData.prediction.prediction_basis.training_samples}</span>
                                    </div>
                                    <div className="methodology-item">
                                        <CheckCircle size={16} />
                                        <span>Cross-Validation: {symbolData.prediction.prediction_basis.cross_validation_folds}-Fold</span>
                                    </div>
                                </div>

                                {/* Top Features */}
                                {symbolData.prediction.prediction_basis.top_features && Object.keys(symbolData.prediction.prediction_basis.top_features).length > 0 && (
                                    <div className="top-correlations">
                                        <h5>Top Important Features (Feature Importance):</h5>
                                        {Object.entries(symbolData.prediction.prediction_basis.top_features).map(([feature, importance], idx) => (
                                            <div key={idx} className="correlation-item">
                                                <span className="correlation-feature">{feature}</span>
                                                <div className="correlation-bar-container">
                                                    <div
                                                        className="correlation-bar"
                                                        style={{
                                                            width: `${importance * 100}%`,
                                                            background: '#6366f1'
                                                        }}
                                                    />
                                                </div>
                                                <span className="correlation-value">
                                                    {(importance * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {/* Top Correlations */}
                                {symbolData.prediction.prediction_basis.top_correlations && (
                                    <div className="top-correlations">
                                        <h5>Top Correlated Features:</h5>
                                        {Object.entries(symbolData.prediction.prediction_basis.top_correlations).slice(0, 5).map(([feature, corr], idx) => (
                                            <div key={idx} className="correlation-item">
                                                <span className="correlation-feature">{feature}</span>
                                                <div className="correlation-bar-container">
                                                    <div
                                                        className="correlation-bar"
                                                        style={{
                                                            width: `${Math.abs(corr) * 100}%`,
                                                            background: corr > 0 ? '#10b981' : '#ef4444'
                                                        }}
                                                    />
                                                </div>
                                                <span className="correlation-value">
                                                    {(corr * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Charts Section */}
                    <div className="charts-section">
                        {/* Price Chart */}
                        <div className="chart-card card">
                            <h3>Price Movement</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={symbolData.rangeData}>
                                    <defs>
                                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Area type="monotone" dataKey="close" stroke="#6366f1" fillOpacity={1} fill="url(#colorPrice)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Returns Distribution */}
                        <div className="chart-card card">
                            <h3>Daily Returns Distribution</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <BarChart data={symbolData.data.slice(-100)}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Bar dataKey="returns" fill="#10b981" />
                                    <ReferenceLine y={0} stroke="#ef4444" />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Z-Score */}
                        <div className="chart-card card">
                            <h3>Z-Score (Price Deviation)</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={symbolData.data.slice(-200)}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Line type="monotone" dataKey="z_score" stroke="#f59e0b" strokeWidth={2} dot={false} />
                                    <ReferenceLine y={2} stroke="#ef4444" strokeDasharray="3 3" label="Overbought" />
                                    <ReferenceLine y={-2} stroke="#10b981" strokeDasharray="3 3" label="Oversold" />
                                    <ReferenceLine y={0} stroke="#64748b" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Normalized Price */}
                        <div className="chart-card card">
                            <h3>Normalized Price Movement</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={symbolData.data}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Line type="monotone" dataKey="normalized_price" stroke="#8b5cf6" strokeWidth={2} dot={false} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Buy/Sell Signals */}
                        <div className="chart-card card">
                            <h3>Buy/Sell Signals (MA Crossover)</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <LineChart data={symbolData.data.slice(-200)}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Line type="monotone" dataKey="close" stroke="#6366f1" strokeWidth={2} dot={false} />
                                    <Line type="monotone" dataKey="ma_20" stroke="#10b981" strokeWidth={1} dot={false} />
                                    <Line type="monotone" dataKey="ma_50" stroke="#ef4444" strokeWidth={1} dot={false} />
                                    <Legend />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Volatility */}
                        <div className="chart-card card">
                            <h3>Rolling Volatility (20-day)</h3>
                            <ResponsiveContainer width="100%" height={300}>
                                <AreaChart data={symbolData.data.slice(-200)}>
                                    <defs>
                                        <linearGradient id="colorVol" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                                            <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                                    <XAxis dataKey="date" stroke="#64748b" />
                                    <YAxis stroke="#64748b" />
                                    <Tooltip contentStyle={{ backgroundColor: '#1e2538', border: '1px solid #2d3748' }} />
                                    <Area type="monotone" dataKey="volatility" stroke="#f59e0b" fillOpacity={1} fill="url(#colorVol)" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Data Table */}
                    <div className="data-table-section card">
                        <div className="table-header">
                            <h3>Historical Data</h3>
                            <button className="btn btn-primary">
                                <Download size={16} />
                                Export CSV
                            </button>
                        </div>
                        <div className="table-wrapper">
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Open</th>
                                        <th>High</th>
                                        <th>Low</th>
                                        <th>Close</th>
                                        <th>Volume</th>
                                        <th>Returns</th>
                                        <th>Signal</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {symbolData.data.slice(-50).reverse().map((row, idx) => (
                                        <tr key={idx}>
                                            <td>{row.date}</td>
                                            <td>{row.open?.toFixed(2) || 'N/A'}</td>
                                            <td>{row.high?.toFixed(2) || 'N/A'}</td>
                                            <td>{row.low?.toFixed(2) || 'N/A'}</td>
                                            <td>{row.close?.toFixed(2) || 'N/A'}</td>
                                            <td>{row.volume?.toLocaleString() || 'N/A'}</td>
                                            <td className={row.returns >= 0 ? 'positive' : 'negative'}>
                                                {row.returns ? (row.returns * 100).toFixed(2) + '%' : 'N/A'}
                                            </td>
                                            <td>
                                                {row.signal === 1 && <span className="signal-badge buy">BUY</span>}
                                                {row.signal === -1 && <span className="signal-badge sell">SELL</span>}
                                                {row.signal === 0 && <span className="signal-badge hold">HOLD</span>}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default SymbolAnalysis;
