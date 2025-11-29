import { useState, useEffect } from 'react';
import './App.css';
import ModernDashboard from './components/ModernDashboard';
import OperationSelector from './components/OperationSelector';
import DataVisualization from './components/DataVisualization';
import SymbolAnalysis from './components/SymbolAnalysis';
import { DemosPage, DocsPage, AboutPage, ContactPage } from './components/InfoPages';
import { TrendingUp, Database, BarChart3, Sun, Moon } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [selectedOperation, setSelectedOperation] = useState(null);
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    document.body.className = theme === 'light' ? 'light-mode' : '';
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const handleOperationSelect = (operation) => {
    setSelectedOperation(operation);
    setCurrentView('visualization');
  };

  const handleBackToHome = () => {
    setCurrentView('home');
    setSelectedOperation(null);
  };

  const handleBackToOperations = () => {
    setCurrentView('operations');
    setSelectedOperation(null);
  };

  const isLandingPage = ['home', 'demos', 'docs', 'about', 'contact'].includes(currentView);

  return (
    <div className={`app ${theme === 'light' ? 'light-mode' : ''}`}>
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo" onClick={() => setCurrentView('home')} style={{ cursor: 'pointer' }}>
            <div className="logo-icon">
              <TrendingUp size={24} />
            </div>
            <span className="logo-text">ForSight</span>
          </div>
          <div className="header-nav">
            <span onClick={() => setCurrentView('demos')} className="nav-link" style={{ cursor: 'pointer' }}>Demos</span>
            <span onClick={() => setCurrentView('docs')} className="nav-link" style={{ cursor: 'pointer' }}>Docs</span>
            <span onClick={() => setCurrentView('about')} className="nav-link" style={{ cursor: 'pointer' }}>About</span>
            <span onClick={() => setCurrentView('contact')} className="nav-link" style={{ cursor: 'pointer' }}>Contact</span>
            <button
              onClick={toggleTheme}
              className="nav-link"
              style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: '0.5rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: '0.5rem'
              }}
              title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
            </button>
            <button className="header-cta" onClick={() => setCurrentView('operations')}>Get Started</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={`app-main ${isLandingPage ? 'landing-view' : ''}`}>
        <div className="container">
          {currentView === 'home' && (
            <ModernDashboard
              onStartAnalysis={() => setCurrentView('operations')}
              onSymbolAnalysis={() => setCurrentView('symbol-analysis')}
            />
          )}

          {currentView === 'operations' && (
            <OperationSelector
              onSelectOperation={handleOperationSelect}
              onBack={handleBackToHome}
            />
          )}

          {currentView === 'visualization' && selectedOperation && (
            <DataVisualization
              operation={selectedOperation}
              onBack={handleBackToOperations}
            />
          )}

          {currentView === 'symbol-analysis' && (
            <SymbolAnalysis onBack={handleBackToHome} />
          )}

          {currentView === 'demos' && (
            <DemosPage
              onSymbolAnalysis={() => setCurrentView('symbol-analysis')}
              onStartAnalysis={() => setCurrentView('operations')}
            />
          )}

          {currentView === 'docs' && <DocsPage />}
          {currentView === 'about' && <AboutPage />}
          {currentView === 'contact' && <ContactPage />}
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="container">
          <p>© 2025 ForSight Analytics. Powered by BIST & Global Market Data</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
