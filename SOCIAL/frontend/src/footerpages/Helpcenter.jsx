import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const HelpCenter = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    {
      icon: '🚀',
      title: 'Getting Started',
      articles: [
        'How to create your first account',
        'Connecting your social media accounts',
        'Understanding the dashboard',
        'Quick start guide for beginners'
      ]
    },
    {
      icon: '📝',
      title: 'Content Creation',
      articles: [
        'Using AI to generate content',
        'Best practices for social media posts',
        'Scheduling posts effectively',
        'Creating image and video content'
      ]
    },
    {
      icon: '📊',
      title: 'Analytics & Reports',
      articles: [
        'Understanding your analytics dashboard',
        'Tracking engagement metrics',
        'Creating custom reports',
        'Export and share analytics'
      ]
    },
    {
      icon: '👥',
      title: 'Team Management',
      articles: [
        'Adding team members',
        'Setting roles and permissions',
        'Collaboration workflows',
        'Managing multiple clients'
      ]
    },
    {
      icon: '💳',
      title: 'Billing & Plans',
      articles: [
        'Understanding pricing plans',
        'Upgrading or downgrading',
        'Payment methods',
        'Invoice and receipts'
      ]
    },
    {
      icon: '🔧',
      title: 'Troubleshooting',
      articles: [
        'Common login issues',
        'Post scheduling problems',
        'Connection errors',
        'Performance optimization'
      ]
    }
  ];

  const popularArticles = [
    { title: 'How to connect Instagram Business Account', views: '12.5K' },
    { title: 'AI Content Generation Best Practices', views: '10.2K' },
    { title: 'Understanding Analytics Dashboard', views: '8.7K' },
    { title: 'Troubleshooting Post Scheduling Issues', views: '7.3K' }
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
            Help Center
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '20px',
            lineHeight: '1.6',
            maxWidth: '800px',
            margin: '0 auto 32px'
          }}>
            Find answers, get support, and learn how to make the most of VelocityPost
          </p>

          {/* Search Bar */}
          <div style={{
            position: 'relative',
            maxWidth: '600px',
            margin: '0 auto'
          }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for help articles..."
              style={{
                width: '100%',
                padding: '16px 50px 16px 20px',
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                fontSize: '16px',
                outline: 'none',
                transition: '0.3s'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
            />
            <div style={{
              position: 'absolute',
              right: '20px',
              top: '50%',
              transform: 'translateY(-50%)',
              fontSize: '20px'
            }}>
              🔍
            </div>
          </div>
        </div>

        {/* Popular Articles */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '32px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{
            fontSize: '24px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            🔥 Popular Articles
          </h2>
          <div style={{
            display: 'grid',
            gap: '12px'
          }}>
            {popularArticles.map((article, idx) => (
              <a
                key={idx}
                href="#"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '16px 20px',
                  background: '#f9fafb',
                  borderRadius: '12px',
                  textDecoration: 'none',
                  color: '#374151',
                  transition: '0.3s',
                  border: '2px solid transparent'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#f3f4f6';
                  e.currentTarget.style.borderColor = '#667eea';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = '#f9fafb';
                  e.currentTarget.style.borderColor = 'transparent';
                }}
              >
                <span style={{ fontWeight: '600', fontSize: '15px' }}>{article.title}</span>
                <span style={{
                  fontSize: '13px',
                  color: '#6b7280',
                  background: 'white',
                  padding: '4px 12px',
                  borderRadius: '8px',
                  fontWeight: '600'
                }}>
                  {article.views} views
                </span>
              </a>
            ))}
          </div>
        </div>

        {/* Categories */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {categories.map((category, idx) => (
            <div key={idx} style={{
              background: 'white',
              borderRadius: '20px',
              padding: '32px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
            }}>
              <div style={{
                fontSize: '40px',
                marginBottom: '16px'
              }}>
                {category.icon}
              </div>
              
              <h3 style={{
                fontSize: '24px',
                fontWeight: '800',
                color: '#1f2937',
                marginBottom: '16px'
              }}>
                {category.title}
              </h3>
              
              <div style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '10px'
              }}>
                {category.articles.map((article, aidx) => (
                  <a
                    key={aidx}
                    href="#"
                    style={{
                      color: '#667eea',
                      textDecoration: 'none',
                      fontSize: '15px',
                      fontWeight: '500',
                      transition: '0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.textDecoration = 'underline'}
                    onMouseLeave={(e) => e.currentTarget.style.textDecoration = 'none'}
                  >
                    → {article}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Contact Support */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          textAlign: 'center'
        }}>
          <div style={{
            fontSize: '56px',
            marginBottom: '20px'
          }}>
            💬
          </div>
          <h2 style={{
            fontSize: '28px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '12px'
          }}>
            Still Need Help?
          </h2>
          <p style={{
            color: '#6b7280',
            fontSize: '16px',
            marginBottom: '24px',
            lineHeight: '1.6'
          }}>
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/contact" style={{
              padding: '14px 28px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              boxShadow: '0 4px 14px rgba(102, 126, 234, 0.4)'
            }}>
              Contact Support
            </Link>
            <a href="mailto:support@velocitypost.com" style={{
              padding: '14px 28px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              border: '2px solid #667eea'
            }}>
              Email Us
            </a>
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
      `}</style>
    </div>
  );
};

export default HelpCenter;