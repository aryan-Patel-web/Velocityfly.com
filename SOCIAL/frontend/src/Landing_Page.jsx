import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from './quickpage/AuthContext';

const Landing_Page = () => {
  const { isAuthenticated } = useAuth();
  const [activeFeature, setActiveFeature] = useState(0);
  const [hoveredPlatform, setHoveredPlatform] = useState(null);

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

  return (
    <div style={{ minHeight: '100vh', background: 'white', overflow: 'hidden' }}>
      {/* Header */}
      <header style={{
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        padding: '16px 0'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0 24px'
        }}>
          <Link to="/" style={{
            fontSize: '28px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            textDecoration: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '32px' }}>🚀</span>
            VelocityPost
          </Link>
          
          <nav style={{ display: 'flex', gap: '32px', alignItems: 'center' }}>
            <a href="#features" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', transition: 'color 0.3s' }}>Features</a>
            <a href="#platforms" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', transition: 'color 0.3s' }}>Platforms</a>
            <a href="#testimonials" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', transition: 'color 0.3s' }}>Testimonials</a>
            
            {isAuthenticated ? (
              <Link to="/facebook-instagram" style={{
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
                <Link to="/login" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px' }}>Sign In</Link>
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
        </div>
      </header>

      {/* Hero Section */}
      <section style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        position: 'relative',
        padding: '100px 24px 200px',
        overflow: 'hidden'
      }}>
        {/* Animated background elements */}
        <div style={{
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
        <div style={{
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
        
        <div style={{ maxWidth: '1400px', margin: '0 auto', position: 'relative', zIndex: 10 }}>
          {/* Badge */}
          <div style={{
            textAlign: 'center',
            marginBottom: '32px',
            animation: 'fadeInDown 1s ease-out'
          }}>
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              borderRadius: '30px',
              padding: '10px 24px',
              color: 'white',
              fontSize: '14px',
              fontWeight: '600'
            }}>
              <span style={{ fontSize: '16px' }}>✨</span>
              Trusted by 50,000+ businesses worldwide
            </span>
          </div>

          {/* Hero Text */}
          <h1 style={{
            fontSize: 'clamp(40px, 8vw, 80px)',
            fontWeight: '800',
            color: 'white',
            textAlign: 'center',
            marginBottom: '24px',
            lineHeight: '1.1',
            animation: 'fadeInUp 1s ease-out 0.2s backwards'
          }}>
            Social Media Automation
            <br />
            <span style={{
              background: 'linear-gradient(to right, #ffffff, #f0f0f0)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              Powered by AI
            </span>
          </h1>

          <p style={{
            fontSize: 'clamp(18px, 2vw, 24px)',
            color: 'rgba(255, 255, 255, 0.95)',
            textAlign: 'center',
            marginBottom: '48px',
            maxWidth: '800px',
            margin: '0 auto 48px',
            lineHeight: '1.6',
            animation: 'fadeInUp 1s ease-out 0.4s backwards'
          }}>
            Automate your Facebook, Instagram, WhatsApp, YouTube, and Reddit presence with intelligent AI. Save 20+ hours per week while boosting engagement by 5x.
          </p>

          {/* CTA Buttons */}
          <div style={{
            display: 'flex',
            gap: '20px',
            justifyContent: 'center',
            flexWrap: 'wrap',
            marginBottom: '80px',
            animation: 'fadeInUp 1s ease-out 0.6s backwards'
          }}>
            <Link to={isAuthenticated ? "/facebook-instagram" : "/register"} style={{
              padding: '18px 40px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '30px',
              fontWeight: '700',
              fontSize: '18px',
              boxShadow: '0 8px 30px rgba(0, 0, 0, 0.3)',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}>
              {isAuthenticated ? 'Go to Dashboard' : 'Start Free Trial'} →
            </Link>
            <a href="#platforms" style={{
              padding: '18px 40px',
              background: 'rgba(255, 255, 255, 0.2)',
              backdropFilter: 'blur(10px)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '30px',
              fontWeight: '600',
              fontSize: '18px',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}>
              See How It Works
            </a>
          </div>

          {/* Dashboard Preview */}
          <div style={{
            position: 'relative',
            maxWidth: '1200px',
            margin: '0 auto',
            animation: 'fadeInUp 1s ease-out 0.8s backwards'
          }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.1)',
              backdropFilter: 'blur(20px)',
              borderRadius: '24px',
              padding: '8px',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
            }}>
              <img
                src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=700&fit=crop"
                alt="Dashboard Preview"
                style={{
                  width: '100%',
                  height: 'auto',
                  borderRadius: '16px',
                  display: 'block'
                }}
              />
            </div>

            {/* Floating Cards */}
            <div style={{
              position: 'absolute',
              top: '10%',
              left: '-5%',
              width: '280px',
              background: 'white',
              borderRadius: '16px',
              padding: '20px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
              animation: 'floatSlow 15s ease-in-out infinite'
            }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>📊</div>
              <h4 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '8px', color: '#1a1a1a' }}>Analytics Dashboard</h4>
              <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>Real-time insights across all platforms</p>
            </div>

            <div style={{
              position: 'absolute',
              top: '20%',
              right: '-5%',
              width: '280px',
              background: 'white',
              borderRadius: '16px',
              padding: '20px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
              animation: 'floatSlow 18s ease-in-out infinite reverse'
            }}>
              <div style={{ fontSize: '32px', marginBottom: '12px' }}>🤖</div>
              <h4 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '8px', color: '#1a1a1a' }}>AI Content Creation</h4>
              <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>Generate engaging posts in seconds</p>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div style={{
          position: 'absolute',
          bottom: '-80px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '90%',
          maxWidth: '1200px',
          background: 'white',
          borderRadius: '24px',
          padding: '48px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
          zIndex: 20
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '40px',
            textAlign: 'center'
          }}>
            {stats.map((stat, index) => (
              <div key={index} style={{ animation: `fadeInUp 1s ease-out ${1 + index * 0.1}s backwards` }}>
                <div style={{
                  fontSize: '48px',
                  fontWeight: '800',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  marginBottom: '8px'
                }}>
                  {stat.value}
                </div>
                <div style={{ fontSize: '16px', color: '#666', fontWeight: '500' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" style={{
        padding: '180px 24px 100px',
        background: 'white'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 56px)',
              fontWeight: '800',
              color: '#1a1a1a',
              marginBottom: '20px'
            }}>
              Everything you need to dominate social media
            </h2>
            <p style={{
              fontSize: '20px',
              color: '#666',
              maxWidth: '700px',
              margin: '0 auto'
            }}>
              Powerful features designed to save time and maximize your social media impact
            </p>
          </div>

          <div style={{ display: 'flex', gap: '40px', alignItems: 'center', marginBottom: '100px', flexWrap: 'wrap' }}>
            {/* Left - Feature Tabs */}
            <div style={{ flex: 1, minWidth: '300px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {features.map((feature, index) => (
                <div
                  key={index}
                  onClick={() => setActiveFeature(index)}
                  onMouseEnter={() => setActiveFeature(index)}
                  style={{
                    padding: '32px',
                    borderRadius: '20px',
                    cursor: 'pointer',
                    transition: 'all 0.3s',
                    background: activeFeature === index 
                      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))'
                      : 'white',
                    border: `2px solid ${activeFeature === index ? '#667eea' : '#e5e7eb'}`,
                    transform: activeFeature === index ? 'translateX(10px)' : 'translateX(0)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                    <div style={{
                      width: '56px',
                      height: '56px',
                      borderRadius: '16px',
                      background: activeFeature === index 
                        ? 'linear-gradient(135deg, #667eea, #764ba2)'
                        : '#f3f4f6',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '28px',
                      transition: 'all 0.3s'
                    }}>
                      {feature.icon}
                    </div>
                    <h3 style={{
                      fontSize: '24px',
                      fontWeight: '700',
                      color: '#1a1a1a',
                      margin: 0
                    }}>
                      {feature.title}
                    </h3>
                  </div>
                  {activeFeature === index && (
                    <p style={{
                      fontSize: '16px',
                      color: '#666',
                      margin: 0,
                      lineHeight: '1.6'
                    }}>
                      {feature.description}
                    </p>
                  )}
                </div>
              ))}
            </div>

            {/* Right - Feature Image */}
            <div style={{ flex: 1, minWidth: '300px' }}>
              <div style={{
                borderRadius: '24px',
                overflow: 'hidden',
                boxShadow: '0 20px 60px rgba(0, 0, 0, 0.15)',
                position: 'relative'
              }}>
                <img
                  src={features[activeFeature].image}
                  alt={features[activeFeature].title}
                  style={{
                    width: '100%',
                    height: 'auto',
                    display: 'block',
                    transition: 'transform 0.5s'
                  }}
                />
                <div style={{
                  position: 'absolute',
                  inset: 0,
                  background: 'linear-gradient(to top, rgba(102, 126, 234, 0.3), transparent)'
                }} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section id="platforms" style={{
        padding: '100px 24px',
        background: 'linear-gradient(to bottom, #f9fafb, white)'
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 56px)',
              fontWeight: '800',
              color: '#1a1a1a',
              marginBottom: '20px'
            }}>
              Automate all your platforms
            </h2>
            <p style={{
              fontSize: '20px',
              color: '#666',
              maxWidth: '700px',
              margin: '0 auto'
            }}>
              Manage Facebook, Instagram, WhatsApp, YouTube, and Reddit from one powerful dashboard
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '32px'
          }}>
            {platforms.map((platform, index) => (
              <div
                key={index}
                onMouseEnter={() => setHoveredPlatform(index)}
                onMouseLeave={() => setHoveredPlatform(null)}
                style={{
                  background: 'white',
                  borderRadius: '24px',
                  overflow: 'hidden',
                  boxShadow: hoveredPlatform === index 
                    ? '0 20px 60px rgba(0, 0, 0, 0.15)'
                    : '0 4px 20px rgba(0, 0, 0, 0.08)',
                  transition: 'all 0.3s',
                  transform: hoveredPlatform === index ? 'translateY(-10px)' : 'translateY(0)',
                  border: `2px solid ${hoveredPlatform === index ? platform.color : 'transparent'}`
                }}
              >
                {/* Image */}
                <div style={{
                  height: '240px',
                  overflow: 'hidden',
                  position: 'relative'
                }}>
                  <img
                    src={platform.image}
                    alt={platform.name}
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      transition: 'transform 0.3s',
                      transform: hoveredPlatform === index ? 'scale(1.1)' : 'scale(1)'
                    }}
                  />
                  <div style={{
                    position: 'absolute',
                    inset: 0,
                    background: `linear-gradient(to top, ${platform.color}33, transparent)`
                  }} />
                  <div style={{
                    position: 'absolute',
                    top: '20px',
                    right: '20px',
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '32px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)'
                  }}>
                    {platform.emoji}
                  </div>
                </div>

                {/* Content */}
                <div style={{ padding: '32px' }}>
                  <h3 style={{
                    fontSize: '28px',
                    fontWeight: '700',
                    color: platform.color,
                    marginBottom: '12px'
                  }}>
                    {platform.name} Automation
                  </h3>
                  <p style={{
                    fontSize: '16px',
                    color: '#666',
                    marginBottom: '24px',
                    lineHeight: '1.6'
                  }}>
                    {platform.description}
                  </p>

                  {/* Features Grid */}
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(2, 1fr)',
                    gap: '12px',
                    marginBottom: '24px'
                  }}>
                    {platform.features.map((feature, fIndex) => (
                      <div key={fIndex} style={{
                        padding: '12px',
                        background: '#f9fafb',
                        borderRadius: '10px',
                        fontSize: '13px',
                        fontWeight: '600',
                        color: '#374151',
                        textAlign: 'center'
                      }}>
                        {feature}
                      </div>
                    ))}
                  </div>

                  <Link
                    to={isAuthenticated ? platform.route : '/register'}
                    style={{
                      display: 'block',
                      textAlign: 'center',
                      padding: '14px',
                      background: platform.color,
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '12px',
                      fontWeight: '600',
                      fontSize: '16px',
                      transition: 'all 0.3s',
                      opacity: hoveredPlatform === index ? 1 : 0.9
                    }}
                  >
                    {isAuthenticated ? `Go to ${platform.name}` : 'Get Started'} →
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" style={{
        padding: '100px 24px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.1,
          backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
          backgroundSize: '40px 40px'
        }} />
        
        <div style={{ maxWidth: '1400px', margin: '0 auto', position: 'relative' }}>
          <div style={{ textAlign: 'center', marginBottom: '80px' }}>
            <h2 style={{
              fontSize: 'clamp(32px, 5vw, 56px)',
              fontWeight: '800',
              color: 'white',
              marginBottom: '20px'
            }}>
              Loved by thousands of businesses
            </h2>
            <p style={{
              fontSize: '20px',
              color: 'rgba(255, 255, 255, 0.9)',
              maxWidth: '700px',
              margin: '0 auto'
            }}>
              See what our customers are saying about VelocityPost
            </p>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
            gap: '32px'
          }}>
            {testimonials.map((testimonial, index) => (
              <div key={index} style={{
                background: 'white',
                borderRadius: '24px',
                padding: '40px',
                boxShadow: '0 10px 40px rgba(0, 0, 0, 0.2)',
                transition: 'transform 0.3s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-10px)'}
              onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                {/* Stars */}
                <div style={{ marginBottom: '20px', display: 'flex', gap: '4px' }}>
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <span key={i} style={{ fontSize: '20px', color: '#FFA500' }}>★</span>
                  ))}
                </div>

                {/* Quote */}
                <p style={{
                  fontSize: '16px',
                  color: '#374151',
                  lineHeight: '1.7',
                  marginBottom: '24px'
                }}>
                  "{testimonial.content}"
                </p>

                {/* Author */}
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
                    <div style={{ fontWeight: '700', color: '#1a1a1a', marginBottom: '4px' }}>
                      {testimonial.name}
                    </div>
                    <div style={{ fontSize: '14px', color: '#666' }}>
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
        background: 'white',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          <h2 style={{
            fontSize: 'clamp(36px, 6vw, 64px)',
            fontWeight: '800',
            color: '#1a1a1a',
            marginBottom: '24px',
            lineHeight: '1.2'
          }}>
            Ready to transform your social media?
          </h2>
          <p style={{
            fontSize: '22px',
            color: '#666',
            marginBottom: '48px',
            lineHeight: '1.6'
          }}>
            Join 50,000+ businesses automating their social media with VelocityPost. Start your free trial today.
          </p>

          <div style={{
            display: 'flex',
            gap: '20px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to={isAuthenticated ? "/facebook-instagram" : "/register"} style={{
              padding: '20px 48px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '30px',
              fontWeight: '700',
              fontSize: '18px',
              boxShadow: '0 10px 30px rgba(102, 126, 234, 0.4)',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}>
              {isAuthenticated ? 'Go to Dashboard' : 'Start Free Trial'} →
            </Link>
            <Link to="/login" style={{
              padding: '20px 48px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '30px',
              fontWeight: '700',
              fontSize: '18px',
              border: '2px solid #667eea',
              transition: 'all 0.3s',
              display: 'inline-block'
            }}>
              Sign In
            </Link>
          </div>

          {/* Trust Badges */}
          <div style={{
            marginTop: '60px',
            paddingTop: '60px',
            borderTop: '1px solid #e5e7eb'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#9ca3af',
              marginBottom: '24px',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '1px'
            }}>
              Trusted by leading companies
            </p>
            <div style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              gap: '48px',
              flexWrap: 'wrap',
              opacity: 0.5
            }}>
              {['TechCorp', 'Digital Agency', 'E-commerce Brand', 'Startup Inc'].map((company, index) => (
                <div key={index} style={{
                  fontSize: '20px',
                  fontWeight: '700',
                  color: '#374151'
                }}>
                  {company}
                </div>
              ))}
            </div>
          </div>
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
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '48px',
            marginBottom: '60px'
          }}>
            {/* Brand */}
            <div>
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
                marginBottom: '24px'
              }}>
                AI-powered social media automation for modern businesses. Save time, boost engagement, grow faster.
              </p>
              <div style={{ display: 'flex', gap: '16px' }}>
                {['T', 'F', 'L', 'I'].map((social, idx) => (
                  <a key={idx} href="#" style={{
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
                    transition: 'all 0.3s'
                  }}>
                    {social}
                  </a>
                ))}
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '24px',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                Product
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {['Features', 'Pricing', 'Integrations', 'API'].map((item) => (
                  <a key={item} href="#" style={{
                    color: '#9ca3af',
                    textDecoration: 'none',
                    transition: 'color 0.3s'
                  }}>
                    {item}
                  </a>
                ))}
              </div>
            </div>

            {/* Company */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '24px',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                Company
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {['About', 'Blog', 'Careers', 'Contact'].map((item) => (
                  <a key={item} href="#" style={{
                    color: '#9ca3af',
                    textDecoration: 'none',
                    transition: 'color 0.3s'
                  }}>
                    {item}
                  </a>
                ))}
              </div>
            </div>

            {/* Resources */}
            <div>
              <h4 style={{
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '24px',
                textTransform: 'uppercase',
                letterSpacing: '1px'
              }}>
                Resources
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {['Help Center', 'Documentation', 'Community', 'Status'].map((item) => (
                  <a key={item} href="#" style={{
                    color: '#9ca3af',
                    textDecoration: 'none',
                    transition: 'color 0.3s'
                  }}>
                    {item}
                  </a>
                ))}
              </div>
            </div>
          </div>

          {/* Bottom */}
          <div style={{
            paddingTop: '40px',
            borderTop: '1px solid #374151',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '20px'
          }}>
            <p style={{ color: '#9ca3af', margin: 0 }}>
              © 2025 VelocityPost. All rights reserved.
            </p>
            <div style={{ display: 'flex', gap: '32px' }}>
              {['Privacy Policy', 'Terms of Service', 'Cookie Policy'].map((item) => (
                <a key={item} href="#" style={{
                  color: '#9ca3af',
                  textDecoration: 'none',
                  fontSize: '14px',
                  transition: 'color 0.3s'
                }}>
                  {item}
                </a>
              ))}
            </div>
          </div>
        </div>
      </footer>

      {/* CSS Animations */}
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

        @keyframes floatSlow {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-20px);
          }
        }

        a:hover, button:hover {
          transform: translateY(-2px);
        }

        @media (max-width: 768px) {
          header nav {
            flex-direction: column;
            gap: 16px !important;
          }
          
          .floating-card {
            display: none;
          }
        }
      `}</style>
    </div>
  );
};

export default Landing_Page;