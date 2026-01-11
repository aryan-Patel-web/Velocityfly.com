// import React, { useState, useEffect } from 'react';
// import { Link, Routes, Route, useLocation } from 'react-router-dom';
// import { useAuth } from './quickpage/AuthContext';
// import Header from './quickpage/Header';

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

// // Import new pages
// import HowToConnect from './footerpages/HowToConnect';
// import FeaturesShowcase from './footerpages/FeaturesShowcase';

// const Landing_Page = () => {
//   const { isAuthenticated } = useAuth();
//   const location = useLocation();
//   const [activeFeature, setActiveFeature] = useState(0);
//   const [hoveredPlatform, setHoveredPlatform] = useState(null);

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
//       image: 'https://images.unsplash.com/photo-1494790242533-d9824626793e?w=200&h=200&fit=crop',
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
//     '/privacypolicy', '/termsofservice', '/cookiepolicy',
//     '/how-to-connect', '/features-showcase'
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
//         <Route path="/how-to-connect" element={<HowToConnect />} />
//         <Route path="/features-showcase" element={<FeaturesShowcase />} />
//       </Routes>
//     );
//   }

//   // Otherwise render the landing page
//   return (
//     <div className="landing-page-container">
//       {/* Header Component */}
//       <Header />

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
//                 <Link to="/features-showcase" className="footer-link">Features</Link>
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
//                 <Link to="/how-to-connect" className="footer-link">How to Connect</Link>
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

//         /* RESPONSIVE DESIGN */
//         @media (max-width: 1200px) {
//           .footer-grid {
//             grid-template-columns: repeat(3, 1fr);
//           }

//           .footer-brand {
//             grid-column: span 3;
//           }
//         }

//         @media (max-width: 768px) {
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
import { BrowserRouter as Router, Link, useNavigate } from 'react-router-dom';

const LandingPage = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const navigate = useNavigate();

  // Auto-rotate features every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  // Smooth scroll to section
  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ 
      behavior: 'smooth' 
    });
  };

  const features = [
    {
      icon: '🚀',
      title: 'Lightning Fast',
      description: 'Deploy your applications in seconds with our optimized infrastructure'
    },
    {
      icon: '🔒',
      title: 'Enterprise Security',
      description: 'Bank-level security with end-to-end encryption and compliance'
    },
    {
      icon: '📊',
      title: 'Real-time Analytics',
      description: 'Monitor performance with detailed insights and custom dashboards'
    },
    {
      icon: '🤝',
      title: 'Seamless Integration',
      description: 'Connect with 100+ tools and services through our API ecosystem'
    }
  ];

  const platforms = [
    {
      emoji: '☁️',
      name: 'Cloud Hosting',
      description: 'Scalable cloud infrastructure',
      features: ['Auto-scaling', '99.9% uptime', 'Global CDN']
    },
    {
      emoji: '📱',
      name: 'Mobile Apps',
      description: 'Native mobile development',
      features: ['iOS & Android', 'Push notifications', 'Offline sync']
    },
    {
      emoji: '🌐',
      name: 'Web Platform',
      description: 'Modern web applications',
      features: ['PWA support', 'Real-time updates', 'SEO optimized']
    },
    {
      emoji: '🔗',
      name: 'API Gateway',
      description: 'Unified API management',
      features: ['Rate limiting', 'Authentication', 'Monitoring']
    },
    {
      emoji: '📈',
      name: 'Analytics',
      description: 'Advanced data insights',
      features: ['Custom dashboards', 'Real-time metrics', 'Export tools']
    },
    {
      emoji: '🛡️',
      name: 'Security',
      description: 'Enterprise-grade protection',
      features: ['SSL certificates', 'DDoS protection', 'Compliance']
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Chen',
      role: 'CTO',
      company: 'TechFlow',
      rating: 5,
      quote: 'This platform transformed our development workflow. We deployed 50% faster and reduced infrastructure costs significantly.',
      avatar: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'Marcus Johnson',
      role: 'Lead Developer',
      company: 'InnovateCorp',
      rating: 5,
      quote: 'The best developer experience I\'ve ever had. The analytics and monitoring tools are game-changers for our team.',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Product Manager',
      company: 'StartupXYZ',
      rating: 5,
      quote: 'Incredible ROI and seamless integration. Our time-to-market improved by 40% since switching to this platform.',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&h=150&fit=crop&crop=face'
    }
  ];

  const styles = `
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #111827;
    }

    /* Animations */
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
        transform: scale(0.9);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    @keyframes float {
      0%, 100% {
        transform: translateY(0px) rotate(0deg);
      }
      50% {
        transform: translateY(-20px) rotate(180deg);
      }
    }

    @keyframes floatAlt {
      0%, 100% {
        transform: translateY(0px) rotate(0deg);
      }
      50% {
        transform: translateY(-15px) rotate(-180deg);
      }
    }

    /* Utility Classes */
    .animate-slide-down {
      animation: slideDown 0.8s ease-out;
    }

    .animate-slide-up {
      animation: slideUp 0.8s ease-out;
    }

    .animate-fade-in {
      animation: fadeIn 1s ease-out;
    }

    .animate-scale-in {
      animation: scaleIn 0.6s ease-out;
    }

    .animate-delay-1 {
      animation-delay: 0.2s;
      animation-fill-mode: both;
    }

    .animate-delay-2 {
      animation-delay: 0.4s;
      animation-fill-mode: both;
    }

    .animate-delay-3 {
      animation-delay: 0.6s;
      animation-fill-mode: both;
    }

    .animate-delay-4 {
      animation-delay: 0.8s;
      animation-fill-mode: both;
    }

    /* Container */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 20px;
    }

    /* Header */
    .header {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: rgba(255, 255, 255, 0.95);
      backdrop-filter: blur(10px);
      z-index: 1000;
      padding: 1rem 0;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .nav {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .logo {
      font-size: clamp(1.5rem, 2.5vw, 2rem);
      font-weight: bold;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .nav-links {
      display: flex;
      list-style: none;
      gap: 2rem;
    }

    .nav-links a {
      text-decoration: none;
      color: #6b7280;
      font-weight: 500;
      transition: color 0.3s ease;
    }

    .nav-links a:hover {
      color: #0ea5e9;
    }

    .nav-cta {
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      color: white;
      padding: 0.75rem 1.5rem;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      border: none;
      cursor: pointer;
    }

    .nav-cta:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 25px rgba(14, 165, 233, 0.3);
    }

    /* Hero Section */
    .hero {
      min-height: 100vh;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      position: relative;
      overflow: hidden;
      display: flex;
      align-items: center;
      padding-top: 80px;
    }

    .floating-shape {
      position: absolute;
      opacity: 0.1;
      pointer-events: none;
    }

    .shape-1 {
      top: 10%;
      left: 10%;
      width: 100px;
      height: 100px;
      background: linear-gradient(45deg, #0ea5e9, #06b6d4);
      border-radius: 20px;
      animation: float 6s ease-in-out infinite;
    }

    .shape-2 {
      top: 60%;
      right: 15%;
      width: 80px;
      height: 80px;
      background: linear-gradient(45deg, #06b6d4, #0ea5e9);
      border-radius: 50%;
      animation: floatAlt 8s ease-in-out infinite;
    }

    .shape-3 {
      bottom: 20%;
      left: 20%;
      width: 60px;
      height: 60px;
      background: linear-gradient(45deg, #0ea5e9, #06b6d4);
      transform: rotate(45deg);
      animation: float 7s ease-in-out infinite;
    }

    .hero-content {
      text-align: center;
      max-width: 800px;
      margin: 0 auto;
    }

    .hero-badge {
      display: inline-block;
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(10px);
      padding: 0.5rem 1rem;
      border-radius: 25px;
      font-size: 0.9rem;
      color: #0ea5e9;
      font-weight: 600;
      margin-bottom: 2rem;
      border: 1px solid rgba(14, 165, 233, 0.2);
    }

    .hero-title {
      font-size: clamp(2.5rem, 6vw, 4rem);
      font-weight: bold;
      margin-bottom: 1.5rem;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4, #0ea5e9);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1.2;
    }

    .hero-subtitle {
      font-size: clamp(1.1rem, 2vw, 1.25rem);
      color: #6b7280;
      margin-bottom: 3rem;
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }

    .hero-buttons {
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 4rem;
    }

    .btn-primary {
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      color: white;
      padding: 1rem 2rem;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      border: none;
      cursor: pointer;
      font-size: 1rem;
    }

    .btn-primary:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 35px rgba(14, 165, 233, 0.4);
    }

    .btn-secondary {
      background: white;
      color: #0ea5e9;
      padding: 1rem 2rem;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      border: 2px solid #0ea5e9;
      cursor: pointer;
      font-size: 1rem;
    }

    .btn-secondary:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 35px rgba(14, 165, 233, 0.2);
      background: #f0f9ff;
    }

    .hero-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 2rem;
      max-width: 600px;
      margin: 0 auto;
    }

    .stat-item {
      text-align: center;
    }

    .stat-number {
      font-size: clamp(1.5rem, 3vw, 2rem);
      font-weight: bold;
      color: #0ea5e9;
      display: block;
    }

    .stat-label {
      color: #6b7280;
      font-size: 0.9rem;
      margin-top: 0.5rem;
    }

    /* Features Section */
    .features {
      padding: 6rem 0;
      background: white;
    }

    .section-header {
      text-align: center;
      margin-bottom: 4rem;
    }

    .section-title {
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: bold;
      margin-bottom: 1rem;
      color: #111827;
    }

    .section-subtitle {
      font-size: clamp(1rem, 2vw, 1.25rem);
      color: #6b7280;
      max-width: 600px;
      margin: 0 auto;
    }

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 2rem;
    }

    .feature-card {
      background: white;
      padding: 2rem;
      border-radius: 20px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
      border: 2px solid transparent;
      cursor: pointer;
    }

    .feature-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
      border-color: #0ea5e9;
    }

    .feature-card.active {
      border-color: #0ea5e9;
      background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    }

    .feature-icon {
      font-size: 3rem;
      margin-bottom: 1rem;
      display: block;
      transition: transform 0.3s ease;
    }

    .feature-card:hover .feature-icon {
      transform: scale(1.1) rotate(5deg);
    }

    .feature-title {
      font-size: 1.5rem;
      font-weight: bold;
      margin-bottom: 1rem;
      color: #111827;
    }

    .feature-description {
      color: #6b7280;
      line-height: 1.6;
    }

    /* Platforms Section */
    .platforms {
      padding: 6rem 0;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    }

    .platforms-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 2rem;
    }

    .platform-card {
      background: white;
      padding: 2rem;
      border-radius: 20px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      cursor: pointer;
      position: relative;
      overflow: hidden;
    }

    .platform-card:hover {
      transform: translateY(-10px);
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
    }

    .platform-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      transform: scaleX(0);
      transition: transform 0.3s ease;
    }

    .platform-card:hover::before {
      transform: scaleX(1);
    }

    .platform-emoji {
      font-size: 3rem;
      margin-bottom: 1rem;
      display: block;
      position: relative;
    }

    .platform-emoji::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 80px;
      height: 80px;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      border-radius: 50%;
      opacity: 0;
      transition: opacity 0.3s ease;
      z-index: -1;
    }

    .platform-card:hover .platform-emoji::before {
      opacity: 0.1;
    }

    .platform-name {
      font-size: 1.5rem;
      font-weight: bold;
      margin-bottom: 0.5rem;
      color: #111827;
    }

    .platform-description {
      color: #6b7280;
      margin-bottom: 1.5rem;
    }

    .platform-features {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
    }

    .platform-tag {
      background: #f0f9ff;
      color: #0ea5e9;
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 500;
    }

    .platform-arrow {
      position: absolute;
      top: 1.5rem;
      right: 1.5rem;
      font-size: 1.5rem;
      color: #0ea5e9;
      transform: translateX(10px);
      opacity: 0;
      transition: transform 0.3s ease, opacity 0.3s ease;
    }

    .platform-card:hover .platform-arrow {
      transform: translateX(0);
      opacity: 1;
    }

    /* Testimonials Section */
    .testimonials {
      padding: 6rem 0;
      background: white;
    }

    .testimonials-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 2rem;
    }

    .testimonial-card {
      background: white;
      padding: 2rem;
      border-radius: 20px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .testimonial-card:hover {
      transform: translateY(-8px);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }

    .testimonial-header {
      display: flex;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .testimonial-avatar {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      margin-right: 1rem;
      border: 3px solid #0ea5e9;
    }

    .testimonial-author {
      flex: 1;
    }

    .testimonial-name {
      font-weight: bold;
      color: #111827;
      margin-bottom: 0.25rem;
    }

    .testimonial-role {
      color: #6b7280;
      font-size: 0.9rem;
    }

    .testimonial-rating {
      display: flex;
      gap: 0.25rem;
      margin-bottom: 1rem;
    }

    .star {
      color: #fbbf24;
      font-size: 1.25rem;
    }

    .testimonial-quote {
      color: #6b7280;
      line-height: 1.6;
      font-style: italic;
    }

    /* CTA Section */
    .cta-section {
      padding: 6rem 0;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      color: white;
      text-align: center;
    }

    .cta-title {
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: bold;
      margin-bottom: 1rem;
    }

    .cta-subtitle {
      font-size: clamp(1rem, 2vw, 1.25rem);
      margin-bottom: 3rem;
      opacity: 0.9;
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }

    .cta-buttons {
      display: flex;
      gap: 1rem;
      justify-content: center;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }

    .btn-white {
      background: white;
      color: #0ea5e9;
      padding: 1rem 2rem;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.3s ease, box-shadow 0.3s ease;
      border: none;
      cursor: pointer;
      font-size: 1rem;
    }

    .btn-white:hover {
      transform: translateY(-3px);
      box-shadow: 0 15px 35px rgba(255, 255, 255, 0.3);
    }

    .btn-outline {
      background: transparent;
      color: white;
      padding: 1rem 2rem;
      border-radius: 12px;
      text-decoration: none;
      font-weight: 600;
      transition: transform 0.3s ease, background 0.3s ease;
      border: 2px solid white;
      cursor: pointer;
      font-size: 1rem;
    }

    .btn-outline:hover {
      transform: translateY(-3px);
      background: rgba(255, 255, 255, 0.1);
    }

    .trust-indicator {
      font-size: 0.9rem;
      opacity: 0.8;
    }

    /* Footer */
    .footer {
      background: #111827;
      color: white;
      padding: 4rem 0 2rem;
    }

    .footer-content {
      display: grid;
      grid-template-columns: 2fr repeat(4, 1fr);
      gap: 3rem;
      margin-bottom: 3rem;
    }

    .footer-brand h3 {
      font-size: 1.5rem;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #0ea5e9, #06b6d4);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    .footer-brand p {
      color: #9ca3af;
      margin-bottom: 1.5rem;
      line-height: 1.6;
    }

    .social-links {
      display: flex;
      gap: 1rem;
    }

    .social-link {
      width: 40px;
      height: 40px;
      background: #374151;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
      color: white;
      transition: background 0.3s ease, transform 0.3s ease;
    }

    .social-link:hover {
      background: #0ea5e9;
      transform: translateY(-2px);
    }

    .footer-column h4 {
      font-size: 1.1rem;
      margin-bottom: 1rem;
      color: white;
    }

    .footer-links {
      list-style: none;
    }

    .footer-links li {
      margin-bottom: 0.75rem;
    }

    .footer-links a {
      color: #9ca3af;
      text-decoration: none;
      transition: color 0.3s ease;
    }

    .footer-links a:hover {
      color: #0ea5e9;
    }

    .footer-bottom {
      border-top: 1px solid #374151;
      padding-top: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }

    .footer-bottom p {
      color: #9ca3af;
    }

    .footer-legal {
      display: flex;
      gap: 2rem;
    }

    .footer-legal a {
      color: #9ca3af;
      text-decoration: none;
      transition: color 0.3s ease;
    }

    .footer-legal a:hover {
      color: #0ea5e9;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
      .nav-links {
        display: none;
      }

      .hero-buttons {
        flex-direction: column;
        align-items: center;
      }

      .hero-stats {
        grid-template-columns: repeat(2, 1fr);
      }

      .features-grid {
        grid-template-columns: 1fr;
      }

      .platforms-grid {
        grid-template-columns: 1fr;
      }

      .testimonials-grid {
        grid-template-columns: 1fr;
      }

      .cta-buttons {
        flex-direction: column;
        align-items: center;
      }

      .footer-content {
        grid-template-columns: 1fr;
        text-align: center;
      }

      .footer-bottom {
        flex-direction: column;
        text-align: center;
      }

      .footer-legal {
        justify-content: center;
      }
    }

    @media (max-width: 480px) {
      .container {
        padding: 0 15px;
      }

      .hero-stats {
        grid-template-columns: 1fr;
      }

      .platforms-grid {
        grid-template-columns: 1fr;
      }

      .testimonials-grid {
        grid-template-columns: 1fr;
      }
    }
  `;

  return (
    <div>
      <style>{styles}</style>
      
      {/* Header */}
      <header className="header">
        <nav className="nav container">
          <div className="logo">SaaSPro</div>
          <ul className="nav-links">
            <li><a href="#features" onClick={() => scrollToSection('features')}>Features</a></li>
            <li><a href="#platforms" onClick={() => scrollToSection('platforms')}>Platforms</a></li>
            <li><a href="#testimonials" onClick={() => scrollToSection('testimonials')}>Testimonials</a></li>
            <li><Link to="/pricing">Pricing</Link></li>
          </ul>
          <button className="nav-cta" onClick={() => scrollToSection('cta')}>
            Get Started
          </button>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="floating-shape shape-1"></div>
        <div className="floating-shape shape-2"></div>
        <div className="floating-shape shape-3"></div>
        
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge animate-slide-down">
              🚀 New: Advanced Analytics Dashboard Available
            </div>
            
            <h1 className="hero-title animate-slide-down animate-delay-1">
              Build, Deploy, Scale with Confidence
            </h1>
            
            <p className="hero-subtitle animate-slide-down animate-delay-2">
              The most powerful SaaS platform for modern teams. Deploy faster, scale seamlessly, 
              and monitor everything with our enterprise-grade infrastructure.
            </p>
            
            <div className="hero-buttons animate-slide-up animate-delay-3">
              <button className="btn-primary" onClick={() => scrollToSection('cta')}>
                Start Free Trial
              </button>
              <button className="btn-secondary" onClick={() => scrollToSection('features')}>
                Watch Demo
              </button>
            </div>
            
            <div className="hero-stats animate-fade-in animate-delay-4">
              <div className="stat-item">
                <span className="stat-number">99.9%</span>
                <span className="stat-label">Uptime</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">50k+</span>
                <span className="stat-label">Developers</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">1M+</span>
                <span className="stat-label">Deployments</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Support</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="section-header animate-slide-up">
            <h2 className="section-title">Powerful Features for Modern Teams</h2>
            <p className="section-subtitle">
              Everything you need to build, deploy, and scale your applications with confidence
            </p>
          </div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <div 
                key={index}
                className={`feature-card animate-scale-in animate-delay-${index + 1} ${
                  activeFeature === index ? 'active' : ''
                }`}
                onMouseEnter={() => setActiveFeature(index)}
              >
                <span className="feature-icon">{feature.icon}</span>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" className="platforms">
        <div className="container">
          <div className="section-header animate-slide-up">
            <h2 className="section-title">Multi-Platform Excellence</h2>
            <p className="section-subtitle">
              Deploy across all major platforms with unified management and monitoring
            </p>
          </div>
          
          <div className="platforms-grid">
            {platforms.map((platform, index) => (
              <div 
                key={index}
                className="platform-card animate-scale-in"
                style={{animationDelay: `${index * 0.1}s`}}
                onClick={() => navigate(`/platforms/${platform.name.toLowerCase().replace(' ', '-')}`)}
              >
                <span className="platform-arrow">→</span>
                <span className="platform-emoji">{platform.emoji}</span>
                <h3 className="platform-name">{platform.name}</h3>
                <p className="platform-description">{platform.description}</p>
                <div className="platform-features">
                  {platform.features.map((feature, idx) => (
                    <span key={idx} className="platform-tag">{feature}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="testimonials">
        <div className="container">
          <div className="section-header animate-slide-up">
            <h2 className="section-title">Trusted by Industry Leaders</h2>
            <p className="section-subtitle">
              See what our customers have to say about their experience with our platform
            </p>
          </div>
          
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index}
                className="testimonial-card animate-scale-in"
                style={{animationDelay: `${index * 0.2}s`}}
              >
                <div className="testimonial-header">
                  <img 
                    src={testimonial.avatar} 
                    alt={testimonial.name}
                    className="testimonial-avatar"
                  />
                  <div className="testimonial-author">
                    <div className="testimonial-name">{testimonial.name}</div>
                    <div className="testimonial-role">{testimonial.role}, {testimonial.company}</div>
                  </div>
                </div>
                
                <div className="testimonial-rating">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} className="star">★</span>
                  ))}
                </div>
                
                <p className="testimonial-quote">"{testimonial.quote}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section id="cta" className="cta-section">
        <div className="container">
          <h2 className="cta-title animate-slide-up">Ready to Transform Your Workflow?</h2>
          <p className="cta-subtitle animate-slide-up animate-delay-1">
            Join thousands of teams already building the future with our platform. 
            Start your free trial today and experience the difference.
          </p>
          
          <div className="cta-buttons animate-slide-up animate-delay-2">
            <Link to="/signup" className="btn-white">Start Free Trial</Link>
            <Link to="/contact" className="btn-outline">Talk to Sales</Link>
          </div>
          
          <p className="trust-indicator animate-fade-in animate-delay-3">
            ✨ No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <h3>SaaSPro</h3>
              <p>
                The most powerful SaaS platform for modern teams. Build, deploy, 
                and scale with confidence using our enterprise-grade infrastructure.
              </p>
              <div className="social-links">
                <Link to="/social/twitter" className="social-link">𝕏</Link>
                <Link to="/social/linkedin" className="social-link">in</Link>
                <Link to="/social/github" className="social-link">⚡</Link>
                <Link to="/social/discord" className="social-link">💬</Link>
              </div>
            </div>
            
            <div className="footer-column">
              <h4>Product</h4>
              <ul className="footer-links">
                <li><Link to="/features">Features</Link></li>
                <li><Link to="/pricing">Pricing</Link></li>
                <li><Link to="/integrations">Integrations</Link></li>
                <li><Link to="/api">API Docs</Link></li>
                <li><Link to="/changelog">Changelog</Link></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Company</h4>
              <ul className="footer-links">
                <li><Link to="/about">About Us</Link></li>
                <li><Link to="/careers">Careers</Link></li>
                <li><Link to="/blog">Blog</Link></li>
                <li><Link to="/press">Press</Link></li>
                <li><Link to="/partners">Partners</Link></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Support</h4>
              <ul className="footer-links">
                <li><Link to="/help">Help Center</Link></li>
                <li><Link to="/contact">Contact</Link></li>
                <li><Link to="/status">Status</Link></li>
                <li><Link to="/community">Community</Link></li>
                <li><Link to="/training">Training</Link></li>
              </ul>
            </div>
            
            <div className="footer-column">
              <h4>Legal</h4>
              <ul className="footer-links">
                <li><Link to="/privacy">Privacy Policy</Link></li>
                <li><Link to="/terms">Terms of Service</Link></li>
                <li><Link to="/security">Security</Link></li>
                <li><Link to="/compliance">Compliance</Link></li>
                <li><Link to="/cookies">Cookie Policy</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="footer-bottom">
            <p>&copy; 2024 SaaSPro. All rights reserved.</p>
            <div className="footer-legal">
              <Link to="/privacy">Privacy</Link>
              <Link to="/terms">Terms</Link>
              <Link to="/sitemap">Sitemap</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

// Main App Component with Router
const App = () => {
  return (
    <Router>
      <LandingPage />
    </Router>
  );
};

export default App;
