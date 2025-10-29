import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Header from '../quickpage/Header';

const FeaturesShowcase = () => {
  const [activeFeature, setActiveFeature] = useState(0);

  const uniqueFeatures = [
    {
      icon: '🧠',
      title: 'Human-Like AI Content',
      description: 'Our AI generates content that sounds 100% human. No robotic text, no detection.',
      color: '#8b5cf6',
      details: [
        '95%+ human authenticity score',
        'Platform-specific writing styles',
        'Contextual awareness',
        'Natural conversation flow'
      ],
      benefit: 'Never get flagged as bot content'
    },
    {
      icon: '🎯',
      title: 'Smart Engagement Predictor',
      description: 'AI predicts which posts will go viral before you publish them.',
      color: '#f59e0b',
      details: [
        'Engagement score prediction',
        'Best time-to-post analysis',
        'Trending topic integration',
        'Hashtag effectiveness scoring'
      ],
      benefit: '3x higher engagement rates'
    },
    {
      icon: '🔄',
      title: 'Cross-Platform Syncing',
      description: 'Post once, distribute everywhere. Automatically adapted for each platform.',
      color: '#06b6d4',
      details: [
        'Auto-format for each platform',
        'Platform-specific optimization',
        'Smart content repurposing',
        'Unified analytics dashboard'
      ],
      benefit: 'Save 15+ hours per week'
    },
    {
      icon: '💬',
      title: 'AI Comment Responder',
      description: 'Automatically reply to comments with context-aware, personalized responses.',
      color: '#10b981',
      details: [
        'Sentiment analysis',
        'Brand voice matching',
        'Auto-moderation',
        'Multi-language support'
      ],
      benefit: '10x faster community management'
    },
    {
      icon: '📊',
      title: 'Competitor Intelligence',
      description: 'Track competitors\' strategies and get alerts when they post winning content.',
      color: '#ef4444',
      details: [
        'Real-time competitor tracking',
        'Content gap analysis',
        'Strategy recommendations',
        'Trend forecasting'
      ],
      benefit: 'Stay ahead of competition'
    },
    {
      icon: '🎨',
      title: 'AI Image Generator',
      description: 'Generate stunning, unique images for every post. No stock photos needed.',
      color: '#ec4899',
      details: [
        'Custom brand styles',
        'Text-to-image generation',
        'Auto-resizing for platforms',
        'Watermark protection'
      ],
      benefit: 'Unlimited unique visuals'
    }
  ];

  const platforms = [
    {
      name: 'Reddit',
      emoji: '🔴',
      uniqueFeature: 'Karma Builder AI',
      description: 'Automatically builds karma by finding and answering relevant questions in your niche',
      stats: { engagement: '+250%', time: '20 hrs/week', automation: '95%' }
    },
    {
      name: 'Facebook',
      emoji: '📘',
      uniqueFeature: 'Multi-Page Orchestrator',
      description: 'Manage unlimited Facebook pages from one dashboard with AI-coordinated campaigns',
      stats: { engagement: '+180%', time: '18 hrs/week', automation: '92%' }
    },
    {
      name: 'Instagram',
      emoji: '📸',
      uniqueFeature: 'Story AI Director',
      description: 'Creates complete story sequences with trending templates and interactive elements',
      stats: { engagement: '+320%', time: '12 hrs/week', automation: '88%' }
    },
    {
      name: 'YouTube',
      emoji: '📺',
      uniqueFeature: 'SEO Script Master',
      description: 'Generates viral video scripts optimized for YouTube algorithm and viewer retention',
      stats: { engagement: '+400%', time: '25 hrs/week', automation: '90%' }
    },
    {
      name: 'WhatsApp',
      emoji: '💬',
      uniqueFeature: 'Smart Broadcast Engine',
      description: 'Personalized mass messaging with AI timing and segmentation for max open rates',
      stats: { engagement: '+150%', time: '10 hrs/week', automation: '85%' }
    }
  ];

  const comparisons = [
    {
      feature: 'Human-Like AI Content',
      competitors: 'Basic templates',
      velocityPost: 'Advanced neural AI',
      icon: '🤖'
    },
    {
      feature: 'Cross-Platform Posting',
      competitors: 'Manual adaptation',
      velocityPost: 'Auto-optimized',
      icon: '🔄'
    },
    {
      feature: 'Engagement Prediction',
      competitors: 'Not available',
      velocityPost: 'AI-powered insights',
      icon: '📈'
    },
    {
      feature: 'Auto-Reply System',
      competitors: 'Basic chatbots',
      velocityPost: 'Context-aware AI',
      icon: '💬'
    },
    {
      feature: 'Image Generation',
      competitors: 'Stock photos only',
      velocityPost: 'Unlimited AI images',
      icon: '🎨'
    },
    {
      feature: 'Competitor Tracking',
      competitors: 'Manual monitoring',
      velocityPost: 'Real-time alerts',
      icon: '🔍'
    }
  ];

  return (
    <div className="features-showcase-page">
      <Header />
      
      <div className="fs-container">
        {/* Hero Section */}
        <section className="fs-hero">
          <div className="fs-hero-badge">
            <span className="badge-sparkle">✨</span>
            Unique Features You Won't Find Anywhere Else
          </div>
          
          <h1 className="fs-hero-title">
            Social Media Automation
            <span className="fs-gradient-text"> Reimagined</span>
          </h1>
          
          <p className="fs-hero-subtitle">
            We're not just another scheduling tool. VelocityPost uses cutting-edge AI 
            to make you look like a social media genius - without the effort.
          </p>

          <div className="fs-hero-stats">
            <div className="hero-stat-card">
              <div className="stat-icon">🚀</div>
              <div className="stat-number">300%</div>
              <div className="stat-label">More Engagement</div>
            </div>
            <div className="hero-stat-card">
              <div className="stat-icon">⏰</div>
              <div className="stat-number">20+ hrs</div>
              <div className="stat-label">Saved Weekly</div>
            </div>
            <div className="hero-stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-number">99.8%</div>
              <div className="stat-label">Uptime</div>
            </div>
          </div>
        </section>

        {/* Unique Features Grid */}
        <section className="fs-unique-features">
          <h2 className="fs-section-title">What Makes Us Different</h2>
          
          <div className="unique-features-grid">
            {uniqueFeatures.map((feature, idx) => (
              <div 
                key={idx}
                className="unique-feature-card"
                style={{ '--feature-color': feature.color }}
                onMouseEnter={() => setActiveFeature(idx)}
              >
                <div className="feature-icon-bg">
                  <span className="feature-icon">{feature.icon}</span>
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
                
                <div className="feature-details">
                  {feature.details.map((detail, dIdx) => (
                    <div key={dIdx} className="feature-detail-item">
                      <span className="detail-check">✓</span>
                      <span className="detail-text">{detail}</span>
                    </div>
                  ))}
                </div>

                <div className="feature-benefit">
                  <span className="benefit-icon">🎯</span>
                  <span className="benefit-text">{feature.benefit}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Platform-Specific Features */}
        <section className="fs-platform-features">
          <h2 className="fs-section-title">Platform-Specific Superpowers</h2>
          <p className="fs-section-subtitle">
            Each platform gets its own AI-powered automation tailored to its unique algorithm
          </p>
          
          <div className="platform-features-grid">
            {platforms.map((platform, idx) => (
              <div key={idx} className="platform-feature-card">
                <div className="platform-emoji-large">{platform.emoji}</div>
                <h3 className="platform-feature-title">{platform.name}</h3>
                <div className="unique-feature-badge">
                  <span className="badge-icon">⚡</span>
                  {platform.uniqueFeature}
                </div>
                <p className="platform-feature-description">{platform.description}</p>
                
                <div className="platform-stats">
                  <div className="platform-stat">
                    <div className="platform-stat-label">Engagement</div>
                    <div className="platform-stat-value">{platform.stats.engagement}</div>
                  </div>
                  <div className="platform-stat">
                    <div className="platform-stat-label">Time Saved</div>
                    <div className="platform-stat-value">{platform.stats.time}</div>
                  </div>
                  <div className="platform-stat">
                    <div className="platform-stat-label">Automation</div>
                    <div className="platform-stat-value">{platform.stats.automation}</div>
                  </div>
                </div>

                <Link 
                  to="/register" 
                  className="platform-feature-cta"
                >
                  Try {platform.name} Automation →
                </Link>
              </div>
            ))}
          </div>
        </section>

        {/* Comparison Table */}
        <section className="fs-comparison">
          <h2 className="fs-section-title">VelocityPost vs Others</h2>
          <p className="fs-section-subtitle">
            See why thousands choose us over traditional tools
          </p>
          
          <div className="comparison-table">
            <div className="comparison-header">
              <div className="comparison-col">Feature</div>
              <div className="comparison-col">Other Tools</div>
              <div className="comparison-col highlight">VelocityPost</div>
            </div>
            
            {comparisons.map((item, idx) => (
              <div key={idx} className="comparison-row">
                <div className="comparison-col feature-col">
                  <span className="comparison-icon">{item.icon}</span>
                  {item.feature}
                </div>
                <div className="comparison-col competitor-col">
                  <span className="cross-icon">✗</span>
                  {item.competitors}
                </div>
                <div className="comparison-col velocity-col">
                  <span className="check-icon">✓</span>
                  {item.velocityPost}
                </div>
              </div>
            ))}
          </div>

          <div className="comparison-cta">
            <p className="comparison-cta-text">
              Ready to experience the difference?
            </p>
            <Link to="/register" className="comparison-cta-btn">
              Start Free Trial - No Credit Card Required
            </Link>
          </div>
        </section>

        {/* Live Demo Section */}
        <section className="fs-demo">
          <div className="demo-container">
            <div className="demo-text-content">
              <h2 className="demo-title">See It In Action</h2>
              <p className="demo-description">
                Watch how our AI generates human-like content, predicts engagement, 
                and automates your entire social media strategy in real-time.
              </p>
              <div className="demo-features">
                <div className="demo-feature-item">
                  <span className="demo-feature-icon">⚡</span>
                  <span className="demo-feature-text">Live content generation</span>
                </div>
                <div className="demo-feature-item">
                  <span className="demo-feature-icon">🎯</span>
                  <span className="demo-feature-text">Engagement predictions</span>
                </div>
                <div className="demo-feature-item">
                  <span className="demo-feature-icon">🚀</span>
                  <span className="demo-feature-text">Multi-platform automation</span>
                </div>
              </div>
              <Link to="/register" className="demo-cta-btn">
                Start Your Free Trial
              </Link>
            </div>
            <div className="demo-visual">
              <div className="demo-screen">
                <div className="demo-screen-header">
                  <div className="screen-dots">
                    <span className="dot red"></span>
                    <span className="dot yellow"></span>
                    <span className="dot green"></span>
                  </div>
                  <div className="screen-title">AI Content Generator</div>
                </div>
                <div className="demo-screen-content">
                  <div className="demo-typing-animation">
                    <div className="typing-line">Generating post for Instagram...</div>
                    <div className="typing-line">Analyzing trending topics...</div>
                    <div className="typing-line">Creating engaging caption...</div>
                    <div className="typing-line success">✓ Ready to post!</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="fs-final-cta">
          <div className="final-cta-content">
            <h2 className="final-cta-title">Ready to 10x Your Social Media?</h2>
            <p className="final-cta-text">
              Join 50,000+ users who've transformed their social media presence with VelocityPost
            </p>
            <div className="final-cta-buttons">
              <Link to="/register" className="final-cta-primary">
                Start Free Trial
                <span className="cta-arrow">→</span>
              </Link>
              <Link to="/how-to-connect" className="final-cta-secondary">
                Learn How to Connect
              </Link>
            </div>
            <p className="final-cta-note">
              ✓ No credit card required • ✓ Cancel anytime • ✓ Full feature access
            </p>
          </div>
        </section>
      </div>

      <style>{`
        .features-showcase-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
          padding-top: 80px;
        }

        .fs-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 24px;
        }

        /* Hero Section */
        .fs-hero {
          text-align: center;
          padding: 80px 20px 60px;
          animation: fadeInUp 0.8s ease-out;
        }

        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .fs-hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: linear-gradient(135deg, #8b5cf6, #7c3aed);
          color: white;
          padding: 12px 28px;
          border-radius: 50px;
          font-size: 14px;
          font-weight: 700;
          margin-bottom: 24px;
          box-shadow: 0 4px 20px rgba(139, 92, 246, 0.3);
          animation: slideDown 0.6s ease-out;
        }

        @keyframes slideDown {
          from { transform: translateY(-30px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }

        .badge-sparkle {
          font-size: 18px;
          animation: sparkle 2s ease-in-out infinite;
        }

        @keyframes sparkle {
          0%, 100% { transform: scale(1) rotate(0deg); }
          50% { transform: scale(1.2) rotate(180deg); }
        }

        .fs-hero-title {
          font-size: clamp(36px, 6vw, 60px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 24px;
          line-height: 1.1;
        }

        .fs-gradient-text {
          background: linear-gradient(135deg, #0ea5e9, #8b5cf6);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .fs-hero-subtitle {
          font-size: clamp(16px, 3vw, 20px);
          color: #64748b;
          max-width: 750px;
          margin: 0 auto 48px;
          line-height: 1.7;
        }

        .fs-hero-stats {
          display: flex;
          justify-content: center;
          gap: 32px;
          flex-wrap: wrap;
        }

        .hero-stat-card {
          background: white;
          padding: 24px 32px;
          border-radius: 16px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
          text-align: center;
          transition: all 0.3s ease;
          animation: scaleIn 0.5s ease-out backwards;
        }

        .hero-stat-card:nth-child(1) { animation-delay: 0.1s; }
        .hero-stat-card:nth-child(2) { animation-delay: 0.2s; }
        .hero-stat-card:nth-child(3) { animation-delay: 0.3s; }

        @keyframes scaleIn {
          from { transform: scale(0); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }

        .hero-stat-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 12px 48px rgba(0, 0, 0, 0.12);
        }

        .stat-icon {
          font-size: 36px;
          margin-bottom: 12px;
        }

        .stat-number {
          font-size: 32px;
          font-weight: 900;
          color: #0ea5e9;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #64748b;
          font-weight: 600;
        }

        /* Unique Features */
        .fs-unique-features {
          padding: 80px 20px;
        }

        .fs-section-title {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: #111827;
          text-align: center;
          margin-bottom: 20px;
        }

        .fs-section-subtitle {
          font-size: clamp(16px, 3vw, 18px);
          color: #64748b;
          text-align: center;
          max-width: 700px;
          margin: 0 auto 48px;
          line-height: 1.6;
        }

        .unique-features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 32px;
          margin-top: 48px;
        }

        .unique-feature-card {
          background: white;
          padding: 36px;
          border-radius: 20px;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          border: 2px solid transparent;
          position: relative;
          overflow: hidden;
        }

        .unique-feature-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: var(--feature-color);
          transform: scaleX(0);
          transition: transform 0.4s ease;
        }

        .unique-feature-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
          border-color: var(--feature-color);
        }

        .unique-feature-card:hover::before {
          transform: scaleX(1);
        }

        .feature-icon-bg {
          width: 72px;
          height: 72px;
          border-radius: 18px;
          background: linear-gradient(135deg, var(--feature-color), var(--feature-color));
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 20px;
          opacity: 0.1;
          transition: all 0.3s ease;
          position: relative;
        }

        .unique-feature-card:hover .feature-icon-bg {
          opacity: 1;
          transform: rotate(10deg) scale(1.1);
        }

        .feature-icon {
          font-size: 36px;
          position: absolute;
          filter: grayscale(1);
        }

        .unique-feature-card:hover .feature-icon {
          filter: grayscale(0);
        }

        .feature-title {
          font-size: 22px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 12px;
        }

        .feature-description {
          font-size: 15px;
          color: #64748b;
          line-height: 1.7;
          margin-bottom: 20px;
        }

        .feature-details {
          margin-bottom: 20px;
        }

        .feature-detail-item {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
        }

        .detail-check {
          color: #10b981;
          font-weight: 900;
          font-size: 16px;
        }

        .detail-text {
          font-size: 14px;
          color: #64748b;
        }

        .feature-benefit {
          display: flex;
          align-items: center;
          gap: 10px;
          background: #f0f9ff;
          padding: 12px 16px;
          border-radius: 10px;
          border-left: 3px solid var(--feature-color);
        }

        .benefit-icon {
          font-size: 18px;
        }

        .benefit-text {
          font-size: 14px;
          font-weight: 700;
          color: #111827;
        }

        /* Platform Features */
        .fs-platform-features {
          padding: 80px 20px;
          background: white;
          border-radius: 40px;
          margin: 40px 0;
        }

        .platform-features-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 32px;
          margin-top: 48px;
        }

        .platform-feature-card {
          background: linear-gradient(135deg, #f8fafc, #f1f5f9);
          padding: 36px;
          border-radius: 20px;
          text-align: center;
          transition: all 0.3s ease;
          border: 2px solid transparent;
        }

        .platform-feature-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
          background: white;
          border-color: #0ea5e9;
        }

        .platform-emoji-large {
          font-size: 64px;
          margin-bottom: 16px;
        }

        .platform-feature-title {
          font-size: 26px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 16px;
        }

        .unique-feature-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 700;
          margin-bottom: 16px;
        }

        .badge-icon {
          font-size: 14px;
        }

        .platform-feature-description {
          font-size: 15px;
          color: #64748b;
          line-height: 1.7;
          margin-bottom: 24px;
        }

        .platform-stats {
          display: flex;
          justify-content: space-around;
          margin-bottom: 24px;
          padding: 20px;
          background: white;
          border-radius: 12px;
        }

        .platform-stat {
          text-align: center;
        }

        .platform-stat-label {
          font-size: 12px;
          color: #64748b;
          font-weight: 600;
          margin-bottom: 6px;
        }

        .platform-stat-value {
          font-size: 20px;
          font-weight: 900;
          color: #0ea5e9;
        }

        .platform-feature-cta {
          display: block;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          padding: 14px 24px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 15px;
          transition: all 0.3s ease;
        }

        .platform-feature-cta:hover {
          transform: scale(1.02);
          box-shadow: 0 8px 24px rgba(14, 165, 233, 0.4);
        }

        /* Comparison Table */
        .fs-comparison {
          padding: 80px 20px;
        }

        .comparison-table {
          max-width: 900px;
          margin: 0 auto 40px;
          background: white;
          border-radius: 20px;
          overflow: hidden;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        }

        .comparison-header {
          display: grid;
          grid-template-columns: 2fr 1.5fr 1.5fr;
          background: linear-gradient(135deg, #1e293b, #334155);
          color: white;
          font-weight: 700;
          font-size: 16px;
        }

        .comparison-col {
          padding: 20px;
          text-align: center;
        }

        .comparison-col.highlight {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        }

        .comparison-row {
          display: grid;
          grid-template-columns: 2fr 1.5fr 1.5fr;
          border-bottom: 1px solid #e5e7eb;
        }

        .comparison-row:last-child {
          border-bottom: none;
        }

        .comparison-row:hover {
          background: #f8fafc;
        }

        .feature-col {
          text-align: left;
          font-weight: 600;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .comparison-icon {
          font-size: 24px;
        }

        .competitor-col {
          color: #94a3b8;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .velocity-col {
          color: #0ea5e9;
          font-weight: 700;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .cross-icon {
          color: #ef4444;
          font-size: 18px;
          font-weight: 900;
        }

        .check-icon {
          color: #10b981;
          font-size: 18px;
          font-weight: 900;
        }

        .comparison-cta {
          text-align: center;
        }

        .comparison-cta-text {
          font-size: 20px;
          font-weight: 600;
          color: #111827;
          margin-bottom: 20px;
        }

        .comparison-cta-btn {
          display: inline-block;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          padding: 16px 40px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s ease;
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        .comparison-cta-btn:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
        }

        /* Demo Section */
        .fs-demo {
          padding: 80px 20px;
          background: linear-gradient(135deg, #1e293b, #334155);
          border-radius: 40px;
          margin: 40px 0;
        }

        .demo-container {
          max-width: 1100px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 48px;
          align-items: center;
        }

        .demo-title {
          font-size: clamp(32px, 4vw, 44px);
          font-weight: 900;
          color: white;
          margin-bottom: 20px;
        }

        .demo-description {
          font-size: 18px;
          color: #cbd5e1;
          line-height: 1.7;
          margin-bottom: 32px;
        }

        .demo-features {
          margin-bottom: 32px;
        }

        .demo-feature-item {
          display: flex;
          align-items: center;
          gap: 12px;
          color: white;
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 16px;
        }

        .demo-feature-icon {
          font-size: 24px;
        }

        .demo-cta-btn {
          display: inline-block;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          padding: 16px 40px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s ease;
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        .demo-cta-btn:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
        }

        .demo-screen {
          background: #0f172a;
          border-radius: 16px;
          overflow: hidden;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }

        .demo-screen-header {
          background: #1e293b;
          padding: 12px 16px;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .screen-dots {
          display: flex;
          gap: 6px;
        }

        .dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .dot.red { background: #ef4444; }
        .dot.yellow { background: #f59e0b; }
        .dot.green { background: #10b981; }

        .screen-title {
          color: #cbd5e1;
          font-size: 14px;
          font-weight: 600;
        }

        .demo-screen-content {
          padding: 24px;
          min-height: 200px;
        }

        .demo-typing-animation {
          font-family: 'Courier New', monospace;
        }

        .typing-line {
          color: #cbd5e1;
          font-size: 14px;
          margin-bottom: 16px;
          animation: typing 2s steps(30) infinite;
        }

        @keyframes typing {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        .typing-line.success {
          color: #10b981;
          font-weight: 700;
        }

        /* Final CTA */
        .fs-final-cta {
          padding: 100px 20px;
          text-align: center;
        }

        .final-cta-title {
          font-size: clamp(32px, 5vw, 52px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 20px;
        }

        .final-cta-text {
          font-size: 20px;
          color: #64748b;
          margin-bottom: 40px;
        }

        .final-cta-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 24px;
        }

        .final-cta-primary,
        .final-cta-secondary {
          padding: 18px 48px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 18px;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 10px;
        }

        .final-cta-primary {
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          color: white;
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        .final-cta-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
        }

        .cta-arrow {
          font-size: 24px;
          transition: transform 0.3s ease;
        }

        .final-cta-primary:hover .cta-arrow {
          transform: translateX(5px);
        }

        .final-cta-secondary {
          background: white;
          color: #0ea5e9;
          border: 2px solid #0ea5e9;
        }

        .final-cta-secondary:hover {
          background: #f0f9ff;
          transform: translateY(-3px);
        }

        .final-cta-note {
          font-size: 15px;
          color: #64748b;
          font-weight: 600;
        }

        /* Responsive */
        @media (max-width: 768px) {
          .fs-hero-stats {
            flex-direction: column;
            align-items: center;
          }

          .unique-features-grid,
          .platform-features-grid {
            grid-template-columns: 1fr;
          }

          .comparison-header,
          .comparison-row {
            grid-template-columns: 1.5fr 1fr 1fr;
            font-size: 13px;
          }

          .comparison-col {
            padding: 16px 8px;
          }

          .demo-container {
            grid-template-columns: 1fr;
          }

          .final-cta-buttons {
            flex-direction: column;
          }

          .final-cta-primary,
          .final-cta-secondary {
            width: 100%;
          }
        }

        @media (max-width: 480px) {
          .comparison-table {
            font-size: 12px;
          }

          .comparison-icon {
            font-size: 18px;
          }
        }
      `}</style>
    </div>
  );
};

export default FeaturesShowcase;