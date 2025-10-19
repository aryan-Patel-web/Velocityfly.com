import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Contact = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name || !formData.email || !formData.message) {
      setStatus('error');
      return;
    }

    setLoading(true);
    
    // Simulate form submission
    setTimeout(() => {
      setStatus('success');
      setFormData({ name: '', email: '', subject: '', message: '' });
      setLoading(false);
      
      setTimeout(() => setStatus(''), 5000);
    }, 1500);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

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
            Contact Us
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '16px',
            lineHeight: '1.6'
          }}>
            Have a question or feedback? We'd love to hear from you. Send us a message and we'll respond as soon as possible.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '40px',
          marginBottom: '40px'
        }}>
          {/* Contact Info */}
          <div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '24px'
            }}>
              Get in Touch
            </h2>

            <div style={{
              background: '#f9fafb',
              padding: '24px',
              borderRadius: '12px',
              marginBottom: '20px'
            }}>
              <div style={{ marginBottom: '20px' }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                  fontSize: '24px'
                }}>
                  📧
                </div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#1f2937',
                  marginBottom: '8px'
                }}>
                  Email
                </h3>
                <a href="mailto:support@velocitypost.com" style={{
                  color: '#667eea',
                  textDecoration: 'none',
                  fontSize: '15px'
                }}>
                  support@velocitypost.com
                </a>
              </div>

              <div style={{ marginBottom: '20px' }}>
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                  fontSize: '24px'
                }}>
                  📞
                </div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#1f2937',
                  marginBottom: '8px'
                }}>
                  Phone
                </h3>
                <a href="tel:+15551234567" style={{
                  color: '#667eea',
                  textDecoration: 'none',
                  fontSize: '15px'
                }}>
                  +1 (555) 123-4567
                </a>
              </div>

              <div>
                <div style={{
                  width: '48px',
                  height: '48px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '12px',
                  fontSize: '24px'
                }}>
                  📍
                </div>
                <h3 style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#1f2937',
                  marginBottom: '8px'
                }}>
                  Address
                </h3>
                <p style={{
                  color: '#6b7280',
                  fontSize: '15px',
                  lineHeight: '1.6'
                }}>
                  123 Tech Street<br />
                  San Francisco, CA 94105<br />
                  United States
                </p>
              </div>
            </div>

            <div style={{
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))',
              padding: '20px',
              borderRadius: '12px',
              border: '2px solid rgba(102, 126, 234, 0.2)'
            }}>
              <h3 style={{
                fontSize: '16px',
                fontWeight: '700',
                color: '#667eea',
                marginBottom: '12px'
              }}>
                Business Hours
              </h3>
              <p style={{
                color: '#374151',
                fontSize: '14px',
                marginBottom: '6px'
              }}>
                Monday - Friday: 9:00 AM - 6:00 PM PST
              </p>
              <p style={{
                color: '#374151',
                fontSize: '14px'
              }}>
                Saturday - Sunday: Closed
              </p>
            </div>
          </div>

          {/* Contact Form */}
          <div>
            <h2 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#1f2937',
              marginBottom: '24px'
            }}>
              Send us a Message
            </h2>

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  Your Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '15px',
                    outline: 'none',
                    transition: '0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  placeholder="John Doe"
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  Email Address *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '15px',
                    outline: 'none',
                    transition: '0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  placeholder="john@example.com"
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  Subject
                </label>
                <input
                  type="text"
                  name="subject"
                  value={formData.subject}
                  onChange={handleChange}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '15px',
                    outline: 'none',
                    transition: '0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  placeholder="How can we help?"
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '700',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  Message *
                </label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  required
                  rows="6"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '15px',
                    outline: 'none',
                    resize: 'vertical',
                    fontFamily: 'inherit',
                    transition: '0.3s'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  placeholder="Tell us more about your inquiry..."
                />
              </div>

              {status === 'success' && (
                <div style={{
                  background: '#d1fae5',
                  border: '2px solid #10b981',
                  borderRadius: '8px',
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <p style={{
                    color: '#065f46',
                    fontSize: '15px',
                    fontWeight: '600',
                    margin: 0
                  }}>
                    ✅ Message sent successfully! We'll get back to you soon.
                  </p>
                </div>
              )}

              {status === 'error' && (
                <div style={{
                  background: '#fee2e2',
                  border: '2px solid #ef4444',
                  borderRadius: '8px',
                  padding: '16px',
                  marginBottom: '20px'
                }}>
                  <p style={{
                    color: '#991b1b',
                    fontSize: '15px',
                    fontWeight: '600',
                    margin: 0
                  }}>
                    ❌ Please fill in all required fields.
                  </p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '14px 24px',
                  background: loading ? '#9ca3af' : 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: loading ? 'none' : '0 4px 14px rgba(102, 126, 234, 0.4)',
                  transition: '0.3s'
                }}
                onMouseEnter={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.5)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = loading ? 'none' : '0 4px 14px rgba(102, 126, 234, 0.4)';
                }}
              >
                {loading ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </div>
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
          <Link to="/help" style={{
            color: '#667eea',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            Help Center
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

          div[style*="gridTemplateColumns: '1fr 1fr'"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};

export default Contact;