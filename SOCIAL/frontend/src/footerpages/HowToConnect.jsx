import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../quickpage/Header';

const HowToConnect = () => {
  const [activeStep, setActiveStep] = useState(0);

  const platforms = [
    {
      name: 'Facebook',
      emoji: '📘',
      color: '#1877f2',
      steps: [
        'Click "Connect Facebook" button',
        'Log in to your Facebook account',
        'Authorize VelocityPost to post on your behalf',
        'Select pages you want to manage',
        'Start automating!'
      ],
      features: ['Multi-page support', 'Scheduled posting', 'AI content generation'],
      secure: true
    },
    {
      name: 'Instagram',
      emoji: '📸',
      color: '#e4405f',
      steps: [
        'Click "Connect Instagram" button',
        'Sign in with Instagram credentials',
        'Grant posting permissions',
        'Confirm business account',
        'Begin automation!'
      ],
      features: ['Story automation', 'AI image generation', 'Smart hashtags'],
      secure: true
    },
    {
      name: 'Reddit',
      emoji: '🔴',
      color: '#ff4500',
      steps: [
        'Click "Connect Reddit" button',
        'Authorize with Reddit OAuth',
        'Select subreddits to manage',
        'Configure posting preferences',
        'Let AI handle the rest!'
      ],
      features: ['Auto-posting', 'Karma building', 'Smart replies'],
      secure: true
    },
    {
      name: 'YouTube',
      emoji: '📺',
      color: '#ff0000',
      steps: [
        'Click "Connect YouTube" button',
        'Sign in with Google account',
        'Grant channel access',
        'Configure upload settings',
        'Start uploading videos!'
      ],
      features: ['Auto upload', 'SEO optimization', 'AI script writing'],
      secure: true
    },
    {
      name: 'WhatsApp',
      emoji: '💬',
      color: '#25d366',
      steps: [
        'Click "Connect WhatsApp" button',
        'Scan QR code with your phone',
        'Authorize web access',
        'Set up auto-reply rules',
        'Automate messaging!'
      ],
      features: ['Auto reply', 'Broadcast messages', 'Templates'],
      secure: true
    }
  ];

  return (
    <div className="how-to-connect-page">
      <Header />
      
      <div className="htc-container">
        {/* Hero Section */}
        <section className="htc-hero">
          <div className="htc-hero-badge">
            <span className="badge-lock">🔒</span>
            100% Secure & Private
          </div>
          
          <h1 className="htc-hero-title">
            Connect Your Social Media
            <span className="htc-gradient-text"> Safely & Securely</span>
          </h1>
          
          <p className="htc-hero-subtitle">
            Your passwords are NEVER stored on our servers. We use official OAuth 2.0 
            authentication provided by each platform to keep your accounts 100% secure.
          </p>

          <div className="htc-trust-badges">
            <div className="trust-badge">
              <span className="trust-icon">🛡️</span>
              <span className="trust-text">OAuth 2.0 Secure</span>
            </div>
            <div className="trust-badge">
              <span className="trust-icon">🔐</span>
              <span className="trust-text">End-to-End Encrypted</span>
            </div>
            <div className="trust-badge">
              <span className="trust-icon">✅</span>
              <span className="trust-text">GDPR Compliant</span>
            </div>
          </div>
        </section>

        {/* Privacy Assurance Section */}
        <section className="htc-privacy-section">
          <div className="privacy-card">
            <div className="privacy-icon">🔒</div>
            <h2 className="privacy-title">Your Privacy is Our Priority</h2>
            <p className="privacy-text">
              When you click "Connect" on any platform, you'll be redirected to the official 
              website of that social media platform. You'll log in directly on their secure 
              page - NOT on VelocityPost.
            </p>
            <div className="privacy-points">
              <div className="privacy-point">
                <span className="point-icon">✓</span>
                <span className="point-text">We NEVER see your password</span>
              </div>
              <div className="privacy-point">
                <span className="point-icon">✓</span>
                <span className="point-text">You can revoke access anytime</span>
              </div>
              <div className="privacy-point">
                <span className="point-icon">✓</span>
                <span className="point-text">We only request posting permissions</span>
              </div>
              <div className="privacy-point">
                <span className="point-icon">✓</span>
                <span className="point-text">All data is encrypted at rest</span>
              </div>
            </div>
          </div>
        </section>

        {/* Step-by-Step Guide */}
        <section className="htc-steps-section">
          <h2 className="htc-section-title">How It Works - Step by Step</h2>
          
          <div className="htc-platforms-grid">
            {platforms.map((platform, idx) => (
              <div 
                key={idx} 
                className="htc-platform-card"
                style={{ '--platform-color': platform.color }}
                onMouseEnter={() => setActiveStep(idx)}
              >
                <div className="platform-header">
                  <div className="platform-icon-wrapper">
                    <span className="platform-emoji">{platform.emoji}</span>
                  </div>
                  <h3 className="platform-name">{platform.name}</h3>
                  {platform.secure && (
                    <span className="secure-badge">
                      <span className="secure-icon">🔒</span>
                      Secure
                    </span>
                  )}
                </div>

                <div className="platform-steps">
                  {platform.steps.map((step, stepIdx) => (
                    <div key={stepIdx} className="step-item">
                      <div className="step-number">{stepIdx + 1}</div>
                      <div className="step-text">{step}</div>
                    </div>
                  ))}
                </div>

                <div className="platform-features">
                  <div className="features-label">Includes:</div>
                  {platform.features.map((feature, fIdx) => (
                    <span key={fIdx} className="feature-tag">
                      • {feature}
                    </span>
                  ))}
                </div>

                <Link 
                  to="/register" 
                  className="platform-connect-btn"
                  style={{ background: platform.color }}
                >
                  Connect {platform.name} →
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* Video Demo Section */}
        <section className="htc-demo-section">
          <div className="demo-content">
            <div className="demo-text">
              <h2 className="demo-title">See It In Action</h2>
              <p className="demo-description">
                Watch how easy it is to connect your social media accounts and start 
                automating your content in less than 2 minutes.
              </p>
              <div className="demo-stats">
                <div className="demo-stat">
                  <div className="stat-number">2 min</div>
                  <div className="stat-label">Setup Time</div>
                </div>
                <div className="demo-stat">
                  <div className="stat-number">5</div>
                  <div className="stat-label">Platforms</div>
                </div>
                <div className="demo-stat">
                  <div className="stat-number">100%</div>
                  <div className="stat-label">Secure</div>
                </div>
              </div>
            </div>
            <div className="demo-video-placeholder">
              <div className="video-icon">▶</div>
              <p className="video-text">Click to watch demo</p>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="htc-faq-section">
          <h2 className="htc-section-title">Frequently Asked Questions</h2>
          
          <div className="faq-grid">
            <div className="faq-card">
              <h3 className="faq-question">🔐 Is my password safe?</h3>
              <p className="faq-answer">
                Absolutely! We use OAuth 2.0, which means you log in directly on the 
                platform's official website. We NEVER see or store your password.
              </p>
            </div>

            <div className="faq-card">
              <h3 className="faq-question">🔄 Can I disconnect anytime?</h3>
              <p className="faq-answer">
                Yes! You can revoke access from your VelocityPost dashboard or directly 
                from your social media platform's settings page.
              </p>
            </div>

            <div className="faq-card">
              <h3 className="faq-question">📱 What permissions do you need?</h3>
              <p className="faq-answer">
                We only request the minimum permissions needed: posting content and reading 
                basic account info. We never access your private messages or personal data.
              </p>
            </div>

            <div className="faq-card">
              <h3 className="faq-question">💳 Do I need to add payment info?</h3>
              <p className="faq-answer">
                No! You can connect all your social media accounts and try our platform 
                completely free. No credit card required.
              </p>
            </div>

            <div className="faq-card">
              <h3 className="faq-question">🌍 Is my data encrypted?</h3>
              <p className="faq-answer">
                Yes! All data is encrypted in transit (HTTPS) and at rest (AES-256). 
                We're GDPR compliant and take data security seriously.
              </p>
            </div>

            <div className="faq-card">
              <h3 className="faq-question">⚡ How fast is the connection?</h3>
              <p className="faq-answer">
                Connecting a social media account takes less than 30 seconds. You'll be 
                up and running with automation in under 2 minutes!
              </p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="htc-cta-section">
          <div className="htc-cta-content">
            <h2 className="htc-cta-title">Ready to Get Started?</h2>
            <p className="htc-cta-text">
              Join thousands of users automating their social media safely and securely
            </p>
            <div className="htc-cta-buttons">
              <Link to="/register" className="htc-cta-primary">
                Connect Your Accounts
                <span className="cta-arrow">→</span>
              </Link>
              <Link to="/features-showcase" className="htc-cta-secondary">
                Explore Features
              </Link>
            </div>
          </div>
        </section>
      </div>

      <style>{`
        .how-to-connect-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
          padding-top: 80px;
        }

        .htc-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
        }

        /* Hero Section */
        .htc-hero {
          text-align: center;
          padding: 80px 20px 60px;
          animation: fadeIn 0.8s ease-out;
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .htc-hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: white;
          padding: 10px 24px;
          border-radius: 50px;
          font-size: 14px;
          font-weight: 700;
          color: #10b981;
          margin-bottom: 24px;
          box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
          animation: slideDown 0.6s ease-out;
        }

        @keyframes slideDown {
          from { transform: translateY(-30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .badge-lock {
          font-size: 18px;
          animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }

        .htc-hero-title {
          font-size: clamp(36px, 6vw, 56px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 24px;
          line-height: 1.2;
          animation: slideUp 0.8s ease-out;
        }

        @keyframes slideUp {
          from { transform: translateY(30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .htc-gradient-text {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .htc-hero-subtitle {
          font-size: clamp(16px, 3vw, 20px);
          color: #64748b;
          max-width: 700px;
          margin: 0 auto 40px;
          line-height: 1.7;
        }

        .htc-trust-badges {
          display: flex;
          justify-content: center;
          gap: 24px;
          flex-wrap: wrap;
        }

        .trust-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          background: white;
          padding: 12px 20px;
          border-radius: 12px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
          animation: scaleIn 0.5s ease-out backwards;
        }

        .trust-badge:nth-child(1) { animation-delay: 0.1s; }
        .trust-badge:nth-child(2) { animation-delay: 0.2s; }
        .trust-badge:nth-child(3) { animation-delay: 0.3s; }

        @keyframes scaleIn {
          from { transform: scale(0); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }

        .trust-icon {
          font-size: 20px;
        }

        .trust-text {
          font-size: 14px;
          font-weight: 600;
          color: #111827;
        }

        /* Privacy Section */
        .htc-privacy-section {
          padding: 60px 20px;
          animation: fadeIn 1s ease-out;
        }

        .privacy-card {
          max-width: 900px;
          margin: 0 auto;
          background: white;
          padding: 48px;
          border-radius: 24px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
          text-align: center;
        }

        .privacy-icon {
          font-size: 64px;
          margin-bottom: 24px;
        }

        .privacy-title {
          font-size: clamp(28px, 4vw, 36px);
          font-weight: 800;
          color: #111827;
          margin-bottom: 20px;
        }

        .privacy-text {
          font-size: 18px;
          color: #64748b;
          line-height: 1.7;
          margin-bottom: 32px;
        }

        .privacy-points {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          text-align: left;
        }

        .privacy-point {
          display: flex;
          align-items: center;
          gap: 12px;
          background: #f0f9ff;
          padding: 16px 20px;
          border-radius: 12px;
          border-left: 4px solid #0ea5e9;
        }

        .point-icon {
          font-size: 20px;
          color: #10b981;
          font-weight: 900;
        }

        .point-text {
          font-size: 15px;
          font-weight: 600;
          color: #111827;
        }

        /* Steps Section */
        .htc-steps-section {
          padding: 60px 20px;
        }

        .htc-section-title {
          font-size: clamp(32px, 5vw, 44px);
          font-weight: 900;
          color: #111827;
          text-align: center;
          margin-bottom: 48px;
        }

        .htc-platforms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 32px;
        }

        .htc-platform-card {
          background: white;
          padding: 32px;
          border-radius: 20px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          border: 2px solid transparent;
          position: relative;
          overflow: hidden;
        }

        .htc-platform-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: var(--platform-color);
          transform: scaleX(0);
          transition: transform 0.4s ease;
        }

        .htc-platform-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
          border-color: var(--platform-color);
        }

        .htc-platform-card:hover::before {
          transform: scaleX(1);
        }

        .platform-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 24px;
        }

        .platform-icon-wrapper {
          width: 60px;
          height: 60px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
          transition: transform 0.3s ease;
        }

        .htc-platform-card:hover .platform-icon-wrapper {
          transform: rotate(10deg) scale(1.1);
        }

        .platform-emoji {
          font-size: 32px;
        }

        .platform-name {
          font-size: 24px;
          font-weight: 700;
          color: #111827;
          flex: 1;
        }

        .secure-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          background: #d4edda;
          color: #155724;
          padding: 6px 12px;
          border-radius: 8px;
          font-size: 12px;
          font-weight: 700;
        }

        .secure-icon {
          font-size: 14px;
        }

        .platform-steps {
          margin-bottom: 24px;
        }

        .step-item {
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 12px;
        }

        .step-number {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 14px;
          font-weight: 700;
          flex-shrink: 0;
        }

        .step-text {
          font-size: 15px;
          color: #64748b;
          line-height: 1.6;
          padding-top: 4px;
        }

        .platform-features {
          margin-bottom: 24px;
          padding: 16px;
          background: #f8fafc;
          border-radius: 12px;
        }

        .features-label {
          font-size: 12px;
          font-weight: 700;
          color: #64748b;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          margin-bottom: 8px;
        }

        .feature-tag {
          display: inline-block;
          font-size: 13px;
          color: #0ea5e9;
          font-weight: 600;
          margin-right: 12px;
          margin-top: 4px;
        }

        .platform-connect-btn {
          display: block;
          width: 100%;
          padding: 14px;
          color: white;
          text-decoration: none;
          text-align: center;
          font-weight: 700;
          font-size: 16px;
          border-radius: 12px;
          transition: all 0.3s ease;
        }

        .platform-connect-btn:hover {
          transform: scale(1.02);
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
        }

        /* Demo Section */
        .htc-demo-section {
          padding: 60px 20px;
        }

        .demo-content {
          max-width: 1100px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 48px;
          align-items: center;
        }

        .demo-title {
          font-size: clamp(32px, 4vw, 42px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 20px;
        }

        .demo-description {
          font-size: 18px;
          color: #64748b;
          line-height: 1.7;
          margin-bottom: 32px;
        }

        .demo-stats {
          display: flex;
          gap: 32px;
        }

        .demo-stat {
          text-align: center;
        }

        .stat-number {
          font-size: 36px;
          font-weight: 900;
          color: #0ea5e9;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #64748b;
          font-weight: 600;
        }

        .demo-video-placeholder {
          aspect-ratio: 16/9;
          background: linear-gradient(135deg, #1e293b, #334155);
          border-radius: 20px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .demo-video-placeholder:hover {
          transform: scale(1.02);
          box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }

        .video-icon {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          background: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
          color: #0ea5e9;
          margin-bottom: 16px;
        }

        .video-text {
          color: white;
          font-size: 18px;
          font-weight: 600;
        }

        /* FAQ Section */
        .htc-faq-section {
          padding: 60px 20px;
        }

        .faq-grid {
          max-width: 1100px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 24px;
        }

        .faq-card {
          background: white;
          padding: 28px;
          border-radius: 16px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
          transition: all 0.3s ease;
        }

        .faq-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }

        .faq-question {
          font-size: 18px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 12px;
        }

        .faq-answer {
          font-size: 15px;
          color: #64748b;
          line-height: 1.7;
        }

        /* CTA Section */
        .htc-cta-section {
          padding: 80px 20px;
          text-align: center;
        }

        .htc-cta-content {
          max-width: 700px;
          margin: 0 auto;
        }

        .htc-cta-title {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 20px;
        }

        .htc-cta-text {
          font-size: 18px;
          color: #64748b;
          margin-bottom: 36px;
        }

        .htc-cta-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
        }

        .htc-cta-primary,
        .htc-cta-secondary {
          padding: 16px 40px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .htc-cta-primary {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        .htc-cta-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
        }

        .cta-arrow {
          font-size: 20px;
          transition: transform 0.3s ease;
        }

        .htc-cta-primary:hover .cta-arrow {
          transform: translateX(5px);
        }

        .htc-cta-secondary {
          background: white;
          color: #0ea5e9;
          border: 2px solid #0ea5e9;
        }

        .htc-cta-secondary:hover {
          background: #f0f9ff;
          transform: translateY(-3px);
        }

        /* Responsive */
        @media (max-width: 768px) {
          .htc-hero {
            padding: 60px 20px 40px;
          }

          .htc-trust-badges {
            flex-direction: column;
            align-items: center;
          }

          .privacy-card {
            padding: 32px 24px;
          }

          .htc-platforms-grid {
            grid-template-columns: 1fr;
          }

          .demo-content {
            grid-template-columns: 1fr;
          }

          .demo-stats {
            justify-content: center;
          }

          .faq-grid {
            grid-template-columns: 1fr;
          }

          .htc-cta-buttons {
            flex-direction: column;
          }

          .htc-cta-primary,
          .htc-cta-secondary {
            width: 100%;
          }
        }

        @media (max-width: 480px) {
          .htc-hero-title {
            font-size: 32px;
          }

          .privacy-points {
            grid-template-columns: 1fr;
          }

          .demo-stats {
            flex-direction: column;
            gap: 20px;
          }
        }
      `}</style>
    </div>
  );
};

export default HowToConnect;