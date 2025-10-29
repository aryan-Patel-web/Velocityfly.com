import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import Landing_Page from './Landing_Page';
import './App.css';

// Lazy load platform components
const RedditAUTO = lazy(() => import('./pages/RedditAUTO'));
const SocialMediaAutomation = lazy(() => import('./pages/Fb'));
const InstagramAutomation = lazy(() => import('./pages/INSTA'));
const WhatsAppAutomation = lazy(() => import('./pages/WhatsApp'));
const YouTubeAutomation = lazy(() => import('./pages/YouTube'));

// Loading Spinner
const LoadingSpinner = ({ platform = '' }) => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)'
  }}>
    <div style={{ textAlign: 'center' }}>
      <div style={{
        width: '60px',
        height: '60px',
        margin: '0 auto 24px',
        border: '4px solid rgba(255, 255, 255, 0.3)',
        borderTopColor: 'white',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite'
      }}></div>
      <div style={{
        color: 'white',
        fontSize: '18px',
        fontWeight: '600'
      }}>
        Loading {platform}...
      </div>
    </div>
  </div>
);

// YouTube OAuth Callback Handler Component
const YouTubeOAuthHandler = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [message, setMessage] = React.useState('Processing...');
  const [isSuccess, setIsSuccess] = React.useState(false);

  useEffect(() => {
    console.log('YouTubeOAuthHandler loaded');
    console.log('URL:', window.location.href);
    console.log('Search params:', location.search);
    
    const params = new URLSearchParams(location.search);
    const youtubeConnected = params.get('youtube_connected');
    const channelName = params.get('channel');
    const error = params.get('error');

    console.log('youtube_connected:', youtubeConnected);
    console.log('channel:', channelName);
    console.log('error:', error);

    if (youtubeConnected === 'true') {
      const decodedChannel = decodeURIComponent(channelName || 'Unknown');
      setIsSuccess(true);
      setMessage(`YouTube Connected! Channel: ${decodedChannel}`);
      console.log('Success! Redirecting to /youtube in 2 seconds');
      
      setTimeout(() => {
        navigate('/youtube', { replace: true });
      }, 2000);
    } else if (error) {
      setIsSuccess(false);
      setMessage(`Connection Failed: ${error}`);
      console.log('Error! Redirecting to /youtube in 3 seconds');
      
      setTimeout(() => {
        navigate('/youtube', { replace: true });
      }, 3000);
    } else {
      console.log('No params, redirecting immediately');
      navigate('/youtube', { replace: true });
    }
  }, [location, navigate]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%)',
      padding: '24px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: '20px',
        padding: '48px',
        maxWidth: '500px',
        width: '100%',
        textAlign: 'center',
        boxShadow: '0 12px 48px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{
          fontSize: '64px',
          marginBottom: '24px'
        }}>
          {isSuccess ? '✅' : message.includes('Failed') ? '❌' : '🔄'}
        </div>
        <h1 style={{
          fontSize: '28px',
          fontWeight: '800',
          color: '#1a1a1a',
          marginBottom: '16px'
        }}>
          {isSuccess ? 'YouTube Connected!' : 
           message.includes('Failed') ? 'Connection Failed' : 'Processing...'}
        </h1>
        <p style={{
          color: '#666',
          fontSize: '16px',
          marginBottom: '24px',
          lineHeight: '1.6'
        }}>
          {message}
        </p>
        <div style={{
          marginTop: '32px'
        }}>
          <Link
            to="/youtube"
            style={{
              display: 'inline-block',
              padding: '14px 32px',
              background: 'linear-gradient(135deg, #0ea5e9, #06b6d4)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              boxShadow: '0 4px 16px rgba(14, 165, 233, 0.35)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 6px 20px rgba(14, 165, 233, 0.45)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 16px rgba(14, 165, 233, 0.35)';
            }}
          >
            Go to YouTube Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
};

// Dashboard Navigation
const DashboardNavbar = () => {
  const { logout } = useAuth();
  const location = useLocation();

  const platformLinks = [
    { path: '/reddit-auto', label: 'Reddit', emoji: '🔴' },
    { path: '/facebook-instagram', label: 'Facebook', emoji: '📘' },
    { path: '/instagram', label: 'Instagram', emoji: '📸' },
    { path: '/whatsapp', label: 'WhatsApp', emoji: '💬' },
    { path: '/youtube', label: 'YouTube', emoji: '📺' }
  ];

  return (
    <nav className="dashboard-navbar">
      <div className="dashboard-nav-content">
        <Link to="/" className="dashboard-logo">
          <span className="logo-emoji">🚀</span>
          <span className="logo-text">VelocityPost</span>
        </Link>

        <div className="dashboard-nav-links">
          {platformLinks.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`dashboard-nav-link ${location.pathname === link.path ? 'active' : ''}`}
            >
              <span className="link-emoji">{link.emoji}</span>
              <span className="link-text">{link.label}</span>
            </Link>
          ))}
          
          <button onClick={logout} className="dashboard-logout-btn">
            <span className="logout-emoji">🚪</span>
            <span className="logout-text">Logout</span>
          </button>
        </div>
      </div>

      <style>{`
        .dashboard-navbar {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 2px solid #e5e7eb;
          z-index: 1000;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        .dashboard-nav-content {
          max-width: 100%;
          margin: 0 auto;
          padding: 12px 16px;
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .dashboard-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: #111827;
          font-weight: 800;
          font-size: 18px;
          flex-shrink: 0;
        }

        .logo-emoji {
          font-size: 24px;
        }

        .logo-text {
          font-size: 18px;
        }

        .dashboard-nav-links {
          display: flex;
          align-items: center;
          gap: 8px;
          overflow-x: auto;
          overflow-y: hidden;
          flex: 1;
          padding: 4px 0;
          -webkit-overflow-scrolling: touch;
          scrollbar-width: none;
        }

        .dashboard-nav-links::-webkit-scrollbar {
          display: none;
        }

        .dashboard-nav-link {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          border-radius: 8px;
          text-decoration: none;
          color: #6b7280;
          font-weight: 600;
          font-size: 14px;
          background: transparent;
          transition: all 0.2s;
          white-space: nowrap;
          flex-shrink: 0;
        }

        .dashboard-nav-link:hover {
          background: #f0f9ff;
          color: #0ea5e9;
        }

        .dashboard-nav-link.active {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
        }

        .link-emoji {
          font-size: 18px;
        }

        .link-text {
          font-size: 13px;
        }

        .dashboard-logout-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          border-radius: 8px;
          border: none;
          background: #fee2e2;
          color: #dc2626;
          font-weight: 600;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
          flex-shrink: 0;
        }

        .dashboard-logout-btn:hover {
          background: #fecaca;
          transform: translateY(-2px);
        }

        .logout-emoji {
          font-size: 18px;
        }

        .logout-text {
          font-size: 13px;
        }

        @media (max-width: 768px) {
          .dashboard-nav-content {
            padding: 10px 12px;
            gap: 12px;
          }

          .dashboard-logo {
            font-size: 16px;
          }

          .logo-emoji {
            font-size: 22px;
          }

          .logo-text {
            font-size: 16px;
          }

          .dashboard-nav-link {
            padding: 7px 12px;
            font-size: 12px;
            gap: 5px;
          }

          .link-emoji {
            font-size: 16px;
          }

          .link-text {
            font-size: 12px;
          }

          .dashboard-logout-btn {
            padding: 7px 12px;
            font-size: 12px;
            gap: 5px;
          }

          .logout-emoji {
            font-size: 16px;
          }

          .logout-text {
            font-size: 12px;
          }
        }

        @media (max-width: 480px) {
          .dashboard-nav-content {
            padding: 8px 10px;
            gap: 10px;
          }

          .dashboard-logo {
            font-size: 14px;
          }

          .logo-emoji {
            font-size: 20px;
          }

          .logo-text {
            font-size: 14px;
          }

          .dashboard-nav-links {
            gap: 6px;
          }

          .dashboard-nav-link {
            padding: 6px 10px;
            font-size: 11px;
            gap: 4px;
          }

          .link-emoji {
            font-size: 14px;
          }

          .link-text {
            font-size: 11px;
          }

          .dashboard-logout-btn {
            padding: 6px 10px;
            font-size: 11px;
            gap: 4px;
          }

          .logout-emoji {
            font-size: 14px;
          }

          .logout-text {
            font-size: 11px;
          }
        }
      `}</style>
    </nav>
  );
};

// Dashboard Layout Wrapper
const DashboardLayout = ({ children }) => {
  return (
    <>
      <DashboardNavbar />
      <div style={{ paddingTop: '70px' }}>
        {children}
      </div>
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* CRITICAL: YouTube OAuth callback MUST be BEFORE /* route */}
          <Route path="/youtube-callback" element={<YouTubeOAuthHandler />} />

          {/* Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Platform Routes (Protected) */}
          <Route 
            path="/reddit-auto" 
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Suspense fallback={<LoadingSpinner platform="Reddit" />}>
                    <RedditAUTO />
                  </Suspense>
                </DashboardLayout>
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/facebook-instagram" 
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Suspense fallback={<LoadingSpinner platform="Facebook" />}>
                    <SocialMediaAutomation />
                  </Suspense>
                </DashboardLayout>
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/instagram" 
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Suspense fallback={<LoadingSpinner platform="Instagram" />}>
                    <InstagramAutomation />
                  </Suspense>
                </DashboardLayout>
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/whatsapp" 
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Suspense fallback={<LoadingSpinner platform="WhatsApp" />}>
                    <WhatsAppAutomation />
                  </Suspense>
                </DashboardLayout>
              </ProtectedRoute>
            } 
          />
          
          <Route 
            path="/youtube" 
            element={
              <ProtectedRoute>
                <DashboardLayout>
                  <Suspense fallback={<LoadingSpinner platform="YouTube" />}>
                    <YouTubeAutomation />
                  </Suspense>
                </DashboardLayout>
              </ProtectedRoute>
            } 
          />

          {/* Landing Page - MUST be LAST (catch-all) */}
          <Route path="/*" element={<Landing_Page />} />
        </Routes>

        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }

          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
          }

          html {
            scroll-behavior: smooth;
          }
        `}</style>
      </Router>
    </AuthProvider>
  );
}

export default App;