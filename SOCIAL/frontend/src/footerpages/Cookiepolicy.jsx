import React from 'react';
import { Link } from 'react-router-dom';

const CookiePolicy = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '20px',
        padding: '48px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
      }}>
        {/* Header */}
        <div style={{ marginBottom: '40px' }}>
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
            fontSize: '42px',
            fontWeight: '900',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '12px'
          }}>
            Cookie Policy
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '16px'
          }}>
            Last updated: January 2025
          </p>
        </div>

        {/* Content */}
        <div style={{
          color: '#374151',
          fontSize: '16px',
          lineHeight: '1.8'
        }}>
          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              What Are Cookies?
            </h2>
            <p style={{ marginBottom: '12px' }}>
              Cookies are small text files that are placed on your computer or mobile device when you visit a website. They are widely used to make websites work more efficiently and provide information to website owners.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              How We Use Cookies
            </h2>
            <p style={{ marginBottom: '12px' }}>
              VelocityPost uses cookies and similar tracking technologies to:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Remember your login information and preferences</li>
              <li style={{ marginBottom: '8px' }}>Understand how you use our service</li>
              <li style={{ marginBottom: '8px' }}>Improve website performance and functionality</li>
              <li style={{ marginBottom: '8px' }}>Provide personalized content and advertisements</li>
              <li style={{ marginBottom: '8px' }}>Analyze traffic and usage patterns</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Types of Cookies We Use
            </h2>

            <div style={{
              background: '#f9fafb',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#667eea',
                marginBottom: '12px'
              }}>
                1. Essential Cookies
              </h3>
              <p style={{ marginBottom: '8px' }}>
                These cookies are necessary for the website to function properly. They enable core functionality such as security, authentication, and session management.
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>
                <strong>Examples:</strong> Login sessions, security tokens, load balancing
              </p>
            </div>

            <div style={{
              background: '#f9fafb',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#667eea',
                marginBottom: '12px'
              }}>
                2. Performance Cookies
              </h3>
              <p style={{ marginBottom: '8px' }}>
                These cookies collect information about how visitors use our website, such as which pages are visited most often and error messages.
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>
                <strong>Examples:</strong> Google Analytics, page load times, error tracking
              </p>
            </div>

            <div style={{
              background: '#f9fafb',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#667eea',
                marginBottom: '12px'
              }}>
                3. Functionality Cookies
              </h3>
              <p style={{ marginBottom: '8px' }}>
                These cookies allow the website to remember choices you make and provide enhanced, personalized features.
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>
                <strong>Examples:</strong> Language preferences, theme settings, user preferences
              </p>
            </div>

            <div style={{
              background: '#f9fafb',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#667eea',
                marginBottom: '12px'
              }}>
                4. Targeting/Advertising Cookies
              </h3>
              <p style={{ marginBottom: '8px' }}>
                These cookies are used to deliver advertisements relevant to you and track campaign performance.
              </p>
              <p style={{ fontSize: '14px', color: '#6b7280' }}>
                <strong>Examples:</strong> Ad targeting, conversion tracking, retargeting
              </p>
            </div>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Third-Party Cookies
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We may use third-party services that set cookies on your device. These include:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}><strong>Google Analytics:</strong> For website analytics and performance monitoring</li>
              <li style={{ marginBottom: '8px' }}><strong>Facebook Pixel:</strong> For targeted advertising and conversion tracking</li>
              <li style={{ marginBottom: '8px' }}><strong>Stripe:</strong> For payment processing</li>
              <li style={{ marginBottom: '8px' }}><strong>Intercom:</strong> For customer support chat</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Managing Cookies
            </h2>
            <p style={{ marginBottom: '12px' }}>
              You can control and manage cookies in several ways:
            </p>

            <div style={{
              background: '#fef3c7',
              border: '2px solid #fbbf24',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#92400e',
                marginBottom: '12px'
              }}>
                Browser Settings
              </h3>
              <p style={{ marginBottom: '12px', color: '#78350f' }}>
                Most web browsers allow you to control cookies through their settings. You can:
              </p>
              <ul style={{ paddingLeft: '24px', color: '#78350f' }}>
                <li style={{ marginBottom: '6px' }}>Block all cookies</li>
                <li style={{ marginBottom: '6px' }}>Block third-party cookies</li>
                <li style={{ marginBottom: '6px' }}>Delete cookies after closing browser</li>
                <li style={{ marginBottom: '6px' }}>Set exceptions for specific websites</li>
              </ul>
            </div>

            <div style={{
              background: '#f3f4f6',
              borderRadius: '12px',
              padding: '20px',
              marginBottom: '16px'
            }}>
              <h3 style={{
                fontSize: '18px',
                fontWeight: '700',
                color: '#1f2937',
                marginBottom: '12px'
              }}>
                Browser-Specific Instructions
              </h3>
              <ul style={{ paddingLeft: '24px' }}>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Chrome:</strong> Settings → Privacy and security → Cookies
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Firefox:</strong> Options → Privacy & Security → Cookies
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Safari:</strong> Preferences → Privacy → Cookies
                </li>
                <li style={{ marginBottom: '8px' }}>
                  <strong>Edge:</strong> Settings → Cookies and site permissions
                </li>
              </ul>
            </div>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Impact of Disabling Cookies
            </h2>
            <div style={{
              background: '#fee2e2',
              border: '2px solid #ef4444',
              borderRadius: '12px',
              padding: '20px'
            }}>
              <p style={{ marginBottom: '12px', color: '#991b1b' }}>
                <strong>⚠️ Important:</strong> Disabling cookies may affect your experience on our website. Some features may not work properly, including:
              </p>
              <ul style={{ paddingLeft: '24px', color: '#991b1b' }}>
                <li style={{ marginBottom: '6px' }}>Login and authentication</li>
                <li style={{ marginBottom: '6px' }}>Saved preferences and settings</li>
                <li style={{ marginBottom: '6px' }}>Shopping cart functionality</li>
                <li style={{ marginBottom: '6px' }}>Personalized content</li>
              </ul>
            </div>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Updates to This Policy
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We may update this Cookie Policy from time to time to reflect changes in technology, legislation, or our business operations. We will notify you of any significant changes by posting the updated policy on this page.
            </p>
          </section>

          <section>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Contact Us
            </h2>
            <p style={{ marginBottom: '12px' }}>
              If you have questions about our use of cookies, please contact us:
            </p>
            <div style={{
              background: '#f3f4f6',
              padding: '20px',
              borderRadius: '12px',
              marginTop: '16px'
            }}>
              <p style={{ marginBottom: '8px' }}><strong>Email:</strong> privacy@velocitypost.com</p>
              <p style={{ marginBottom: '8px' }}><strong>Address:</strong> VelocityPost Inc., 123 Tech Street, San Francisco, CA 94105</p>
              <p><strong>Phone:</strong> +1 (555) 123-4567</p>
            </div>
          </section>
        </div>

        {/* Footer Links */}
        <div style={{
          marginTop: '48px',
          paddingTop: '24px',
          borderTop: '2px solid #e5e7eb',
          display: 'flex',
          gap: '24px',
          flexWrap: 'wrap',
          justifyContent: 'center'
        }}>
          <Link to="/privacy" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Privacy Policy
          </Link>
          <Link to="/terms" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Terms of Service
          </Link>
          <Link to="/contact" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Contact Us
          </Link>
        </div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          div[style*="padding: 48px"] {
            padding: 32px 24px !important;
          }
          
          h1[style*="fontSize: 42px"] {
            font-size: 32px !important;
          }
          
          h2[style*="fontSize: 24px"] {
            font-size: 20px !important;
          }

          h3[style*="fontSize: 18px"] {
            font-size: 16px !important;
          }
        }
      `}</style>
    </div>
  );
};

export default CookiePolicy;