import React from 'react';
import { Link } from 'react-router-dom';

// TEMPLATE INSTRUCTIONS:
// 1. Copy this entire file
// 2. Rename the component (e.g., const About = () => {)
// 3. Update the page title and description in the banner
// 4. Add your specific content in the main section
// 5. Update the active nav link to match current page
// 6. Update the export at the bottom

const PAGENAME = () => {
  return (
    <div className="page-container">
      {/* Header - Keep this consistent */}
      <header className="page-header">
        <div className="header-content">
          <Link to="/" className="logo">
            <span className="logo-emoji">🚀</span>
            <span className="logo-text">VelocityPost</span>
          </Link>
          
          <nav className="nav-links">
            <Link to="/" className="nav-link">Home</Link>
            <Link to="/features" className="nav-link">Features</Link>
            <Link to="/pricing" className="nav-link">Pricing</Link>
            <Link to="/about" className="nav-link">About</Link>
            <Link to="/contact" className="nav-link">Contact</Link>
            <Link to="/login" className="nav-link-secondary">Sign In</Link>
            <Link to="/register" className="nav-cta-button">Get Started</Link>
          </nav>
        </div>
      </header>

      {/* Page Banner - UPDATE TITLE & DESCRIPTION */}
      <section className="page-banner">
        <h1 className="page-title">Your Page Title</h1>
        <p className="page-description">
          Your page description goes here. Make it engaging!
        </p>
      </section>

      {/* Main Content - ADD YOUR CONTENT HERE */}
      <main className="page-content">
        <section className="content-section">
          <h2 className="section-title">Section Title</h2>
          <p className="section-text">
            Add your content here. You can add multiple paragraphs, sections, and components.
          </p>
        </section>

        {/* Example Content Grid */}
        <div className="content-grid">
          <div className="content-card">
            <div className="card-icon">🚀</div>
            <h3 className="card-title">Feature 1</h3>
            <p className="card-text">Description goes here...</p>
          </div>

          <div className="content-card">
            <div className="card-icon">⚡</div>
            <h3 className="card-title">Feature 2</h3>
            <p className="card-text">Description goes here...</p>
          </div>

          <div className="content-card">
            <div className="card-icon">🎯</div>
            <h3 className="card-title">Feature 3</h3>
            <p className="card-text">Description goes here...</p>
          </div>
        </div>

        {/* Optional CTA Section */}
        <section className="cta-section">
          <h2 className="cta-title">Ready to Get Started?</h2>
          <p className="cta-text">Join thousands of users today</p>
          <Link to="/register" className="cta-button">Start Free Trial</Link>
        </section>
      </main>

      {/* Footer - Keep this consistent */}
      <footer className="page-footer">
        <div className="footer-content">
          <div className="footer-grid">
            <div className="footer-column">
              <h4>Product</h4>
              <Link to="/features">Features</Link>
              <Link to="/pricing">Pricing</Link>
              <Link to="/integrations">Integrations</Link>
              <Link to="/api">API</Link>
            </div>
            <div className="footer-column">
              <h4>Company</h4>
              <Link to="/about">About</Link>
              <Link to="/careers">Careers</Link>
              <Link to="/blog">Blog</Link>
              <Link to="/contact">Contact</Link>
            </div>
            <div className="footer-column">
              <h4>Support</h4>
              <Link to="/helpcenter">Help Center</Link>
              <Link to="/documentation">Documentation</Link>
              <Link to="/community">Community</Link>
              <Link to="/status">Status</Link>
            </div>
            <div className="footer-column">
              <h4>Legal</h4>
              <Link to="/privacypolicy">Privacy Policy</Link>
              <Link to="/termsofservice">Terms of Service</Link>
              <Link to="/cookiepolicy">Cookie Policy</Link>
            </div>
          </div>
          <div className="footer-bottom">
            <p>© {new Date().getFullYear()} VelocityPost. All rights reserved.</p>
          </div>
        </div>
      </footer>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .page-container {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        /* Header */
        .page-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid #e5e7eb;
          padding: 16px 0;
          z-index: 100;
        }

        .header-content {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .logo {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: #111827;
          font-weight: 800;
          font-size: 20px;
        }

        .logo-emoji {
          font-size: 24px;
        }

        .nav-links {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
        }

        .nav-link,
        .nav-link-secondary {
          color: #6b7280;
          text-decoration: none;
          font-size: 14px;
          font-weight: 600;
          padding: 8px 16px;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .nav-link.active {
          color: #0ea5e9;
          background: #f0f9ff;
        }

        .nav-link:hover,
        .nav-link-secondary:hover {
          color: #0ea5e9;
          background: #f0f9ff;
        }

        .nav-cta-button {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          padding: 10px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 700;
          font-size: 14px;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
        }

        .nav-cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
        }

        /* Page Banner */
        .page-banner {
          margin-top: 64px;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          padding: 80px 24px;
          text-align: center;
          color: white;
        }

        .page-title {
          font-size: clamp(36px, 6vw, 56px);
          font-weight: 900;
          margin-bottom: 16px;
        }

        .page-description {
          font-size: clamp(16px, 3vw, 20px);
          opacity: 0.95;
          max-width: 700px;
          margin: 0 auto;
        }

        /* Main Content */
        .page-content {
          flex: 1;
          max-width: 1200px;
          margin: 0 auto;
          padding: 60px 24px;
          width: 100%;
        }

        .content-section {
          margin-bottom: 60px;
        }

        .section-title {
          font-size: clamp(28px, 5vw, 40px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 24px;
          text-align: center;
        }

        .section-text {
          font-size: 17px;
          line-height: 1.8;
          color: #4b5563;
          text-align: center;
          max-width: 800px;
          margin: 0 auto 20px;
        }

        .content-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 28px;
          margin: 60px 0;
        }

        .content-card {
          background: #f9fafb;
          padding: 36px;
          border-radius: 16px;
          transition: all 0.3s;
          text-align: center;
        }

        .content-card:hover {
          background: white;
          box-shadow: 0 20px 60px rgba(14, 165, 233, 0.15);
          transform: translateY(-8px);
        }

        .card-icon {
          font-size: 48px;
          margin-bottom: 20px;
        }

        .card-title {
          font-size: 22px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 12px;
        }

        .card-text {
          color: #6b7280;
          line-height: 1.6;
          font-size: 15px;
        }

        /* CTA Section */
        .cta-section {
          background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
          padding: 60px 40px;
          border-radius: 20px;
          text-align: center;
          margin: 60px 0;
        }

        .cta-title {
          font-size: clamp(28px, 5vw, 40px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 16px;
        }

        .cta-text {
          font-size: 18px;
          color: #6b7280;
          margin-bottom: 32px;
        }

        .cta-button {
          display: inline-block;
          padding: 14px 36px;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          border-radius: 10px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s;
        }

        .cta-button:hover {
          transform: translateY(-3px);
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        /* Footer */
        .page-footer {
          background: #111827;
          color: white;
          padding: 60px 24px 40px;
          margin-top: auto;
        }

        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
        }

        .footer-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 40px;
          margin-bottom: 40px;
        }

        .footer-column {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .footer-column h4 {
          font-size: 14px;
          font-weight: 700;
          text-transform: uppercase;
          margin-bottom: 8px;
          letter-spacing: 1px;
        }

        .footer-column a {
          color: #9ca3af;
          text-decoration: none;
          font-size: 14px;
          transition: color 0.2s;
        }

        .footer-column a:hover {
          color: #0ea5e9;
        }

        .footer-bottom {
          border-top: 1px solid #1f2937;
          padding-top: 24px;
          text-align: center;
        }

        .footer-bottom p {
          color: #9ca3af;
          font-size: 14px;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .nav-links {
            gap: 4px;
          }

          .nav-link,
          .nav-link-secondary {
            padding: 6px 10px;
            font-size: 12px;
          }

          .nav-cta-button {
            padding: 8px 16px;
            font-size: 12px;
          }

          .content-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 480px) {
          .nav-links {
            gap: 2px;
          }

          .nav-link,
          .nav-link-secondary {
            padding: 6px 8px;
            font-size: 11px;
          }

          .logo-text {
            font-size: 16px;
          }
        }
      `}</style>
    </div>
  );
};

export default PAGENAME;  // UPDATE THIS TO MATCH YOUR COMPONENT NAME