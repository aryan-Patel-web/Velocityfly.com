import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicy = () => {
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
            Privacy Policy
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
              1. Information We Collect
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We collect information you provide directly to us when you create an account, use our services, or communicate with us. This includes:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Account information (name, email, password)</li>
              <li style={{ marginBottom: '8px' }}>Social media account connections and credentials</li>
              <li style={{ marginBottom: '8px' }}>Content you create or upload through our platform</li>
              <li style={{ marginBottom: '8px' }}>Usage data and analytics</li>
              <li style={{ marginBottom: '8px' }}>Payment and billing information</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              2. How We Use Your Information
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We use the information we collect to:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Provide, maintain, and improve our services</li>
              <li style={{ marginBottom: '8px' }}>Process transactions and send related information</li>
              <li style={{ marginBottom: '8px' }}>Send you technical notices and support messages</li>
              <li style={{ marginBottom: '8px' }}>Respond to your comments and questions</li>
              <li style={{ marginBottom: '8px' }}>Analyze usage patterns and optimize user experience</li>
              <li style={{ marginBottom: '8px' }}>Protect against fraudulent or illegal activity</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              3. Information Sharing
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We do not sell your personal information. We may share your information only in the following circumstances:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>With your consent or at your direction</li>
              <li style={{ marginBottom: '8px' }}>With service providers who help us operate our platform</li>
              <li style={{ marginBottom: '8px' }}>To comply with legal obligations</li>
              <li style={{ marginBottom: '8px' }}>To protect our rights and prevent fraud</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              4. Data Security
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We implement appropriate technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. These measures include:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Encryption of data in transit and at rest</li>
              <li style={{ marginBottom: '8px' }}>Regular security assessments and updates</li>
              <li style={{ marginBottom: '8px' }}>Access controls and authentication</li>
              <li style={{ marginBottom: '8px' }}>Secure data storage infrastructure</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              5. Your Rights
            </h2>
            <p style={{ marginBottom: '12px' }}>
              You have the right to:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Access and receive a copy of your personal data</li>
              <li style={{ marginBottom: '8px' }}>Correct inaccurate or incomplete data</li>
              <li style={{ marginBottom: '8px' }}>Delete your account and associated data</li>
              <li style={{ marginBottom: '8px' }}>Object to processing of your data</li>
              <li style={{ marginBottom: '8px' }}>Export your data in a portable format</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              6. Cookies and Tracking
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We use cookies and similar tracking technologies to collect information about your browsing activities. You can control cookies through your browser settings. For more details, see our <Link to="/cookie-policy" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600' }}>Cookie Policy</Link>.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              7. Children's Privacy
            </h2>
            <p style={{ marginBottom: '12px' }}>
              Our services are not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              8. Changes to This Policy
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new policy on this page and updating the "Last updated" date.
            </p>
          </section>

          <section>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              9. Contact Us
            </h2>
            <p style={{ marginBottom: '12px' }}>
              If you have questions about this Privacy Policy, please contact us at:
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
          <Link to="/terms" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Terms of Service
          </Link>
          <Link to="/cookie-policy" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Cookie Policy
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
        }
      `}</style>
    </div>
  );
};

export default PrivacyPolicy;