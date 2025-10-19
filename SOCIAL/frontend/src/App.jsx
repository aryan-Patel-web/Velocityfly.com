import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import Landing_Page from './Landing_Page';
import './App.css';

// Footer Pages Imports - Using ACTUAL file names (case-sensitive!)
let PrivacyPolicy, TermsOfService, CookiePolicy, Contact, About;
let Features, Pricing, HelpCenter, Documentation, Blog;
let Careers, Status, Community, Integrations, API;

// Import with EXACT file names that exist
try {
  PrivacyPolicy = require('./footerpages/Privacypolicy').default;
} catch { PrivacyPolicy = () => <ComingSoon page="Privacy Policy" />; }

try {
  TermsOfService = require('./footerpages/Termsofservice').default;
} catch { TermsOfService = () => <ComingSoon page="Terms of Service" />; }

try {
  CookiePolicy = require('./footerpages/Cookiepolicy').default;
} catch { CookiePolicy = () => <ComingSoon page="Cookie Policy" />; }

try {
  Contact = require('./footerpages/Contact').default;
} catch { Contact = () => <ComingSoon page="Contact" />; }

try {
  About = require('./footerpages/About').default;
} catch { About = () => <ComingSoon page="About" />; }

try {
  Features = require('./footerpages/Features').default;
} catch { Features = () => <ComingSoon page="Features" />; }

try {
  Pricing = require('./footerpages/Pricing').default;
} catch { Pricing = () => <ComingSoon page="Pricing" />; }

try {
  HelpCenter = require('./footerpages/Helpcenter').default;
} catch { HelpCenter = () => <ComingSoon page="Help Center" />; }

try {
  Documentation = require('./footerpages/Documentation').default;
} catch { Documentation = () => <ComingSoon page="Documentation" />; }

try {
  Blog = require('./footerpages/Blog').default;
} catch { Blog = () => <ComingSoon page="Blog" />; }

try {
  Careers = require('./footerpages/Careers').default;
} catch { Careers = () => <ComingSoon page="Careers" />; }

try {
  Status = require('./footerpages/Status').default;
} catch { Status = () => <ComingSoon page="Status" />; }

try {
  Community = require('./footerpages/Community').default;
} catch { Community = () => <ComingSoon page="Community" />; }

try {
  Integrations = require('./footerpages/Integrations').default;
} catch { Integrations = () => <ComingSoon page="Integrations" />; }

try {
  API = require('./footerpages/Api').default;
} catch { API = () => <ComingSoon page="API" />; }

// Coming Soon fallback component
const ComingSoon = ({ page }) => (
  <div style={{
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '40px 20px'
  }}>
    <div style={{
      background: 'white',
      borderRadius: '20px',
      padding: '48px',
      textAlign: 'center',
      maxWidth: '500px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
    }}>
      <div style={{ fontSize: '64px', marginBottom: '24px' }}>🚧</div>
      <h1 style={{
        fontSize: '32px',
        fontWeight: '800',
        color: '#1f2937',
        marginBottom: '16px'
      }}>
        {page}
      </h1>
      <p style={{
        color: '#6b7280',
        fontSize: '16px',
        marginBottom: '32px'
      }}>
        This page is coming soon. We're working hard to bring it to you!
      </p>
      <Link to="/" style={{
        display: 'inline-block',
        padding: '14px 32px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        color: 'white',
        textDecoration: 'none',
        borderRadius: '12px',
        fontSize: '16px',
        fontWeight: '700',
        boxShadow: '0 4px 14px rgba(102, 126, 234, 0.4)'
      }}>
        ← Back to Home
      </Link>
    </div>
  </div>
);

// Lazy load platform components
const RedditAUTO = lazy(() => 
  import('./pages/RedditAUTO').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Reddit Component Error</h2>
      <p>Please check if RedditAUTO.jsx exists.</p>
    </div>
  }))
);

const SocialMediaAutomation = lazy(() => 
  import('./pages/Fb').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Facebook Component Error</h2>
      <p>Please check if Fb.jsx exists.</p>
    </div>
  }))
);

const InstagramAutomation = lazy(() => 
  import('./pages/INSTA').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Instagram Component Error</h2>
      <p>Please check if INSTA.jsx exists.</p>
    </div>
  }))
);

const WhatsAppAutomation = lazy(() => 
  import('./pages/WhatsApp').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>WhatsApp Component Error</h2>
      <p>Please check if WhatsApp.jsx exists.</p>
    </div>
  }))
);

const YouTubeAutomation = lazy(() => 
  import('./pages/YouTube').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>YouTube Component Error</h2>
      <p>Please check if YouTube.jsx exists.</p>
    </div>
  }))
);

// YouTube Route Wrapper
const YouTubeRouteWrapper = () => {
  const location = useLocation();
  const urlParams = new URLSearchParams(location.search);
  const youtubeConnected = urlParams.get('youtube_connected');
  const channelName = urlParams.get('channel');
  const errorParam = urlParams.get('error');
  
  if (youtubeConnected === 'true') {
    return (
      <div className="oauth-success-container">
        <div className="oauth-success-card">
          <div className="success-icon">✅</div>
          <h1 className="success-title">YouTube Connected!</h1>
          <p className="success-channel">Channel: {decodeURIComponent(channelName || 'Unknown')}</p>
          <p className="success-message">You can now set up automation and upload videos.</p>
          <button 
            onClick={() => {
              window.history.replaceState({}, '', '/youtube');
              window.location.reload();
            }}
            className="success-button"
          >
            Continue to Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  if (errorParam) {
    return (
      <div className="oauth-error-container">
        <div className="oauth-error-card">
          <div className="error-icon">❌</div>
          <h1 className="error-title">Connection Failed</h1>
          <p className="error-message">Error: {decodeURIComponent(errorParam)}</p>
          <button 
            onClick={() => {
              window.history.replaceState({}, '', '/youtube');
              window.location.reload();
            }}
            className="error-button"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <ProtectedRoute>
      <Suspense fallback={<LoadingSpinner platform="YouTube" />}>
        <YouTubeAutomation />
      </Suspense>
    </ProtectedRoute>
  );
};

// Loading Spinner
const LoadingSpinner = ({ platform = '' }) => (
  <div className="loading-container">
    <div className="loading-content">
      <div className="spinner-wrapper">
        <div className="spinner"></div>
      </div>
      <div className="loading-text">Loading {platform}...</div>
    </div>
  </div>
);

// Error Boundary
class ErrorBoundary extends React.Component {
  constructor(props) { 
    super(props); 
    this.state = { hasError: false, error: null }; 
  }
  
  static getDerivedStateFromError(error) { 
    return { hasError: true }; 
  }
  
  componentDidCatch(error, errorInfo) { 
    console.error('Error:', error, errorInfo); 
    this.setState({ error }); 
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-card">
            <div className="error-emoji">⚠️</div>
            <h1>Oops! Something went wrong</h1>
            <p>{this.state.error?.message || 'An unexpected error occurred'}</p>
            <button onClick={() => window.location.reload()}>
              Reload Page
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Mobile Menu
const MobileMenu = ({ isOpen, onClose, isAuthenticated, user, logout }) => {
  const navigate = useNavigate();
  
  const handleNav = (path) => {
    navigate(path);
    onClose();
  };

  return (
    <>
      {isOpen && <div className="overlay" onClick={onClose}></div>}
      
      <div className={`mobile-menu ${isOpen ? 'open' : ''}`}>
        <div className="menu-header">
          <div className="menu-logo">
            <span className="logo-emoji">🚀</span>
            <span>Social AI</span>
          </div>
          <button className="close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="menu-content">
          {isAuthenticated && user && (
            <div className="user-card">
              <div className="avatar">👤</div>
              <div className="user-info">
                <div className="name">{user?.name || 'User'}</div>
                <div className="email">{user?.email}</div>
              </div>
            </div>
          )}

          <nav className="menu-nav">
            <button onClick={() => handleNav('/')} className="menu-item">
              <span>🏠</span>Home
            </button>
            
            {isAuthenticated && (
              <>
                <button onClick={() => handleNav('/reddit-auto')} className="menu-item">
                  <span>🔴</span>Reddit
                </button>
                <button onClick={() => handleNav('/facebook-instagram')} className="menu-item">
                  <span>📘</span>Facebook
                </button>
                <button onClick={() => handleNav('/instagram')} className="menu-item">
                  <span>📸</span>Instagram
                </button>
                <button onClick={() => handleNav('/whatsapp')} className="menu-item">
                  <span>💬</span>WhatsApp
                </button>
                <button onClick={() => handleNav('/youtube')} className="menu-item">
                  <span>📺</span>YouTube
                </button>
              </>
            )}
          </nav>

          {isAuthenticated && (
            <button onClick={() => { logout(); onClose(); }} className="logout">
              <span>🚪</span>Logout
            </button>
          )}
        </div>
      </div>
    </>
  );
};

// Navbar
const ConditionalNavbar = () => {
  const location = useLocation();
  const { isAuthenticated, user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  
  const hideNavbarPaths = ['/', '/login', '/register'];
  if (hideNavbarPaths.includes(location.pathname)) return null;

  return (
    <>
      <nav className="navbar">
        <div className="nav-container">
          <button className="hamburger" onClick={() => setMenuOpen(true)}>
            <span></span>
            <span></span>
            <span></span>
          </button>

          <Link to="/" className="brand">
            <span className="brand-icon">🚀</span>
            <span className="brand-text">Social AI</span>
          </Link>
          
          <div className="nav-links">
            <Link to="/" className="link">
              <span>🏠</span><span className="text">Home</span>
            </Link>
            
            {isAuthenticated && (
              <>
                <Link to="/reddit-auto" className="link">
                  <span>🔴</span><span className="text">Reddit</span>
                </Link>
                <Link to="/facebook-instagram" className="link">
                  <span>📘</span><span className="text">Facebook</span>
                </Link>
                <Link to="/instagram" className="link">
                  <span>📸</span><span className="text">Instagram</span>
                </Link>
                <Link to="/whatsapp" className="link">
                  <span>💬</span><span className="text">WhatsApp</span>
                </Link>
                <Link to="/youtube" className="link">
                  <span>📺</span><span className="text">YouTube</span>
                </Link>
                
                <div className="user-box">
                  <span className="welcome">Hi, {user?.name || user?.email?.split('@')[0]}</span>
                  <button onClick={logout} className="btn-logout">Exit</button>
                </div>
              </>
            )}
          </div>
        </div>
      </nav>
      
      <MobileMenu 
        isOpen={menuOpen} 
        onClose={() => setMenuOpen(false)}
        isAuthenticated={isAuthenticated}
        user={user}
        logout={logout}
      />
    </>
  );
};

// Main App
function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <ConditionalNavbar />
          <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Landing_Page />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Footer Pages - Now using ACTUAL file names */}
            <Route path="/privacy" element={<PrivacyPolicy />} />
            <Route path="/terms" element={<TermsOfService />} />
            <Route path="/cookie-policy" element={<CookiePolicy />} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/about" element={<About />} />
            <Route path="/features" element={<Features />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/help" element={<HelpCenter />} />
            <Route path="/documentation" element={<Documentation />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/careers" element={<Careers />} />
            <Route path="/status" element={<Status />} />
            <Route path="/community" element={<Community />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/api" element={<API />} />

            {/* Protected Platform Routes */}
            <Route path="/reddit-auto" element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner platform="Reddit" />}>
                  <RedditAUTO />
                </Suspense>
              </ProtectedRoute>
            } />
            
            <Route path="/facebook-instagram" element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner platform="Facebook" />}>
                  <SocialMediaAutomation />
                </Suspense>
              </ProtectedRoute>
            } />
            
            <Route path="/instagram" element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner platform="Instagram" />}>
                  <InstagramAutomation />
                </Suspense>
              </ProtectedRoute>
            } />
            
            <Route path="/whatsapp" element={
              <ProtectedRoute>
                <Suspense fallback={<LoadingSpinner platform="WhatsApp" />}>
                  <WhatsAppAutomation />
                </Suspense>
              </ProtectedRoute>
            } />
            
            <Route path="/youtube" element={<YouTubeRouteWrapper />} />

            {/* 404 Not Found */}
            <Route path="*" element={
              <div className="not-found">
                <h1>404</h1>
                <h2>Page Not Found</h2>
                <p>The page you're looking for doesn't exist.</p>
                <Link to="/" className="home-link">Go Home</Link>
              </div>
            } />
          </Routes>
        </AuthProvider>
      </Router>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', sans-serif;
          -webkit-font-smoothing: antialiased;
          -moz-osx-font-smoothing: grayscale;
          background: #f8f9fa;
          overflow-x: hidden;
        }

        .navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: rgba(255, 255, 255, 0.98);
          backdrop-filter: blur(12px);
          border-bottom: 2px solid #f0f0f0;
          z-index: 999;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        }

        .nav-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 68px;
          gap: 16px;
        }

        .hamburger {
          display: none;
          flex-direction: column;
          justify-content: space-between;
          width: 28px;
          height: 22px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 0;
          z-index: 1001;
        }

        .hamburger span {
          display: block;
          width: 100%;
          height: 3px;
          background: #333;
          border-radius: 2px;
          transition: 0.3s;
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
          color: #1a1a1a;
          font-weight: 800;
          font-size: 22px;
          letter-spacing: -0.5px;
        }

        .brand-icon {
          font-size: 28px;
          line-height: 1;
        }

        .brand-text {
          display: none;
        }

        .nav-links {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .link {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          text-decoration: none;
          color: #374151;
          font-weight: 600;
          font-size: 15px;
          border-radius: 10px;
          transition: 0.2s;
        }

        .link:hover {
          background: #f3f4f6;
          color: #667eea;
        }

        .link span:first-child {
          font-size: 18px;
          line-height: 1;
        }

        .link .text {
          display: none;
        }

        .user-box {
          display: flex;
          align-items: center;
          gap: 12px;
          padding-left: 16px;
          border-left: 2px solid #e5e7eb;
          margin-left: 8px;
        }

        .welcome {
          color: #6b7280;
          font-size: 14px;
          font-weight: 600;
          max-width: 120px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .btn-logout {
          padding: 8px 18px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 700;
          font-size: 13px;
          cursor: pointer;
          transition: 0.3s;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        }

        .btn-logout:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(4px);
          z-index: 998;
          animation: fadeIn 0.3s;
        }

        .mobile-menu {
          position: fixed;
          top: 0;
          right: -100%;
          width: 85%;
          max-width: 340px;
          height: 100vh;
          background: white;
          box-shadow: -4px 0 24px rgba(0, 0, 0, 0.15);
          z-index: 999;
          transition: right 0.3s ease;
          display: flex;
          flex-direction: column;
        }

        .mobile-menu.open {
          right: 0;
        }

        .menu-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 22px;
          border-bottom: 2px solid #f3f4f6;
          background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .menu-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          color: white;
          font-weight: 800;
          font-size: 20px;
        }

        .logo-emoji {
          font-size: 26px;
        }

        .close-btn {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 22px;
          font-weight: 700;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: 0.2s;
        }

        .close-btn:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        .menu-content {
          flex: 1;
          padding: 22px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }

        .user-card {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 16px;
          background: linear-gradient(135deg, #f0f4ff, #e8f0ff);
          border-radius: 14px;
          margin-bottom: 24px;
          border: 2px solid #e0e7ff;
        }

        .avatar {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea, #764ba2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          flex-shrink: 0;
        }

        .user-info {
          flex: 1;
          min-width: 0;
        }

        .name {
          font-weight: 700;
          font-size: 16px;
          color: #1a1a1a;
          margin-bottom: 4px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .email {
          font-size: 13px;
          color: #6b7280;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .menu-nav {
          display: flex;
          flex-direction: column;
          gap: 6px;
          margin-bottom: 24px;
        }

        .menu-item {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 14px 16px;
          background: transparent;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 600;
          color: #374151;
          cursor: pointer;
          transition: 0.2s;
          text-align: left;
        }

        .menu-item:hover {
          background: #f3f4f6;
          color: #667eea;
        }

        .menu-item span:first-child {
          font-size: 20px;
          width: 24px;
          text-align: center;
        }

        .logout {
          margin-top: auto;
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #ff4444, #cc0000);
          border: none;
          border-radius: 12px;
          color: white;
          font-weight: 700;
          font-size: 15px;
          cursor: pointer;
          transition: 0.3s;
          box-shadow: 0 3px 12px rgba(255, 68, 68, 0.3);
        }

        .logout:hover {
          transform: translateY(-2px);
          box-shadow: 0 5px 18px rgba(255, 68, 68, 0.4);
        }

        .logout span {
          font-size: 20px;
        }

        .loading-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .loading-content {
          text-align: center;
        }

        .spinner-wrapper {
          width: 60px;
          height: 60px;
          margin: 0 auto 22px;
        }

        .spinner {
          width: 100%;
          height: 100%;
          border: 4px solid rgba(255, 255, 255, 0.25);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        .loading-text {
          color: white;
          font-size: 17px;
          font-weight: 600;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .oauth-success-container,
        .oauth-error-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 24px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .oauth-success-card,
        .oauth-error-card {
          background: white;
          border-radius: 20px;
          padding: 48px 40px;
          max-width: 480px;
          width: 100%;
          text-align: center;
          box-shadow: 0 12px 48px rgba(0, 0, 0, 0.2);
        }

        .success-icon,
        .error-icon {
          font-size: 68px;
          margin-bottom: 22px;
        }

        .success-title,
        .error-title {
          font-size: 28px;
          font-weight: 800;
          color: #1a1a1a;
          margin-bottom: 14px;
        }

        .success-channel {
          display: inline-block;
          background: rgba(102, 126, 234, 0.12);
          color: #667eea;
          padding: 10px 20px;
          border-radius: 10px;
          font-weight: 700;
          font-size: 15px;
          margin-bottom: 18px;
        }

        .success-message,
        .error-message {
          color: #666;
          font-size: 15px;
          line-height: 1.6;
          margin-bottom: 28px;
        }

        .success-button,
        .error-button {
          padding: 14px 32px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          transition: 0.3s;
          box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
        }

        .success-button:hover,
        .error-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 22px rgba(102, 126, 234, 0.45);
        }

        .not-found {
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 24px;
          text-align: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
        }

        .not-found h1 {
          font-size: 96px;
          font-weight: 900;
          margin-bottom: 16px;
          line-height: 1;
        }

        .not-found h2 {
          font-size: 32px;
          font-weight: 800;
          margin-bottom: 14px;
        }

        .not-found p {
          font-size: 17px;
          margin-bottom: 32px;
          opacity: 0.92;
        }

        .home-link {
          padding: 14px 32px;
          background: white;
          color: #667eea;
          text-decoration: none;
          border-radius: 12px;
          font-weight: 700;
          font-size: 16px;
          transition: 0.3s;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        }

        .home-link:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 22px rgba(0, 0, 0, 0.25);
        }

        .error-boundary {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          padding: 24px;
          background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
        }

        .error-card {
          background: white;
          border-radius: 20px;
          padding: 48px 40px;
          max-width: 500px;
          width: 100%;
          text-align: center;
          box-shadow: 0 12px 48px rgba(0, 0, 0, 0.3);
        }

        .error-emoji {
          font-size: 72px;
          margin-bottom: 22px;
        }

        .error-card h1 {
          font-size: 28px;
          color: #1a1a1a;
          margin-bottom: 14px;
        }

        .error-card p {
          color: #666;
          font-size: 15px;
          margin-bottom: 28px;
          line-height: 1.6;
        }

        .error-card button {
          padding: 14px 32px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          transition: 0.3s;
          box-shadow: 0 4px 16px rgba(102, 126, 234, 0.35);
        }

        .error-card button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 22px rgba(102, 126, 234, 0.45);
        }

        @media (max-width: 480px) {
          .navbar { height: 56px; }
          .nav-container { padding: 0 14px; gap: 10px; }
          .hamburger { display: flex; }
          .brand { font-size: 16px; flex: 1; justify-content: center; }
          .brand-icon { font-size: 22px; }
          .brand-text { display: none; }
          .nav-links { display: none; }
          .mobile-menu { width: 90%; max-width: 280px; }
        }

        @media (min-width: 481px) and (max-width: 767px) {
          .hamburger { display: flex; }
          .brand-text { display: inline; }
          .nav-links { display: none; }
        }

        @media (min-width: 768px) and (max-width: 1024px) {
          .hamburger { display: flex; }
          .nav-links { display: none; }
        }

        @media (min-width: 1025px) {
          .brand-text { display: inline; }
          .link .text { display: inline; }
          .welcome { max-width: 180px; }
        }
      `}</style>
    </ErrorBoundary>
  );
}

export default App;