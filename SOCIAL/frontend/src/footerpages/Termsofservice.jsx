import React from 'react';
import { Link } from 'react-router-dom';

const TermsOfService = () => {
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
            Terms of Service
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
              1. Acceptance of Terms
            </h2>
            <p style={{ marginBottom: '12px' }}>
              By accessing and using VelocityPost ("Service"), you accept and agree to be bound by these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use our Service.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              2. Description of Service
            </h2>
            <p style={{ marginBottom: '12px' }}>
              VelocityPost provides AI-powered social media automation tools that allow users to:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Schedule and automate social media posts</li>
              <li style={{ marginBottom: '8px' }}>Generate AI-powered content for multiple platforms</li>
              <li style={{ marginBottom: '8px' }}>Manage multiple social media accounts</li>
              <li style={{ marginBottom: '8px' }}>Analyze performance and engagement metrics</li>
              <li style={{ marginBottom: '8px' }}>Access API for custom integrations</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              3. User Accounts
            </h2>
            <p style={{ marginBottom: '12px' }}>
              To use our Service, you must:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Be at least 18 years old</li>
              <li style={{ marginBottom: '8px' }}>Provide accurate and complete registration information</li>
              <li style={{ marginBottom: '8px' }}>Maintain the security of your account credentials</li>
              <li style={{ marginBottom: '8px' }}>Accept responsibility for all activities under your account</li>
              <li style={{ marginBottom: '8px' }}>Notify us immediately of any unauthorized access</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              4. Acceptable Use Policy
            </h2>
            <p style={{ marginBottom: '12px' }}>
              You agree not to use the Service to:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Violate any laws or regulations</li>
              <li style={{ marginBottom: '8px' }}>Post spam, malicious content, or misinformation</li>
              <li style={{ marginBottom: '8px' }}>Infringe on intellectual property rights</li>
              <li style={{ marginBottom: '8px' }}>Harass, abuse, or harm other users</li>
              <li style={{ marginBottom: '8px' }}>Attempt to gain unauthorized access to systems</li>
              <li style={{ marginBottom: '8px' }}>Use automated scripts to abuse the Service</li>
              <li style={{ marginBottom: '8px' }}>Resell or redistribute the Service without permission</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              5. Subscription and Payments
            </h2>
            <p style={{ marginBottom: '12px' }}>
              <strong>Billing:</strong> Subscription fees are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law.
            </p>
            <p style={{ marginBottom: '12px' }}>
              <strong>Price Changes:</strong> We may change our pricing with 30 days' notice. Continued use after price changes constitutes acceptance.
            </p>
            <p style={{ marginBottom: '12px' }}>
              <strong>Cancellation:</strong> You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              6. Intellectual Property
            </h2>
            <p style={{ marginBottom: '12px' }}>
              The Service and its original content, features, and functionality are owned by VelocityPost and are protected by international copyright, trademark, and other intellectual property laws.
            </p>
            <p style={{ marginBottom: '12px' }}>
              You retain ownership of content you create using our Service. By using the Service, you grant us a limited license to host, store, and display your content.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              7. Third-Party Services
            </h2>
            <p style={{ marginBottom: '12px' }}>
              Our Service integrates with third-party platforms (e.g., Facebook, Instagram, Twitter, YouTube). Your use of these platforms is subject to their respective terms of service. We are not responsible for the availability or functionality of third-party services.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              8. Limitation of Liability
            </h2>
            <p style={{ marginBottom: '12px' }}>
              To the maximum extent permitted by law, VelocityPost shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, or other intangible losses resulting from:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Your use or inability to use the Service</li>
              <li style={{ marginBottom: '8px' }}>Unauthorized access to your data</li>
              <li style={{ marginBottom: '8px' }}>Third-party conduct or content</li>
              <li style={{ marginBottom: '8px' }}>Service interruptions or errors</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              9. Warranty Disclaimer
            </h2>
            <p style={{ marginBottom: '12px' }}>
              The Service is provided "AS IS" and "AS AVAILABLE" without warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              10. Termination
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We may terminate or suspend your account and access to the Service immediately, without prior notice, for:
            </p>
            <ul style={{ paddingLeft: '24px', marginBottom: '16px' }}>
              <li style={{ marginBottom: '8px' }}>Violation of these Terms</li>
              <li style={{ marginBottom: '8px' }}>Fraudulent or illegal activity</li>
              <li style={{ marginBottom: '8px' }}>Non-payment of fees</li>
              <li style={{ marginBottom: '8px' }}>Upon your request</li>
            </ul>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              11. Governing Law
            </h2>
            <p style={{ marginBottom: '12px' }}>
              These Terms shall be governed by and construed in accordance with the laws of the State of California, United States, without regard to its conflict of law provisions.
            </p>
          </section>

          <section style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              12. Changes to Terms
            </h2>
            <p style={{ marginBottom: '12px' }}>
              We reserve the right to modify these Terms at any time. We will notify users of material changes via email or through the Service. Continued use after changes constitutes acceptance of modified Terms.
            </p>
          </section>

          <section>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              13. Contact Information
            </h2>
            <p style={{ marginBottom: '12px' }}>
              For questions about these Terms, please contact us:
            </p>
            <div style={{
              background: '#f3f4f6',
              padding: '20px',
              borderRadius: '12px',
              marginTop: '16px'
            }}>
              <p style={{ marginBottom: '8px' }}><strong>Email:</strong> legal@velocitypost.com</p>
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

export default TermsOfService;