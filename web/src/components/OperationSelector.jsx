import { useState } from 'react';
import {
    TrendingUp,
    TrendingDown,
    BarChart3,
    Activity,
    PieChart,
    Target,
    Zap,
    Brain,
    ArrowLeft,
    ArrowRight
} from 'lucide-react';
import './OperationSelector.css';

const OperationSelector = ({ onSelectOperation, onBack }) => {
    const operations = [
        {
            id: 'time-series',
            title: 'Time Series Analysis',
            description: 'Analyze historical price trends, patterns, and seasonality over time',
            icon: <TrendingUp size={32} />,
            color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            category: 'Technical Analysis',
            features: ['Historical Trends', 'Pattern Recognition', 'Seasonality Detection']
        },
        {
            id: 'valuation',
            title: 'Valuation Metrics',
            description: 'Comprehensive valuation analysis including P/E, P/B, EV/EBITDA ratios',
            icon: <Target size={32} />,
            color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            category: 'Fundamental Analysis',
            features: ['P/E Ratio', 'P/B Ratio', 'EV/EBITDA', 'Dividend Yield']
        },
        {
            id: 'correlation',
            title: 'Correlation Analysis',
            description: 'Discover relationships between BIST stocks and global market indices',
            icon: <Activity size={32} />,
            color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            category: 'Statistical Analysis',
            features: ['Stock Correlations', 'Index Relationships', 'Sector Analysis']
        },
        {
            id: 'volatility',
            title: 'Volatility & Risk',
            description: 'Measure market volatility, risk metrics, and price fluctuations',
            icon: <Zap size={32} />,
            color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            category: 'Risk Analysis',
            features: ['Historical Volatility', 'Beta Analysis', 'VaR Calculation']
        },
        {
            id: 'ai-prediction',
            title: 'AI Price Prediction',
            description: 'Multi-model ML predictions with Random Forest, XGBoost, and LSTM',
            icon: <Brain size={32} />,
            color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
            category: 'AI & Machine Learning',
            features: ['3 ML Models', 'Ensemble Predictions', 'Confidence Scores']
        },
        {
            id: 'portfolio',
            title: 'Portfolio Optimization',
            description: 'Optimize portfolio allocation using Modern Portfolio Theory',
            icon: <PieChart size={32} />,
            color: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
            category: 'Portfolio Management',
            features: ['Efficient Frontier', 'Risk-Return Optimization', 'Asset Allocation']
        },
        {
            id: 'technical',
            title: 'Technical Indicators',
            description: 'Advanced technical analysis with 40+ indicators and oscillators',
            icon: <BarChart3 size={32} />,
            color: 'linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)',
            category: 'Technical Analysis',
            features: ['RSI', 'MACD', 'Bollinger Bands', 'Moving Averages']
        },
        {
            id: 'sentiment',
            title: 'Market Sentiment',
            description: 'Analyze market sentiment using news, social media, and trading volume',
            icon: <TrendingDown size={32} />,
            color: 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)',
            category: 'Sentiment Analysis',
            features: ['News Analysis', 'Volume Trends', 'Market Mood']
        },
        {
            id: 'comparison',
            title: 'Multi-Symbol Comparison',
            description: 'Compare multiple stocks side-by-side with normalized metrics',
            icon: <Activity size={32} />,
            color: 'linear-gradient(135deg, #fdcbf1 0%, #e6dee9 100%)',
            category: 'Comparative Analysis',
            features: ['Side-by-Side Comparison', 'Normalized Charts', 'Performance Metrics']
        }
    ];

    const categories = [...new Set(operations.map(op => op.category))];

    return (
        <div className="operation-selector animate-fade-in">
            <div className="selector-header">
                <div className="quick-stats" style={{ marginTop: '2rem', width: '100%' }}>
                    <div className="stat-item">
                        <span className="stat-value">{operations.length}</span>
                        <span className="stat-label">Analysis Tools</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">{categories.length}</span>
                        <span className="stat-label">Categories</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-value">28</span>
                        <span className="stat-label">Years of Data</span>
                    </div>
                </div>
            </div>

            <div className="operations-container">
                {categories.map(category => (
                    <div key={category} className="category-section">
                        <h2 className="category-title">{category}</h2>
                        <div className="operations-grid">
                            {operations
                                .filter(op => op.category === category)
                                .map(operation => (
                                    <div
                                        key={operation.id}
                                        className="operation-card card"
                                        onClick={() => onSelectOperation(operation)}
                                    >
                                        <div
                                            className="operation-icon"
                                            style={{ background: operation.color }}
                                        >
                                            {operation.icon}
                                        </div>
                                        <div className="operation-content">
                                            <h3 className="operation-title">{operation.title}</h3>
                                            <p className="operation-description">
                                                {operation.description}
                                            </p>
                                            <div className="operation-features">
                                                {operation.features.map((feature, idx) => (
                                                    <span key={idx} className="feature-tag">
                                                        {feature}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="operation-arrow">
                                            <ArrowRight size={20} />
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>
                ))}
            </div>


        </div >
    );
};

export default OperationSelector;
