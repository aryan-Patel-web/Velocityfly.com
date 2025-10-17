import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      // TODO: Replace with your actual API call
      // const response = await fetch('YOUR_API_ENDPOINT/forgot-password', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ email })
      // });
      
      // Simulating API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
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

      <div style={{
        width: '100%',
        maxWidth: '480px',
        position: 'relative',
        zIndex: 10
      }}>
        {/* Logo and Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <Link to="/" style={{
            fontSize: '36px',
            fontWeight: '800',
            color: 'white',
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '12px',
            marginBottom: '16px'
          }}>
            <span style={{ fontSize: '40px' }}>🚀</span>
            VelocityPost
          </Link>
        </div>

        {/* Main Card */}
        <div style={{
          background: 'white',
          borderRadius: '24px',
          padding: '48px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          backdropFilter: 'blur(10px)'
        }}>
          {!success ? (
            <>
              {/* Header */}
              <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                <div style={{
                  width: '80px',
                  height: '80px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 20px',
                  fontSize: '36px'
                }}>
                  🔒
                </div>
                <h2 style={{
                  fontSize: '28px',
                  fontWeight: '700',
                  color: '#1a1a1a',
                  marginBottom: '12px'
                }}>
                  Forgot Password?
                </h2>
                <p style={{
                  fontSize: '16px',
                  color: '#6b7280',
                  lineHeight: '1.6'
                }}>
                  No worries! Enter your email address and we'll send you instructions to reset your password.
                </p>
              </div>

              {/* Error Message */}
              {error && (
                <div style={{
                  padding: '14px',
                  background: '#fee2e2',
                  border: '1px solid #fca5a5',
                  borderRadius: '12px',
                  color: '#dc2626',
                  fontSize: '14px',
                  marginBottom: '24px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontSize: '18px' }}>⚠️</span>
                  {error}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit}>
                {/* Email Input */}
                <div style={{ marginBottom: '32px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '14px',
                    fontWeight: '600',
                    color: '#374151',
                    marginBottom: '8px'
                  }}>
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your.email@example.com"
                    required
                    style={{
                      width: '100%',
                      padding: '14px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '16px',
                      outline: 'none',
                      transition: 'all 0.3s',
                      boxSizing: 'border-box'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#667eea'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '16px',
                    background: loading ? '#9ca3af' : 'linear-gradient(135deg, #667eea, #764ba2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.3s',
                    boxShadow: loading ? 'none' : '0 4px 20px rgba(102, 126, 234, 0.4)',
                    marginBottom: '24px'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  {loading ? (
                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                      <span style={{
                        width: '16px',
                        height: '16px',
                        border: '2px solid white',
                        borderTop: '2px solid transparent',
                        borderRadius: '50%',
                        animation: 'spin 1s linear infinite'
                      }} />
                      Sending...
                    </span>
                  ) : (
                    'Send Reset Link'
                  )}
                </button>

                {/* Back to Login */}
                <div style={{ textAlign: 'center' }}>
                  <Link
                    to="/login"
                    style={{
                      color: '#667eea',
                      textDecoration: 'none',
                      fontSize: '14px',
                      fontWeight: '600',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '6px'
                    }}
                  >
                    ← Back to Login
                  </Link>
                </div>
              </form>
            </>
          ) : (
            /* Success State */
            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: '80px',
                height: '80px',
                background: 'linear-gradient(135deg, #10b981, #059669)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                fontSize: '40px',
                animation: 'scaleIn 0.5s ease-out'
              }}>
                ✅
              </div>
              <h2 style={{
                fontSize: '28px',
                fontWeight: '700',
                color: '#1a1a1a',
                marginBottom: '12px'
              }}>
                Check Your Email
              </h2>
              <p style={{
                fontSize: '16px',
                color: '#6b7280',
                lineHeight: '1.6',
                marginBottom: '32px'
              }}>
                We've sent password reset instructions to
                <br />
                <strong style={{ color: '#667eea' }}>{email}</strong>
              </p>

              {/* Info Box */}
              <div style={{
                padding: '16px',
                background: '#f0f9ff',
                border: '1px solid #bae6fd',
                borderRadius: '12px',
                marginBottom: '32px',
                textAlign: 'left'
              }}>
                <p style={{
                  fontSize: '14px',
                  color: '#0369a1',
                  lineHeight: '1.6',
                  margin: 0
                }}>
                  <strong>📧 Didn't receive the email?</strong>
                  <br />
                  • Check your spam/junk folder
                  <br />
                  • Make sure you entered the correct email
                  <br />
                  • Wait a few minutes and check again
                </p>
              </div>

              {/* Resend Button */}
              <button
                onClick={() => {
                  setSuccess(false);
                  setEmail('');
                }}
                style={{
                  width: '100%',
                  padding: '14px',
                  background: 'white',
                  border: '2px solid #667eea',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  color: '#667eea',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  marginBottom: '16px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = '#667eea';
                  e.currentTarget.style.color = 'white';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'white';
                  e.currentTarget.style.color = '#667eea';
                }}
              >
                Resend Email
              </button>

              {/* Back to Login */}
              <Link
                to="/login"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: '#667eea',
                  textDecoration: 'none',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                ← Back to Login
              </Link>
            </div>
          )}
        </div>

        {/* Back to Home */}
        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Link
            to="/"
            style={{
              color: 'white',
              textDecoration: 'none',
              fontSize: '14px',
              fontWeight: '500',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            ← Back to Home
          </Link>
        </div>
      </div>

      {/* Animations */}
      <style>{`
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

        @keyframes spin {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }

        @keyframes scaleIn {
          from {
            transform: scale(0);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};

export default ForgotPassword;