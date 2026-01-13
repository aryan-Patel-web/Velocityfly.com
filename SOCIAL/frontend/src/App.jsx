import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import Home from './pages/Home';
import './App.css';

const RedditAUTO = lazy(() => import('./pages/RedditAUTO'));
const SocialMediaAutomation = lazy(() => import('./pages/Fb'));
const InstagramAutomation = lazy(() => import('./pages/INSTA'));
const WhatsAppAutomation = lazy(() => import('./pages/WhatsApp'));
const YouTubeAutomation = lazy(() => import('./pages/YouTube'));

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

const YouTubeOAuthHandler = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [message, setMessage] = React.useState('Processing...');
  const [isSuccess, setIsSuccess] = React.useState(false);

  React.useEffect(() => {
    const params = new URLSearchParams(location.search);
    const youtubeConnected = params.get('youtube_connected');
    const channelName = params.get('channel');
    const error = params.get('error');

    if (youtubeConnected === 'true') {
      const decodedChannel = decodeURIComponent(channelName || 'Unknown');
      setIsSuccess(true);
      setMessage(`YouTube Connected! Channel: ${decodedChannel}`);
      setTimeout(() => navigate('/youtube', { replace: true }), 2000);
    } else if (error) {
      setIsSuccess(false);
      setMessage(`Connection Failed: ${error}`);
      setTimeout(() => navigate('/youtube', { replace: true }), 3000);
    } else {
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
        <div style={{ fontSize: '64px', marginBottom: '24px' }}>
          {isSuccess ? '✅' : message.includes('Failed') ? '❌' : '🔄'}
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: '800', color: '#1a1a1a', marginBottom: '16px' }}>
          {isSuccess ? 'YouTube Connected!' : message.includes('Failed') ? 'Connection Failed' : 'Processing...'}
        </h1>
        <p style={{ color: '#666', fontSize: '16px', marginBottom: '24px', lineHeight: '1.6' }}>
          {message}
        </p>
      </div>
    </div>
  );
};

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
            <Link key={link.path} to={link.path} className={`dashboard-nav-link ${location.pathname === link.path ? 'active' : ''}`}>
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
    </nav>
  );
};

const DashboardLayout = ({ children }) => {
  return (
    <>
      <DashboardNavbar />
      <div style={{ paddingTop: '70px' }}>{children}</div>
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Routes>
          <Route path="/youtube-callback" element={<YouTubeOAuthHandler />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/reddit-auto" element={
            <ProtectedRoute>
              <DashboardLayout>
                <Suspense fallback={<LoadingSpinner platform="Reddit" />}>
                  <RedditAUTO />
                </Suspense>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/facebook-instagram" element={
            <ProtectedRoute>
              <DashboardLayout>
                <Suspense fallback={<LoadingSpinner platform="Facebook" />}>
                  <SocialMediaAutomation />
                </Suspense>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/instagram" element={
            <ProtectedRoute>
              <DashboardLayout>
                <Suspense fallback={<LoadingSpinner platform="Instagram" />}>
                  <InstagramAutomation />
                </Suspense>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/whatsapp" element={
            <ProtectedRoute>
              <DashboardLayout>
                <Suspense fallback={<LoadingSpinner platform="WhatsApp" />}>
                  <WhatsAppAutomation />
                </Suspense>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/youtube" element={
            <ProtectedRoute>
              <DashboardLayout>
                <Suspense fallback={<LoadingSpinner platform="YouTube" />}>
                  <YouTubeAutomation />
                </Suspense>
              </DashboardLayout>
            </ProtectedRoute>
          } />
          <Route path="/*" element={<Home />} />
        </Routes>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            overflow-x: hidden;
          }
          html { scroll-behavior: smooth; }
        `}</style>
      </Router>
    </AuthProvider>
  );
}

export default App;