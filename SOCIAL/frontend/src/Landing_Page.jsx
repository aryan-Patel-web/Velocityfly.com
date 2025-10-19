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
        <div className="section-container">
          <div className="section-header">
            <div className="section-badge">FEATURES</div>
            <h2 className="section-title">Everything You Need to Succeed</h2>
            <p className="section-subtitle">
              Powerful features designed to help you grow your social media presence effortlessly
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
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" className="platforms-section">
        <div className="section-container">
          <div className="section-header">
            <div className="section-badge">PLATFORMS</div>
            <h2 className="section-title">Connect All Your Channels</h2>
            <p className="section-subtitle">
              Seamless integration with all major social media platforms
            </p>
          </div>

          <div className="platforms-grid">
            {platforms.map((platform, idx) => (
              <Link
                key={idx}
                to={isAuthenticated ? platform.route : '/register'}
                className={`platform-card ${hoveredPlatform === idx ? 'hovered' : ''}`}
                onMouseEnter={() => setHoveredPlatform(idx)}
                onMouseLeave={() => setHoveredPlatform(null)}
              >
                <div className="platform-icon-wrapper">
                  <div className="platform-icon">{platform.emoji}</div>
                </div>
                <h3 className="platform-title">{platform.name}</h3>
                <p className="platform-description">{platform.description}</p>
                <div className="platform-features">
                  {platform.features.map((feat, featIdx) => (
                    <span key={featIdx} className="platform-feature-tag">
                      {feat}
                    </span>
                  ))}
                </div>
                <div className="platform-cta">
                  Get Started <span>→</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials-section">
        <div className="section-container">
          <div className="section-header">
            <div className="section-badge">TESTIMONIALS</div>
            <h2 className="section-title">Loved by Thousands</h2>
            <p className="section-subtitle">
              See what our customers are saying about VelocityPost
            </p>
          </div>

          <div className="testimonials-grid">
            {testimonials.map((testimonial, idx) => (
              <div key={idx} className="testimonial-card">
                <div className="testimonial-stars">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i}>★</span>
                  ))}
                </div>
                <p className="testimonial-content">"{testimonial.content}"</p>
                <div className="testimonial-author">
                  <img src={testimonial.image} alt={testimonial.name} className="author-image" />
                  <div>
                    <div className="author-name">{testimonial.name}</div>
                    <div className="author-role">
                      {testimonial.role} at {testimonial.company}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="floating-bg floating-bg-3"></div>
        
        <div className="cta-content">
          <h2 className="cta-title">Ready to Transform Your Social Media?</h2>
          <p className="cta-subtitle">
            Join 50,000+ businesses already automating their social media success
          </p>
          <div className="cta-buttons">
            <Link to="/register" className="cta-button-primary">
              Start Free 14-Day Trial
            </Link>
            <Link to="/contact" className="cta-button-secondary">
              Contact Sales
            </Link>
          </div>
          <p className="cta-note">
            No credit card required • Cancel anytime • 24/7 support
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-grid">
            {/* Brand */}
            <div className="footer-brand">
              <div className="footer-logo">
                <span>🚀</span>
                VelocityPost
              </div>
              <p className="footer-description">
                AI-powered social media automation for modern businesses. Save time, boost engagement, grow faster.
              </p>
              <div className="footer-socials">
                {[
                  { icon: '𝕏', name: 'Twitter' },
                  { icon: 'f', name: 'Facebook' },
                  { icon: 'in', name: 'LinkedIn' },
                  { icon: 'IG', name: 'Instagram' }
                ].map((social, idx) => (
                  <a key={idx} href="#" className="footer-social-link" aria-label={social.name}>
                    {social.icon}
                  </a>
                ))}
              </div>
            </div>

            {/* Product */}
            <div className="footer-column">
              <h4 className="footer-column-title">Product</h4>
              <div className="footer-links">
                <Link to="/features" className="footer-link">Features</Link>
                <Link to="/pricing" className="footer-link">Pricing</Link>
                <Link to="/integrations" className="footer-link">Integrations</Link>
                <Link to="/api" className="footer-link">API</Link>
              </div>
            </div>

            {/* Company */}
            <div className="footer-column">
              <h4 className="footer-column-title">Company</h4>
              <div className="footer-links">
                <Link to="/about" className="footer-link">About</Link>
                <Link to="/blog" className="footer-link">Blog</Link>
                <Link to="/careers" className="footer-link">Careers</Link>
                <Link to="/contact" className="footer-link">Contact</Link>
              </div>
            </div>

            {/* Resources */}
            <div className="footer-column">
              <h4 className="footer-column-title">Resources</h4>
              <div className="footer-links">
                <Link to="/help" className="footer-link">Help Center</Link>
                <Link to="/documentation" className="footer-link">Documentation</Link>
                <Link to="/community" className="footer-link">Community</Link>
                <Link to="/status" className="footer-link">Status</Link>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="footer-bottom">
            <p className="footer-copyright">
              © 2025 VelocityPost. All rights reserved.
            </p>
            <div className="footer-legal-links">
              <Link to="/privacy" className="footer-legal-link">Privacy Policy</Link>
              <Link to="/terms" className="footer-legal-link">Terms of Service</Link>
              <Link to="/cookie-policy" className="footer-legal-link">Cookie Policy</Link>
            </div>
          </div>
        </div>
      </footer>

      {/* Styles */}
      <style>{`
        /* Reset & Base Styles */
        .landing-page-container {
          min-height: 100vh;
          background: white;
          overflow-x: hidden;
        }

        /* Header Styles */
        .landing-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 998;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          padding: 16px 0;
          transition: all 0.3s ease;
        }

        .landing-header.scrolled {
          background: rgba(255, 255, 255, 0.98);
          border-bottom: 1px solid rgba(0, 0, 0, 0.1);
          box-shadow: 0 2px 20px rgba(0,0,0,0.1);
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
          font-size: 28px;
          fontWeight: 700;
          background: linear-gradient(135deg, #667eea, #764ba2);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          text-decoration: none;
          display: flex;
          align-items: center;
          gap: 8px;
          z-index: 999;
        }

        .logo-emoji {
          font-size: 32px;
        }

        .landing-desktop-nav {
          display: flex;
          gap: 32px;
          align-items: center;
        }

        .nav-button {
          background: none;
          border: none;
          color: #374151;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          text-decoration: none;
          padding: 8px 0;
          transition: color 0.3s;
        }

        .nav-button:hover {
          color: #667eea;
        }

        .cta-button {
          padding: 12px 28px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          text-decoration: none;
          border-radius: 30px;
          font-weight: 600;
          font-size: 15px;
          box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
          transition: all 0.3s;
          display: inline-block;
        }

        .cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
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
          z-index: 999;
        }

        .landing-mobile-menu-btn span {
          width: 25px;
          height: 3px;
          background: #374151;
          border-radius: 2px;
          transition: all 0.3s;
        }

        .landing-mobile-menu-btn span.active:nth-child(1) {
          transform: rotate(45deg) translateY(8px);
        }

        .landing-mobile-menu-btn span.active:nth-child(2) {
          opacity: 0;
        }

        .landing-mobile-menu-btn span.active:nth-child(3) {
          transform: rotate(-45deg) translateY(-8px);
        }

        .landing-mobile-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 997;
          backdrop-filter: blur(5px);
        }

        .landing-mobile-menu {
          position: fixed;
          top: 0;
          right: 0;
          bottom: 0;
          width: 80%;
          max-width: 320px;
          background: white;
          box-shadow: -4px 0 24px rgba(0, 0, 0, 0.2);
          transform: translateX(100%);
          transition: transform 0.3s ease;
          z-index: 998;
          padding: 80px 24px 24px;
          overflow-y: auto;
        }

        .landing-mobile-menu.open {
          transform: translateX(0);
        }

        .mobile-menu-item {
          display: block;
          width: 100%;
          padding: 12px 0;
          color: #374151;
          font-size: 18px;
          font-weight: 500;
          text-decoration: none;
          border: none;
          background: none;
          text-align: left;
          border-bottom: 1px solid #f3f4f6;
          cursor: pointer;
        }

        .mobile-signin-button {
          display: block;
          width: 100%;
          padding: 14px 24px;
          margin-top: 16px;
          background: transparent;
          color: #667eea;
          border: 2px solid #667eea;
          border-radius: 12px;
          font-weight: 600;
          font-size: 16px;
          text-align: center;
          text-decoration: none;
        }

        .mobile-cta-button {
          display: block;
          width: 100%;
          padding: 14px 24px;
          margin-top: 12px;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          border-radius: 12px;
          font-weight: 600;
          font-size: 16px;
          text-align: center;
          text-decoration: none;
        }

        /* Hero Section */
        .hero-section {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
          position: relative;
          padding: 140px 24px 100px;
          display: flex;
          align-items: center;
          overflow: hidden;
        }

        .floating-bg {
          position: absolute;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 50%;
          filter: blur(60px);
          animation: float 20s ease-in-out infinite;
        }

        .floating-bg-1 {
          top: 10%;
          left: 5%;
          width: 300px;
          height: 300px;
        }

        .floating-bg-2 {
          bottom: 10%;
          right: 5%;
          width: 400px;
          height: 400px;
          animation-duration: 25s;
          animation-direction: reverse;
        }

        .floating-bg-3 {
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 600px;
          height: 600px;
          filter: blur(80px);
        }

        @keyframes float {
          0%, 100% {
            transform: translate(0, 0) rotate(0deg);
          }
          33% {
            transform: translate(30px, -50px) rotate(120deg);
          }
          66% {
            transform: translate(-20px, 30px) rotate(240deg);
          }
        }

        .hero-content {
          max-width: 1400px;
          margin: 0 auto;
          text-align: center;
          color: white;
          position: relative;
          z-index: 1;
        }

        .hero-badge {
          display: inline-block;
          padding: 10px 24px;
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
          border-radius: 30px;
          border: 1px solid rgba(255, 255, 255, 0.3);
          font-size: 14px;
          font-weight: 600;
          margin-bottom: 32px;
          animation: fadeInDown 1s ease-out;
        }

        .hero-title {
          font-size: clamp(40px, 8vw, 72px);
          font-weight: 900;
          line-height: 1.1;
          margin-bottom: 24px;
          animation: fadeInUp 1s ease-out 0.2s both;
        }

        .gradient-text {
          background: linear-gradient(90deg, #fff, #f0f0f0);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }

        .hero-subtitle {
          font-size: clamp(18px, 3vw, 24px);
          line-height: 1.6;
          opacity: 0.95;
          max-width: 700px;
          margin: 0 auto 40px;
          animation: fadeInUp 1s ease-out 0.4s both;
        }

        .hero-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
          animation: fadeInUp 1s ease-out 0.6s both;
        }

        .hero-cta-primary {
          padding: 16px 40px;
          background: white;
          color: #667eea;
          text-decoration: none;
          border-radius: 30px;
          font-weight: 700;
          font-size: 18px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
          transition: all 0.3s;
        }

        .hero-cta-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }

        .hero-cta-secondary {
          padding: 16px 40px;
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          color: white;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 30px;
          font-weight: 700;
          font-size: 18px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .hero-cta-secondary:hover {
          background: rgba(255, 255, 255, 0.25);
          transform: translateY(-3px);
        }

        .hero-stats {
          margin-top: 60px;
          display: flex;
          gap: 40px;
          justify-content: center;
          flex-wrap: wrap;
          opacity: 0.9;
          animation: fadeInUp 1s ease-out 0.8s both;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          font-size: 36px;
          font-weight: 900;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          opacity: 0.9;
        }

        @keyframes fadeInDown {
          from {
            opacity: 0;
            transform: translateY(-30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        /* Section Styles */
        .features-section,
        .platforms-section,
        .testimonials-section {
          padding: 120px 24px;
        }

        .platforms-section {
          background: linear-gradient(180deg, #f9fafb 0%, white 100%);
        }

        .section-container {
          max-width: 1400px;
          margin: 0 auto;
        }

        .section-header {
          text-align: center;
          margin-bottom: 80px;
        }

        .section-badge {
          display: inline-block;
          padding: 8px 20px;
          background: rgba(102, 126, 234, 0.1);
          border-radius: 20px;
          color: #667eea;
          font-weight: 700;
          font-size: 14px;
          margin-bottom: 16px;
        }

        .section-title {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: #1a1a1a;
          margin-bottom: 16px;
        }

        .section-subtitle {
          font-size: clamp(16px, 2.5vw, 20px);
          color: #6b7280;
          max-width: 600px;
          margin: 0 auto;
        }

        /* Features Grid */
        .features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 32px;
        }

        .feature-card {
          padding: 40px;
          background: white;
          border-radius: 24px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          transition: all 0.4s;
          cursor: pointer;
          border: 1px solid #f3f4f6;
        }

        .feature-card.active {
          background: linear-gradient(135deg, #667eea, #764ba2);
          box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
          transform: translateY(-8px);
          border: none;
        }

        .feature-icon {
          font-size: 48px;
          margin-bottom: 20px;
        }

        .feature-title {
          font-size: 24px;
          font-weight: 800;
          color: #1a1a1a;
          margin-bottom: 12px;
        }

        .feature-card.active .feature-title {
          color: white;
        }

        .feature-description {
          color: #6b7280;
          line-height: 1.7;
          font-size: 16px;
        }

        .feature-card.active .feature-description {
          color: rgba(255, 255, 255, 0.9);
        }

        /* Platforms Grid */
        .platforms-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 32px;
        }

        .platform-card {
          display: block;
          padding: 32px;
          background: white;
          border-radius: 24px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          transition: all 0.4s;
          text-decoration: none;
          border: 1px solid #f3f4f6;
          cursor: pointer;
        }

        .platform-card.hovered {
          background: linear-gradient(135deg, #667eea, #764ba2);
          box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
          transform: translateY(-8px) scale(1.02);
          border: none;
        }

        .platform-icon-wrapper {
          margin-bottom: 20px;
        }

        .platform-icon {
          width: 64px;
          height: 64px;
          border-radius: 16px;
          background: rgba(102, 126, 234, 0.1);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 32px;
          transition: all 0.3s;
        }

        .platform-card.hovered .platform-icon {
          background: rgba(255, 255, 255, 0.2);
        }

        .platform-title {
          font-size: 24px;
          font-weight: 800;
          color: #1a1a1a;
          margin-bottom: 12px;
        }

        .platform-card.hovered .platform-title {
          color: white;
        }

        .platform-description {
          color: #6b7280;
          line-height: 1.7;
          font-size: 15px;
          margin-bottom: 20px;
        }

        .platform-card.hovered .platform-description {
          color: rgba(255, 255, 255, 0.9);
        }

        .platform-features {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 24px;
        }

        .platform-feature-tag {
          padding: 6px 14px;
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
          border-radius: 12px;
          font-size: 13px;
          font-weight: 600;
        }

        .platform-card.hovered .platform-feature-tag {
          background: rgba(255, 255, 255, 0.2);
          color: white;
        }

        .platform-cta {
          color: #667eea;
          font-weight: 700;
          font-size: 15px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .platform-card.hovered .platform-cta {
          color: white;
        }

        .platform-cta span {
          font-size: 20px;
        }

        /* Testimonials Grid */
        .testimonials-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 32px;
        }

        .testimonial-card {
          padding: 40px;
          background: white;
          border-radius: 24px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
          border: 1px solid #f3f4f6;
          transition: all 0.3s;
        }

        .testimonial-card:hover {
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
          transform: translateY(-4px);
        }

        .testimonial-stars {
          display: flex;
          gap: 4px;
          margin-bottom: 20px;
          color: #fbbf24;
          font-size: 20px;
        }

        .testimonial-content {
          color: #374151;
          line-height: 1.8;
          font-size: 16px;
          margin-bottom: 24px;
          font-style: italic;
        }

        .testimonial-author {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .author-image {
          width: 56px;
          height: 56px;
          border-radius: 50%;
          object-fit: cover;
        }

        .author-name {
          font-weight: 700;
          color: #1a1a1a;
          font-size: 16px;
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