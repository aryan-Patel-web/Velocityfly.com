import React from 'react';
import { Link } from 'react-router-dom';

const Features = () => {
  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Content Generation',
      description: 'Generate engaging, human-like content for any platform in seconds using advanced AI technology.',
      benefits: ['Save 10+ hours per week', 'Consistent brand voice', 'Multiple language support']
    },
    {
      icon: '📅',
      title: 'Smart Scheduling',
      description: 'Schedule posts across all platforms with intelligent timing based on audience engagement patterns.',
      benefits: ['Optimal posting times', 'Bulk scheduling', 'Auto-queue management']
    },
    {
      icon: '📊',
      title: 'Advanced Analytics',
      description: 'Track performance, engagement, and ROI with comprehensive analytics and insights.',
      benefits: ['Real-time metrics', 'Custom reports', 'Competitor analysis']
    },
    {
      icon: '🎨',
      title: 'Image & Video Generation',
      description: 'Create stunning visuals and videos with AI-powered design tools integrated into the platform.',
      benefits: ['AI image generation', 'Video templates', 'Brand kit integration']
    },
    {
      icon: '🔄',
      title: 'Multi-Platform Support',
      description: 'Manage all your social accounts from one dashboard - Instagram, Facebook, Twitter, LinkedIn, YouTube, and more.',
      benefits: ['8+ platforms', 'Unified inbox', 'Cross-posting']
    },
    {
      icon: '👥',
      title: 'Team Collaboration',
      description: 'Work seamlessly with your team with role-based permissions and approval workflows.',
      benefits: ['Unlimited team members', 'Approval workflows', 'Activity logs']
    },
    {
      icon: '🎯',
      title: 'Audience Targeting',
      description: 'Reach the right audience with smart targeting and segmentation tools.',
      benefits: ['Demographic targeting', 'Behavioral insights', 'A/B testing']
    },
    {
      icon: '💬',
      title: 'Auto-Reply & Chatbots',
      description: 'Never miss a message with intelligent auto-replies and AI chatbots.',
      benefits: ['24/7 availability', 'Custom responses', 'Lead qualification']
    },
    {
      icon: '📱',
      title: 'Mobile App',
      description: 'Manage your social media on-the-go with our fully-featured mobile apps.',
      benefits: ['iOS & Android', 'Push notifications', 'Offline mode']
    },
    {
      icon: '🔐',
      title: 'Enterprise Security',
      description: 'Bank-level security with encryption, 2FA, and compliance certifications.',
      benefits: ['SOC 2 compliant', 'GDPR ready', 'SSO support']
    },
    {
      icon: '🔗',
      title: 'API & Integrations',
      description: 'Connect with 100+ tools and build custom integrations with our powerful API.',
      benefits: ['REST API', 'Webhooks', 'Zapier integration']
    },
    {
      icon: '⚡',
      title: 'Automation Workflows',
      description: 'Create custom automation workflows to streamline your social media tasks.',
      benefits: ['No-code automation', 'Trigger-based actions', 'Custom rules']
    }
  ];

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          textAlign: 'center'
        }}>
          <Link to="/" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '20px'
          }}>
            ← Back to Home
          </Link>
          
          <h1 style={{
            fontSize: '48px',
            fontWeight: '900',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '16px'
          }}>
            Powerful Features
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '20px',
            lineHeight: '1.6',
            maxWidth: '800px',
            margin: '0 auto'
          }}>
            Everything you need to dominate social media, all in one intelligent platform
          </p>
        </div>

        {/* Features Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {features.map((feature, idx) => (
            <div key={idx} style={{
              background: 'white',
              borderRadius: '20px',
              padding: '32px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              transition: '0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-8px)';
              e.currentTarget.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.25)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.2)';
            }}>
              <div style={{
                fontSize: '48px',
                marginBottom: '16px'
              }}>
                {feature.icon}
              </div>
              
              <h3 style={{
                fontSize: '24px',
                fontWeight: '800',
                color: '#1f2937',
                marginBottom: '12px'
              }}>
                {feature.title}
              </h3>
              
              <p style={{
                color: '#6b7280',
                fontSize: '15px',
                lineHeight: '1.6',
                marginBottom: '20px'
              }}>
                {feature.description}
              </p>
              
              <div style={{
                background: '#f9fafb',
                padding: '16px',
                borderRadius: '12px'
              }}>
                {feature.benefits.map((benefit, bidx) => (
                  <div key={bidx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    marginBottom: bidx < feature.benefits.length - 1 ? '8px' : '0',
                    color: '#374151',
                    fontSize: '14px',
                    fontWeight: '500'
                  }}>
                    <span style={{ color: '#10b981' }}>✓</span>
                    {benefit}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '16px'
          }}>
            Ready to Get Started?
          </h2>
          <p style={{
            color: '#6b7280',
            fontSize: '18px',
            marginBottom: '32px'
          }}>
            Join thousands of businesses already using VelocityPost
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/register" style={{
              padding: '16px 32px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              boxShadow: '0 4px 14px rgba(102, 126, 234, 0.4)'
            }}>
              Start Free Trial
            </Link>
            <Link to="/pricing" style={{
              padding: '16px 32px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              border: '2px solid #667eea'
            }}>
              View Pricing
            </Link>
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          div[style*="padding: 48px"] {
            padding: 32px 24px !important;
          }
          
          h1[style*="fontSize: 48px"] {
            font-size: 32px !important;
          }
          
          div[style*="gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))'"] {
            grid-template-columns: 1fr !important;
          }
        }

        @media (max-width: 480px) {
          div[style*="fontSize: 48px"] {
            font-size: 36px !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Features;