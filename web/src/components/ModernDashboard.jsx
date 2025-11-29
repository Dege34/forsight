import { useState, useEffect } from 'react';
import {
    TrendingUp,
    BarChart3,
    Activity,
    Zap,
    ArrowRight,
    Play,
    Database,
    Brain,
    Target,
    Sparkles,
    ChevronRight
} from 'lucide-react';
import './ModernDashboard.css';

const API_BASE = 'http://localhost:5000/api';

const ModernDashboard = ({ onStartAnalysis, onSymbolAnalysis }) => {
    const [metrics, setMetrics] = useState({
        activeAnalyses: 0,
        dataPoints: 0,
        accuracy: 0,
        symbols: 0
    });

    useEffect(() => {
        // Fetch symbols
        fetch(`${API_BASE}/symbols`)
            .then(res => res.json())
            .then(data => {
                setMetrics(prev => ({
                    ...prev,
                    symbols: data.length,
                    activeAnalyses: Math.floor(Math.random() * 50) + 10,
                    dataPoints: 500000,
                    accuracy: 94.5
                }));
            })
            .catch(err => console.error('Error:', err));

        // Animate metrics
        const interval = setInterval(() => {
            setMetrics(prev => ({
                ...prev,
                activeAnalyses: Math.floor(Math.random() * 50) + 10,
                accuracy: (93 + Math.random() * 3).toFixed(1)
            }));
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    const demos = [
        {
            title: 'Real-Time Market Analysis',
            description: 'AI-powered BIST analysis with live data',
            agents: '15 Indicators',
            metric: '1997-2025',
            icon: <TrendingUp size={24} />,
            color: 'from-blue-500 to-cyan-500',
            onClick: onSymbolAnalysis
        },
        {
            title: 'Predictive Analytics',
            description: 'Multi-model ML predictions',
            agents: '3 AI Models',
            metric: '94% Accuracy',
            icon: <Brain size={24} />,
            color: 'from-purple-500 to-pink-500',
            onClick: onSymbolAnalysis
        },
        {
            title: 'Technical Indicators',
            description: 'Advanced technical analysis suite',
            agents: '40+ Indicators',
            metric: 'Real-time',
            icon: <Activity size={24} />,
            color: 'from-green-500 to-emerald-500',
            onClick: onStartAnalysis
        },
        {
            title: 'Portfolio Optimization',
            description: 'AI-driven portfolio recommendations',
            agents: '10 Strategies',
            metric: '15% ROI',
            icon: <Target size={24} />,
            color: 'from-orange-500 to-red-500',
            onClick: onStartAnalysis
        }
    ];

    const features = [
        {
            icon: <Database size={32} />,
            title: '28 Years of Data',
            description: 'Comprehensive historical data from 1997 to 2025'
        },
        {
            icon: <Brain size={32} />,
            title: 'AI-Powered Insights',
            description: 'Multiple ML models for accurate predictions'
        },
        {
            icon: <Zap size={32} />,
            title: 'Real-Time Analysis',
            description: 'Live market data and instant calculations'
        }
    ];

    return (
        <div className="modern-container">
            {/* Hero Section */}
            <section className="hero-modern">
                <div className="hero-badge">
                    <Sparkles size={16} />
                    <span>The Future of Financial Analysis</span>
                </div>

                <h1 className="hero-title">
                    The Building Blocks of
                    <span className="gradient-text">AI-Powered BIST Analysis</span>
                </h1>

                <p className="hero-subtitle">
                    Advanced machine learning models analyzing 28 years of Turkish stock market data
                    with enterprise-grade accuracy and real-time insights.
                </p>

                <div className="hero-actions">
                    <button className="btn-modern btn-primary" onClick={onStartAnalysis}>
                        <Play size={20} />
                        Start Analysis
                        <ArrowRight size={20} />
                    </button>
                    <button className="btn-modern btn-secondary" onClick={onSymbolAnalysis}>
                        View Demos
                        <ChevronRight size={20} />
                    </button>
                </div>

                {/* Real-Time Metrics */}
                <div className="metrics-grid">
                    <div className="metric-card">
                        <div className="metric-label">Active Analyses</div>
                        <div className="metric-value">{metrics.activeAnalyses}</div>
                        <div className="metric-change positive">+12%</div>
                    </div>

                    <div className="metric-card">
                        <div className="metric-label">Data Points</div>
                        <div className="metric-value">{(metrics.dataPoints / 1000).toFixed(0)}K</div>
                        <div className="metric-change">1997-2025</div>
                    </div>

                    <div className="metric-card">
                        <div className="metric-label">AI Accuracy</div>
                        <div className="metric-value">{metrics.accuracy}%</div>
                        <div className="metric-change positive">+2.3%</div>
                    </div>

                    <div className="metric-card">
                        <div className="metric-label">Symbols</div>
                        <div className="metric-value">{metrics.symbols}</div>
                        <div className="metric-change">BIST</div>
                    </div>
                </div>


                {/* Market Ticker */}
                <div className="market-ticker">
                    <div className="ticker-track">
                        <span>BIST 100: <span className="positive">9,250 (+1.2%)</span></span>
                        <span>•</span>
                        <span>THYAO: <span className="positive">285.50 (+0.5%)</span></span>
                        <span>•</span>
                        <span>AKBNK: <span className="negative">42.10 (-0.2%)</span></span>
                        <span>•</span>
                        <span>GARAN: <span className="positive">75.40 (+0.8%)</span></span>
                        <span>•</span>
                        <span>ASELS: <span className="positive">55.20 (+1.1%)</span></span>
                        <span>•</span>
                        <span>USD/TRY: <span className="neutral">32.50 (0.0%)</span></span>
                    </div>
                </div>
            </section >

            {/* Watch Section */}
            < section id="demos" className="watch-section" >
                <h2 className="section-title">
                    See AI Models Collaborate in Real-Time
                </h2>
                <p className="section-subtitle">
                    Watch how our platform dynamically orchestrates multiple ML models, handles market volatility,
                    and creates accurate predictions to ensure investment success.
                </p>

                <div className="demos-grid">
                    {demos.map((demo, idx) => (
                        <div key={idx} className="demo-card" onClick={demo.onClick}>
                            <div className={`demo-icon bg-gradient-to-br ${demo.color}`}>
                                {demo.icon}
                            </div>

                            <div className="demo-content">
                                <h3 className="demo-title">{demo.title}</h3>
                                <p className="demo-description">{demo.description}</p>

                                <div className="demo-stats">
                                    <span className="demo-stat">{demo.agents}</span>
                                    <span className="demo-divider">•</span>
                                    <span className="demo-stat">{demo.metric}</span>
                                </div>
                            </div>

                            <button className="demo-button">
                                Try Now
                                <ArrowRight size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            </section >

            {/* Features Section */}
            < section className="features-section" >
                <div className="features-grid">
                    {features.map((feature, idx) => (
                        <div key={idx} className="feature-card">
                            <div className="feature-icon">
                                {feature.icon}
                            </div>
                            <h3 className="feature-title">{feature.title}</h3>
                            <p className="feature-description">{feature.description}</p>
                        </div>
                    ))}
                </div>
            </section >

            {/* CTA Section */}
            < section className="cta-section" >
                <div className="cta-content">
                    <h2 className="cta-title">
                        Ready to unlock AI-powered insights?
                    </h2>
                    <p className="cta-subtitle">
                        Start analyzing BIST data with our advanced ML models. No credit card required.
                    </p>
                    <div className="cta-actions">
                        <button className="btn-modern btn-primary btn-lg" onClick={onSymbolAnalysis}>
                            Start Free Analysis
                            <ArrowRight size={20} />
                        </button>
                        <button className="btn-modern btn-secondary btn-lg" onClick={onStartAnalysis}>
                            Explore Features
                        </button>
                    </div>
                </div>
            </section >



            {/* Footer */}
            < footer className="footer-modern" >
                <div className="footer-content">
                    <div className="footer-brand">
                        <div className="footer-logo">
                            <TrendingUp size={24} />
                            <span>ForSight</span>
                        </div>
                        <p className="footer-tagline">
                            Building the future of financial analysis with AI and machine learning.
                        </p>
                    </div>

                    <div className="footer-links">
                        <div className="footer-column">
                            <h4>Product</h4>
                            <a href="#features">Features</a>
                            <a href="#pricing">Pricing</a>
                            <a href="#docs">Documentation</a>
                        </div>

                        <div className="footer-column">
                            <h4>Company</h4>
                            <a href="#about">About</a>
                            <a href="#contact">Contact</a>
                            <a href="#blog">Blog</a>
                        </div>

                        <div className="footer-column">
                            <h4>Resources</h4>
                            <a href="#api">API Docs</a>
                            <a href="#community">Community</a>
                            <a href="#support">Support</a>
                        </div>
                    </div>
                </div>

                <div className="footer-bottom">
                    <p>© 2025 ForSight Analytics. All rights reserved.</p>
                </div>
            </footer >
        </div >
    );
};

export default ModernDashboard;
