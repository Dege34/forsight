import { TrendingUp, Database, BarChart3, Activity, Zap, Globe } from 'lucide-react';
import './Dashboard.css';

const Dashboard = ({ onStartAnalysis, onSymbolAnalysis }) => {
    const features = [
        {
            icon: <Database size={32} />,
            title: 'Comprehensive Database',
            description: '28 years of historical data from 1997 to 2025',
            color: '#6366f1'
        },
        {
            icon: <BarChart3 size={32} />,
            title: '40+ Indicators',
            description: 'BIST, Brent Oil, S&P 500, VIX and more',
            color: '#8b5cf6'
        },
        {
            icon: <Activity size={32} />,
            title: 'Advanced Analytics',
            description: 'Technical indicators including ATR, OBV, MFI',
            color: '#10b981'
        },
        {
            icon: <Globe size={32} />,
            title: 'Global Markets',
            description: 'International market data and correlations',
            color: '#3b82f6'
        }
    ];

    const stats = [
        { label: 'Total Records', value: '500K+', trend: '+12%' },
        { label: 'Data Points', value: '40+', trend: 'Active' },
        { label: 'Years Coverage', value: '28', trend: '1997-2025' },
        { label: 'Update Frequency', value: 'Daily', trend: 'Real-time' }
    ];

    return (
        <div className="dashboard animate-fade-in">
            {/* Hero Section */}
            <section className="hero-section">
                <div className="hero-content">
                    <div className="hero-badge">
                        <Zap size={16} />
                        <span>Powered by Advanced Analytics</span>
                    </div>
                    <h1 className="hero-title">
                        Unlock the Power of
                        <span className="gradient-text"> Financial Data</span>
                    </h1>
                    <p className="hero-description">
                        Explore 28 years of BIST and global market data with advanced technical indicators.
                        Make informed decisions with comprehensive analytics and beautiful visualizations.
                    </p>
                    <div className="hero-actions">
                        <button className="btn btn-primary btn-lg" onClick={onStartAnalysis}>
                            <TrendingUp size={20} />
                            Start Analysis
                        </button>
                        <button className="btn btn-secondary btn-lg" onClick={onSymbolAnalysis}>
                            <Database size={20} />
                            Symbol Search
                        </button>
                    </div>
                </div>
                <div className="hero-visual">
                    <div className="floating-card card-1">
                        <div className="card-icon" style={{ background: '#6366f1' }}>
                            <TrendingUp size={24} />
                        </div>
                        <div className="card-content">
                            <span className="card-label">BIST 100</span>
                            <span className="card-value">10,234.56</span>
                            <span className="card-change positive">+2.34%</span>
                        </div>
                    </div>
                    <div className="floating-card card-2">
                        <div className="card-icon" style={{ background: '#10b981' }}>
                            <Activity size={24} />
                        </div>
                        <div className="card-content">
                            <span className="card-label">S&P 500</span>
                            <span className="card-value">4,567.89</span>
                            <span className="card-change positive">+1.23%</span>
                        </div>
                    </div>
                    <div className="floating-card card-3">
                        <div className="card-icon" style={{ background: '#f59e0b' }}>
                            <BarChart3 size={24} />
                        </div>
                        <div className="card-content">
                            <span className="card-label">Brent Oil</span>
                            <span className="card-value">$82.45</span>
                            <span className="card-change negative">-0.56%</span>
                        </div>
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="stats-section">
                <div className="stats-grid">
                    {stats.map((stat, index) => (
                        <div key={index} className="stat-card card glass">
                            <div className="stat-header">
                                <span className="stat-label">{stat.label}</span>
                                <span className="badge badge-info">{stat.trend}</span>
                            </div>
                            <div className="stat-value">{stat.value}</div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Features Section */}
            <section className="features-section">
                <div className="section-header">
                    <h2 className="section-title">Powerful Features</h2>
                    <p className="section-description">
                        Everything you need for comprehensive financial market analysis
                    </p>
                </div>
                <div className="features-grid grid grid-2">
                    {features.map((feature, index) => (
                        <div key={index} className="feature-card card">
                            <div className="feature-icon" style={{ background: feature.color }}>
                                {feature.icon}
                            </div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="cta-section">
                <div className="cta-card card glass">
                    <div className="cta-content">
                        <h2 className="cta-title">Ready to Start Analyzing?</h2>
                        <p className="cta-description">
                            Access powerful analytics tools and visualize your data like never before
                        </p>
                        <button className="btn btn-primary btn-lg" onClick={onStartAnalysis}>
                            <TrendingUp size={20} />
                            Get Started Now
                        </button>
                    </div>
                    <div className="cta-visual">
                        <div className="pulse-ring"></div>
                        <div className="pulse-ring delay-1"></div>
                        <div className="pulse-ring delay-2"></div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Dashboard;
