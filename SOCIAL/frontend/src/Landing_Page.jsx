import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './quickpage/AuthContext';

const Landing_Page = () => {
  const { isAuthenticated } = useAuth();
  const [activeFeature, setActiveFeature] = useState(0);
  const [hoveredPlatform, setHoveredPlatform] = useState(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  // Handle scroll for header
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Auto-rotate features
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [mobileMenuOpen]);

  const platforms = [
    { 
      name: 'Facebook', 
      emoji: '📘', 
      route: '/facebook-instagram', 
      features: ['AI Content Generation', 'Multi-Page Management', 'Smart Scheduling', 'Advanced Analytics'],
      description: 'Automate your Facebook presence with AI-powered content creation and intelligent scheduling.'
    },
    { 
      name: 'Instagram', 
      emoji: '📸', 
      route: '/instagram', 
      features: ['AI Image Generation', 'Smart Hashtags', 'Story Automation', 'Engagement Boost'],
      description: 'Create stunning Instagram content automatically with AI-powered images and captions.'
    },
    { 
      name: 'WhatsApp', 
      emoji: '💬', 
      route: '/whatsapp', 
      features: ['Auto Reply', 'Broadcast Messages', 'Templates', 'Chat Analytics'],
      description: 'Streamline your WhatsApp communication with automated responses and broadcast capabilities.'
    },
    { 
      name: 'YouTube', 
      emoji: '📺', 
      route: '/youtube', 
      features: ['AI Script Writing', 'Auto Upload', 'SEO Optimization', 'Shorts Creation'],
      description: 'Grow your YouTube channel with AI-generated scripts and automated video uploads.'
    },
    { 
      name: 'Reddit', 
      emoji: '🔴', 
      route: '/reddit-auto', 
      features: ['Auto Posting', 'Smart Replies', 'Karma Building', 'Multi-Subreddit'],
      description: 'Build your Reddit presence with intelligent posting and automated engagement.'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Content',
      description: 'Generate engaging posts, captions, and images automatically with advanced AI',
      icon: '🤖'
    },
    {
      title: 'Smart Scheduling',
      description: 'Post at optimal times for maximum engagement across all platforms',
      icon: '⚡'
    },
    {
      title: 'Analytics Dashboard',
      description: 'Track performance and optimize your strategy with real-time insights',
      icon: '📊'
    },
    {
      title: 'Multi-Platform',
      description: 'Manage all your social media accounts from one unified dashboard',
      icon: '🎯'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Marketing Director',
      company: 'TechCorp',
      content: 'VelocityPost has transformed our social media strategy. We\'ve seen a 300% increase in engagement and saved 20 hours per week.',
      image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop',
      rating: 5
    },
    {
      name: 'Michael Chen',
      role: 'Content Creator',
      company: 'Digital Agency',
      content: 'The AI content generation is incredible. It understands our brand voice perfectly and creates posts that resonate with our audience.',
      image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop',
      rating: 5
    },
    {
      name: 'Emily Rodriguez',
      role: 'Social Media Manager',
      company: 'E-commerce Brand',
      content: 'Managing 5 platforms used to be overwhelming. Now it\'s effortless. The automation features are game-changing.',
      image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop',
      rating: 5
    }
  ];

  const stats = [
    { value: '50K+', label: 'Active Users' },
    { value: '10M+', label: 'Posts Automated' },
    { value: '98%', label: 'Satisfaction Rate' },
    { value: '5x', label: 'Engagement Boost' }
  ];

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setMobileMenuOpen(false);
    }
  };

  return (
    <div className="landing-page-container">
      {/* Header */}
      <header className={`landing-header ${scrolled ? 'scrolled' : ''}`}>
        <div className="landing-header-content">
          {/* Logo */}
          <Link to="/" className="landing-logo">
            <span className="logo-emoji">🚀</span>
            <span className="logo-text">VelocityPost</span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="landing-desktop-nav">
            <button onClick={() => scrollToSection('features')} className="nav-button">
              Features
            </button>
            <button onClick={() => scrollToSection('platforms')} className="nav-button">
              Platforms
            </button>
            <button onClick={() => scrollToSection('testimonials')} className="nav-button">
              Testimonials
            </button>
            <Link to="/pricing" className="nav-button">
              Pricing
            </Link>
            
            {isAuthenticated ? (
              <Link to="/reddit-auto" className="cta-button">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="nav-button">Sign In</Link>
                <Link to="/register" className="cta-button">
                  Get Started Free
                </Link>
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="landing-mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span className={mobileMenuOpen ? 'active' : ''}></span>
            <span className={mobileMenuOpen ? 'active' : ''}></span>
            <span className={mobileMenuOpen ? 'active' : ''}></span>
          </button>
        </div>

        {/* Mobile Menu Overlay */}
        {mobileMenuOpen && (
          <div className="landing-mobile-overlay" onClick={() => setMobileMenuOpen(false)} />
        )}

        {/* Mobile Menu */}
        <div className={`landing-mobile-menu ${mobileMenuOpen ? 'open' : ''}`}>
          <button onClick={() => scrollToSection('features')} className="mobile-menu-item">
            Features
          </button>
          <button onClick={() => scrollToSection('platforms')} className="mobile-menu-item">
            Platforms
          </button>
          <button onClick={() => scrollToSection('testimonials')} className="mobile-menu-item">
            Testimonials
          </button>
          <Link to="/pricing" onClick={() => setMobileMenuOpen(false)} className="mobile-menu-item">
            Pricing
          </Link>

          {isAuthenticated ? (
            <Link to="/reddit-auto" onClick={() => setMobileMenuOpen(false)} className="mobile-cta-button">
              Dashboard
            </Link>
          ) : (
            <>
              <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="mobile-signin-button">
                Sign In
              </Link>
              <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="mobile-cta-button">
                Get Started Free
              </Link>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="floating-bg floating-bg-1"></div>
        <div className="floating-bg floating-bg-2"></div>
        
        <div className="hero-content">
          <div className="hero-badge">
            🎉 New: AI-Powered Instagram Stories!
          </div>

          <h1 className="hero-title">
            Automate Your<br />
            <span className="gradient-text">Social Media Magic</span>
          </h1>

          <p className="hero-subtitle">
            AI-powered automation for Facebook, Instagram, WhatsApp, YouTube & Reddit. 
            Save 20+ hours weekly while boosting engagement by 300%.
          </p>

          <div className="hero-buttons">
            <Link to="/register" className="hero-cta-primary">
              Start Free Trial
            </Link>
            <button onClick={() => scrollToSection('platforms')} className="hero-cta-secondary">
              Watch Demo
            </button>
          </div>

          <div className="hero-stats">
            {stats.map((stat, idx) => (
              <div key={idx} className="stat-item">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="section-header">
          <h2 className="section-title">Powerful Features</h2>
          <p className="section-subtitle">
            Everything you need to dominate social media
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className={`feature-card ${activeFeature === idx ? 'active' : ''}`}
              onMouseEnter={() => setActiveFeature(idx)}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" className="platforms-section">
        <div className="section-header">
          <h2 className="section-title">Supported Platforms</h2>
          <p className="section-subtitle">
            One dashboard to rule them all
          </p>
        </div>

        <div className="platforms-grid">
          {platforms.map((platform, idx) => (
            <Link
              key={idx}
              to={platform.route}
              className="platform-card"
              onMouseEnter={() => setHoveredPlatform(idx)}
              onMouseLeave={() => setHoveredPlatform(null)}
            >
              <div className="platform-emoji">{platform.emoji}</div>
              <h3 className="platform-name">{platform.name}</h3>
              <p className="platform-description">{platform.description}</p>
              
              <div className={`platform-features ${hoveredPlatform === idx ? 'visible' : ''}`}>
                {platform.features.map((feature, fIdx) => (
                  <span key={fIdx} className="platform-feature-tag">
                    {feature}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section">
        <div className="section-header">
          <h2 className="section-title">Loved by Thousands</h2>
          <p className="section-subtitle">
            See what our users are saying
          </p>
        </div>

        <div className="testimonials-grid">
          {testimonials.map((testimonial, idx) => (
            <div key={idx} className="testimonial-card">
              <div className="testimonial-rating">
                {'⭐'.repeat(testimonial.rating)}
              </div>
              <p className="testimonial-content">"{testimonial.content}"</p>
              <div className="testimonial-author">
                <img
                  src={testimonial.image}
                  alt={testimonial.name}
                  className="author-image"
                />
                <div className="author-info">
                  <div className="author-name">{testimonial.name}</div>
                  <div className="author-role">
                    {testimonial.role} at {testimonial.company}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your Social Media?</h2>
          <p className="cta-subtitle">
            Join 50,000+ users automating their social media success
          </p>
          <div className="cta-buttons">
            <Link to="/register" className="cta-button-primary">
              Start Free Trial
            </Link>
            <Link to="/contact" className="cta-button-secondary">
              Contact Sales
            </Link>
          </div>
          <p className="cta-note">No credit card required • Cancel anytime</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-grid">
            {/* Brand Section */}
            <div className="footer-brand">
              <div className="footer-logo">
                <span>🚀</span>
                VelocityPost
              </div>
              <p className="footer-description">
                AI-powered social media automation platform helping businesses save time and boost engagement.
              </p>
              <div className="footer-socials">
                <a href="https://facebook.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">
                  f
                </a>
                <a href="https://twitter.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">
                  𝕏
                </a>
                <a href="https://instagram.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">
                  📷
                </a>
                <a href="https://linkedin.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">
                  in
                </a>
              </div>
            </div>

            {/* Product Links */}
            <div className="footer-column">
              <h4 className="footer-column-title">Product</h4>
              <div className="footer-links">
                <Link to="/features" className="footer-link">Features</Link>
                <Link to="/pricing" className="footer-link">Pricing</Link>
                <Link to="/integrations" className="footer-link">Integrations</Link>
                <Link to="/api" className="footer-link">API</Link>
              </div>
            </div>

            {/* Company Links */}
            <div className="footer-column">
              <h4 className="footer-column-title">Company</h4>
              <div className="footer-links">
                <Link to="/about" className="footer-link">About Us</Link>
                <Link to="/careers" className="footer-link">Careers</Link>
                <Link to="/blog" className="footer-link">Blog</Link>
                <Link to="/contact" className="footer-link">Contact</Link>
              </div>
            </div>

            {/* Support Links */}
            <div className="footer-column">
              <h4 className="footer-column-title">Support</h4>
              <div className="footer-links">
                <Link to="/helpcenter" className="footer-link">Help Center</Link>
                <Link to="/documentation" className="footer-link">Documentation</Link>
                <Link to="/community" className="footer-link">Community</Link>
                <Link to="/status" className="footer-link">Status</Link>
              </div>
            </div>

            {/* Legal Links */}
            <div className="footer-column">
              <h4 className="footer-column-title">Legal</h4>
              <div className="footer-links">
                <Link to="/privacypolicy" className="footer-link">Privacy Policy</Link>
                <Link to="/termsofservice" className="footer-link">Terms of Service</Link>
                <Link to="/cookiepolicy" className="footer-link">Cookie Policy</Link>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <p className="footer-copyright">
              © {new Date().getFullYear()} VelocityPost. All rights reserved.
            </p>
            <div className="footer-legal-links">
              <Link to="/privacypolicy" className="footer-legal-link">Privacy</Link>
              <Link to="/termsofservice" className="footer-legal-link">Terms</Link>
              <Link to="/cookiepolicy" className="footer-legal-link">Cookies</Link>
            </div>
          </div>
        </div>
      </footer>

      <style>{`
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .landing-page-container {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
          overflow-x: hidden;
        }

        /* Header Styles */
        .landing-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(20px);
          transition: all 0.3s;
          padding: 16px 0;
        }

        .landing-header.scrolled {
          background: rgba(255, 255, 255, 0.95);
          box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
        }

        .landing-header-content {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .landing-logo {
          display: flex;
          align-items: center;
          gap: 8px;
          text-decoration: none;
          color: #1a1a1a;
          font-weight: 800;
          font-size: 24px;
          transition: transform 0.3s;
        }

        .landing-logo:hover {
          transform: scale(1.05);
        }

        .logo-emoji {
          font-size: 28px;
        }

        .logo-text {
          font-size: 20px;
        }

        .landing-desktop-nav {
          display: flex;
          align-items: center;
          gap: 32px;
        }

        .nav-button {
          background: none;
          border: none;
          color: #4b5563;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          transition: color 0.3s;
          padding: 8px 0;
        }

        .nav-button:hover {
          color: #667eea;
        }

        .cta-button {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 12px 28px;
          border-radius: 25px;
          text-decoration: none;
          font-weight: 700;
          font-size: 15px;
          transition: all 0.3s;
          box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        /* Mobile Menu */
        .landing-mobile-menu-btn {
          display: none;
          flex-direction: column;
          gap: 5px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          z-index: 1001;
        }

        .landing-mobile-menu-btn span {
          width: 25px;
          height: 3px;
          background: #1a1a1a;
          border-radius: 3px;
          transition: all 0.3s;
        }

        .landing-mobile-menu-btn span.active:nth-child(1) {
          transform: rotate(45deg) translate(8px, 8px);
        }

        .landing-mobile-menu-btn span.active:nth-child(2) {
          opacity: 0;
        }

        .landing-mobile-menu-btn span.active:nth-child(3) {
          transform: rotate(-45deg) translate(7px, -7px);
        }

        .landing-mobile-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 999;
          animation: fadeIn 0.3s;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .landing-mobile-menu {
          position: fixed;
          top: 0;
          right: -100%;
          width: 280px;
          height: 100vh;
          background: white;
          z-index: 1000;
          padding: 80px 24px 24px;
          display: flex;
          flex-direction: column;
          gap: 16px;
          transition: right 0.3s ease;
          box-shadow: -5px 0 20px rgba(0, 0, 0, 0.1);
          overflow-y: auto;
        }

        .landing-mobile-menu.open {
          right: 0;
        }

        .mobile-menu-item {
          background: none;
          border: none;
          color: #1a1a1a;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          padding: 12px 16px;
          border-radius: 8px;
          transition: all 0.3s;
          text-align: left;
        }

        .mobile-menu-item:hover {
          background: #f3f4f6;
          color: #667eea;
        }

        .mobile-signin-button {
          background: #f3f4f6;
          color: #667eea;
          padding: 12px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 700;
          text-align: center;
          transition: all 0.3s;
          margin-top: 8px;
        }

        .mobile-signin-button:hover {
          background: #e5e7eb;
        }

        .mobile-cta-button {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 14px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 700;
          text-align: center;
          transition: all 0.3s;
          margin-top: 8px;
        }

        .mobile-cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }

        /* Hero Section */
        .hero-section {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 120px 24px 80px;
          position: relative;
          overflow: hidden;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        .floating-bg {
          position: absolute;
          width: 400px;
          height: 400px;
          border-radius: 50%;
          filter: blur(100px);
          opacity: 0.3;
          animation: float 20s infinite ease-in-out;
        }

        .floating-bg-1 {
          background: #667eea;
          top: 10%;
          left: 10%;
          animation-delay: 0s;
        }

        .floating-bg-2 {
          background: #764ba2;
          bottom: 10%;
          right: 10%;
          animation-delay: 5s;
        }

        @keyframes float {
          0%, 100% { transform: translate(0, 0); }
          25% { transform: translate(30px, -30px); }
          50% { transform: translate(-20px, 20px); }
          75% { transform: translate(40px, 10px); }
        }

        .hero-content {
          max-width: 1200px;
          text-align: center;
          position: relative;
          z-index: 1;
        }

        .hero-badge {
          display: inline-block;
          background: white;
          padding: 12px 24px;
          border-radius: 30px;
          font-size: 14px;
          font-weight: 600;
          color: #667eea;
          margin-bottom: 32px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
          animation: slideDown 0.6s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .hero-title {
          font-size: clamp(40px, 7vw, 80px);
          font-weight: 900;
          line-height: 1.1;
          margin-bottom: 24px;
          color: #1a1a1a;
          animation: slideUp 0.8s ease-out;
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .gradient-text {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-subtitle {
          font-size: clamp(18px, 3vw, 24px);
          color: #4b5563;
          max-width: 800px;
          margin: 0 auto 48px;
          line-height: 1.6;
          animation: slideUp 1s ease-out;
        }

        .hero-buttons {
          display: flex;
          gap: 20px;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 60px;
          animation: slideUp 1.2s ease-out;
        }

        .hero-cta-primary {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          padding: 18px 48px;
          border-radius: 30px;
          text-decoration: none;
          font-weight: 700;
          font-size: 18px;
          box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
          transition: all 0.3s;
        }

        .hero-cta-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        }

        .hero-cta-secondary {
          background: white;
          color: #667eea;
          padding: 18px 48px;
          border: 2px solid #667eea;
          border-radius: 30px;
          font-weight: 700;
          font-size: 18px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .hero-cta-secondary:hover {
          background: #667eea;
          color: white;
          transform: translateY(-3px);
        }

        .hero-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 32px;
          max-width: 900px;
          margin: 0 auto;
          animation: slideUp 1.4s ease-out;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: #667eea;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #6b7280;
          font-weight: 600;
        }

        /* Features Section */
        .features-section {
          padding: 120px 24px;
          background: white;
        }

        .section-header {
          text-align: center;
          max-width: 800px;
          margin: 0 auto 64px;
        }

        .section-title {
          font-size: clamp(36px, 5vw, 56px);
          font-weight: 900;
          color: #1a1a1a;
          margin-bottom: 16px;
        }

        .section-subtitle {
          font-size: clamp(16px, 3vw, 20px);
          color: #6b7280;
          line-height: 1.6;
        }

        .features-grid {
          max-width: 1400px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 32px;
        }

        .feature-card {
          background: #f9fafb;
          padding: 40px;
          border-radius: 20px;
          transition: all 0.3s;
          cursor: pointer;
          border: 2px solid transparent;
        }

        .feature-card:hover,
        .feature-card.active {
          background: white;
          border-color: #667eea;
          box-shadow: 0 20px 60px rgba(102, 126, 234, 0.15);
          transform: translateY(-5px);
        }

        .feature-icon {
          font-size: 48px;
          margin-bottom: 24px;
        }

        .feature-title {
          font-size: 24px;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 12px;
        }

        .feature-description {
          color: #6b7280;
          line-height: 1.6;
          font-size: 16px;
        }

        /* Platforms Section */
        .platforms-section {
          padding: 120px 24px;
          background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        .platforms-grid {
          max-width: 1400px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 32px;
        }

        .platform-card {
          background: white;
          padding: 40px;
          border-radius: 20px;
          text-decoration: none;
          transition: all 0.3s;
          cursor: pointer;
          border: 2px solid transparent;
          display: flex;
          flex-direction: column;
        }

        .platform-card:hover {
          border-color: #667eea;
          transform: translateY(-10px);
          box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
        }

        .platform-emoji {
          font-size: 64px;
          margin-bottom: 20px;
        }

        .platform-name {
          font-size: 28px;
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 12px;
        }

        .platform-description {
          color: #6b7280;
          line-height: 1.6;
          margin-bottom: 20px;
          flex-grow: 1;
        }

        .platform-features {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          opacity: 0;
          max-height: 0;
          overflow: hidden;
          transition: all 0.3s;
        }

        .platform-features.visible {
          opacity: 1;
          max-height: 200px;
        }

        .platform-feature-tag {
          background: #f3f4f6;
          color: #667eea;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
        }

        /* Testimonials Section */
        .testimonials-section {
          padding: 120px 24px;
          background: white;
        }

        .testimonials-grid {
          max-width: 1400px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 32px;
        }

        .testimonial-card {
          background: #f9fafb;
          padding: 40px;
          border-radius: 20px;
          transition: all 0.3s;
        }

        .testimonial-card:hover {
          background: white;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
          transform: translateY(-5px);
        }

        .testimonial-rating {
          font-size: 20px;
          margin-bottom: 16px;
        }

        .testimonial-content {
          color: #1a1a1a;
          font-size: 16px;
          line-height: 1.6;
          margin-bottom: 24px;
          font-style: italic;
        }

        .testimonial-author {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .author-image {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          object-fit: cover;
        }

        .author-name {
          font-weight: 700;
          color: #1a1a1a;
          margin-bottom: 4px;
        }

        .author-role {
          color: #6b7280;
          font-size: 14px;
        }

        /* CTA Section */
        .cta-section {
          padding: 120px 24px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          position: relative;
          overflow: hidden;
        }

        .cta-content {
          max-width: 900px;
          margin: 0 auto;
          text-align: center;
          position: relative;
          z-index: 1;
        }

        .cta-title {
          font-size: clamp(32px, 5vw, 56px);
          font-weight: 900;
          color: white;
          margin-bottom: 24px;
          line-height: 1.2;
        }

        .cta-subtitle {
          font-size: clamp(18px, 3vw, 24px);
          color: rgba(255, 255, 255, 0.95);
          margin-bottom: 40px;
          line-height: 1.6;
        }

        .cta-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
        }

        .cta-button-primary {
          padding: 18px 48px;
          background: white;
          color: #667eea;
          text-decoration: none;
          border-radius: 30px;
          font-weight: 700;
          font-size: 18px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
          transition: all 0.3s;
        }

        .cta-button-primary:hover {
          transform: translateY(-3px) scale(1.05);
          box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }

        .cta-button-secondary {
          padding: 18px 48px;
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          color: white;
          text-decoration: none;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 30px;
          font-weight: 700;
          font-size: 18px;
          transition: all 0.3s;
        }

        .cta-button-secondary:hover {
          background: rgba(255, 255, 255, 0.25);
          transform: translateY(-3px);
        }

        .cta-note {
          margin-top: 24px;
          color: rgba(255, 255, 255, 0.8);
          font-size: 14px;
        }

        /* Footer */
        .landing-footer {
          background: #1a1a1a;
          color: white;
          padding: 80px 24px 40px;
        }

        .footer-content {
          max-width: 1400px;
          margin: 0 auto;
        }

        .footer-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 48px;
          margin-bottom: 60px;
        }

        .footer-brand {
          grid-column: span 2;
        }

        .footer-logo {
          font-size: 28px;
          font-weight: 700;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .footer-logo span {
          font-size: 32px;
        }

        .footer-description {
          color: #9ca3af;
          line-height: 1.6;
          margin-bottom: 24px;
          max-width: 300px;
        }

        .footer-socials {
          display: flex;
          gap: 12px;
        }

        .footer-social-link {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #374151;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          text-decoration: none;
          font-weight: 700;
          font-size: 14px;
          transition: all 0.3s;
        }

        .footer-social-link:hover {
          background: #667eea;
          transform: translateY(-3px);
        }

        .footer-column-title {
          font-size: 16px;
          font-weight: 700;
          margin-bottom: 20px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: white;
        }

        .footer-links {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .footer-link {
          color: #9ca3af;
          text-decoration: none;
          font-size: 15px;
          transition: color 0.3s;
        }

        .footer-link:hover {
          color: #667eea;
        }

        .footer-bottom {
          padding-top: 32px;
          border-top: 1px solid #374151;
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 20px;
        }

        .footer-copyright {
          color: #9ca3af;
          margin: 0;
          font-size: 14px;
        }

        .footer-legal-links {
          display: flex;
          gap: 24px;
          flex-wrap: wrap;
        }

        .footer-legal-link {
          color: #9ca3af;
          text-decoration: none;
          font-size: 14px;
          transition: color 0.3s;
        }

        .footer-legal-link:hover {
          color: #667eea;
        }

        /* Responsive Styles */
        @media (max-width: 1024px) {
          .landing-mobile-menu-btn {
            display: flex;
          }
          
          .landing-desktop-nav {
            display: none;
          }
        }

        @media (max-width: 768px) {
          .floating-bg {
            width: 200px !important;
            height: 200px !important;
          }

          .footer-brand {
            grid-column: span 1;
          }

          .hero-stats {
            grid-template-columns: repeat(2, 1fr);
          }

          .features-grid,
          .platforms-grid,
          .testimonials-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 480px) {
          .landing-header {
            padding: 12px 0;
          }

          .logo-text {
            display: none;
          }

          .hero-section,
          .features-section,
          .platforms-section,
          .testimonials-section,
          .cta-section {
            padding: 80px 16px;
          }

          .landing-footer {
            padding: 60px 16px 32px;
          }

          .hero-buttons,
          .cta-buttons {
            flex-direction: column;
            width: 100%;
          }

          .hero-cta-primary,
          .hero-cta-secondary,
          .cta-button-primary,
          .cta-button-secondary {
            width: 100%;
            text-align: center;
          }

          .hero-stats {
            grid-template-columns: 1fr;
            gap: 24px;
          }
        }

        /* Smooth Scrolling */
        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </div>
  );
};

export default Landing_Page;