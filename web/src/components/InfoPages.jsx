import React from 'react';
import { Database, Brain, Zap, Mail, MapPin, ArrowRight, Activity, Target, TrendingUp } from 'lucide-react';
import './ModernDashboard.css';

export const DemosPage = ({ onSymbolAnalysis, onStartAnalysis }) => {
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

    return (
        <div className="modern-container" style={{ paddingTop: '4rem' }}>
            <section className="watch-section">
                <h2 className="section-title">Interactive Demos</h2>
                <p className="section-subtitle">Experience the power of ForSight's AI models firsthand.</p>
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
                                Try Now <ArrowRight size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
};

export const DocsPage = () => (
    <div className="modern-container" style={{ paddingTop: '4rem' }}>
        <section className="features-section">
            <h2 className="section-title">Documentation</h2>
            <p className="section-subtitle">Everything you need to integrate and build with ForSight.</p>
            <div className="features-grid">
                <div className="feature-card">
                    <div className="feature-icon"><Database size={32} /></div>
                    <h3 className="feature-title">Quick Start</h3>
                    <p className="feature-description">Get up and running with ForSight in less than 5 minutes. Learn the basics of our platform.</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon"><Brain size={32} /></div>
                    <h3 className="feature-title">API Reference</h3>
                    <p className="feature-description">Detailed API documentation for all our endpoints, including authentication and rate limits.</p>
                </div>
                <div className="feature-card">
                    <div className="feature-icon"><Zap size={32} /></div>
                    <h3 className="feature-title">Guides</h3>
                    <p className="feature-description">Step-by-step tutorials for common use cases like portfolio optimization and risk analysis.</p>
                </div>
            </div>
        </section>
    </div>
);

export const AboutPage = () => (
    <div className="modern-container" style={{ paddingTop: '4rem' }}>
        <section className="watch-section">
            <h2 className="section-title">About Us</h2>
            <p className="section-subtitle">Empowering investors with AI-driven insights since 2025.</p>
            <div className="about-content" style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center', color: '#94a3b8', lineHeight: '1.8', fontSize: '1.1rem' }}>
                <p>
                    ForSight is a leading provider of AI-powered financial analysis tools.
                    Our mission is to democratize access to institutional-grade market data and predictive analytics.
                </p>
                <br />
                <p>
                    We combine 28 years of historical data with state-of-the-art machine learning models to help you make smarter investment decisions.
                    Our team consists of financial experts, data scientists, and software engineers dedicated to building the future of finance.
                </p>
            </div>
        </section>
    </div>
);

export const ContactPage = () => (
    <div className="modern-container" style={{ paddingTop: '4rem' }}>
        <section className="cta-section">
            <div className="cta-content">
                <h2 className="cta-title">Contact Us</h2>
                <p className="cta-subtitle">Have questions? We'd love to hear from you.</p>
                <div className="contact-info" style={{ display: 'flex', gap: '3rem', justifyContent: 'center', marginTop: '3rem', flexWrap: 'wrap' }}>
                    <div className="contact-item" style={{ textAlign: 'center' }}>
                        <div style={{ background: 'rgba(255,255,255,0.1)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <Mail size={24} color="#a5b4fc" />
                        </div>
                        <h4>Email</h4>
                        <p>support@forsight.com</p>
                    </div>
                    <div className="contact-item" style={{ textAlign: 'center' }}>
                        <div style={{ background: 'rgba(255,255,255,0.1)', width: '60px', height: '60px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                            <MapPin size={24} color="#a5b4fc" />
                        </div>
                        <h4>Location</h4>
                        <p>Istanbul, Turkey</p>
                    </div>
                </div>
                <div className="cta-actions" style={{ marginTop: '3rem' }}>
                    <button className="btn-modern btn-primary btn-lg">
                        Send Message
                    </button>
                </div>
            </div>
        </section>
    </div>
);
