import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const BACKEND_URL = 'https://velocityfly.onrender.com';

const Header = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [serverLoading, setServerLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [window.location.pathname]);

  // Wake up Render backend
  const wakeUpServer = async () => {
    setServerLoading(true);
    setServerStatus('loading');
    
    try {
      const response = await fetch(BACKEND_URL, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (response.ok) {
        setServerStatus('success');
        setTimeout(() => {
          setServerStatus('');
          setServerLoading(false);
        }, 2000);
      } else {
        throw new Error('Server response error');
      }
    } catch (error) {
      console.error('Server wake-up error:', error);
      setServerStatus('success');
      setTimeout(() => {
        setServerStatus('');
        setServerLoading(false);
      }, 2000);
    }
  };

  return (
    <>
      <header className={`modern-header ${scrolled ? 'scrolled' : ''}`}>
        <div className="header-container">
          {/* Logo */}
          <Link to="/" className="header-logo" onClick={() => setMobileMenuOpen(false)}>
            <span className="logo-icon">🚀</span>
            <span className="logo-text">VelocityPost</span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="desktop-nav">
            <Link to="/pricing" className="nav-item">
              Pricing
            </Link>

            <Link to="/how-to-connect" className="nav-item">
              How to Connect
            </Link>

            <Link to="/features-showcase" className="nav-item">
              Features
            </Link>

            {/* Server Start Button */}
            <button 
              onClick={wakeUpServer} 
              disabled={serverLoading}
              className="server-btn"
              title="Wake up backend server"
            >
              {serverLoading ? (
                <>
                  <span className="spinner-mini"></span>
                  <span className="btn-text">Starting</span>
                </>
              ) : serverStatus === 'success' ? (
                <>
                  <span className="success-icon">✓</span>
                  <span className="btn-text">Ready</span>
                </>
              ) : (
                <>
                  <span className="bolt-icon">⚡</span>
                  <span className="btn-text-desktop">Server Start</span>
                  <span className="btn-text-mobile">⚡</span>
                </>
              )}
            </button>

            {isAuthenticated ? (
              <Link to="/reddit-auto" className="cta-btn">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="nav-item-alt">
                  Sign In
                </Link>
                <Link to="/register" className="cta-btn">
                  Get Started
                </Link>
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button 
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            ) : (
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            )}
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className={`mobile-nav ${mobileMenuOpen ? 'open' : ''}`}>
          <Link to="/pricing" className="mobile-nav-item" onClick={() => setMobileMenuOpen(false)}>
            Pricing
          </Link>

          <Link to="/how-to-connect" className="mobile-nav-item" onClick={() => setMobileMenuOpen(false)}>
            How to Connect
          </Link>

          <Link to="/features-showcase" className="mobile-nav-item" onClick={() => setMobileMenuOpen(false)}>
            Features
          </Link>

          <button 
            onClick={() => {
              wakeUpServer();
              setMobileMenuOpen(false);
            }} 
            disabled={serverLoading}
            className="mobile-server-btn"
          >
            {serverLoading ? '⏳ Starting Server...' : serverStatus === 'success' ? '✓ Server Ready!' : '⚡ Start Server'}
          </button>

          {isAuthenticated ? (
            <Link to="/reddit-auto" className="mobile-cta-btn" onClick={() => setMobileMenuOpen(false)}>
              📊 Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" className="mobile-nav-item-alt" onClick={() => setMobileMenuOpen(false)}>
                Sign In
              </Link>
              <Link to="/register" className="mobile-cta-btn" onClick={() => setMobileMenuOpen(false)}>
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </header>

      <style>{`
        /* Header Styles */
        .modern-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(12px);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          padding: 12px 0;
          border-bottom: 1px solid transparent;
          animation: slideDown 0.5s ease-out;
        }

        .modern-header.scrolled {
          background: rgba(255, 255, 255, 0.98);
          box-shadow: 0 4px 24px rgba(14, 165, 233, 0.08);
          border-bottom-color: #e0f2fe;
          padding: 10px 0;
        }

        @keyframes slideDown {
          from {
            transform: translateY(-100%);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .header-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 24px;
        }

        /* Logo */
        .header-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: #111827;
          font-weight: 800;
          font-size: 20px;
          transition: transform 0.3s ease;
          flex-shrink: 0;
          z-index: 1001;
        }

        .header-logo:hover {
          transform: scale(1.05);
        }

        .logo-icon {
          font-size: 24px;
          animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-5px); }
        }

        /* Desktop Navigation */
        .desktop-nav {
          display: flex;
          align-items: center;
          gap: 6px;
          flex-wrap: nowrap;
        }

        .nav-item,
        .nav-item-alt {
          padding: 8px 14px;
          color: #64748b;
          text-decoration: none;
          font-size: 14px;
          font-weight: 600;
          border-radius: 8px;
          transition: all 0.2s ease;
          white-space: nowrap;
          position: relative;
          overflow: hidden;
        }

        .nav-item::before {
          content: '';
          position: absolute;
          bottom: 0;
          left: 50%;
          width: 0;
          height: 2px;
          background: linear-gradient(90deg, #0ea5e9, #06b6d4);
          transition: all 0.3s ease;
          transform: translateX(-50%);
        }

        .nav-item:hover::before {
          width: 80%;
        }

        .nav-item:hover,
        .nav-item-alt:hover {
          color: #0ea5e9;
          background: #f0f9ff;
        }

        /* Server Button */
        .server-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 16px;
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 700;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          white-space: nowrap;
          box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
          position: relative;
          overflow: hidden;
        }

        .server-btn::before {
          content: '';
          position: absolute;
          top: 50%;
          left: 50%;
          width: 0;
          height: 0;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.2);
          transform: translate(-50%, -50%);
          transition: width 0.6s ease, height 0.6s ease;
        }

        .server-btn:hover::before {
          width: 300px;
          height: 300px;
        }

        .server-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(16, 185, 129, 0.4);
        }

        .server-btn:disabled {
          opacity: 0.8;
          cursor: not-allowed;
        }

        .spinner-mini {
          width: 12px;
          height: 12px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .success-icon {
          font-size: 14px;
          animation: scaleIn 0.3s ease;
        }

        @keyframes scaleIn {
          from { transform: scale(0); }
          to { transform: scale(1); }
        }

        .bolt-icon {
          font-size: 16px;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }

        .btn-text-mobile {
          display: none;
        }

        /* CTA Button */
        .cta-btn {
          padding: 8px 20px;
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          color: white;
          text-decoration: none;
          font-weight: 700;
          font-size: 14px;
          border-radius: 8px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          white-space: nowrap;
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
          position: relative;
          overflow: hidden;
        }

        .cta-btn::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
          transition: left 0.5s ease;
        }

        .cta-btn:hover::before {
          left: 100%;
        }

        .cta-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
        }

        /* Mobile Menu Button */
        .mobile-menu-btn {
          display: none;
          background: none;
          border: none;
          color: #111827;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
          transition: all 0.2s ease;
          z-index: 1001;
        }

        .mobile-menu-btn:hover {
          background: #f0f9ff;
          color: #0ea5e9;
        }

        /* Mobile Navigation */
        .mobile-nav {
          display: none;
          position: fixed;
          top: 60px;
          left: 0;
          right: 0;
          background: white;
          padding: 20px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          transform: translateY(-100%);
          opacity: 0;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          max-height: calc(100vh - 60px);
          overflow-y: auto;
        }

        .mobile-nav.open {
          transform: translateY(0);
          opacity: 1;
        }

        .mobile-nav-item,
        .mobile-nav-item-alt {
          display: block;
          padding: 12px 16px;
          color: #64748b;
          text-decoration: none;
          font-size: 16px;
          font-weight: 600;
          border-radius: 8px;
          transition: all 0.2s ease;
          margin-bottom: 8px;
        }

        .mobile-nav-item:hover,
        .mobile-nav-item-alt:hover {
          color: #0ea5e9;
          background: #f0f9ff;
        }

        .mobile-server-btn {
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 700;
          font-size: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
          margin: 12px 0;
        }

        .mobile-server-btn:hover:not(:disabled) {
          transform: scale(1.02);
          box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
        }

        .mobile-cta-btn {
          display: block;
          width: 100%;
          padding: 14px;
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          color: white;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          border-radius: 8px;
          text-align: center;
          transition: all 0.3s ease;
          margin-top: 12px;
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }

        .mobile-cta-btn:hover {
          transform: scale(1.02);
          box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
        }

        /* Tablet Responsive (768px - 1024px) */
        @media (max-width: 1024px) {
          .header-container {
            padding: 0 20px;
          }

          .desktop-nav {
            gap: 4px;
          }

          .nav-item,
          .nav-item-alt {
            padding: 8px 12px;
            font-size: 13px;
          }

          .server-btn {
            padding: 8px 14px;
            font-size: 12px;
          }

          .cta-btn {
            padding: 8px 18px;
            font-size: 13px;
          }
        }

        /* Mobile Responsive (max-width: 768px) */
        @media (max-width: 768px) {
          .header-container {
            padding: 0 16px;
          }

          .header-logo {
            font-size: 18px;
          }

          .logo-icon {
            font-size: 22px;
          }

          .desktop-nav {
            display: none;
          }

          .mobile-menu-btn {
            display: block;
          }

          .mobile-nav {
            display: block;
          }
        }

        /* Small Mobile (max-width: 480px) */
        @media (max-width: 480px) {
          .header-container {
            padding: 0 12px;
            gap: 12px;
          }

          .header-logo {
            font-size: 16px;
          }

          .logo-icon {
            font-size: 20px;
          }

          .logo-text {
            font-size: 16px;
          }

          .mobile-nav {
            padding: 16px;
          }

          .mobile-nav-item,
          .mobile-nav-item-alt {
            font-size: 15px;
            padding: 10px 14px;
          }

          .mobile-server-btn,
          .mobile-cta-btn {
            font-size: 15px;
            padding: 12px;
          }
        }

        /* Extra Small Mobile (max-width: 360px) */
        @media (max-width: 360px) {
          .header-logo {
            font-size: 14px;
          }

          .logo-icon {
            font-size: 18px;
          }

          .logo-text {
            display: none;
          }
        }
      `}</style>
    </>
  );
};

export default Header;