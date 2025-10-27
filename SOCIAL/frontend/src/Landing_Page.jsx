// // import React, { useState, useEffect } from 'react';
// // import { Link } from 'react-router-dom';
// // import { useAuth } from './quickpage/AuthContext';

// // const Landing_Page = () => {
// //   const { isAuthenticated } = useAuth();
// //   const [activeFeature, setActiveFeature] = useState(0);
// //   const [hoveredPlatform, setHoveredPlatform] = useState(null);
// //   const [scrolled, setScrolled] = useState(false);

// //   useEffect(() => {
// //     const handleScroll = () => {
// //       setScrolled(window.scrollY > 50);
// //     };
// //     window.addEventListener('scroll', handleScroll);
// //     return () => window.removeEventListener('scroll', handleScroll);
// //   }, []);

// //   useEffect(() => {
// //     const interval = setInterval(() => {
// //       setActiveFeature((prev) => (prev + 1) % 4);
// //     }, 5000);
// //     return () => clearInterval(interval);
// //   }, []);

// //   const platforms = [
// //     { 
// //       name: 'Facebook', 
// //       emoji: '📘', 
// //       route: '/facebook-instagram', 
// //       features: ['AI Content Generation', 'Multi-Page Management', 'Smart Scheduling', 'Advanced Analytics'],
// //       description: 'Automate your Facebook presence with AI-powered content creation and intelligent scheduling.'
// //     },
// //     { 
// //       name: 'Instagram', 
// //       emoji: '📸', 
// //       route: '/instagram', 
// //       features: ['AI Image Generation', 'Smart Hashtags', 'Story Automation', 'Engagement Boost'],
// //       description: 'Create stunning Instagram content automatically with AI-powered images and captions.'
// //     },
// //     { 
// //       name: 'WhatsApp', 
// //       emoji: '💬', 
// //       route: '/whatsapp', 
// //       features: ['Auto Reply', 'Broadcast Messages', 'Templates', 'Chat Analytics'],
// //       description: 'Streamline your WhatsApp communication with automated responses and broadcast capabilities.'
// //     },
// //     { 
// //       name: 'YouTube', 
// //       emoji: '📺', 
// //       route: '/youtube', 
// //       features: ['AI Script Writing', 'Auto Upload', 'SEO Optimization', 'Shorts Creation'],
// //       description: 'Grow your YouTube channel with AI-generated scripts and automated video uploads.'
// //     },
// //     { 
// //       name: 'Reddit', 
// //       emoji: '🔴', 
// //       route: '/reddit-auto', 
// //       features: ['Auto Posting', 'Smart Replies', 'Karma Building', 'Multi-Subreddit'],
// //       description: 'Build your Reddit presence with intelligent posting and automated engagement.'
// //     }
// //   ];

// //   const features = [
// //     {
// //       title: 'AI-Powered Content',
// //       description: 'Generate engaging posts, captions, and images automatically with advanced AI',
// //       icon: '🤖'
// //     },
// //     {
// //       title: 'Smart Scheduling',
// //       description: 'Post at optimal times for maximum engagement across all platforms',
// //       icon: '⚡'
// //     },
// //     {
// //       title: 'Analytics Dashboard',
// //       description: 'Track performance and optimize your strategy with real-time insights',
// //       icon: '📊'
// //     },
// //     {
// //       title: 'Multi-Platform',
// //       description: 'Manage all your social media accounts from one unified dashboard',
// //       icon: '🎯'
// //     }
// //   ];

// //   const testimonials = [
// //     {
// //       name: 'Sarah Johnson',
// //       role: 'Marketing Director',
// //       company: 'TechCorp',
// //       content: 'VelocityPost has transformed our social media strategy. We\'ve seen a 300% increase in engagement and saved 20 hours per week.',
// //       image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop',
// //       rating: 5
// //     },
// //     {
// //       name: 'Michael Chen',
// //       role: 'Content Creator',
// //       company: 'Digital Agency',
// //       content: 'The AI content generation is incredible. It understands our brand voice perfectly and creates posts that resonate with our audience.',
// //       image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop',
// //       rating: 5
// //     },
// //     {
// //       name: 'Emily Rodriguez',
// //       role: 'Social Media Manager',
// //       company: 'E-commerce Brand',
// //       content: 'Managing 5 platforms used to be overwhelming. Now it\'s effortless. The automation features are game-changing.',
// //       image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop',
// //       rating: 5
// //     }
// //   ];

// //   const stats = [
// //     { value: '50K+', label: 'Active Users' },
// //     { value: '10M+', label: 'Posts Automated' },
// //     { value: '98%', label: 'Satisfaction Rate' },
// //     { value: '5x', label: 'Engagement Boost' }
// //   ];

// //   const scrollToSection = (sectionId) => {
// //     const element = document.getElementById(sectionId);
// //     if (element) {
// //       element.scrollIntoView({ behavior: 'smooth', block: 'start' });
// //     }
// //   };

// //   return (
// //     <div className="landing-page-container">
// //       {/* Header */}
// //       <header className={`landing-header ${scrolled ? 'scrolled' : ''}`}>
// //         <div className="landing-header-content">
// //           <Link to="/" className="landing-logo">
// //             <span className="logo-emoji">🚀</span>
// //             <span className="logo-text">VelocityPost</span>
// //           </Link>
          
// //           <nav className="landing-nav">
// //             <button onClick={() => scrollToSection('features')} className="nav-link">
// //               Features
// //             </button>
// //             <button onClick={() => scrollToSection('platforms')} className="nav-link">
// //               Platforms
// //             </button>
// //             <Link to="/pricing" className="nav-link">
// //               Pricing
// //             </Link>
// //             <Link to="/about" className="nav-link">
// //               About
// //             </Link>
// //             <Link to="/contact" className="nav-link">
// //               Contact
// //             </Link>
            
// //             {isAuthenticated ? (
// //               <Link to="/reddit-auto" className="nav-cta-button">
// //                 Dashboard
// //               </Link>
// //             ) : (
// //               <>
// //                 <Link to="/login" className="nav-link-secondary">Sign In</Link>
// //                 <Link to="/register" className="nav-cta-button">
// //                   Get Started
// //                 </Link>
// //               </>
// //             )}
// //           </nav>
// //         </div>
// //       </header>

// //       {/* Hero Section */}
// //       <section className="hero-section">
// //         <div className="hero-bg-animation">
// //           <div className="floating-shape shape-1"></div>
// //           <div className="floating-shape shape-2"></div>
// //           <div className="floating-shape shape-3"></div>
// //         </div>
        
// //         <div className="hero-content">
// //           <div className="hero-badge animate-slide-down">
// //             <span className="badge-icon">✨</span>
// //             New: AI-Powered Instagram Stories!
// //           </div>

// //           <h1 className="hero-title animate-slide-up">
// //             Automate Your<br />
// //             <span className="gradient-text">Social Media Magic</span>
// //           </h1>

// //           <p className="hero-subtitle animate-fade-in">
// //             AI-powered automation for Facebook, Instagram, WhatsApp, YouTube & Reddit. 
// //             Save 20+ hours weekly while boosting engagement by 300%.
// //           </p>

// //           <div className="hero-buttons animate-fade-in-delay">
// //             <Link to="/register" className="hero-cta-primary">
// //               <span>Start Free Trial</span>
// //               <span className="button-arrow">→</span>
// //             </Link>
// //             <button onClick={() => scrollToSection('platforms')} className="hero-cta-secondary">
// //               <span>Watch Demo</span>
// //               <span className="play-icon">▶</span>
// //             </button>
// //           </div>

// //           <div className="hero-stats">
// //             {stats.map((stat, idx) => (
// //               <div key={idx} className="stat-item animate-scale-in" style={{ animationDelay: `${idx * 0.1}s` }}>
// //                 <div className="stat-value">{stat.value}</div>
// //                 <div className="stat-label">{stat.label}</div>
// //               </div>
// //             ))}
// //           </div>
// //         </div>
// //       </section>

// //       {/* Features Section */}
// //       <section id="features" className="features-section">
// //         <div className="section-header">
// //           <h2 className="section-title">Powerful Features</h2>
// //           <p className="section-subtitle">
// //             Everything you need to dominate social media
// //           </p>
// //         </div>

// //         <div className="features-grid">
// //           {features.map((feature, idx) => (
// //             <div
// //               key={idx}
// //               className={`feature-card ${activeFeature === idx ? 'active' : ''}`}
// //               onMouseEnter={() => setActiveFeature(idx)}
// //             >
// //               <div className="feature-icon-wrapper">
// //                 <div className="feature-icon">{feature.icon}</div>
// //               </div>
// //               <h3 className="feature-title">{feature.title}</h3>
// //               <p className="feature-description">{feature.description}</p>
// //               <div className="feature-hover-line"></div>
// //             </div>
// //           ))}
// //         </div>
// //       </section>

// //       {/* Platforms Section */}
// //       <section id="platforms" className="platforms-section">
// //         <div className="section-header">
// //           <h2 className="section-title">Supported Platforms</h2>
// //           <p className="section-subtitle">
// //             One dashboard to rule them all
// //           </p>
// //         </div>

// //         <div className="platforms-grid">
// //           {platforms.map((platform, idx) => (
// //             <Link
// //               key={idx}
// //               to={platform.route}
// //               className="platform-card"
// //               onMouseEnter={() => setHoveredPlatform(idx)}
// //               onMouseLeave={() => setHoveredPlatform(null)}
// //             >
// //               <div className="platform-icon-bg">
// //                 <div className="platform-emoji">{platform.emoji}</div>
// //               </div>
// //               <h3 className="platform-name">{platform.name}</h3>
// //               <p className="platform-description">{platform.description}</p>
              
// //               <div className="platform-features">
// //                 {platform.features.map((feature, fIdx) => (
// //                   <span key={fIdx} className="platform-feature-tag">
// //                     <span className="tag-dot">•</span>
// //                     {feature}
// //                   </span>
// //                 ))}
// //               </div>
// //               <div className="platform-arrow">→</div>
// //             </Link>
// //           ))}
// //         </div>
// //       </section>

// //       {/* Testimonials Section */}
// //       <section id="testimonials" className="testimonials-section">
// //         <div className="section-header">
// //           <h2 className="section-title">Loved by Thousands</h2>
// //           <p className="section-subtitle">
// //             See what our users are saying
// //           </p>
// //         </div>

// //         <div className="testimonials-grid">
// //           {testimonials.map((testimonial, idx) => (
// //             <div key={idx} className="testimonial-card">
// //               <div className="testimonial-rating">
// //                 {'⭐'.repeat(testimonial.rating)}
// //               </div>
// //               <p className="testimonial-content">"{testimonial.content}"</p>
// //               <div className="testimonial-author">
// //                 <img
// //                   src={testimonial.image}
// //                   alt={testimonial.name}
// //                   className="author-image"
// //                 />
// //                 <div className="author-info">
// //                   <div className="author-name">{testimonial.name}</div>
// //                   <div className="author-role">
// //                     {testimonial.role} at {testimonial.company}
// //                   </div>
// //                 </div>
// //               </div>
// //             </div>
// //           ))}
// //         </div>
// //       </section>

// //       {/* CTA Section */}
// //       <section className="cta-section">
// //         <div className="cta-content">
// //           <h2 className="cta-title">Ready to Transform Your Social Media?</h2>
// //           <p className="cta-subtitle">
// //             Join 50,000+ users automating their social media success
// //           </p>
// //           <div className="cta-buttons">
// //             <Link to="/register" className="cta-button-primary">
// //               Start Free Trial
// //             </Link>
// //             <Link to="/contact" className="cta-button-secondary">
// //               Contact Sales
// //             </Link>
// //           </div>
// //           <p className="cta-note">No credit card required • Cancel anytime</p>
// //         </div>
// //       </section>

// //       {/* Footer */}
// //       <footer className="landing-footer">
// //         <div className="footer-content">
// //           <div className="footer-grid">
// //             <div className="footer-brand">
// //               <div className="footer-logo">
// //                 <span>🚀</span>
// //                 VelocityPost
// //               </div>
// //               <p className="footer-description">
// //                 AI-powered social media automation platform helping businesses save time and boost engagement.
// //               </p>
// //               <div className="footer-socials">
// //                 <a href="https://facebook.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">f</a>
// //                 <a href="https://twitter.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">𝕏</a>
// //                 <a href="https://instagram.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">📷</a>
// //                 <a href="https://linkedin.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">in</a>
// //               </div>
// //             </div>

// //             <div className="footer-column">
// //               <h4 className="footer-column-title">Product</h4>
// //               <div className="footer-links">
// //                 <Link to="/features" className="footer-link">Features</Link>
// //                 <Link to="/pricing" className="footer-link">Pricing</Link>
// //                 <Link to="/integrations" className="footer-link">Integrations</Link>
// //                 <Link to="/api" className="footer-link">API</Link>
// //               </div>
// //             </div>

// //             <div className="footer-column">
// //               <h4 className="footer-column-title">Company</h4>
// //               <div className="footer-links">
// //                 <Link to="/about" className="footer-link">About Us</Link>
// //                 <Link to="/careers" className="footer-link">Careers</Link>
// //                 <Link to="/blog" className="footer-link">Blog</Link>
// //                 <Link to="/contact" className="footer-link">Contact</Link>
// //               </div>
// //             </div>

// //             <div className="footer-column">
// //               <h4 className="footer-column-title">Support</h4>
// //               <div className="footer-links">
// //                 <Link to="/helpcenter" className="footer-link">Help Center</Link>
// //                 <Link to="/documentation" className="footer-link">Documentation</Link>
// //                 <Link to="/community" className="footer-link">Community</Link>
// //                 <Link to="/status" className="footer-link">Status</Link>
// //               </div>
// //             </div>

// //             <div className="footer-column">
// //               <h4 className="footer-column-title">Legal</h4>
// //               <div className="footer-links">
// //                 <Link to="/privacypolicy" className="footer-link">Privacy Policy</Link>
// //                 <Link to="/termsofservice" className="footer-link">Terms of Service</Link>
// //                 <Link to="/cookiepolicy" className="footer-link">Cookie Policy</Link>
// //               </div>
// //             </div>
// //           </div>

// //           <div className="footer-bottom">
// //             <p className="footer-copyright">
// //               © {new Date().getFullYear()} VelocityPost. All rights reserved.
// //             </p>
// //             <div className="footer-legal-links">
// //               <Link to="/privacypolicy" className="footer-legal-link">Privacy</Link>
// //               <Link to="/termsofservice" className="footer-legal-link">Terms</Link>
// //               <Link to="/cookiepolicy" className="footer-legal-link">Cookies</Link>
// //             </div>
// //           </div>
// //         </div>
// //       </footer>

// //       <style>{`
// //         * {
// //           margin: 0;
// //           padding: 0;
// //           box-sizing: border-box;
// //         }

// //         .landing-page-container {
// //           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
// //           overflow-x: hidden;
// //           background: #ffffff;
// //         }

// //         /* Animations */
// //         @keyframes slideDown {
// //           from {
// //             opacity: 0;
// //             transform: translateY(-30px);
// //           }
// //           to {
// //             opacity: 1;
// //             transform: translateY(0);
// //           }
// //         }

// //         @keyframes slideUp {
// //           from {
// //             opacity: 0;
// //             transform: translateY(30px);
// //           }
// //           to {
// //             opacity: 1;
// //             transform: translateY(0);
// //           }
// //         }

// //         @keyframes fadeIn {
// //           from {
// //             opacity: 0;
// //           }
// //           to {
// //             opacity: 1;
// //           }
// //         }

// //         @keyframes scaleIn {
// //           from {
// //             opacity: 0;
// //             transform: scale(0.8);
// //           }
// //           to {
// //             opacity: 1;
// //             transform: scale(1);
// //           }
// //         }

// //         @keyframes float {
// //           0%, 100% { transform: translate(0, 0) rotate(0deg); }
// //           25% { transform: translate(10px, -10px) rotate(5deg); }
// //           50% { transform: translate(-5px, 5px) rotate(-5deg); }
// //           75% { transform: translate(-10px, -5px) rotate(3deg); }
// //         }

// //         .animate-slide-down {
// //           animation: slideDown 0.8s ease-out;
// //         }

// //         .animate-slide-up {
// //           animation: slideUp 0.9s ease-out;
// //         }

// //         .animate-fade-in {
// //           animation: fadeIn 1s ease-out;
// //         }

// //         .animate-fade-in-delay {
// //           animation: fadeIn 1s ease-out 0.3s backwards;
// //         }

// //         .animate-scale-in {
// //           animation: scaleIn 0.6s ease-out backwards;
// //         }

// //         /* Header */
// //         .landing-header {
// //           position: fixed;
// //           top: 0;
// //           left: 0;
// //           right: 0;
// //           z-index: 1000;
// //           background: rgba(255, 255, 255, 0.95);
// //           backdrop-filter: blur(10px);
// //           transition: all 0.3s ease;
// //           padding: 16px 0;
// //           border-bottom: 1px solid transparent;
// //         }

// //         .landing-header.scrolled {
// //           background: rgba(255, 255, 255, 0.98);
// //           box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
// //           border-bottom-color: #e5e7eb;
// //         }

// //         .landing-header-content {
// //           max-width: 1400px;
// //           margin: 0 auto;
// //           padding: 0 24px;
// //           display: flex;
// //           justify-content: space-between;
// //           align-items: center;
// //         }

// //         .landing-logo {
// //           display: flex;
// //           align-items: center;
// //           gap: 10px;
// //           text-decoration: none;
// //           color: #111827;
// //           font-weight: 800;
// //           font-size: 22px;
// //           transition: transform 0.3s ease;
// //         }

// //         .landing-logo:hover {
// //           transform: scale(1.05);
// //         }

// //         .logo-emoji {
// //           font-size: 26px;
// //         }

// //         .landing-nav {
// //           display: flex;
// //           align-items: center;
// //           gap: 8px;
// //           flex-wrap: wrap;
// //         }

// //         .nav-link,
// //         .nav-link-secondary {
// //           background: none;
// //           border: none;
// //           color: #4b5563;
// //           font-size: 14px;
// //           font-weight: 600;
// //           cursor: pointer;
// //           text-decoration: none;
// //           padding: 8px 16px;
// //           border-radius: 8px;
// //           transition: all 0.2s ease;
// //         }

// //         .nav-link:hover,
// //         .nav-link-secondary:hover {
// //           color: #0ea5e9;
// //           background: #f0f9ff;
// //         }

// //         .nav-cta-button {
// //           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
// //           color: white;
// //           padding: 10px 24px;
// //           border-radius: 8px;
// //           text-decoration: none;
// //           font-weight: 700;
// //           font-size: 14px;
// //           transition: all 0.3s ease;
// //           box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
// //         }

// //         .nav-cta-button:hover {
// //           transform: translateY(-2px);
// //           box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
// //         }

// //         /* Hero Section */
// //         .hero-section {
// //           min-height: 100vh;
// //           display: flex;
// //           align-items: center;
// //           justify-content: center;
// //           padding: 140px 24px 80px;
// //           position: relative;
// //           overflow: hidden;
// //           background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
// //         }

// //         .hero-bg-animation {
// //           position: absolute;
// //           top: 0;
// //           left: 0;
// //           right: 0;
// //           bottom: 0;
// //           overflow: hidden;
// //         }

// //         .floating-shape {
// //           position: absolute;
// //           border-radius: 50%;
// //           filter: blur(60px);
// //           opacity: 0.4;
// //           animation: float 20s infinite ease-in-out;
// //         }

// //         .shape-1 {
// //           width: 400px;
// //           height: 400px;
// //           background: linear-gradient(135deg, #0ea5e9, #06b6d4);
// //           top: -100px;
// //           left: -100px;
// //         }

// //         .shape-2 {
// //           width: 300px;
// //           height: 300px;
// //           background: linear-gradient(135deg, #06b6d4, #0284c7);
// //           bottom: -50px;
// //           right: -50px;
// //           animation-delay: 5s;
// //         }

// //         .shape-3 {
// //           width: 250px;
// //           height: 250px;
// //           background: linear-gradient(135deg, #0ea5e9, #38bdf8);
// //           top: 50%;
// //           left: 50%;
// //           animation-delay: 10s;
// //         }

// //         .hero-content {
// //           max-width: 1000px;
// //           text-align: center;
// //           position: relative;
// //           z-index: 1;
// //         }

// //         .hero-badge {
// //           display: inline-flex;
// //           align-items: center;
// //           gap: 8px;
// //           background: white;
// //           padding: 10px 20px;
// //           border-radius: 50px;
// //           font-size: 14px;
// //           font-weight: 600;
// //           color: #0ea5e9;
// //           margin-bottom: 32px;
// //           box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
// //         }

// //         .badge-icon {
// //           font-size: 16px;
// //         }

// //         .hero-title {
// //           font-size: clamp(40px, 8vw, 72px);
// //           font-weight: 900;
// //           line-height: 1.1;
// //           margin-bottom: 24px;
// //           color: #111827;
// //           letter-spacing: -0.02em;
// //         }

// //         .gradient-text {
// //           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
// //           -webkit-background-clip: text;
// //           -webkit-text-fill-color: transparent;
// //           background-clip: text;
// //         }

// //         .hero-subtitle {
// //           font-size: clamp(16px, 3vw, 20px);
// //           color: #6b7280;
// //           max-width: 700px;
// //           margin: 0 auto 40px;
// //           line-height: 1.7;
// //         }

// //         .hero-buttons {
// //           display: flex;
// //           gap: 16px;
// //           justify-content: center;
// //           flex-wrap: wrap;
// //           margin-bottom: 60px;
// //         }

// //         .hero-cta-primary,
// //         .hero-cta-secondary {
// //           padding: 16px 32px;
// //           border-radius: 12px;
// //           text-decoration: none;
// //           font-weight: 700;
// //           font-size: 16px;
// //           transition: all 0.3s ease;
// //           display: inline-flex;
// //           align-items: center;
// //           gap: 8px;
// //           border: none;
// //           cursor: pointer;
// //           background: none;
// //         }

// //         .hero-cta-primary {
// //           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
// //           color: white;
// //           box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
// //         }

// //         .hero-cta-primary:hover {
// //           transform: translateY(-3px);
// //           box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
// //         }

// //         .hero-cta-secondary {
// //           background: white;
// //           color: #0ea5e9;
// //           border: 2px solid #0ea5e9;
// //         }

// //         .hero-cta-secondary:hover {
// //           background: #0ea5e9;
// //           color: white;
// //           transform: translateY(-3px);
// //         }

// //         .button-arrow,
// //         .play-icon {
// //           font-size: 18px;
// //           transition: transform 0.3s ease;
// //         }

// //         .hero-cta-primary:hover .button-arrow {
// //           transform: translateX(5px);
// //         }

// //         .hero-stats {
// //           display: grid;
// //           grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
// //           gap: 32px;
// //           max-width: 800px;
// //           margin: 0 auto;
// //         }

// //         .stat-item {
// //           text-align: center;
// //         }

// //         .stat-value {
// //           font-size: clamp(28px, 5vw, 42px);
// //           font-weight: 900;
// //           color: #0ea5e9;
// //           margin-bottom: 4px;
// //         }

// //         .stat-label {
// //           font-size: 13px;
// //           color: #6b7280;
// //           font-weight: 600;
// //           text-transform: uppercase;
// //           letter-spacing: 0.5px;
// //         }

// //         /* Features Section */
// //         .features-section {
// //           padding: 100px 24px;
// //           background: white;
// //         }

// //         .section-header {
// //           text-align: center;
// //           max-width: 800px;
// //           margin: 0 auto 64px;
// //         }

// //         .section-title {
// //           font-size: clamp(32px, 5vw, 48px);
// //           font-weight: 900;
// //           color: #111827;
// //           margin-bottom: 16px;
// //           letter-spacing: -0.02em;
// //         }

// //         .section-subtitle {
// //           font-size: clamp(16px, 3vw, 18px);
// //           color: #6b7280;
// //           line-height: 1.6;
// //         }

// //         .features-grid {
// //           max-width: 1200px;
// //           margin: 0 auto;
// //           display: grid;
// //           grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
// //           gap: 32px;
// //         }

// //         .feature-card {
// //           background: #f9fafb;
// //           padding: 36px 28px;
// //           border-radius: 16px;
// //           transition: all 0.3s ease;
// //           cursor: pointer;
// //           border: 2px solid transparent;
// //           position: relative;
// //           overflow: hidden;
// //         }

// //         .feature-card::before {
// //           content: '';
// //           position: absolute;
// //           top: 0;
// //           left: 0;
// //           right: 0;
// //           height: 4px;
// //           background: linear-gradient(90deg, #0ea5e9, #06b6d4);
// //           transform: scaleX(0);
// //           transition: transform 0.3s ease;
// //         }

// //         .feature-card:hover,
// //         .feature-card.active {
// //           background: white;
// //           border-color: #0ea5e9;
// //           box-shadow: 0 20px 60px rgba(14, 165, 233, 0.15);
// //           transform: translateY(-8px);
// //         }

// //         .feature-card:hover::before,
// //         .feature-card.active::before {
// //           transform: scaleX(1);
// //         }

// //         .feature-icon-wrapper {
// //           margin-bottom: 20px;
// //         }

// //         .feature-icon {
// //           font-size: 48px;
// //           display: inline-block;
// //           transition: transform 0.3s ease;
// //         }

// //         .feature-card:hover .feature-icon {
// //           transform: scale(1.1) rotate(5deg);
// //         }

// //         .feature-title {
// //           font-size: 22px;
// //           font-weight: 700;
// //           color: #111827;
// //           margin-bottom: 12px;
// //         }

// //         .feature-description {
// //           color: #6b7280;
// //           line-height: 1.7;
// //           font-size: 15px;
// //         }

// //         /* Platforms Section */
// //         .platforms-section {
// //           padding: 100px 24px;
// //           background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
// //         }

// //         .platforms-grid {
// //           max-width: 1200px;
// //           margin: 0 auto;
// //           display: grid;
// //           grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
// //           gap: 28px;
// //         }

// //         .platform-card {
// //           background: white;
// //           padding: 32px;
// //           border-radius: 20px;
// //           text-decoration: none;
// //           transition: all 0.3s ease;
// //           cursor: pointer;
// //           border: 2px solid transparent;
// //           display: flex;
// //           flex-direction: column;
// //           position: relative;
// //           overflow: hidden;
// //         }

// //         .platform-card::after {
// //           content: '';
// //           position: absolute;
// //           top: 0;
// //           left: 0;
// //           right: 0;
// //           bottom: 0;
// //           background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(6, 182, 212, 0.05));
// //           opacity: 0;
// //           transition: opacity 0.3s ease;
// //         }

// //         .platform-card:hover {
// //           border-color: #0ea5e9;
// //           transform: translateY(-10px);
// //           box-shadow: 0 25px 70px rgba(14, 165, 233, 0.2);
// //         }

// //         .platform-card:hover::after {
// //           opacity: 1;
// //         }

// //         .platform-icon-bg {
// //           width: 80px;
// //           height: 80px;
// //           background: linear-gradient(135deg, #0ea5e9, #06b6d4);
// //           border-radius: 20px;
// //           display: flex;
// //           align-items: center;
// //           justify-content: center;
// //           margin-bottom: 20px;
// //           position: relative;
// //           z-index: 1;
// //           transition: transform 0.3s ease;
// //         }

// //         .platform-card:hover .platform-icon-bg {
// //           transform: scale(1.1) rotate(5deg);
// //         }

// //         .platform-emoji {
// //           font-size: 48px;
// //         }

// //         .platform-name {
// //           font-size: 26px;
// //           font-weight: 700;
// //           color: #111827;
// //           margin-bottom: 12px;
// //           position: relative;
// //           z-index: 1;
// //         }

// //         .platform-description {
// //           color: #6b7280;
// //           line-height: 1.7;
// //           margin-bottom: 20px;
// //           flex-grow: 1;
// //           font-size: 15px;
// //           position: relative;
// //           z-index: 1;
// //         }

// //         .platform-features {
// //           display: flex;
// //           flex-direction: column;
// //           gap: 8px;
// //           position: relative;
// //           z-index: 1;
// //         }

// //         .platform-feature-tag {
// //           display: flex;
// //           align-items: center;
// //           gap: 8px;
// //           color: #0ea5e9;
// //           font-size: 13px;
// //           font-weight: 600;
// //         }

// //         .tag-dot {
// //           font-size: 20px;
// //         }

// //         .platform-arrow {
// //           position: absolute;
// //           bottom: 24px;
// //           right: 24px;
// //           font-size: 24px;
// //           color: #0ea5e9;
// //           opacity: 0;
// //           transform: translateX(-10px);
// //           transition: all 0.3s ease;
// //         }

// //         .platform-card:hover .platform-arrow {
// //           opacity: 1;
// //           transform: translateX(0);
// //         }

// //         /* Testimonials Section */
// //         .testimonials-section {
// //           padding: 100px 24px;
// //           background: white;
// //         }

// //         .testimonials-grid {
// //           max-width: 1200px;
// //           margin: 0 auto;
// //           display: grid;
// //           grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
// //           gap: 32px;
// //         }

// //         .testimonial-card {
// //           background: #f9fafb;
// //           padding: 36px;
// //           border-radius: 20px;
// //           transition: all 0.3s ease;
// //         }

// //         .testimonial-card:hover {
// //           background: white;
// //           box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
// //           transform: translateY(-8px);
// //         }

// //         .testimonial-rating {
// //           font-size: 18px;
// //           margin-bottom: 16px;
// //         }

// //         .testimonial-content {
// //           color: #111827;
// //           font-size: 16px;
// //           line-height: 1.7;
// //           margin-bottom: 24px;
// //           font-style: italic;
// //         }

// //         .testimonial-author {
// //           display: flex;
// //           align-items: center;
// //           gap: 16px;
// //         }

// //         .author-image {
// //           width: 56px;
// //           height: 56px;
// //           border-radius: 50%;
// //           object-fit: cover;
// //           border: 3px solid #0ea5e9;
// //         }

// //         .author-name {
// //           font-weight: 700;
// //           color: #111827;
// //           margin-bottom: 4px;
// //           font-size: 15px;
// //         }

// //         .author-role {
// //           color: #6b7280;
// //           font-size: 13px;
// //         }

// //         /* CTA Section */
// //         .cta-section {
// //           padding: 100px 24px;
// //           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
// //           position: relative;
// //           overflow: hidden;
// //         }

// //         .cta-content {
// //           max-width: 800px;
// //           margin: 0 auto;
// //           text-align: center;
// //           position: relative;
// //           z-index: 1;
// //         }

// //         .cta-title {
// //           font-size: clamp(32px, 5vw, 48px);
// //           font-weight: 900;
// //           color: white;
// //           margin-bottom: 20px;
// //           line-height: 1.2;
// //         }

// //         .cta-subtitle {
// //           font-size: clamp(16px, 3vw, 20px);
// //           color: rgba(255, 255, 255, 0.95);
// //           margin-bottom: 36px;
// //           line-height: 1.6;
// //         }

// //         .cta-buttons {
// //           display: flex;
// //           gap: 16px;
// //           justify-content: center;
// //           flex-wrap: wrap;
// //         }

// //         .cta-button-primary,
// //         .cta-button-secondary {
// //           padding: 16px 40px;
// //           border-radius: 12px;
// //           text-decoration: none;
// //           font-weight: 700;
// //           font-size: 16px;
// //           transition: all 0.3s ease;
// //         }

// //         .cta-button-primary {
// //           background: white;
// //           color: #0ea5e9;
// //           box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
// //         }

// //         .cta-button-primary:hover {
// //           transform: translateY(-3px) scale(1.05);
// //           box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
// //         }

// //         .cta-button-secondary {
// //           background: rgba(255, 255, 255, 0.15);
// //           backdrop-filter: blur(10px);
// //           color: white;
// //           border: 2px solid rgba(255, 255, 255, 0.3);
// //         }

// //         .cta-button-secondary:hover {
// //           background: rgba(255, 255, 255, 0.25);
// //           transform: translateY(-3px);
// //         }

// //         .cta-note {
// //           margin-top: 20px;
// //           color: rgba(255, 255, 255, 0.9);
// //           font-size: 14px;
// //         }

// //         /* Footer */
// //         .landing-footer {
// //           background: #111827;
// //           color: white;
// //           padding: 80px 24px 40px;
// //         }

// //         .footer-content {
// //           max-width: 1200px;
// //           margin: 0 auto;
// //         }

// //         .footer-grid {
// //           display: grid;
// //           grid-template-columns: 2fr repeat(4, 1fr);
// //           gap: 40px;
// //           margin-bottom: 48px;
// //         }

// //         .footer-logo {
// //           font-size: 24px;
// //           font-weight: 700;
// //           margin-bottom: 16px;
// //           display: flex;
// //           align-items: center;
// //           gap: 8px;
// //         }

// //         .footer-logo span {
// //           font-size: 28px;
// //         }

// //         .footer-description {
// //           color: #9ca3af;
// //           line-height: 1.6;
// //           margin-bottom: 20px;
// //           max-width: 320px;
// //           font-size: 14px;
// //         }

// //         .footer-socials {
// //           display: flex;
// //           gap: 12px;
// //         }

// //         .footer-social-link {
// //           width: 40px;
// //           height: 40px;
// //           border-radius: 50%;
// //           background: #1f2937;
// //           display: flex;
// //           align-items: center;
// //           justify-content: center;
// //           color: white;
// //           text-decoration: none;
// //           font-weight: 700;
// //           font-size: 14px;
// //           transition: all 0.3s ease;
// //         }

// //         .footer-social-link:hover {
// //           background: #0ea5e9;
// //           transform: translateY(-3px);
// //         }

// //         .footer-column-title {
// //           font-size: 14px;
// //           font-weight: 700;
// //           margin-bottom: 16px;
// //           text-transform: uppercase;
// //           letter-spacing: 1px;
// //           color: white;
// //         }

// //         .footer-links {
// //           display: flex;
// //           flex-direction: column;
// //           gap: 10px;
// //         }

// //         .footer-link {
// //           color: #9ca3af;
// //           text-decoration: none;
// //           font-size: 14px;
// //           transition: color 0.2s ease;
// //         }

// //         .footer-link:hover {
// //           color: #0ea5e9;
// //         }

// //         .footer-bottom {
// //           padding-top: 32px;
// //           border-top: 1px solid #1f2937;
// //           display: flex;
// //           justify-content: space-between;
// //           align-items: center;
// //           flex-wrap: wrap;
// //           gap: 16px;
// //         }

// //         .footer-copyright {
// //           color: #9ca3af;
// //           margin: 0;
// //           font-size: 14px;
// //         }

// //         .footer-legal-links {
// //           display: flex;
// //           gap: 20px;
// //           flex-wrap: wrap;
// //         }

// //         .footer-legal-link {
// //           color: #9ca3af;
// //           text-decoration: none;
// //           font-size: 14px;
// //           transition: color 0.2s ease;
// //         }

// //         .footer-legal-link:hover {
// //           color: #0ea5e9;
// //         }

// //         /* Responsive Design */
// //         @media (max-width: 1200px) {
// //           .footer-grid {
// //             grid-template-columns: repeat(3, 1fr);
// //           }

// //           .footer-brand {
// //             grid-column: span 3;
// //           }
// //         }

// //         @media (max-width: 768px) {
// //           .landing-nav {
// //             gap: 4px;
// //             justify-content: center;
// //           }

// //           .nav-link,
// //           .nav-link-secondary {
// //             padding: 6px 10px;
// //             font-size: 12px;
// //           }

// //           .nav-cta-button {
// //             padding: 8px 16px;
// //             font-size: 12px;
// //           }

// //           .hero-section {
// //             padding: 120px 20px 60px;
// //           }

// //           .hero-stats {
// //             grid-template-columns: repeat(2, 1fr);
// //             gap: 24px;
// //           }

// //           .features-grid,
// //           .platforms-grid,
// //           .testimonials-grid {
// //             grid-template-columns: 1fr;
// //           }

// //           .footer-grid {
// //             grid-template-columns: repeat(2, 1fr);
// //           }

// //           .footer-brand {
// //             grid-column: span 2;
// //           }

// //           .cta-buttons {
// //             flex-direction: column;
// //           }

// //           .cta-button-primary,
// //           .cta-button-secondary {
// //             width: 100%;
// //           }
// //         }

// //         @media (max-width: 480px) {
// //           .landing-header-content {
// //             padding: 0 16px;
// //           }

// //           .landing-nav {
// //             gap: 2px;
// //           }

// //           .nav-link,
// //           .nav-link-secondary {
// //             padding: 6px 8px;
// //             font-size: 11px;
// //           }

// //           .logo-text {
// //             font-size: 16px;
// //           }

// //           .footer-grid {
// //             grid-template-columns: 1fr;
// //           }

// //           .footer-brand {
// //             grid-column: span 1;
// //           }
// //         }

// //         html {
// //           scroll-behavior: smooth;
// //         }
// //       `}</style>
// //     </div>
// //   );
// // };

// // export default Landing_Page;

// import React, { useState, useEffect } from 'react';
// import { Link, Routes, Route, useLocation } from 'react-router-dom';
// import { useAuth } from './quickpage/AuthContext';

// // Import ALL footer pages
// import About from './footerpages/About';
// import Api from './footerpages/Api';
// import Blog from './footerpages/Blog';
// import Careers from './footerpages/Careers';
// import Community from './footerpages/Community';
// import Contact from './footerpages/Contact';
// import Cookiepolicy from './footerpages/Cookiepolicy';
// import Documentation from './footerpages/Documentation';
// import Features from './footerpages/Features';
// import Helpcenter from './footerpages/Helpcenter';
// import Integrations from './footerpages/Integrations';
// import Pricing from './footerpages/Pricing';
// import Privacypolicy from './footerpages/Privacypolicy';
// import Status from './footerpages/Status';
// import Termsofservice from './footerpages/Termsofservice';

// const Landing_Page = () => {
//   const { isAuthenticated } = useAuth();
//   const location = useLocation();
//   const [activeFeature, setActiveFeature] = useState(0);
//   const [hoveredPlatform, setHoveredPlatform] = useState(null);
//   const [scrolled, setScrolled] = useState(false);

//   useEffect(() => {
//     const handleScroll = () => {
//       setScrolled(window.scrollY > 50);
//     };
//     window.addEventListener('scroll', handleScroll);
//     return () => window.removeEventListener('scroll', handleScroll);
//   }, []);

//   useEffect(() => {
//     const interval = setInterval(() => {
//       setActiveFeature((prev) => (prev + 1) % 4);
//     }, 5000);
//     return () => clearInterval(interval);
//   }, []);

//   const platforms = [
//     { 
//       name: 'Facebook', 
//       emoji: '📘', 
//       route: '/facebook-instagram', 
//       features: ['AI Content Generation', 'Multi-Page Management', 'Smart Scheduling', 'Advanced Analytics'],
//       description: 'Automate your Facebook presence with AI-powered content creation and intelligent scheduling.'
//     },
//     { 
//       name: 'Instagram', 
//       emoji: '📸', 
//       route: '/instagram', 
//       features: ['AI Image Generation', 'Smart Hashtags', 'Story Automation', 'Engagement Boost'],
//       description: 'Create stunning Instagram content automatically with AI-powered images and captions.'
//     },
//     { 
//       name: 'WhatsApp', 
//       emoji: '💬', 
//       route: '/whatsapp', 
//       features: ['Auto Reply', 'Broadcast Messages', 'Templates', 'Chat Analytics'],
//       description: 'Streamline your WhatsApp communication with automated responses and broadcast capabilities.'
//     },
//     { 
//       name: 'YouTube', 
//       emoji: '📺', 
//       route: '/youtube', 
//       features: ['AI Script Writing', 'Auto Upload', 'SEO Optimization', 'Shorts Creation'],
//       description: 'Grow your YouTube channel with AI-generated scripts and automated video uploads.'
//     },
//     { 
//       name: 'Reddit', 
//       emoji: '🔴', 
//       route: '/reddit-auto', 
//       features: ['Auto Posting', 'Smart Replies', 'Karma Building', 'Multi-Subreddit'],
//       description: 'Build your Reddit presence with intelligent posting and automated engagement.'
//     }
//   ];

//   const features = [
//     {
//       title: 'AI-Powered Content',
//       description: 'Generate engaging posts, captions, and images automatically with advanced AI',
//       icon: '🤖'
//     },
//     {
//       title: 'Smart Scheduling',
//       description: 'Post at optimal times for maximum engagement across all platforms',
//       icon: '⚡'
//     },
//     {
//       title: 'Analytics Dashboard',
//       description: 'Track performance and optimize your strategy with real-time insights',
//       icon: '📊'
//     },
//     {
//       title: 'Multi-Platform',
//       description: 'Manage all your social media accounts from one unified dashboard',
//       icon: '🎯'
//     }
//   ];

//   const testimonials = [
//     {
//       name: 'Sarah Johnson',
//       role: 'Marketing Director',
//       company: 'TechCorp',
//       content: 'VelocityPost has transformed our social media strategy. We\'ve seen a 300% increase in engagement and saved 20 hours per week.',
//       image: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=200&h=200&fit=crop',
//       rating: 5
//     },
//     {
//       name: 'Michael Chen',
//       role: 'Content Creator',
//       company: 'Digital Agency',
//       content: 'The AI content generation is incredible. It understands our brand voice perfectly and creates posts that resonate with our audience.',
//       image: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop',
//       rating: 5
//     },
//     {
//       name: 'Emily Rodriguez',
//       role: 'Social Media Manager',
//       company: 'E-commerce Brand',
//       content: 'Managing 5 platforms used to be overwhelming. Now it\'s effortless. The automation features are game-changing.',
//       image: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=200&h=200&fit=crop',
//       rating: 5
//     }
//   ];

//   const stats = [
//     { value: '50K+', label: 'Active Users' },
//     { value: '10M+', label: 'Posts Automated' },
//     { value: '98%', label: 'Satisfaction Rate' },
//     { value: '5x', label: 'Engagement Boost' }
//   ];

//   const scrollToSection = (sectionId) => {
//     const element = document.getElementById(sectionId);
//     if (element) {
//       element.scrollIntoView({ behavior: 'smooth', block: 'start' });
//     }
//   };

//   // Check if we're on a footer page route
//   const isFooterPage = [
//     '/features', '/pricing', '/integrations', '/api',
//     '/about', '/careers', '/blog', '/contact',
//     '/helpcenter', '/documentation', '/community', '/status',
//     '/privacypolicy', '/termsofservice', '/cookiepolicy'
//   ].includes(location.pathname);

//   // If on footer page, render that page
//   if (isFooterPage) {
//     return (
//       <Routes>
//         <Route path="/features" element={<Features />} />
//         <Route path="/pricing" element={<Pricing />} />
//         <Route path="/integrations" element={<Integrations />} />
//         <Route path="/api" element={<Api />} />
//         <Route path="/about" element={<About />} />
//         <Route path="/careers" element={<Careers />} />
//         <Route path="/blog" element={<Blog />} />
//         <Route path="/contact" element={<Contact />} />
//         <Route path="/helpcenter" element={<Helpcenter />} />
//         <Route path="/documentation" element={<Documentation />} />
//         <Route path="/community" element={<Community />} />
//         <Route path="/status" element={<Status />} />
//         <Route path="/privacypolicy" element={<Privacypolicy />} />
//         <Route path="/termsofservice" element={<Termsofservice />} />
//         <Route path="/cookiepolicy" element={<Cookiepolicy />} />
//       </Routes>
//     );
//   }

//   // Otherwise render the landing page
//   return (
//     <div className="landing-page-container">
//       {/* Header */}
//       <header className={`landing-header ${scrolled ? 'scrolled' : ''}`}>
//         <div className="landing-header-content">
//           <Link to="/" className="landing-logo">
//             <span className="logo-emoji">🚀</span>
//             <span className="logo-text">VelocityPost</span>
//           </Link>
          
//           <nav className="landing-nav">
//             <button onClick={() => scrollToSection('features')} className="nav-link">
//               Features
//             </button>
//             <button onClick={() => scrollToSection('platforms')} className="nav-link">
//               Platforms
//             </button>
//             <Link to="/pricing" className="nav-link">
//               Pricing
//             </Link>
//             <Link to="/about" className="nav-link">
//               About
//             </Link>
//             <Link to="/contact" className="nav-link">
//               Contact
//             </Link>
            
//             {isAuthenticated ? (
//               <Link to="/reddit-auto" className="nav-cta-button">
//                 Dashboard
//               </Link>
//             ) : (
//               <>
//                 <Link to="/login" className="nav-link-secondary">Sign In</Link>
//                 <Link to="/register" className="nav-cta-button">
//                   Get Started
//                 </Link>
//               </>
//             )}
//           </nav>
//         </div>
//       </header>

//       {/* Hero Section */}
//       <section className="hero-section">
//         <div className="hero-bg-animation">
//           <div className="floating-shape shape-1"></div>
//           <div className="floating-shape shape-2"></div>
//           <div className="floating-shape shape-3"></div>
//         </div>
        
//         <div className="hero-content">
//           <div className="hero-badge animate-slide-down">
//             <span className="badge-icon">✨</span>
//             New: AI-Powered Instagram Stories!
//           </div>

//           <h1 className="hero-title animate-slide-up">
//             Automate Your<br />
//             <span className="gradient-text">Social Media Magic</span>
//           </h1>

//           <p className="hero-subtitle animate-fade-in">
//             AI-powered automation for Facebook, Instagram, WhatsApp, YouTube & Reddit. 
//             Save 20+ hours weekly while boosting engagement by 300%.
//           </p>

//           <div className="hero-buttons animate-fade-in-delay">
//             <Link to="/register" className="hero-cta-primary">
//               <span>Start Free Trial</span>
//               <span className="button-arrow">→</span>
//             </Link>
//             <button onClick={() => scrollToSection('platforms')} className="hero-cta-secondary">
//               <span>Watch Demo</span>
//               <span className="play-icon">▶</span>
//             </button>
//           </div>

//           <div className="hero-stats">
//             {stats.map((stat, idx) => (
//               <div key={idx} className="stat-item animate-scale-in" style={{ animationDelay: `${idx * 0.1}s` }}>
//                 <div className="stat-value">{stat.value}</div>
//                 <div className="stat-label">{stat.label}</div>
//               </div>
//             ))}
//           </div>
//         </div>
//       </section>

//       {/* Features Section */}
//       <section id="features" className="features-section">
//         <div className="section-header">
//           <h2 className="section-title">Powerful Features</h2>
//           <p className="section-subtitle">
//             Everything you need to dominate social media
//           </p>
//         </div>

//         <div className="features-grid">
//           {features.map((feature, idx) => (
//             <div
//               key={idx}
//               className={`feature-card ${activeFeature === idx ? 'active' : ''}`}
//               onMouseEnter={() => setActiveFeature(idx)}
//             >
//               <div className="feature-icon-wrapper">
//                 <div className="feature-icon">{feature.icon}</div>
//               </div>
//               <h3 className="feature-title">{feature.title}</h3>
//               <p className="feature-description">{feature.description}</p>
//               <div className="feature-hover-line"></div>
//             </div>
//           ))}
//         </div>
//       </section>

//       {/* Platforms Section */}
//       <section id="platforms" className="platforms-section">
//         <div className="section-header">
//           <h2 className="section-title">Supported Platforms</h2>
//           <p className="section-subtitle">
//             One dashboard to rule them all
//           </p>
//         </div>

//         <div className="platforms-grid">
//           {platforms.map((platform, idx) => (
//             <Link
//               key={idx}
//               to={platform.route}
//               className="platform-card"
//               onMouseEnter={() => setHoveredPlatform(idx)}
//               onMouseLeave={() => setHoveredPlatform(null)}
//             >
//               <div className="platform-icon-bg">
//                 <div className="platform-emoji">{platform.emoji}</div>
//               </div>
//               <h3 className="platform-name">{platform.name}</h3>
//               <p className="platform-description">{platform.description}</p>
              
//               <div className="platform-features">
//                 {platform.features.map((feature, fIdx) => (
//                   <span key={fIdx} className="platform-feature-tag">
//                     <span className="tag-dot">•</span>
//                     {feature}
//                   </span>
//                 ))}
//               </div>
//               <div className="platform-arrow">→</div>
//             </Link>
//           ))}
//         </div>
//       </section>

//       {/* Testimonials Section */}
//       <section id="testimonials" className="testimonials-section">
//         <div className="section-header">
//           <h2 className="section-title">Loved by Thousands</h2>
//           <p className="section-subtitle">
//             See what our users are saying
//           </p>
//         </div>

//         <div className="testimonials-grid">
//           {testimonials.map((testimonial, idx) => (
//             <div key={idx} className="testimonial-card">
//               <div className="testimonial-rating">
//                 {'⭐'.repeat(testimonial.rating)}
//               </div>
//               <p className="testimonial-content">"{testimonial.content}"</p>
//               <div className="testimonial-author">
//                 <img
//                   src={testimonial.image}
//                   alt={testimonial.name}
//                   className="author-image"
//                 />
//                 <div className="author-info">
//                   <div className="author-name">{testimonial.name}</div>
//                   <div className="author-role">
//                     {testimonial.role} at {testimonial.company}
//                   </div>
//                 </div>
//               </div>
//             </div>
//           ))}
//         </div>
//       </section>

//       {/* CTA Section */}
//       <section className="cta-section">
//         <div className="cta-content">
//           <h2 className="cta-title">Ready to Transform Your Social Media?</h2>
//           <p className="cta-subtitle">
//             Join 50,000+ users automating their social media success
//           </p>
//           <div className="cta-buttons">
//             <Link to="/register" className="cta-button-primary">
//               Start Free Trial
//             </Link>
//             <Link to="/contact" className="cta-button-secondary">
//               Contact Sales
//             </Link>
//           </div>
//           <p className="cta-note">No credit card required • Cancel anytime</p>
//         </div>
//       </section>

//       {/* Footer */}
//       <footer className="landing-footer">
//         <div className="footer-content">
//           <div className="footer-grid">
//             <div className="footer-brand">
//               <div className="footer-logo">
//                 <span>🚀</span>
//                 VelocityPost
//               </div>
//               <p className="footer-description">
//                 AI-powered social media automation platform helping businesses save time and boost engagement.
//               </p>
//               <div className="footer-socials">
//                 <a href="https://facebook.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">f</a>
//                 <a href="https://twitter.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">𝕏</a>
//                 <a href="https://instagram.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">📷</a>
//                 <a href="https://linkedin.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">in</a>
//               </div>
//             </div>

//             <div className="footer-column">
//               <h4 className="footer-column-title">Product</h4>
//               <div className="footer-links">
//                 <Link to="/features" className="footer-link">Features</Link>
//                 <Link to="/pricing" className="footer-link">Pricing</Link>
//                 <Link to="/integrations" className="footer-link">Integrations</Link>
//                 <Link to="/api" className="footer-link">API</Link>
//               </div>
//             </div>

//             <div className="footer-column">
//               <h4 className="footer-column-title">Company</h4>
//               <div className="footer-links">
//                 <Link to="/about" className="footer-link">About Us</Link>
//                 <Link to="/careers" className="footer-link">Careers</Link>
//                 <Link to="/blog" className="footer-link">Blog</Link>
//                 <Link to="/contact" className="footer-link">Contact</Link>
//               </div>
//             </div>

//             <div className="footer-column">
//               <h4 className="footer-column-title">Support</h4>
//               <div className="footer-links">
//                 <Link to="/helpcenter" className="footer-link">Help Center</Link>
//                 <Link to="/documentation" className="footer-link">Documentation</Link>
//                 <Link to="/community" className="footer-link">Community</Link>
//                 <Link to="/status" className="footer-link">Status</Link>
//               </div>
//             </div>

//             <div className="footer-column">
//               <h4 className="footer-column-title">Legal</h4>
//               <div className="footer-links">
//                 <Link to="/privacypolicy" className="footer-link">Privacy Policy</Link>
//                 <Link to="/termsofservice" className="footer-link">Terms of Service</Link>
//                 <Link to="/cookiepolicy" className="footer-link">Cookie Policy</Link>
//               </div>
//             </div>
//           </div>

//           <div className="footer-bottom">
//             <p className="footer-copyright">
//               © {new Date().getFullYear()} VelocityPost. All rights reserved.
//             </p>
//             <div className="footer-legal-links">
//               <Link to="/privacypolicy" className="footer-legal-link">Privacy</Link>
//               <Link to="/termsofservice" className="footer-legal-link">Terms</Link>
//               <Link to="/cookiepolicy" className="footer-legal-link">Cookies</Link>
//             </div>
//           </div>
//         </div>
//       </footer>

//       <style>{`
//         * {
//           margin: 0;
//           padding: 0;
//           box-sizing: border-box;
//         }

//         .landing-page-container {
//           font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
//           overflow-x: hidden;
//           background: #ffffff;
//         }

//         @keyframes slideDown {
//           from {
//             opacity: 0;
//             transform: translateY(-30px);
//           }
//           to {
//             opacity: 1;
//             transform: translateY(0);
//           }
//         }

//         @keyframes slideUp {
//           from {
//             opacity: 0;
//             transform: translateY(30px);
//           }
//           to {
//             opacity: 1;
//             transform: translateY(0);
//           }
//         }

//         @keyframes fadeIn {
//           from {
//             opacity: 0;
//           }
//           to {
//             opacity: 1;
//           }
//         }

//         @keyframes scaleIn {
//           from {
//             opacity: 0;
//             transform: scale(0.8);
//           }
//           to {
//             opacity: 1;
//             transform: scale(1);
//           }
//         }

//         @keyframes float {
//           0%, 100% { transform: translate(0, 0) rotate(0deg); }
//           25% { transform: translate(10px, -10px) rotate(5deg); }
//           50% { transform: translate(-5px, 5px) rotate(-5deg); }
//           75% { transform: translate(-10px, -5px) rotate(3deg); }
//         }

//         .animate-slide-down {
//           animation: slideDown 0.8s ease-out;
//         }

//         .animate-slide-up {
//           animation: slideUp 0.9s ease-out;
//         }

//         .animate-fade-in {
//           animation: fadeIn 1s ease-out;
//         }

//         .animate-fade-in-delay {
//           animation: fadeIn 1s ease-out 0.3s backwards;
//         }

//         .animate-scale-in {
//           animation: scaleIn 0.6s ease-out backwards;
//         }

//         .landing-header {
//           position: fixed;
//           top: 0;
//           left: 0;
//           right: 0;
//           z-index: 1000;
//           background: rgba(255, 255, 255, 0.95);
//           backdrop-filter: blur(10px);
//           transition: all 0.3s ease;
//           padding: 16px 0;
//           border-bottom: 1px solid transparent;
//         }

//         .landing-header.scrolled {
//           background: rgba(255, 255, 255, 0.98);
//           box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
//           border-bottom-color: #e5e7eb;
//         }

//         .landing-header-content {
//           max-width: 100%;
//           margin: 0 auto;
//           padding: 0 20px;
//           display: flex;
//           justify-content: space-between;
//           align-items: center;
//           gap: 16px;
//         }

//         .landing-logo {
//           display: flex;
//           align-items: center;
//           gap: 10px;
//           text-decoration: none;
//           color: #111827;
//           font-weight: 800;
//           font-size: 20px;
//           transition: transform 0.3s ease;
//           flex-shrink: 0;
//         }

//         .landing-logo:hover {
//           transform: scale(1.05);
//         }

//         .logo-emoji {
//           font-size: 24px;
//         }

//         .landing-nav {
//           display: flex;
//           align-items: center;
//           gap: 6px;
//           overflow-x: auto;
//           overflow-y: hidden;
//           flex: 1;
//           padding: 4px 0;
//           -webkit-overflow-scrolling: touch;
//           scrollbar-width: none;
//         }

//         .landing-nav::-webkit-scrollbar {
//           display: none;
//         }

//         .nav-link,
//         .nav-link-secondary {
//           background: none;
//           border: none;
//           color: #6b7280;
//           font-size: 13px;
//           font-weight: 600;
//           cursor: pointer;
//           text-decoration: none;
//           padding: 7px 13px;
//           border-radius: 8px;
//           transition: all 0.2s ease;
//           white-space: nowrap;
//           flex-shrink: 0;
//         }

//         .nav-link:hover,
//         .nav-link-secondary:hover {
//           color: #0ea5e9;
//           background: #f0f9ff;
//         }

//         .nav-cta-button {
//           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
//           color: white;
//           padding: 8px 18px;
//           border-radius: 8px;
//           text-decoration: none;
//           font-weight: 700;
//           font-size: 13px;
//           transition: all 0.3s ease;
//           box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
//           white-space: nowrap;
//           flex-shrink: 0;
//         }

//         .nav-cta-button:hover {
//           transform: translateY(-2px);
//           box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
//         }

//         .hero-section {
//           min-height: 100vh;
//           display: flex;
//           align-items: center;
//           justify-content: center;
//           padding: 140px 24px 80px;
//           position: relative;
//           overflow: hidden;
//           background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
//         }

//         .hero-bg-animation {
//           position: absolute;
//           top: 0;
//           left: 0;
//           right: 0;
//           bottom: 0;
//           overflow: hidden;
//         }

//         .floating-shape {
//           position: absolute;
//           border-radius: 50%;
//           filter: blur(60px);
//           opacity: 0.4;
//           animation: float 20s infinite ease-in-out;
//         }

//         .shape-1 {
//           width: 400px;
//           height: 400px;
//           background: linear-gradient(135deg, #0ea5e9, #06b6d4);
//           top: -100px;
//           left: -100px;
//         }

//         .shape-2 {
//           width: 300px;
//           height: 300px;
//           background: linear-gradient(135deg, #06b6d4, #0284c7);
//           bottom: -50px;
//           right: -50px;
//           animation-delay: 5s;
//         }

//         .shape-3 {
//           width: 250px;
//           height: 250px;
//           background: linear-gradient(135deg, #0ea5e9, #38bdf8);
//           top: 50%;
//           left: 50%;
//           animation-delay: 10s;
//         }

//         .hero-content {
//           max-width: 1000px;
//           text-align: center;
//           position: relative;
//           z-index: 1;
//         }

//         .hero-badge {
//           display: inline-flex;
//           align-items: center;
//           gap: 8px;
//           background: white;
//           padding: 10px 20px;
//           border-radius: 50px;
//           font-size: 14px;
//           font-weight: 600;
//           color: #0ea5e9;
//           margin-bottom: 32px;
//           box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
//         }

//         .badge-icon {
//           font-size: 16px;
//         }

//         .hero-title {
//           font-size: clamp(40px, 8vw, 72px);
//           font-weight: 900;
//           line-height: 1.1;
//           margin-bottom: 24px;
//           color: #111827;
//           letter-spacing: -0.02em;
//         }

//         .gradient-text {
//           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
//           -webkit-background-clip: text;
//           -webkit-text-fill-color: transparent;
//           background-clip: text;
//         }

//         .hero-subtitle {
//           font-size: clamp(16px, 3vw, 20px);
//           color: #6b7280;
//           max-width: 700px;
//           margin: 0 auto 40px;
//           line-height: 1.7;
//         }

//         .hero-buttons {
//           display: flex;
//           gap: 16px;
//           justify-content: center;
//           flex-wrap: wrap;
//           margin-bottom: 60px;
//         }

//         .hero-cta-primary,
//         .hero-cta-secondary {
//           padding: 16px 32px;
//           border-radius: 12px;
//           text-decoration: none;
//           font-weight: 700;
//           font-size: 16px;
//           transition: all 0.3s ease;
//           display: inline-flex;
//           align-items: center;
//           gap: 8px;
//           border: none;
//           cursor: pointer;
//           background: none;
//         }

//         .hero-cta-primary {
//           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
//           color: white;
//           box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
//         }

//         .hero-cta-primary:hover {
//           transform: translateY(-3px);
//           box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
//         }

//         .hero-cta-secondary {
//           background: white;
//           color: #0ea5e9;
//           border: 2px solid #0ea5e9;
//         }

//         .hero-cta-secondary:hover {
//           background: #0ea5e9;
//           color: white;
//           transform: translateY(-3px);
//         }

//         .button-arrow,
//         .play-icon {
//           font-size: 18px;
//           transition: transform 0.3s ease;
//         }

//         .hero-cta-primary:hover .button-arrow {
//           transform: translateX(5px);
//         }

//         .hero-stats {
//           display: grid;
//           grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
//           gap: 32px;
//           max-width: 800px;
//           margin: 0 auto;
//         }

//         .stat-item {
//           text-align: center;
//         }

//         .stat-value {
//           font-size: clamp(28px, 5vw, 42px);
//           font-weight: 900;
//           color: #0ea5e9;
//           margin-bottom: 4px;
//         }

//         .stat-label {
//           font-size: 13px;
//           color: #6b7280;
//           font-weight: 600;
//           text-transform: uppercase;
//           letter-spacing: 0.5px;
//         }

//         .features-section {
//           padding: 100px 24px;
//           background: white;
//         }

//         .section-header {
//           text-align: center;
//           max-width: 800px;
//           margin: 0 auto 64px;
//         }

//         .section-title {
//           font-size: clamp(32px, 5vw, 48px);
//           font-weight: 900;
//           color: #111827;
//           margin-bottom: 16px;
//           letter-spacing: -0.02em;
//         }

//         .section-subtitle {
//           font-size: clamp(16px, 3vw, 18px);
//           color: #6b7280;
//           line-height: 1.6;
//         }

//         .features-grid {
//           max-width: 1200px;
//           margin: 0 auto;
//           display: grid;
//           grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
//           gap: 32px;
//         }

//         .feature-card {
//           background: #f9fafb;
//           padding: 36px 28px;
//           border-radius: 16px;
//           transition: all 0.3s ease;
//           cursor: pointer;
//           border: 2px solid transparent;
//           position: relative;
//           overflow: hidden;
//         }

//         .feature-card::before {
//           content: '';
//           position: absolute;
//           top: 0;
//           left: 0;
//           right: 0;
//           height: 4px;
//           background: linear-gradient(90deg, #0ea5e9, #06b6d4);
//           transform: scaleX(0);
//           transition: transform 0.3s ease;
//         }

//         .feature-card:hover,
//         .feature-card.active {
//           background: white;
//           border-color: #0ea5e9;
//           box-shadow: 0 20px 60px rgba(14, 165, 233, 0.15);
//           transform: translateY(-8px);
//         }

//         .feature-card:hover::before,
//         .feature-card.active::before {
//           transform: scaleX(1);
//         }

//         .feature-icon-wrapper {
//           margin-bottom: 20px;
//         }

//         .feature-icon {
//           font-size: 48px;
//           display: inline-block;
//           transition: transform 0.3s ease;
//         }

//         .feature-card:hover .feature-icon {
//           transform: scale(1.1) rotate(5deg);
//         }

//         .feature-title {
//           font-size: 22px;
//           font-weight: 700;
//           color: #111827;
//           margin-bottom: 12px;
//         }

//         .feature-description {
//           color: #6b7280;
//           line-height: 1.7;
//           font-size: 15px;
//         }

//         .platforms-section {
//           padding: 100px 24px;
//           background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
//         }

//         .platforms-grid {
//           max-width: 1200px;
//           margin: 0 auto;
//           display: grid;
//           grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
//           gap: 28px;
//         }

//         .platform-card {
//           background: white;
//           padding: 32px;
//           border-radius: 20px;
//           text-decoration: none;
//           transition: all 0.3s ease;
//           cursor: pointer;
//           border: 2px solid transparent;
//           display: flex;
//           flex-direction: column;
//           position: relative;
//           overflow: hidden;
//         }

//         .platform-card::after {
//           content: '';
//           position: absolute;
//           top: 0;
//           left: 0;
//           right: 0;
//           bottom: 0;
//           background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(6, 182, 212, 0.05));
//           opacity: 0;
//           transition: opacity 0.3s ease;
//         }

//         .platform-card:hover {
//           border-color: #0ea5e9;
//           transform: translateY(-10px);
//           box-shadow: 0 25px 70px rgba(14, 165, 233, 0.2);
//         }

//         .platform-card:hover::after {
//           opacity: 1;
//         }

//         .platform-icon-bg {
//           width: 80px;
//           height: 80px;
//           background: linear-gradient(135deg, #0ea5e9, #06b6d4);
//           border-radius: 20px;
//           display: flex;
//           align-items: center;
//           justify-content: center;
//           margin-bottom: 20px;
//           position: relative;
//           z-index: 1;
//           transition: transform 0.3s ease;
//         }

//         .platform-card:hover .platform-icon-bg {
//           transform: scale(1.1) rotate(5deg);
//         }

//         .platform-emoji {
//           font-size: 48px;
//         }

//         .platform-name {
//           font-size: 26px;
//           font-weight: 700;
//           color: #111827;
//           margin-bottom: 12px;
//           position: relative;
//           z-index: 1;
//         }

//         .platform-description {
//           color: #6b7280;
//           line-height: 1.7;
//           margin-bottom: 20px;
//           flex-grow: 1;
//           font-size: 15px;
//           position: relative;
//           z-index: 1;
//         }

//         .platform-features {
//           display: flex;
//           flex-direction: column;
//           gap: 8px;
//           position: relative;
//           z-index: 1;
//         }

//         .platform-feature-tag {
//           display: flex;
//           align-items: center;
//           gap: 8px;
//           color: #0ea5e9;
//           font-size: 13px;
//           font-weight: 600;
//         }

//         .tag-dot {
//           font-size: 20px;
//         }

//         .platform-arrow {
//           position: absolute;
//           bottom: 24px;
//           right: 24px;
//           font-size: 24px;
//           color: #0ea5e9;
//           opacity: 0;
//           transform: translateX(-10px);
//           transition: all 0.3s ease;
//         }

//         .platform-card:hover .platform-arrow {
//           opacity: 1;
//           transform: translateX(0);
//         }

//         .testimonials-section {
//           padding: 100px 24px;
//           background: white;
//         }

//         .testimonials-grid {
//           max-width: 1200px;
//           margin: 0 auto;
//           display: grid;
//           grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
//           gap: 32px;
//         }

//         .testimonial-card {
//           background: #f9fafb;
//           padding: 36px;
//           border-radius: 20px;
//           transition: all 0.3s ease;
//         }

//         .testimonial-card:hover {
//           background: white;
//           box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
//           transform: translateY(-8px);
//         }

//         .testimonial-rating {
//           font-size: 18px;
//           margin-bottom: 16px;
//         }

//         .testimonial-content {
//           color: #111827;
//           font-size: 16px;
//           line-height: 1.7;
//           margin-bottom: 24px;
//           font-style: italic;
//         }

//         .testimonial-author {
//           display: flex;
//           align-items: center;
//           gap: 16px;
//         }

//         .author-image {
//           width: 56px;
//           height: 56px;
//           border-radius: 50%;
//           object-fit: cover;
//           border: 3px solid #0ea5e9;
//         }

//         .author-name {
//           font-weight: 700;
//           color: #111827;
//           margin-bottom: 4px;
//           font-size: 15px;
//         }

//         .author-role {
//           color: #6b7280;
//           font-size: 13px;
//         }

//         .cta-section {
//           padding: 100px 24px;
//           background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
//           position: relative;
//           overflow: hidden;
//         }

//         .cta-content {
//           max-width: 800px;
//           margin: 0 auto;
//           text-align: center;
//           position: relative;
//           z-index: 1;
//         }

//         .cta-title {
//           font-size: clamp(32px, 5vw, 48px);
//           font-weight: 900;
//           color: white;
//           margin-bottom: 20px;
//           line-height: 1.2;
//         }

//         .cta-subtitle {
//           font-size: clamp(16px, 3vw, 20px);
//           color: rgba(255, 255, 255, 0.95);
//           margin-bottom: 36px;
//           line-height: 1.6;
//         }

//         .cta-buttons {
//           display: flex;
//           gap: 16px;
//           justify-content: center;
//           flex-wrap: wrap;
//         }

//         .cta-button-primary,
//         .cta-button-secondary {
//           padding: 16px 40px;
//           border-radius: 12px;
//           text-decoration: none;
//           font-weight: 700;
//           font-size: 16px;
//           transition: all 0.3s ease;
//         }

//         .cta-button-primary {
//           background: white;
//           color: #0ea5e9;
//           box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
//         }

//         .cta-button-primary:hover {
//           transform: translateY(-3px) scale(1.05);
//           box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
//         }

//         .cta-button-secondary {
//           background: rgba(255, 255, 255, 0.15);
//           backdrop-filter: blur(10px);
//           color: white;
//           border: 2px solid rgba(255, 255, 255, 0.3);
//         }

//         .cta-button-secondary:hover {
//           background: rgba(255, 255, 255, 0.25);
//           transform: translateY(-3px);
//         }

//         .cta-note {
//           margin-top: 20px;
//           color: rgba(255, 255, 255, 0.9);
//           font-size: 14px;
//         }

//         .landing-footer {
//           background: #111827;
//           color: white;
//           padding: 80px 24px 40px;
//         }

//         .footer-content {
//           max-width: 1200px;
//           margin: 0 auto;
//         }

//         .footer-grid {
//           display: grid;
//           grid-template-columns: 2fr repeat(4, 1fr);
//           gap: 40px;
//           margin-bottom: 48px;
//         }

//         .footer-logo {
//           font-size: 24px;
//           font-weight: 700;
//           margin-bottom: 16px;
//           display: flex;
//           align-items: center;
//           gap: 8px;
//         }

//         .footer-logo span {
//           font-size: 28px;
//         }

//         .footer-description {
//           color: #9ca3af;
//           line-height: 1.6;
//           margin-bottom: 20px;
//           max-width: 320px;
//           font-size: 14px;
//         }

//         .footer-socials {
//           display: flex;
//           gap: 12px;
//         }

//         .footer-social-link {
//           width: 40px;
//           height: 40px;
//           border-radius: 50%;
//           background: #1f2937;
//           display: flex;
//           align-items: center;
//           justify-content: center;
//           color: white;
//           text-decoration: none;
//           font-weight: 700;
//           font-size: 14px;
//           transition: all 0.3s ease;
//         }

//         .footer-social-link:hover {
//           background: #0ea5e9;
//           transform: translateY(-3px);
//         }

//         .footer-column-title {
//           font-size: 14px;
//           font-weight: 700;
//           margin-bottom: 16px;
//           text-transform: uppercase;
//           letter-spacing: 1px;
//           color: white;
//         }

//         .footer-links {
//           display: flex;
//           flex-direction: column;
//           gap: 10px;
//         }

//         .footer-link {
//           color: #9ca3af;
//           text-decoration: none;
//           font-size: 14px;
//           transition: color 0.2s ease;
//         }

//         .footer-link:hover {
//           color: #0ea5e9;
//         }

//         .footer-bottom {
//           padding-top: 32px;
//           border-top: 1px solid #1f2937;
//           display: flex;
//           justify-content: space-between;
//           align-items: center;
//           flex-wrap: wrap;
//           gap: 16px;
//         }

//         .footer-copyright {
//           color: #9ca3af;
//           margin: 0;
//           font-size: 14px;
//         }

//         .footer-legal-links {
//           display: flex;
//           gap: 20px;
//           flex-wrap: wrap;
//         }

//         .footer-legal-link {
//           color: #9ca3af;
//           text-decoration: none;
//           font-size: 14px;
//           transition: color 0.2s ease;
//         }

//         .footer-legal-link:hover {
//           color: #0ea5e9;
//         }

//         @media (max-width: 1200px) {
//           .footer-grid {
//             grid-template-columns: repeat(3, 1fr);
//           }

//           .footer-brand {
//             grid-column: span 3;
//           }
//         }

//         @media (max-width: 768px) {
//           .landing-nav {
//             gap: 4px;
//           }

//           .nav-link,
//           .nav-link-secondary {
//             padding: 6px 10px;
//             font-size: 12px;
//           }

//           .nav-cta-button {
//             padding: 7px 15px;
//             font-size: 12px;
//           }

//           .hero-section {
//             padding: 120px 20px 60px;
//           }

//           .hero-stats {
//             grid-template-columns: repeat(2, 1fr);
//             gap: 24px;
//           }

//           .features-grid,
//           .platforms-grid,
//           .testimonials-grid {
//             grid-template-columns: 1fr;
//           }

//           .footer-grid {
//             grid-template-columns: repeat(2, 1fr);
//           }

//           .footer-brand {
//             grid-column: span 2;
//           }

//           .cta-buttons {
//             flex-direction: column;
//           }

//           .cta-button-primary,
//           .cta-button-secondary {
//             width: 100%;
//           }
//         }

//         @media (max-width: 480px) {
//           .landing-header-content {
//             padding: 0 16px;
//           }

//           .landing-nav {
//             gap: 3px;
//           }

//           .nav-link,
//           .nav-link-secondary {
//             padding: 5px 9px;
//             font-size: 11px;
//           }

//           .nav-cta-button {
//             padding: 6px 13px;
//             font-size: 11px;
//           }

//           .logo-text {
//             font-size: 16px;
//           }

//           .footer-grid {
//             grid-template-columns: 1fr;
//           }

//           .footer-brand {
//             grid-column: span 1;
//           }
//         }

//         html {
//           scroll-behavior: smooth;
//         }
//       `}</style>
//     </div>
//   );
// };

// export default Landing_Page;


import React, { useState, useEffect } from 'react';
import { Link, Routes, Route, useLocation } from 'react-router-dom';
import { useAuth } from './quickpage/AuthContext';

// Import ALL footer pages
import About from './footerpages/About';
import Api from './footerpages/Api';
import Blog from './footerpages/Blog';
import Careers from './footerpages/Careers';
import Community from './footerpages/Community';
import Contact from './footerpages/Contact';
import Cookiepolicy from './footerpages/Cookiepolicy';
import Documentation from './footerpages/Documentation';
import Features from './footerpages/Features';
import Helpcenter from './footerpages/Helpcenter';
import Integrations from './footerpages/Integrations';
import Pricing from './footerpages/Pricing';
import Privacypolicy from './footerpages/Privacypolicy';
import Status from './footerpages/Status';
import Termsofservice from './footerpages/Termsofservice';

const BACKEND_URL = 'https://agentic-u5lx.onrender.com';

const Landing_Page = () => {
  const { isAuthenticated } = useAuth();
  const location = useLocation();
  const [activeFeature, setActiveFeature] = useState(0);
  const [hoveredPlatform, setHoveredPlatform] = useState(null);
  const [scrolled, setScrolled] = useState(false);
  const [serverLoading, setServerLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState(''); // 'loading', 'success', 'error'

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

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
      setServerStatus('success'); // Show success anyway (server is waking up)
      setTimeout(() => {
        setServerStatus('');
        setServerLoading(false);
      }, 2000);
    }
  };

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
    }
  };

  // Check if we're on a footer page route
  const isFooterPage = [
    '/features', '/pricing', '/integrations', '/api',
    '/about', '/careers', '/blog', '/contact',
    '/helpcenter', '/documentation', '/community', '/status',
    '/privacypolicy', '/termsofservice', '/cookiepolicy'
  ].includes(location.pathname);

  // If on footer page, render that page
  if (isFooterPage) {
    return (
      <Routes>
        <Route path="/features" element={<Features />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/integrations" element={<Integrations />} />
        <Route path="/api" element={<Api />} />
        <Route path="/about" element={<About />} />
        <Route path="/careers" element={<Careers />} />
        <Route path="/blog" element={<Blog />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="/helpcenter" element={<Helpcenter />} />
        <Route path="/documentation" element={<Documentation />} />
        <Route path="/community" element={<Community />} />
        <Route path="/status" element={<Status />} />
        <Route path="/privacypolicy" element={<Privacypolicy />} />
        <Route path="/termsofservice" element={<Termsofservice />} />
        <Route path="/cookiepolicy" element={<Cookiepolicy />} />
      </Routes>
    );
  }

  // Otherwise render the landing page
  return (
    <div className="landing-page-container">
      {/* Header - Logo LEFT, Navigation RIGHT */}
      <header className={`landing-header ${scrolled ? 'scrolled' : ''}`}>
        <div className="landing-header-content">
          {/* Logo - LEFT SIDE */}
          <Link to="/" className="landing-logo">
            <span className="logo-emoji">🚀</span>
            <span className="logo-text">VelocityPost</span>
          </Link>
          
          {/* Navigation - RIGHT SIDE */}
          <nav className="landing-nav">
            <button onClick={() => scrollToSection('features')} className="nav-link">
              Features
            </button>
            <button onClick={() => scrollToSection('platforms')} className="nav-link">
              Platforms
            </button>
            <Link to="/pricing" className="nav-link">
              Pricing
            </Link>
            {/* <Link to="/about" className="nav-link">
              About
            </Link> */}
            {/* <Link to="/contact" className="nav-link">
              Contact
            </Link> */}
            
            {/* Server Start Button */}
            <button 
              onClick={wakeUpServer} 
              disabled={serverLoading}
              className="server-button"
            >
              {serverLoading ? (
                <>
                  <span className="spinner"></span>
                  <span>Starting...</span>
                </>
              ) : serverStatus === 'success' ? (
                <>
                  <span>✓</span>
                  <span>Ready!</span>
                </>
              ) : (
                <>
                  <span>⚡</span>
                  <span>Server Start</span>
                </>
              )}
            </button>

            {isAuthenticated ? (
              <Link to="/reddit-auto" className="nav-cta-button">
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" className="nav-link-secondary">Sign In</Link>
                <Link to="/register" className="nav-cta-button">
                  Get Started
                </Link>
              </>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-bg-animation">
          <div className="floating-shape shape-1"></div>
          <div className="floating-shape shape-2"></div>
          <div className="floating-shape shape-3"></div>
        </div>
        
        <div className="hero-content">
          <div className="hero-badge animate-slide-down">
            <span className="badge-icon">✨</span>
            New: AI-Powered Instagram Stories!
          </div>

          <h1 className="hero-title animate-slide-up">
            Automate Your<br />
            <span className="gradient-text">Social Media Magic</span>
          </h1>

          <p className="hero-subtitle animate-fade-in">
            AI-powered automation for Facebook, Instagram, WhatsApp, YouTube & Reddit. 
            Save 20+ hours weekly while boosting engagement by 300%.
          </p>

          <div className="hero-buttons animate-fade-in-delay">
            <Link to="/register" className="hero-cta-primary">
              <span>Start Free Trial</span>
              <span className="button-arrow">→</span>
            </Link>
            <button onClick={() => scrollToSection('platforms')} className="hero-cta-secondary">
              <span>Watch Demo</span>
              <span className="play-icon">▶</span>
            </button>
          </div>

          <div className="hero-stats">
            {stats.map((stat, idx) => (
              <div key={idx} className="stat-item animate-scale-in" style={{ animationDelay: `${idx * 0.1}s` }}>
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
              <div className="feature-icon-wrapper">
                <div className="feature-icon">{feature.icon}</div>
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-hover-line"></div>
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
              <div className="platform-icon-bg">
                <div className="platform-emoji">{platform.emoji}</div>
              </div>
              <h3 className="platform-name">{platform.name}</h3>
              <p className="platform-description">{platform.description}</p>
              
              <div className="platform-features">
                {platform.features.map((feature, fIdx) => (
                  <span key={fIdx} className="platform-feature-tag">
                    <span className="tag-dot">•</span>
                    {feature}
                  </span>
                ))}
              </div>
              <div className="platform-arrow">→</div>
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
            <div className="footer-brand">
              <div className="footer-logo">
                <span>🚀</span>
                VelocityPost
              </div>
              <p className="footer-description">
                AI-powered social media automation platform helping businesses save time and boost engagement.
              </p>
              <div className="footer-socials">
                <a href="https://facebook.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">f</a>
                <a href="https://twitter.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">𝕏</a>
                <a href="https://instagram.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">📷</a>
                <a href="https://linkedin.com" className="footer-social-link" target="_blank" rel="noopener noreferrer">in</a>
              </div>
            </div>

            <div className="footer-column">
              <h4 className="footer-column-title">Product</h4>
              <div className="footer-links">
                <Link to="/features" className="footer-link">Features</Link>
                <Link to="/pricing" className="footer-link">Pricing</Link>
                <Link to="/integrations" className="footer-link">Integrations</Link>
                <Link to="/api" className="footer-link">API</Link>
              </div>
            </div>

            <div className="footer-column">
              <h4 className="footer-column-title">Company</h4>
              <div className="footer-links">
                <Link to="/about" className="footer-link">About Us</Link>
                <Link to="/careers" className="footer-link">Careers</Link>
                <Link to="/blog" className="footer-link">Blog</Link>
                <Link to="/contact" className="footer-link">Contact</Link>
              </div>
            </div>

            <div className="footer-column">
              <h4 className="footer-column-title">Support</h4>
              <div className="footer-links">
                <Link to="/helpcenter" className="footer-link">Help Center</Link>
                <Link to="/documentation" className="footer-link">Documentation</Link>
                <Link to="/community" className="footer-link">Community</Link>
                <Link to="/status" className="footer-link">Status</Link>
              </div>
            </div>

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
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
          overflow-x: hidden;
          background: #ffffff;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
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

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            opacity: 0;
            transform: scale(0.8);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }

        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          25% { transform: translate(10px, -10px) rotate(5deg); }
          50% { transform: translate(-5px, 5px) rotate(-5deg); }
          75% { transform: translate(-10px, -5px) rotate(3deg); }
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .animate-slide-down {
          animation: slideDown 0.8s ease-out;
        }

        .animate-slide-up {
          animation: slideUp 0.9s ease-out;
        }

        .animate-fade-in {
          animation: fadeIn 1s ease-out;
        }

        .animate-fade-in-delay {
          animation: fadeIn 1s ease-out 0.3s backwards;
        }

        .animate-scale-in {
          animation: scaleIn 0.6s ease-out backwards;
        }

        /* HEADER - Logo LEFT, Nav RIGHT (Professional Layout) */
        .landing-header {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          z-index: 1000;
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          transition: all 0.3s ease;
          padding: 16px 0;
          border-bottom: 1px solid transparent;
        }

        .landing-header.scrolled {
          background: rgba(255, 255, 255, 0.98);
          box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
          border-bottom-color: #e5e7eb;
          padding: 12px 0;
        }

        .landing-header-content {
          max-width: 1400px;
          margin: 0 auto;
          padding: 0 40px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 40px;
        }

        /* Logo - LEFT SIDE */
        .landing-logo {
          display: flex;
          align-items: center;
          gap: 10px;
          text-decoration: none;
          color: #111827;
          font-weight: 800;
          font-size: 22px;
          transition: transform 0.3s ease;
          flex-shrink: 0;
        }

        .landing-logo:hover {
          transform: scale(1.05);
        }

        .logo-emoji {
          font-size: 28px;
        }

        /* Navigation - RIGHT SIDE (Evenly Spaced) */
        .landing-nav {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-wrap: wrap;
          justify-content: flex-end;
        }

        .nav-link,
        .nav-link-secondary {
          background: none;
          border: none;
          color: #6b7280;
          font-size: 15px;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          padding: 10px 16px;
          border-radius: 8px;
          transition: all 0.2s ease;
          white-space: nowrap;
        }

        .nav-link:hover,
        .nav-link-secondary:hover {
          color: #0ea5e9;
          background: #f0f9ff;
        }

        /* Server Start Button */
        .server-button {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 10px 20px;
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          border: none;
          border-radius: 8px;
          font-weight: 700;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.3s ease;
          white-space: nowrap;
        }

        .server-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
        }

        .server-button:disabled {
          opacity: 0.8;
          cursor: not-allowed;
        }

        .server-button .spinner {
          width: 14px;
          height: 14px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-top-color: white;
          border-radius: 50%;
          animation: spin 0.6s linear infinite;
        }

        .nav-cta-button {
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          color: white;
          padding: 10px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 700;
          font-size: 15px;
          transition: all 0.3s ease;
          box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
          white-space: nowrap;
        }

        .nav-cta-button:hover {
          transform: translateY(-2px);
          box-shadow: 0 6px 16px rgba(14, 165, 233, 0.4);
        }

        .hero-section {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 140px 24px 80px;
          position: relative;
          overflow: hidden;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #f0f9ff 100%);
        }

        .hero-bg-animation {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          overflow: hidden;
        }

        .floating-shape {
          position: absolute;
          border-radius: 50%;
          filter: blur(60px);
          opacity: 0.4;
          animation: float 20s infinite ease-in-out;
        }

        .shape-1 {
          width: 400px;
          height: 400px;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          top: -100px;
          left: -100px;
        }

        .shape-2 {
          width: 300px;
          height: 300px;
          background: linear-gradient(135deg, #06b6d4, #0284c7);
          bottom: -50px;
          right: -50px;
          animation-delay: 5s;
        }

        .shape-3 {
          width: 250px;
          height: 250px;
          background: linear-gradient(135deg, #0ea5e9, #38bdf8);
          top: 50%;
          left: 50%;
          animation-delay: 10s;
        }

        .hero-content {
          max-width: 1000px;
          text-align: center;
          position: relative;
          z-index: 1;
        }

        .hero-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          background: white;
          padding: 10px 20px;
          border-radius: 50px;
          font-size: 14px;
          font-weight: 600;
          color: #0ea5e9;
          margin-bottom: 32px;
          box-shadow: 0 4px 20px rgba(14, 165, 233, 0.2);
        }

        .badge-icon {
          font-size: 16px;
        }

        .hero-title {
          font-size: clamp(40px, 8vw, 72px);
          font-weight: 900;
          line-height: 1.1;
          margin-bottom: 24px;
          color: #111827;
          letter-spacing: -0.02em;
        }

        .gradient-text {
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .hero-subtitle {
          font-size: clamp(16px, 3vw, 20px);
          color: #6b7280;
          max-width: 700px;
          margin: 0 auto 40px;
          line-height: 1.7;
        }

        .hero-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
          margin-bottom: 60px;
        }

        .hero-cta-primary,
        .hero-cta-secondary {
          padding: 16px 32px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border: none;
          cursor: pointer;
          background: none;
        }

        .hero-cta-primary {
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          color: white;
          box-shadow: 0 10px 30px rgba(14, 165, 233, 0.3);
        }

        .hero-cta-primary:hover {
          transform: translateY(-3px);
          box-shadow: 0 15px 40px rgba(14, 165, 233, 0.4);
        }

        .hero-cta-secondary {
          background: white;
          color: #0ea5e9;
          border: 2px solid #0ea5e9;
        }

        .hero-cta-secondary:hover {
          background: #0ea5e9;
          color: white;
          transform: translateY(-3px);
        }

        .button-arrow,
        .play-icon {
          font-size: 18px;
          transition: transform 0.3s ease;
        }

        .hero-cta-primary:hover .button-arrow {
          transform: translateX(5px);
        }

        .hero-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
          gap: 32px;
          max-width: 800px;
          margin: 0 auto;
        }

        .stat-item {
          text-align: center;
        }

        .stat-value {
          font-size: clamp(28px, 5vw, 42px);
          font-weight: 900;
          color: #0ea5e9;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 13px;
          color: #6b7280;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .features-section {
          padding: 100px 24px;
          background: white;
        }

        .section-header {
          text-align: center;
          max-width: 800px;
          margin: 0 auto 64px;
        }

        .section-title {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: #111827;
          margin-bottom: 16px;
          letter-spacing: -0.02em;
        }

        .section-subtitle {
          font-size: clamp(16px, 3vw, 18px);
          color: #6b7280;
          line-height: 1.6;
        }

        .features-grid {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
          gap: 32px;
        }

        .feature-card {
          background: #f9fafb;
          padding: 36px 28px;
          border-radius: 16px;
          transition: all 0.3s ease;
          cursor: pointer;
          border: 2px solid transparent;
          position: relative;
          overflow: hidden;
        }

        .feature-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, #0ea5e9, #06b6d4);
          transform: scaleX(0);
          transition: transform 0.3s ease;
        }

        .feature-card:hover,
        .feature-card.active {
          background: white;
          border-color: #0ea5e9;
          box-shadow: 0 20px 60px rgba(14, 165, 233, 0.15);
          transform: translateY(-8px);
        }

        .feature-card:hover::before,
        .feature-card.active::before {
          transform: scaleX(1);
        }

        .feature-icon-wrapper {
          margin-bottom: 20px;
        }

        .feature-icon {
          font-size: 48px;
          display: inline-block;
          transition: transform 0.3s ease;
        }

        .feature-card:hover .feature-icon {
          transform: scale(1.1) rotate(5deg);
        }

        .feature-title {
          font-size: 22px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 12px;
        }

        .feature-description {
          color: #6b7280;
          line-height: 1.7;
          font-size: 15px;
        }

        .platforms-section {
          padding: 100px 24px;
          background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        }

        .platforms-grid {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 28px;
        }

        .platform-card {
          background: white;
          padding: 32px;
          border-radius: 20px;
          text-decoration: none;
          transition: all 0.3s ease;
          cursor: pointer;
          border: 2px solid transparent;
          display: flex;
          flex-direction: column;
          position: relative;
          overflow: hidden;
        }

        .platform-card::after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: linear-gradient(135deg, rgba(14, 165, 233, 0.05), rgba(6, 182, 212, 0.05));
          opacity: 0;
          transition: opacity 0.3s ease;
        }

        .platform-card:hover {
          border-color: #0ea5e9;
          transform: translateY(-10px);
          box-shadow: 0 25px 70px rgba(14, 165, 233, 0.2);
        }

        .platform-card:hover::after {
          opacity: 1;
        }

        .platform-icon-bg {
          width: 80px;
          height: 80px;
          background: linear-gradient(135deg, #0ea5e9, #06b6d4);
          border-radius: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 20px;
          position: relative;
          z-index: 1;
          transition: transform 0.3s ease;
        }

        .platform-card:hover .platform-icon-bg {
          transform: scale(1.1) rotate(5deg);
        }

        .platform-emoji {
          font-size: 48px;
        }

        .platform-name {
          font-size: 26px;
          font-weight: 700;
          color: #111827;
          margin-bottom: 12px;
          position: relative;
          z-index: 1;
        }

        .platform-description {
          color: #6b7280;
          line-height: 1.7;
          margin-bottom: 20px;
          flex-grow: 1;
          font-size: 15px;
          position: relative;
          z-index: 1;
        }

        .platform-features {
          display: flex;
          flex-direction: column;
          gap: 8px;
          position: relative;
          z-index: 1;
        }

        .platform-feature-tag {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #0ea5e9;
          font-size: 13px;
          font-weight: 600;
        }

        .tag-dot {
          font-size: 20px;
        }

        .platform-arrow {
          position: absolute;
          bottom: 24px;
          right: 24px;
          font-size: 24px;
          color: #0ea5e9;
          opacity: 0;
          transform: translateX(-10px);
          transition: all 0.3s ease;
        }

        .platform-card:hover .platform-arrow {
          opacity: 1;
          transform: translateX(0);
        }

        .testimonials-section {
          padding: 100px 24px;
          background: white;
        }

        .testimonials-grid {
          max-width: 1200px;
          margin: 0 auto;
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 32px;
        }

        .testimonial-card {
          background: #f9fafb;
          padding: 36px;
          border-radius: 20px;
          transition: all 0.3s ease;
        }

        .testimonial-card:hover {
          background: white;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
          transform: translateY(-8px);
        }

        .testimonial-rating {
          font-size: 18px;
          margin-bottom: 16px;
        }

        .testimonial-content {
          color: #111827;
          font-size: 16px;
          line-height: 1.7;
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
          border: 3px solid #0ea5e9;
        }

        .author-name {
          font-weight: 700;
          color: #111827;
          margin-bottom: 4px;
          font-size: 15px;
        }

        .author-role {
          color: #6b7280;
          font-size: 13px;
        }

        .cta-section {
          padding: 100px 24px;
          background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
          position: relative;
          overflow: hidden;
        }

        .cta-content {
          max-width: 800px;
          margin: 0 auto;
          text-align: center;
          position: relative;
          z-index: 1;
        }

        .cta-title {
          font-size: clamp(32px, 5vw, 48px);
          font-weight: 900;
          color: white;
          margin-bottom: 20px;
          line-height: 1.2;
        }

        .cta-subtitle {
          font-size: clamp(16px, 3vw, 20px);
          color: rgba(255, 255, 255, 0.95);
          margin-bottom: 36px;
          line-height: 1.6;
        }

        .cta-buttons {
          display: flex;
          gap: 16px;
          justify-content: center;
          flex-wrap: wrap;
        }

        .cta-button-primary,
        .cta-button-secondary {
          padding: 16px 40px;
          border-radius: 12px;
          text-decoration: none;
          font-weight: 700;
          font-size: 16px;
          transition: all 0.3s ease;
        }

        .cta-button-primary {
          background: white;
          color: #0ea5e9;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
        }

        .cta-button-primary:hover {
          transform: translateY(-3px) scale(1.05);
          box-shadow: 0 15px 50px rgba(0, 0, 0, 0.3);
        }

        .cta-button-secondary {
          background: rgba(255, 255, 255, 0.15);
          backdrop-filter: blur(10px);
          color: white;
          border: 2px solid rgba(255, 255, 255, 0.3);
        }

        .cta-button-secondary:hover {
          background: rgba(255, 255, 255, 0.25);
          transform: translateY(-3px);
        }

        .cta-note {
          margin-top: 20px;
          color: rgba(255, 255, 255, 0.9);
          font-size: 14px;
        }

        .landing-footer {
          background: #111827;
          color: white;
          padding: 80px 24px 40px;
        }

        .footer-content {
          max-width: 1200px;
          margin: 0 auto;
        }

        .footer-grid {
          display: grid;
          grid-template-columns: 2fr repeat(4, 1fr);
          gap: 40px;
          margin-bottom: 48px;
        }

        .footer-logo {
          font-size: 24px;
          font-weight: 700;
          margin-bottom: 16px;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .footer-logo span {
          font-size: 28px;
        }

        .footer-description {
          color: #9ca3af;
          line-height: 1.6;
          margin-bottom: 20px;
          max-width: 320px;
          font-size: 14px;
        }

        .footer-socials {
          display: flex;
          gap: 12px;
        }

        .footer-social-link {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: #1f2937;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          text-decoration: none;
          font-weight: 700;
          font-size: 14px;
          transition: all 0.3s ease;
        }

        .footer-social-link:hover {
          background: #0ea5e9;
          transform: translateY(-3px);
        }

        .footer-column-title {
          font-size: 14px;
          font-weight: 700;
          margin-bottom: 16px;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: white;
        }

        .footer-links {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .footer-link {
          color: #9ca3af;
          text-decoration: none;
          font-size: 14px;
          transition: color 0.2s ease;
        }

        .footer-link:hover {
          color: #0ea5e9;
        }

        .footer-bottom {
          padding-top: 32px;
          border-top: 1px solid #1f2937;
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 16px;
        }

        .footer-copyright {
          color: #9ca3af;
          margin: 0;
          font-size: 14px;
        }

        .footer-legal-links {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
        }

        .footer-legal-link {
          color: #9ca3af;
          text-decoration: none;
          font-size: 14px;
          transition: color 0.2s ease;
        }

        .footer-legal-link:hover {
          color: #0ea5e9;
        }

        /* RESPONSIVE DESIGN */
        @media (max-width: 1200px) {
          .landing-header-content {
            padding: 0 30px;
            gap: 20px;
          }

          .landing-nav {
            gap: 6px;
          }

          .footer-grid {
            grid-template-columns: repeat(3, 1fr);
          }

          .footer-brand {
            grid-column: span 3;
          }
        }

        @media (max-width: 768px) {
          .landing-header-content {
            padding: 0 20px;
            gap: 16px;
            flex-wrap: wrap;
          }

          .landing-logo {
            font-size: 18px;
          }

          .logo-emoji {
            font-size: 24px;
          }

          .landing-nav {
            flex: 1;
            justify-content: flex-end;
            gap: 4px;
          }

          .nav-link,
          .nav-link-secondary {
            padding: 8px 12px;
            font-size: 13px;
          }

          .server-button {
            padding: 8px 16px;
            font-size: 13px;
          }

          .nav-cta-button {
            padding: 8px 18px;
            font-size: 13px;
          }

          .hero-section {
            padding: 120px 20px 60px;
          }

          .hero-stats {
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
          }

          .features-grid,
          .platforms-grid,
          .testimonials-grid {
            grid-template-columns: 1fr;
          }

          .footer-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .footer-brand {
            grid-column: span 2;
          }

          .cta-buttons {
            flex-direction: column;
          }

          .cta-button-primary,
          .cta-button-secondary {
            width: 100%;
          }
        }

        @media (max-width: 480px) {
          .landing-header-content {
            padding: 0 16px;
            gap: 12px;
          }

          .landing-logo {
            font-size: 16px;
          }

          .logo-emoji {
            font-size: 20px;
          }

          .logo-text {
            font-size: 16px;
          }

          .landing-nav {
            gap: 3px;
          }

          .nav-link,
          .nav-link-secondary {
            padding: 6px 10px;
            font-size: 11px;
          }

          .server-button {
            padding: 6px 12px;
            font-size: 11px;
          }

          .server-button span:last-child {
            display: none;
          }

          .nav-cta-button {
            padding: 6px 14px;
            font-size: 12px;
          }

          .footer-grid {
            grid-template-columns: 1fr;
          }

          .footer-brand {
            grid-column: span 1;
          }
        }

        html {
          scroll-behavior: smooth;
        }
      `}</style>
    </div>
  );
};

export default Landing_Page;