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
      setActiveFeature((prev) => (prev + 1) % features.length);
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
      color: '#4267B2', 
      route: '/facebook-instagram', 
      features: ['AI Content Generation', 'Multi-Page Management', 'Smart Scheduling', 'Advanced Analytics'],
      description: 'Automate your Facebook presence with AI-powered content creation and intelligent scheduling.',
      image: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&h=600&fit=crop'
    },
    { 
      name: 'Instagram', 
      emoji: '📸', 
      color: '#E4405F', 
      route: '/instagram', 
      features: ['AI Image Generation', 'Smart Hashtags', 'Story Automation', 'Engagement Boost'],
      description: 'Create stunning Instagram content automatically with AI-powered images and captions.',
      image: 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&h=600&fit=crop'
    },
    { 
      name: 'WhatsApp', 
      emoji: '💬', 
      color: '#25D366', 
      route: '/whatsapp', 
      features: ['Auto Reply', 'Broadcast Messages', 'Templates', 'Chat Analytics'],
      description: 'Streamline your WhatsApp communication with automated responses and broadcast capabilities.',
      image: 'https://images.unsplash.com/photo-1611606063065-ee7946f0787a?w=800&h=600&fit=crop'
    },
    { 
      name: 'YouTube', 
      emoji: '📺', 
      color: '#FF0000', 
      route: '/youtube', 
      features: ['AI Script Writing', 'Auto Upload', 'SEO Optimization', 'Shorts Creation'],
      description: 'Grow your YouTube channel with AI-generated scripts and automated video uploads.',
      image: 'https://images.unsplash.com/photo-1611162618071-b39a2ec055fb?w=800&h=600&fit=crop'
    },
    { 
      name: 'Reddit', 
      emoji: '🔴', 
      color: '#FF4500', 
      route: '/reddit-auto', 
      features: ['Auto Posting', 'Smart Replies', 'Karma Building', 'Multi-Subreddit'],
      description: 'Build your Reddit presence with intelligent posting and automated engagement.',
      image: 'https://images.unsplash.com/photo-1634942537034-2531766767d1?w=800&h=600&fit=crop'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Content',
      description: 'Generate engaging posts, captions, and images automatically with advanced AI',
      icon: '🤖',
      image: 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop'
    },
    {
      title: 'Smart Scheduling',
      description: 'Post at optimal times for maximum engagement across all platforms',
      icon: '⚡',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop'
    },
    {
      title: 'Analytics Dashboard',
      description: 'Track performance and optimize your strategy with real-time insights',
      icon: '📊',
      image: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop'
    },
    {
      title: 'Multi-Platform',
      description: 'Manage all your social media accounts from one unified dashboard',
      icon: '🎯',
      image: 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop'
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
    <div style={{ minHeight: '100vh', background: 'white', overflow: 'hidden' }}>
      {/* Header */}
      <header style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: scrolled ? 'rgba(255, 255, 255, 0.98)' : 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: scrolled ? '1px solid rgba(0, 0, 0, 0.1)' : 'none',
        padding: '16px 0',
        boxShadow: scrolled ? '0 2px 20px rgba(0,0,0,0.1)' : 'none',
        transition: 'all 0.3s ease'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 24px'
        }}>
          {/* Logo */}
          <Link to="/" style={{
            fontSize: '28px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            zIndex: 1002
          }}>
            <span style={{ fontSize: '32px' }}>🚀</span>
            <span className="logo-text">VelocityPost</span>
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="desktop-nav" style={{ 
            display: 'flex', 
            gap: '32px', 
            alignItems: 'center' 
          }}>
            <button 
              onClick={() => scrollToSection('features')}
              style={{ 
                background: 'none',
                border: 'none',
                color: '#374151', 
                cursor: 'pointer',
                textDecoration: 'none', 
                fontWeight: '500', 
                fontSize: '16px', 
                transition: 'color 0.3s',
                padding: '8px 0'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#374151'}
            >
              Features
            </button>
            <button 
              onClick={() => scrollToSection('platforms')}
              style={{ 
                background: 'none',
                border: 'none',
                color: '#374151', 
                cursor: 'pointer',
                textDecoration: 'none', 
                fontWeight: '500', 
                fontSize: '16px', 
                transition: 'color 0.3s',
                padding: '8px 0'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#374151'}
            >
              Platforms
            </button>
            <button 
              onClick={() => scrollToSection('testimonials')}
              style={{ 
                background: 'none',
                border: 'none',
                color: '#374151', 
                cursor: 'pointer',
                textDecoration: 'none', 
                fontWeight: '500', 
                fontSize: '16px', 
                transition: 'color 0.3s',
                padding: '8px 0'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#374151'}
            >
              Testimonials
            </button>
            <Link 
              to="/pricing"
              style={{ 
                color: '#374151', 
                textDecoration: 'none', 
                fontWeight: '500', 
                fontSize: '16px', 
                transition: 'color 0.3s',
                padding: '8px 0'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#374151'}
            >
              Pricing
            </Link>
            
            {isAuthenticated ? (
              <Link to="/reddit-auto" style={{
                padding: '12px 28px',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '30px',
                fontWeight: '600',
                fontSize: '15px',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                transition: 'all 0.3s',
                display: 'inline-block'
              }}>
                Dashboard
              </Link>
            ) : (
              <>
                <Link to="/login" style={{ 
                  color: '#374151', 
                  textDecoration: 'none', 
                  fontWeight: '500', 
                  fontSize: '16px',
                  transition: 'color 0.3s'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#374151'}
                >
                  Sign In
                </Link>
                <Link to="/register" style={{
                  padding: '12px 28px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '30px',
                  fontWeight: '600',
                  fontSize: '15px',
                  boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                  transition: 'all 0.3s'
                }}>
                  Get Started Free
                </Link>
              </>
            )}
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="mobile-menu-btn"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            style={{
              display: 'none',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '8px',
              zIndex: 1002
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              <span style={{
                width: '25px',
                height: '3px',
                background: '#374151',
                borderRadius: '2px',
                transition: 'all 0.3s',
                transform: mobileMenuOpen ? 'rotate(45deg) translateY(8px)' : 'none'
              }} />
              <span style={{
                width: '25px',
                height: '3px',
                background: '#374151',
                borderRadius: '2px',
                transition: 'all 0.3s',
                opacity: mobileMenuOpen ? 0 : 1
              }} />
              <span style={{
                width: '25px',
                height: '3px',
                background: '#374151',
                borderRadius: '2px',
                transition: 'all 0.3s',
                transform: mobileMenuOpen ? 'rotate(-45deg) translateY(-8px)' : 'none'
              }} />
            </div>
          </button>
        </div>

        {/* Mobile Menu */}
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.5)',
          backdropFilter: 'blur(5px)',
          opacity: mobileMenuOpen ? 1 : 0,
          visibility: mobileMenuOpen ? 'visible' : 'hidden',
          transition: 'all 0.3s ease',
          zIndex: 1001
        }} onClick={() => setMobileMenuOpen(false)} />

        <div className="mobile-menu" style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '80%',
          maxWidth: '320px',
          background: 'white',
          boxShadow: '-4px 0 24px rgba(0, 0, 0, 0.2)',
          transform: mobileMenuOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s ease',
          zIndex: 1002,
          overflowY: 'auto',
          padding: '80px 24px 24px'
        }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <button 
              onClick={() => scrollToSection('features')}
              style={{
                background: 'none',
                border: 'none',
                color: '#374151',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: '18px',
                fontWeight: '500',
                padding: '12px 0',
                borderBottom: '1px solid #f3f4f6'
              }}
            >
              Features
            </button>
            <button 
              onClick={() => scrollToSection('platforms')}
              style={{
                background: 'none',
                border: 'none',
                color: '#374151',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: '18px',
                fontWeight: '500',
                padding: '12px 0',
                borderBottom: '1px solid #f3f4f6'
              }}
            >
              Platforms
            </button>
            <button 
              onClick={() => scrollToSection('testimonials')}
              style={{
                background: 'none',
                border: 'none',
                color: '#374151',
                cursor: 'pointer',
                textAlign: 'left',
                fontSize: '18px',
                fontWeight: '500',
                padding: '12px 0',
                borderBottom: '1px solid #f3f4f6'
              }}
            >
              Testimonials
            </button>
            <Link 
              to="/pricing"
              onClick={() => setMobileMenuOpen(false)}
              style={{
                color: '#374151',
                textDecoration: 'none',
                fontSize: '18px',
                fontWeight: '500',
                padding: '12px 0',
                borderBottom: '1px solid #f3f4f6',
                display: 'block'
              }}
            >
              Pricing
            </Link>

            {isAuthenticated ? (
              <Link 
                to="/reddit-auto"
                onClick={() => setMobileMenuOpen(false)}
                style={{
                  padding: '14px 24px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '12px',
                  fontWeight: '600',
                  fontSize: '16px',
                  textAlign: 'center',
                  marginTop: '16px',
                  display: 'block'
                }}
              >
                Dashboard
              </Link>
            ) : (
              <>
                <Link 
                  to="/login"
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    padding: '14px 24px',
                    background: 'transparent',
                    color: '#667eea',
                    textDecoration: 'none',
                    border: '2px solid #667eea',
                    borderRadius: '12px',
                    fontWeight: '600',
                    fontSize: '16px',
                    textAlign: 'center',
                    marginTop: '16px',
                    display: 'block'
                  }}
                >
                  Sign In
                </Link>
                <Link 
                  to="/register"
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    padding: '14px 24px',
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    color: 'white',
                    textDecoration: 'none',
                    borderRadius: '12px',
                    fontWeight: '600',
                    fontSize: '16px',
                    textAlign: 'center',
                    display: 'block'
                  }}
                >
                  Get Started Free
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        position: 'relative',
        padding: '140px 24px 100px',
        overflow: 'hidden',
        display: 'flex',
        alignItems: 'center'
      }}>
        {/* Animated background elements */}
        <div className="floating-bg" style={{
          position: 'absolute',
          top: '10%',
          left: '5%',
          width: '300px',
          height: '300px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          filter: 'blur(60px)',
          animation: 'float 20s ease-in-out infinite'
        }} />
        <div className="floating-bg" style={{
          position: 'absolute',
          bottom: '10%',
          right: '5%',
          width: '400px',
          height: '400px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          filter: 'blur(80px)',
          animation: 'float 25s ease-in-out infinite reverse'
        }} />
        
        <div style={{ maxWidth: '1400px', margin: '0 auto', width: '100%', position: 'relative', zIndex: 1 }}>
          <div style={{
            textAlign: 'center',
            color: 'white'
          }}>
            {/* Badge */}
            <div style={{
              display: 'inline-block',
              padding: '10px 24px',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              borderRadius: '30px',
              marginBottom: '32px',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              fontSize: '14px',
              fontWeight: '600',
              animation: 'fadeInDown 1s ease-out'
            }}>
              🎉 New: AI-Powered Instagram Stories!
            </div>

            {/* Main Heading */}
            <h1 style={{
              fontSize: 'clamp(40px, 8vw, 72px)',
              fontWeight: '900',
              lineHeight: '1.1',
              marginBottom: '24px',
              animation: 'fadeInUp 1s ease-out 0.2s both'
            }}>
              Automate Your<br />
              <span style={{
                background: 'linear-gradient(90deg, #fff, #f0f0f0)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                Social Media Magic
              </span>
            </h1>

            {/* Subtitle */}
            <p style={{
              fontSize: 'clamp(18px, 3vw, 24px)',
              lineHeight: '1.6',
              opacity: 0.95,
              maxWidth: '700px',
              margin: '0 auto 40px',
              animation: 'fadeInUp 1s ease-out 0.4s both'
            }}>
              AI-powered automation for Facebook, Instagram, WhatsApp, YouTube & Reddit. 
              Save 20+ hours weekly while boosting engagement by 300%.
            </p>

            {/* CTA Buttons */}
            <div style={{
              display: 'flex',
              gap: '16px',
              justifyContent: 'center',
              flexWrap: 'wrap',
              animation: 'fadeInUp 1s ease-out 0.6s both'
            }}>
              <Link to="/register" style={{
                padding: '16px 40px',
                background: 'white',
                color: '#667eea',
                textDecoration: 'none',
                borderRadius: '30px',
                fontWeight: '700',
                fontSize: '18px',
                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
                transition: 'all 0.3s',
                display: 'inline-block'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-3px)';
                e.target.style.boxShadow = '0 15px 50px rgba(0, 0, 0, 0.3)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.2)';
              }}
              >
                Start Free Trial
              </Link>
              <button 
                onClick={() => scrollToSection('platforms')}
                style={{
                  padding: '16px 40px',
                  background: 'rgba(255, 255, 255, 0.15)',
                  backdropFilter: 'blur(10px)',
                  color: 'white',
                  border: '2px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '30px',
                  fontWeight: '700',
                  fontSize: '18px',
                  cursor: 'pointer',
                  transition: 'all 0.3s'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.25)';
                  e.target.style.transform = 'translateY(-3px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'rgba(255, 255, 255, 0.15)';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                Watch Demo
              </button>
            </div>

            {/* Trust Badges */}
            <div style={{
              marginTop: '60px',
              display: 'flex',
              gap: '40px',
              justifyContent: 'center',
              flexWrap: 'wrap',
              opacity: 0.9,
              animation: 'fadeInUp 1s ease-out 0.8s both'
            }}>
              {stats.map((stat, idx) => (
                <div key={idx} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '36px', fontWeight: '900', marginBottom: '8px' }}>
                    {stat.value}
                  </div>
                  <div style={{ fontSize: '14px', opacity: 0.9 }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={{
        padding: '120px 24px',
        background: 'white'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <div style={{
              display: 'inline-block',
              padding: '8px 20px',
              background: 'rgba(102, 126, 234, 0.1)',
              borderRadius: '20px',
              color: '#667eea',
              fontWeight: '700',
              fontSize: '14px',
              marginBottom: '16px'
            }}>
              FEATURES
            </div>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 48px)',
              fontWeight: '900',
              color: '#1a1a1a',
              marginBottom: '16px'
            }}>
              Everything You Need to Succeed
            </h2>
            <p style={{
              fontSize: 'clamp(16px, 2.5vw, 20px)',
              color: '#6b7280',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Powerful features designed to help you grow your social media presence effortlessly
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '32px'
          }}>
            {features.map((feature, idx) => (
              <div
                key={idx}
                onMouseEnter={() => setActiveFeature(idx)}
                style={{
                  padding: '40px',
                  background: activeFeature === idx ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'white',
                  borderRadius: '24px',
                  boxShadow: activeFeature === idx ? '0 20px 60px rgba(102, 126, 234, 0.4)' : '0 4px 20px rgba(0, 0, 0, 0.08)',
                  transition: 'all 0.4s',
                  cursor: 'pointer',
                  transform: activeFeature === idx ? 'translateY(-8px)' : 'translateY(0)',
                  border: activeFeature === idx ? 'none' : '1px solid #f3f4f6'
                }}
              >
                <div style={{
                  fontSize: '48px',
                  marginBottom: '20px',
                  filter: activeFeature === idx ? 'grayscale(0) brightness(1.2)' : 'grayscale(0)',
                  transition: 'all 0.3s'
                }}>
                  {feature.icon}
                </div>
                <h3 style={{
                  fontSize: '24px',
                  fontWeight: '800',
                  color: activeFeature === idx ? 'white' : '#1a1a1a',
                  marginBottom: '12px'
                }}>
                  {feature.title}
                </h3>
                <p style={{
                  color: activeFeature === idx ? 'rgba(255, 255, 255, 0.9)' : '#6b7280',
                  lineHeight: '1.7',
                  fontSize: '16px'
                }}>
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" style={{
        padding: '120px 24px',
        background: 'linear-gradient(180deg, #f9fafb 0%, white 100%)'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <div style={{
              display: 'inline-block',
              padding: '8px 20px',
              background: 'rgba(102, 126, 234, 0.1)',
              borderRadius: '20px',
              color: '#667eea',
              fontWeight: '700',
              fontSize: '14px',
              marginBottom: '16px'
            }}>
              PLATFORMS
            </div>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 48px)',
              fontWeight: '900',
              color: '#1a1a1a',
              marginBottom: '16px'
            }}>
              Connect All Your Channels
            </h2>
            <p style={{
              fontSize: 'clamp(16px, 2.5vw, 20px)',
              color: '#6b7280',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              Seamless integration with all major social media platforms
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '32px'
          }}>
            {platforms.map((platform, idx) => (
              <Link
                key={idx}
                to={isAuthenticated ? platform.route : '/register'}
                onMouseEnter={() => setHoveredPlatform(idx)}
                onMouseLeave={() => setHoveredPlatform(null)}
                style={{
                  display: 'block',
                  padding: '32px',
                  background: hoveredPlatform === idx ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'white',
                  borderRadius: '24px',
                  boxShadow: hoveredPlatform === idx ? '0 20px 60px rgba(102, 126, 234, 0.3)' : '0 4px 20px rgba(0, 0, 0, 0.08)',
                  transition: 'all 0.4s',
                  textDecoration: 'none',
                  transform: hoveredPlatform === idx ? 'translateY(-8px) scale(1.02)' : 'translateY(0) scale(1)',
                  border: hoveredPlatform === idx ? 'none' : '1px solid #f3f4f6',
                  cursor: 'pointer'
                }}
              >
                <div style={{ marginBottom: '20px' }}>
                  <div style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '16px',
                    background: hoveredPlatform === idx ? 'rgba(255, 255, 255, 0.2)' : 'rgba(102, 126, 234, 0.1)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '32px',
                    marginBottom: '20px',
                    transition: 'all 0.3s'
                  }}>
                    {platform.emoji}
                  </div>
                  <h3 style={{
                    fontSize: '24px',
                    fontWeight: '800',
                    color: hoveredPlatform === idx ? 'white' : '#1a1a1a',
                    marginBottom: '12px'
                  }}>
                    {platform.name}
                  </h3>
                  <p style={{
                    color: hoveredPlatform === idx ? 'rgba(255, 255, 255, 0.9)' : '#6b7280',
                    lineHeight: '1.7',
                    fontSize: '15px',
                    marginBottom: '20px'
                  }}>
                    {platform.description}
                  </p>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {platform.features.map((feat, featIdx) => (
                    <span key={featIdx} style={{
                      padding: '6px 14px',
                      background: hoveredPlatform === idx ? 'rgba(255, 255, 255, 0.2)' : 'rgba(102, 126, 234, 0.1)',
                      color: hoveredPlatform === idx ? 'white' : '#667eea',
                      borderRadius: '12px',
                      fontSize: '13px',
                      fontWeight: '600'
                    }}>
                      {feat}
                    </span>
                  ))}
                </div>
                <div style={{
                  marginTop: '24px',
                  color: hoveredPlatform === idx ? 'white' : '#667eea',
                  fontWeight: '700',
                  fontSize: '15px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  Get Started
                  <span style={{ fontSize: '20px' }}>→</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" style={{
        padding: '120px 24px',
        background: 'white'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <div style={{
              display: 'inline-block',
              padding: '8px 20px',
              background: 'rgba(102, 126, 234, 0.1)',
              borderRadius: '20px',
              color: '#667eea',
              fontWeight: '700',
              fontSize: '14px',
              marginBottom: '16px'
            }}>
              TESTIMONIALS
            </div>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 48px)',
              fontWeight: '900',
              color: '#1a1a1a',
              marginBottom: '16px'
            }}>
              Loved by Thousands
            </h2>
            <p style={{
              fontSize: 'clamp(16px, 2.5vw, 20px)',
              color: '#6b7280',
              maxWidth: '600px',
              margin: '0 auto'
            }}>
              See what our customers are saying about VelocityPost
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
            gap: '32px'
          }}>
            {testimonials.map((testimonial, idx) => (
              <div key={idx} style={{
                padding: '40px',
                background: 'white',
                borderRadius: '24px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                border: '1px solid #f3f4f6',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.12)';
                e.currentTarget.style.transform = 'translateY(-4px)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
              >
                <div style={{
                  display: 'flex',
                  gap: '4px',
                  marginBottom: '20px'
                }}>
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} style={{ color: '#fbbf24', fontSize: '20px' }}>★</span>
                  ))}
                </div>
                <p style={{
                  color: '#374151',
                  lineHeight: '1.8',
                  fontSize: '16px',
                  marginBottom: '24px',
                  fontStyle: 'italic'
                }}>
                  "{testimonial.content}"
                </p>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <img
                    src={testimonial.image}
                    alt={testimonial.name}
                    style={{
                      width: '56px',
                      height: '56px',
                      borderRadius: '50%',
                      objectFit: 'cover'
                    }}
                  />
                  <div>
                    <div style={{
                      fontWeight: '700',
                      color: '#1a1a1a',
                      fontSize: '16px',
                      marginBottom: '4px'
                    }}>
                      {testimonial.name}
                    </div>
                    <div style={{
                      color: '#6b7280',
                      fontSize: '14px'
                    }}>
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
      <section style={{
        padding: '120px 24px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div className="floating-bg" style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '600px',
          height: '600px',
          background: 'rgba(255, 255, 255, 0.1)',
          borderRadius: '50%',
          filter: 'blur(80px)'
        }} />
        
        <div style={{
          maxWidth: '900px',
          margin: '0 auto',
          textAlign: 'center',
          position: 'relative',
          zIndex: 1
        }}>
          <h2 style={{
            fontSize: 'clamp(32px, 5vw, 56px)',
            fontWeight: '900',
            color: 'white',
            marginBottom: '24px',
            lineHeight: '1.2'
          }}>
            Ready to Transform Your Social Media?
          </h2>
          <p style={{
            fontSize: 'clamp(18px, 3vw, 24px)',
            color: 'rgba(255, 255, 255, 0.95)',
            marginBottom: '40px',
            lineHeight: '1.6'
          }}>
            Join 50,000+ businesses already automating their social media success
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/register" style={{
              padding: '18px 48px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '30px',
              fontWeight: '700',
              fontSize: '18px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-3px) scale(1.05)';
              e.target.style.boxShadow = '0 15px 50px rgba(0, 0, 0, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0) scale(1)';
              e.target.style.boxShadow = '0 10px 40px rgba(0, 0, 0, 0.2)';
            }}
            >
              Start Free 14-Day Trial
            </Link>
            <Link to="/contact" style={{
              padding: '18px 48px',
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(10px)',
              color: 'white',
              textDecoration: 'none',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '30px',
              fontWeight: '700',
              fontSize: '18px',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}
            onMouseEnter={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.25)';
              e.target.style.transform = 'translateY(-3px)';
            }}
            onMouseLeave={(e) => {
              e.target.style.background = 'rgba(255, 255, 255, 0.15)';
              e.target.style.transform = 'translateY(0)';
            }}
            >
              Contact Sales
            </Link>
          </div>
          <p style={{
            marginTop: '24px',
            color: 'rgba(255, 255, 255, 0.8)',
            fontSize: '14px'
          }}>
            No credit card required • Cancel anytime • 24/7 support
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        background: '#1a1a1a',
        color: 'white',
        padding: '80px 24px 40px'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '48px',
            marginBottom: '60px'
          }}>
            {/* Brand */}
            <div style={{ gridColumn: window.innerWidth > 768 ? 'span 2' : 'span 1' }}>
              <div style={{
                fontSize: '28px',
                fontWeight: '700',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{ fontSize: '32px' }}>🚀</span>
                VelocityPost
              </div>
              <p style={{
                color: '#9ca3af',
                lineHeight: '1.6',
                marginBottom: '24px',
                maxWidth: '300px'
              }}>
                AI-powered social media automation for modern businesses. Save time, boost engagement, grow faster.
              </p>
              <div style={{ display: 'flex', gap: '12px' }}>
                {[
                  { icon: '𝕏', name: 'Twitter', url: '#' },
                  { icon: 'f', name: 'Facebook', url: '#' },
                  { icon: 'in', name: 'LinkedIn', url: '#' },
                  { icon: 'IG', name: 'Instagram', url: '#' }
                ].map((social, idx) => (
                  <a key={idx} href={social.url} style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: '#374151',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    textDecoration: 'none',
                    fontWeight: '700',
                    fontSize: '14px',
                    transition: 'all 0.3s'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = '#667eea';
                    e.target.style.transform = 'translateY(-3px)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = '#374151';
                    e.target.style.transform = 'translateY(0)';
                  }}
                  >
                    {social.icon}
                  </a>
                ))}
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '20px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                color: 'white'
              }}>
                Product
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <Link to="/features" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Features
                </Link>
                <Link to="/pricing" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Pricing
                </Link>
                <Link to="/integrations" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Integrations
                </Link>
                <Link to="/api" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  API
                </Link>
              </div>
            </div>

            {/* Company */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '20px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                color: 'white'
              }}>
                Company
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <Link to="/about" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  About
                </Link>
                <Link to="/blog" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Blog
                </Link>
                <Link to="/careers" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Careers
                </Link>
                <Link to="/contact" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Contact
                </Link>
              </div>
            </div>

            {/* Resources */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '20px',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                color: 'white'
              }}>
                Resources
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <Link to="/help" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Help Center
                </Link>
                <Link to="/documentation" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Documentation
                </Link>
                <Link to="/community" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Community
                </Link>
                <Link to="/status" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  transition: 'color 0.3s',
                  fontSize: '15px'
                }}
                onMouseEnter={(e) => e.target.style.color = '#667eea'}
                onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
                >
                  Status
                </Link>
              </div>
            </div>
          </div>

          {/* Bottom */}
          <div style={{
            paddingTop: '32px',
            borderTop: '1px solid #374151',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '20px'
          }}>
            <p style={{ color: '#9ca3af', margin: 0, fontSize: '14px' }}>
              © 2025 VelocityPost. All rights reserved.
            </p>
            <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
              <Link to="/privacy" style={{
                color: '#9ca3af',
                textDecoration: 'none',
                fontSize: '14px',
                transition: 'color 0.3s'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
              >
                Privacy Policy
              </Link>
              <Link to="/terms" style={{
                color: '#9ca3af',
                textDecoration: 'none',
                fontSize: '14px',
                transition: 'color 0.3s'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
              >
                Terms of Service
              </Link>
              <Link to="/cookie-policy" style={{
                color: '#9ca3af',
                textDecoration: 'none',
                fontSize: '14px',
                transition: 'color 0.3s'
              }}
              onMouseEnter={(e) => e.target.style.color = '#667eea'}
              onMouseLeave={(e) => e.target.style.color = '#9ca3af'}
              >
                Cookie Policy
              </Link>
            </div>
          </div>
        </div>
      </footer>

      {/* CSS Animations & Responsive Styles */}
      <style>{`
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

        * {
          box-sizing: border-box;
        }

        /* Mobile Menu Button - Show on tablets and mobile */
        @media (max-width: 1024px) {
          .mobile-menu-btn {
            display: block !important;
          }
          
          .desktop-nav {
            display: none !important;
          }

          .logo-text {
            font-size: 20px;
          }
        }

        /* Tablet Responsiveness */
        @media (max-width: 768px) {
          .floating-bg {
            width: 200px !important;
            height: 200px !important;
          }
        }

        /* Mobile Responsiveness */
        @media (max-width: 480px) {
          header {
            padding: 12px 0 !important;
          }

          .logo-text {
            display: none;
          }

          section {
            padding: 80px 16px !important;
          }

          footer {
            padding: 60px 16px 32px !important;
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