import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import Landing_Page from './Landing_Page';
import './App.css';
import PrivacyPolicy from './footerpages/Privacypolicy.jsx';
import TermsOfService from './footerpages/TermsOfService';
import CookiePolicy from './footerpages/CookiePolicy';
import Contact from './footerpages/Contact';
import About from './footerpages/About';

// Lazy load all platform components with error handling
const RedditAUTO = lazy(() => 
  import('./pages/RedditAUTO').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Reddit Component Error</h2>
      <p>Please check if RedditAUTO.jsx exists and has a default export.</p>
    </div>
  }))
);

const SocialMediaAutomation = lazy(() => 
  import('./pages/Fb').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Facebook Component Error</h2>
      <p>Please check if Fb.jsx exists and has a default export.</p>
    </div>
  }))
);

const InstagramAutomation = lazy(() => 
  import('./pages/INSTA').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>Instagram Component Error</h2>
      <p>Please check if INSTA.jsx exists and has a default export.</p>
    </div>
  }))
);

const WhatsAppAutomation = lazy(() => 
  import('./pages/WhatsApp').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>WhatsApp Component Error</h2>
      <p>Please check if WhatsApp.jsx exists and has a default export.</p>
    </div>
  }))
);

const YouTubeAutomation = lazy(() => 
  import('./pages/YouTube').catch(() => ({
    default: () => <div style={{ padding: '40px', textAlign: 'center', color: '#ff4444' }}>
      <h2>YouTube Component Error</h2>
      <p>Please check if YouTube.jsx exists and has a default export.</p>
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
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="app">
            <ConditionalNavbar />
            <main>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/" element={<Landing_Page />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />



                  // In Routes:
<Route path="/privacy" element={<PrivacyPolicy />} />
<Route path="/terms" element={<TermsOfService />} />
<Route path="/cookie-policy" element={<CookiePolicy />} />
<Route path="/contact" element={<Contact />} />
<Route path="/about" element={<About />} />
                  
                  <Route 
                    path="/reddit-auto" 
                    element={<ProtectedRoute><RedditAUTO /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/facebook-instagram" 
                    element={<ProtectedRoute><SocialMediaAutomation /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/instagram" 
                    element={<ProtectedRoute><InstagramAutomation /></ProtectedRoute>} 
                  />
                  <Route 
                    path="/whatsapp" 
                    element={<ProtectedRoute><WhatsAppAutomation /></ProtectedRoute>} 
                  />
                  <Route path="/youtube" element={<YouTubeRouteWrapper />} />
                  
                  <Route 
                    path="*" 
                    element={
                      <div className="not-found">
                        <h1>404</h1>
                        <h2>Page Not Found</h2>
                        <p>The page you're looking for doesn't exist.</p>
                        <Link to="/">Go Home</Link>
                      </div>
                    } 
                  />
                </Routes>
              </Suspense>
            </main>
          </div>
        </Router>
      </AuthProvider>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          -webkit-tap-highlight-color: transparent;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          -webkit-font-smoothing: antialiased;
          overflow-x: hidden;
        }

        .app {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Navbar */
        .navbar {
          background: rgba(255, 255, 255, 0.98);
          backdrop-filter: blur(20px);
          box-shadow: 0 2px 12px rgba(0,0,0,0.1);
          position: sticky;
          top: 0;
          z-index: 100;
          height: 60px;
        }

        .nav-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 16px;
          height: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .hamburger {
          display: none;
          flex-direction: column;
          gap: 4px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
        }

        .hamburger span {
          width: 22px;
          height: 2.5px;
          background: #667eea;
          border-radius: 2px;
          transition: 0.3s;
        }

        .hamburger:active {
          background: rgba(102, 126, 234, 0.1);
        }

        .brand {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          font-weight: 800;
          font-size: 18px;
          color: #1f2937;
        }

        .brand-icon {
          font-size: 24px;
        }

        .brand-text {
          white-space: nowrap;
        }

        .nav-links {
          display: flex;
          align-items: center;
          gap: 6px;
          margin-left: auto;
        }

        .link {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          text-decoration: none;
          color: #374151;
          font-weight: 600;
          font-size: 14px;
          border-radius: 8px;
          transition: 0.2s;
          white-space: nowrap;
        }

        .link:hover {
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
        }

        .link span:first-child {
          font-size: 16px;
        }

        .user-box {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 14px;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 20px;
          margin-left: 8px;
        }

        .welcome {
          font-size: 13px;
          color: #667eea;
          font-weight: 700;
          max-width: 120px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .btn-logout {
          padding: 6px 12px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
          white-space: nowrap;
        }

        .btn-logout:active {
          transform: scale(0.95);
        }

        /* Mobile Menu Overlay */
        .overlay {
          position: fixed;
          inset: 0;
          background: rgba(0,0,0,0.5);
          backdrop-filter: blur(4px);
          z-index: 998;
          animation: fadeIn 0.3s;
        }

        /* Mobile Menu */
        .mobile-menu {
          position: fixed;
          top: 0;
          left: -100%;
          width: 85%;
          max-width: 300px;
          height: 100vh;
          background: white;
          z-index: 999;
          display: flex;
          flex-direction: column;
          box-shadow: 4px 0 24px rgba(0,0,0,0.2);
          transition: left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          overflow-y: auto;
        }

        .mobile-menu.open {
          left: 0;
        }

        .menu-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 18px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          min-height: 70px;
        }

        .menu-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: 800;
          font-size: 18px;
        }

        .logo-emoji {
          font-size: 26px;
        }

        .close-btn {
          width: 38px;
          height: 38px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255,255,255,0.2);
          border: none;
          border-radius: 8px;
          color: white;
          font-size: 22px;
          cursor: pointer;
          font-weight: 300;
        }

        .close-btn:active {
          background: rgba(255,255,255,0.3);
          transform: scale(0.95);
        }

        .menu-content {
          flex: 1;
          padding: 18px;
          display: flex;
          flex-direction: column;
        }

        .user-card {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 16px;
          background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
          border-radius: 14px;
          margin-bottom: 20px;
          border: 2px solid rgba(102,126,234,0.2);
        }

        .avatar {
          width: 46px;
          height: 46px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea, #764ba2);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          flex-shrink: 0;
        }

        .user-info {
          flex: 1;
          min-width: 0;
        }

        .name {
          font-weight: 700;
          font-size: 15px;
          color: #1f2937;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .email {
          font-size: 12px;
          color: #6b7280;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-top: 2px;
        }

        .menu-nav {
          display: flex;
          flex-direction: column;
          gap: 8px;
          flex: 1;
        }

        .menu-item {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 15px 18px;
          background: white;
          border: 2px solid #f3f4f6;
          border-radius: 12px;
          font-size: 15px;
          font-weight: 600;
          color: #374151;
          cursor: pointer;
          transition: 0.2s;
        }

        .menu-item:active {
          background: rgba(102,126,234,0.1);
          border-color: rgba(102,126,234,0.3);
          transform: scale(0.98);
        }

        .menu-item span {
          font-size: 22px;
          width: 28px;
        }

        .logout {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 15px;
          background: linear-gradient(135deg, #ef4444, #dc2626);
          color: white;
          border: none;
          border-radius: 12px;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
          margin-top: auto;
        }

        .logout:active {
          transform: scale(0.98);
        }

        .logout span {
          font-size: 18px;
        }

        /* Loading */
        .loading-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .loading-content {
          text-align: center;
          color: white;
          padding: 20px;
        }

        .spinner-wrapper {
          width: 60px;
          height: 60px;
          margin: 0 auto 20px;
          position: relative;
        }

        .spinner {
          width: 100%;
          height: 100%;
          border: 4px solid rgba(255,255,255,0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        .loading-text {
          font-size: 16px;
          font-weight: 600;
        }

        /* OAuth Pages */
        .oauth-success-container,
        .oauth-error-container {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea, #764ba2);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .oauth-success-card,
        .oauth-error-card {
          background: white;
          border-radius: 20px;
          padding: 40px 28px;
          max-width: 480px;
          width: 100%;
          box-shadow: 0 12px 40px rgba(0,0,0,0.2);
          text-align: center;
          animation: slideUp 0.5s;
        }

        .success-icon,
        .error-icon {
          font-size: 64px;
          margin-bottom: 20px;
        }

        .success-title,
        .error-title {
          font-size: 24px;
          font-weight: 800;
          margin-bottom: 14px;
          color: #1f2937;
        }

        .success-channel {
          font-size: 16px;
          color: #667eea;
          font-weight: 700;
          margin-bottom: 14px;
          padding: 10px 18px;
          background: rgba(102,126,234,0.1);
          border-radius: 10px;
          border: 2px solid rgba(102,126,234,0.2);
        }

        .success-message,
        .error-message {
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 28px;
          line-height: 1.5;
        }

        .success-button,
        .error-button {
          width: 100%;
          padding: 14px 28px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
          box-shadow: 0 4px 14px rgba(102,126,234,0.3);
        }

        .success-button:active,
        .error-button:active {
          transform: scale(0.98);
        }

        /* Error Boundary */
        .error-boundary {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea, #764ba2);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .error-card {
          background: white;
          border-radius: 20px;
          padding: 40px 28px;
          max-width: 480px;
          width: 100%;
          text-align: center;
        }

        .error-emoji {
          font-size: 64px;
          margin-bottom: 20px;
        }

        .error-card h1 {
          font-size: 24px;
          font-weight: 800;
          color: #1f2937;
          margin-bottom: 14px;
        }

        .error-card p {
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 28px;
        }

        .error-card button {
          width: 100%;
          padding: 14px 28px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border: none;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 700;
          cursor: pointer;
        }

        /* 404 Page */
        .not-found {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea, #764ba2);
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: white;
          text-align: center;
          padding: 20px;
        }

        .not-found h1 {
          font-size: 100px;
          font-weight: 900;
          margin-bottom: 16px;
          line-height: 1;
        }

        .not-found h2 {
          font-size: 28px;
          font-weight: 800;
          margin-bottom: 12px;
        }

        .not-found p {
          font-size: 16px;
          margin-bottom: 28px;
          opacity: 0.9;
        }

        .not-found a {
          display: inline-block;
          padding: 14px 36px;
          background: white;
          color: #667eea;
          text-decoration: none;
          border-radius: 10px;
          font-size: 15px;
          font-weight: 700;
          box-shadow: 0 4px 14px rgba(0,0,0,0.2);
        }

        .not-found a:active {
          transform: scale(0.98);
        }

        /* Animations */
        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        /* Mobile Responsive (320px - 480px) */
        @media (max-width: 480px) {
          .navbar {
            height: 56px;
          }

          .nav-container {
            padding: 0 14px;
            gap: 10px;
          }

          .hamburger {
            display: flex;
          }

          .brand {
            font-size: 16px;
            flex: 1;
            justify-content: center;
          }

          .brand-icon {
            font-size: 22px;
          }

          .brand-text {
            display: none;
          }

          .nav-links {
            display: none;
          }

          .mobile-menu {
            width: 90%;
            max-width: 280px;
          }

          .menu-header {
            padding: 16px;
            min-height: 66px;
          }

          .menu-logo {
            font-size: 17px;
            gap: 9px;
          }

          .logo-emoji {
            font-size: 24px;
          }

          .close-btn {
            width: 36px;
            height: 36px;
            font-size: 20px;
          }

          .menu-content {
            padding: 16px;
          }

          .user-card {
            padding: 14px;
            gap: 12px;
          }

          .avatar {
            width: 42px;
            height: 42px;
            font-size: 20px;
          }

          .name {
            font-size: 14px;
          }

          .email {
            font-size: 11px;
          }

          .menu-item {
            padding: 13px 16px;
            font-size: 14px;
          }

          .menu-item span {
            font-size: 20px;
            width: 26px;
          }

          .logout {
            padding: 13px;
            font-size: 14px;
          }

          .oauth-success-card,
          .oauth-error-card {
            padding: 32px 22px;
          }

          .success-icon,
          .error-icon {
            font-size: 56px;
          }

          .success-title,
          .error-title {
            font-size: 20px;
          }

          .success-channel {
            font-size: 14px;
            padding: 9px 16px;
          }

          .success-message,
          .error-message {
            font-size: 13px;
          }

          .not-found h1 {
            font-size: 72px;
          }

          .not-found h2 {
            font-size: 24px;
          }

          .not-found p {
            font-size: 14px;
          }

          .spinner-wrapper {
            width: 52px;
            height: 52px;
          }

          .loading-text {
            font-size: 15px;
          }
        }

        /* Small Mobile (320px - 375px) */
        @media (max-width: 375px) {
          .mobile-menu {
            width: 92%;
            max-width: 260px;
          }

          .menu-logo {
            font-size: 16px;
          }

          .user-card {
            padding: 12px;
          }

          .menu-item {
            padding: 12px 14px;
            font-size: 13px;
          }
        }

        /* Small Tablets (481px - 767px) */
        @media (min-width: 481px) and (max-width: 767px) {
          .hamburger {
            display: flex;
          }

          .brand-text {
            display: inline;
          }

          .nav-links {
            display: none;
          }
        }

        /* Tablets (768px - 1024px) */
        @media (min-width: 768px) and (max-width: 1024px) {
          .hamburger {
            display: flex;
          }

          .nav-links {
            display: none;
          }

          .mobile-menu {
            max-width: 320px;
          }
        }

        /* Desktop (1025px+) */
        @media (min-width: 1025px) {
          .brand-text {
            display: inline;
          }

          .link .text {
            display: inline;
          }

          .welcome {
            max-width: 180px;
          }
        }

        /* Large Desktop (1400px+) */
        @media (min-width: 1400px) {
          .nav-container {
            padding: 0 32px;
          }

          .brand {
            font-size: 20px;
          }

          .link {
            font-size: 15px;
            padding: 9px 16px;
          }

          .welcome {
            max-width: 200px;
            font-size: 14px;
          }
        }

        /* Landscape Mobile */
        @media (max-height: 500px) and (orientation: landscape) {
          .menu-header {
            min-height: 56px;
            padding: 12px 16px;
          }

          .user-card {
            padding: 10px;
          }

          .menu-item {
            padding: 10px 14px;
          }

          .logout {
            padding: 10px;
          }
        }

        /* Safe Areas for Notched Devices */
        @supports (padding: max(0px)) {
          .navbar {
            padding-left: max(0px, env(safe-area-inset-left));
            padding-right: max(0px, env(safe-area-inset-right));
          }

          .mobile-menu {
            padding-top: max(0px, env(safe-area-inset-top));
            padding-bottom: max(0px, env(safe-area-inset-bottom));
          }
        }

        /* Focus Styles */
        .link:focus-visible,
        .menu-item:focus-visible,
        .btn-logout:focus-visible,
        .logout:focus-visible {
          outline: 3px solid #667eea;
          outline-offset: 2px;
        }

        /* Reduced Motion */
        @media (prefers-reduced-motion: reduce) {
          * {
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
          }
        }

        /* Print */
        @media print {
          .navbar,
          .mobile-menu,
          .hamburger {
            display: none !important;
          }
        }
      `}</style>
    </ErrorBoundary>
  );
}

export default App;