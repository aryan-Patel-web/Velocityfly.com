import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import './App.css';

// Safer lazy loading with better error handling
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






// FIXED YouTube Route Wrapper - handles OAuth success/error and normal visits
// FIXED YouTube Route Wrapper - handles OAuth success/error and normal visits
const YouTubeRouteWrapper = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  
  // Parse URL parameters
  const urlParams = new URLSearchParams(location.search);
  const youtubeConnected = urlParams.get('youtube_connected');
  const channelName = urlParams.get('channel');
  const errorParam = urlParams.get('error');
  
  console.log('YouTube Route Wrapper:', {
    youtubeConnected,
    channelName,
    errorParam,
    search: location.search,
    isAuthenticated
  });
  
  // Show success page for OAuth callback
  if (youtubeConnected === 'true') {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        textAlign: 'center',
        padding: '20px'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '20px',
          padding: '40px',
          maxWidth: '500px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
          <h1 style={{ fontSize: '28px', marginBottom: '16px', fontWeight: '700' }}>YouTube Connected Successfully!</h1>
          <p style={{ fontSize: '18px', marginBottom: '20px', opacity: 0.9 }}>
            Channel: {decodeURIComponent(channelName || 'Unknown Channel')}
          </p>
          <p style={{ fontSize: '14px', opacity: 0.7, marginBottom: '30px' }}>
            You can now set up YouTube automation and upload videos.
          </p>
          <button 
            onClick={() => {
              window.history.replaceState({}, '', '/youtube');
              window.location.reload();
            }}
            style={{
              padding: '12px 24px',
              background: 'white',
              color: '#667eea',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            }}
          >
            Continue to YouTube Dashboard
          </button>
        </div>
      </div>
    );
  }
  
  // Show error page for OAuth failure
  if (errorParam) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        textAlign: 'center',
        padding: '20px'
      }}>
        <div style={{
          background: 'rgba(255, 0, 0, 0.1)',
          borderRadius: '20px',
          padding: '40px',
          maxWidth: '500px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>❌</div>
          <h1 style={{ fontSize: '28px', marginBottom: '16px', fontWeight: '700' }}>YouTube Connection Failed</h1>
          <p style={{ fontSize: '18px', marginBottom: '20px', opacity: 0.9 }}>
            Error: {decodeURIComponent(errorParam)}
          </p>
          <button 
            onClick={() => {
              window.history.replaceState({}, '', '/youtube');
              window.location.reload();
            }}
            style={{
              padding: '12px 24px',
              background: 'white',
              color: '#667eea',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)'
            }}
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // For normal visits, require authentication and show YouTube component
  return (
    <ProtectedRoute>
      <Suspense fallback={
        <div style={{ 
          minHeight: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '18px', fontWeight: '600' }}>Loading YouTube Dashboard...</div>
          </div>
        </div>
      }>
        <YouTubeAutomation />
      </Suspense>
    </ProtectedRoute>
  );
};










const LoadingSpinner = () => (
  <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
    <div style={{ textAlign: 'center', color: 'white' }}>
      <div style={{ width: '40px', height: '40px', border: '4px solid #f3f3f3', borderTop: '4px solid #667eea', borderRadius: '50%', margin: '0 auto 16px', animation: 'spin 1s linear infinite' }}></div>
      <div style={{ fontSize: '18px', fontWeight: '600' }}>Loading...</div>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
    </div>
  </div>
);



class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false, error: null }; }
  static getDerivedStateFromError(error) { return { hasError: true }; }
  componentDidCatch(error, errorInfo) { console.error('Error Boundary:', error, errorInfo); this.setState({ error }); }
  
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '20px' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', maxWidth: '500px', textAlign: 'center', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#dc2626', marginBottom: '16px' }}>Application Error</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>Something went wrong with the social media automation platform.</p>
            <details style={{ textAlign: 'left', marginBottom: '20px', background: '#f8f9fa', padding: '12px', borderRadius: '8px', fontSize: '12px' }}>
              <summary style={{ cursor: 'pointer', fontWeight: '600' }}>Error Details</summary>
              <pre style={{ marginTop: '8px', fontSize: '11px', overflow: 'auto', whiteSpace: 'pre-wrap' }}>
                {this.state.error ? this.state.error.toString() : 'Unknown error'}
              </pre>
            </details>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={() => this.setState({ hasError: false, error: null })} style={{ padding: '12px 24px', background: '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Try Again</button>
              <button onClick={() => window.location.reload()} style={{ padding: '12px 24px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Reload Page</button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav style={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '12px 0', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', position: 'sticky', top: 0, zIndex: 1000 }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 20px' }}>
        <Link to="/" style={{ fontSize: '24px', fontWeight: '700', color: '#667eea', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🚀</span>VelocityPost
        </Link>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
          <Link to="/" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px' }}>Home</Link>
          
          {isAuthenticated ? (
            <>
              <Link to="/reddit-auto" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>🔴</span>Reddit
              </Link>
              <Link to="/facebook-instagram" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📘</span>Facebook
              </Link>
              <Link to="/instagram" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📸</span>Instagram
              </Link>
              <Link to="/whatsapp" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>💬</span>WhatsApp
              </Link>
              <Link to="/youtube" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📺</span>YouTube
              </Link>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '20px', padding: '8px 16px', background: 'rgba(102, 126, 234, 0.1)', borderRadius: '20px' }}>
                <span style={{ fontSize: '14px', color: '#667eea', fontWeight: '600' }}>Welcome, {user?.name || user?.email}</span>
                <button onClick={logout} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}>Logout</button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px' }}>Login</Link>
              <Link to="/register" style={{ padding: '10px 20px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600', fontSize: '14px' }}>Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  const platforms = [
    { name: 'Facebook', emoji: '📘', color: '#4267B2', route: '/facebook-instagram', features: ['AI Content', 'Multi-Page', 'Smart Scheduling', 'Analytics'] },
    { name: 'Instagram', emoji: '📸', color: '#E4405F', route: '/instagram', features: ['AI Images', 'Smart Tags', 'Story Auto', 'Engagement'] },
    { name: 'WhatsApp', emoji: '💬', color: '#25D366', route: '/whatsapp', features: ['Auto Reply', 'Broadcast', 'Templates', 'Analytics'] },
    { name: 'YouTube', emoji: '📺', color: '#FF0000', route: '/youtube', features: ['AI Scripts', 'Auto Upload', 'SEO Tags', 'Shorts'] },
    { name: 'Reddit', emoji: '🔴', color: '#FF4500', route: '/reddit-auto', features: ['Auto Post', 'Smart Reply', 'Karma Build', 'Multi-Sub'] }
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div style={{ padding: '80px 20px', textAlign: 'center', color: 'white' }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '20px', textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)' }}>Complete Social Media Automation Suite</h1>
          <p style={{ fontSize: '20px', marginBottom: '40px', opacity: 0.9, lineHeight: 1.6 }}>AI-powered automation for Facebook, Instagram, WhatsApp, YouTube, and Reddit.</p>
          
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
            {isAuthenticated ? (
              <Link to="/facebook-instagram" style={{ padding: '16px 32px', background: 'white', color: '#667eea', textDecoration: 'none', borderRadius: '12px', fontWeight: '700', fontSize: '16px', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)' }}>Launch Dashboard</Link>
            ) : (
              <>
                <Link to="/register" style={{ padding: '16px 32px', background: 'white', color: '#667eea', textDecoration: 'none', borderRadius: '12px', fontWeight: '700', fontSize: '16px', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)' }}>Start Free Trial</Link>
                <Link to="/login" style={{ padding: '16px 32px', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(10px)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontWeight: '600', fontSize: '16px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>Sign In</Link>
              </>
            )}
          </div>
        </div>
      </div>

      <div style={{ padding: '60px 20px', background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: '36px', fontWeight: '700', color: 'white', marginBottom: '50px' }}>Automate All Your Social Platforms</h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '25px' }}>
            {platforms.map((platform, index) => (
              <div key={index} style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '30px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', border: `2px solid ${platform.color}` }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                  <span style={{ fontSize: '32px' }}>{platform.emoji}</span>
                  <h3 style={{ margin: 0, color: platform.color, fontSize: '24px', fontWeight: '700' }}>{platform.name} Automation</h3>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
                  {platform.features.map((feature, fIndex) => (
                    <div key={fIndex} style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                      <div style={{ fontSize: '14px', fontWeight: 'bold', color: platform.color }}>{feature}</div>
                    </div>
                  ))}
                </div>
                
                {isAuthenticated ? (
                  <Link to={platform.route} style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: platform.color, color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>Go to {platform.name} →</Link>
                ) : (
                  <Link to="/register" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: platform.color, color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>Get Started →</Link>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="App" style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Navbar />
            <main>
              <Suspense fallback={<LoadingSpinner />}>
                <Routes>
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/reddit-auto" element={<ProtectedRoute><RedditAUTO /></ProtectedRoute>} />
                  <Route path="/facebook-instagram" element={<ProtectedRoute><SocialMediaAutomation /></ProtectedRoute>} />
                  <Route path="/instagram" element={<ProtectedRoute><InstagramAutomation /></ProtectedRoute>} />
                  <Route path="/whatsapp" element={<ProtectedRoute><WhatsAppAutomation /></ProtectedRoute>} />
                  <Route path="/youtube" element={<YouTubeRouteWrapper />} />
                </Routes>
              </Suspense>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}




export default App;