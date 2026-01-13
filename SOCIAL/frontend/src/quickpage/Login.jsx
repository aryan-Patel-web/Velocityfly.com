// import React, { useState, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { useAuth } from './AuthContext';

// const Login = () => {
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [error, setError] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [showPassword, setShowPassword] = useState(false);
//   const { login, isAuthenticated } = useAuth();
//   const navigate = useNavigate();

//   // Redirect if already logged in
//   useEffect(() => {
//     if (isAuthenticated) {
//       console.log('User already authenticated, redirecting...');
//       navigate('/reddit-auto', { replace: true });
//     }
//   }, [isAuthenticated, navigate]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     setError('');
//     setLoading(true);

//     console.log('🔐 Login attempt:', email);

//     try {
//       const result = await login(email, password);
      
//       console.log('Login result:', result);

//       if (result.success) {
//         console.log('✅ Login successful, redirecting to /reddit-auto');
//         navigate('/reddit-auto', { replace: true });
//       } else {
//         setError(result.error || 'Login failed. Please check your credentials.');
//       }
//     } catch (err) {
//       console.error('Login error:', err);
//       setError(err.message || 'An error occurred during login. Please try again.');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div style={{
//       minHeight: '100vh',
//       background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
//       display: 'flex',
//       alignItems: 'center',
//       justifyContent: 'center',
//       padding: '20px',
//       position: 'relative',
//       overflow: 'hidden'
//     }}>
//       {/* Animated Background Elements */}
//       <div style={{
//         position: 'absolute',
//         top: '10%',
//         left: '5%',
//         width: '300px',
//         height: '300px',
//         background: 'rgba(255, 255, 255, 0.1)',
//         borderRadius: '50%',
//         filter: 'blur(60px)',
//         animation: 'float 20s ease-in-out infinite'
//       }} />
//       <div style={{
//         position: 'absolute',
//         bottom: '10%',
//         right: '5%',
//         width: '400px',
//         height: '400px',
//         background: 'rgba(255, 255, 255, 0.1)',
//         borderRadius: '50%',
//         filter: 'blur(80px)',
//         animation: 'float 25s ease-in-out infinite reverse'
//       }} />

//       <div style={{
//         width: '100%',
//         maxWidth: '480px',
//         position: 'relative',
//         zIndex: 10
//       }}>
//         {/* Logo and Header */}
//         <div style={{ textAlign: 'center', marginBottom: '40px' }}>
//           <Link to="/" style={{
//             fontSize: '36px',
//             fontWeight: '800',
//             color: 'white',
//             textDecoration: 'none',
//             display: 'inline-flex',
//             alignItems: 'center',
//             gap: '12px',
//             marginBottom: '16px'
//           }}>
//             <span style={{ fontSize: '40px' }}>🚀</span>
//             VelocityPost
//           </Link>
//           <p style={{
//             color: 'rgba(255, 255, 255, 0.9)',
//             fontSize: '18px',
//             marginTop: '12px'
//           }}>
//             Welcome back! Sign in to your account
//           </p>
//         </div>

//         {/* Main Card */}
//         <div style={{
//           background: 'white',
//           borderRadius: '24px',
//           padding: '48px',
//           boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
//           backdropFilter: 'blur(10px)'
//         }}>
//           {/* Error Message */}
//           {error && (
//             <div style={{
//               padding: '14px',
//               background: '#fee2e2',
//               border: '1px solid #fca5a5',
//               borderRadius: '12px',
//               color: '#dc2626',
//               fontSize: '14px',
//               marginBottom: '24px',
//               display: 'flex',
//               alignItems: 'center',
//               gap: '8px'
//             }}>
//               <span style={{ fontSize: '18px' }}>⚠️</span>
//               {error}
//             </div>
//           )}

//           {/* Login Form */}
//           <form onSubmit={handleSubmit}>
//             {/* Email Input */}
//             <div style={{ marginBottom: '24px' }}>
//               <label style={{
//                 display: 'block',
//                 fontSize: '14px',
//                 fontWeight: '600',
//                 color: '#374151',
//                 marginBottom: '8px'
//               }}>
//                 Email Address
//               </label>
//               <input
//                 type="email"
//                 value={email}
//                 onChange={(e) => setEmail(e.target.value)}
//                 placeholder="your.email@example.com"
//                 required
//                 disabled={loading}
//                 style={{
//                   width: '100%',
//                   padding: '14px 16px',
//                   border: '2px solid #e5e7eb',
//                   borderRadius: '12px',
//                   fontSize: '16px',
//                   outline: 'none',
//                   transition: 'all 0.3s',
//                   boxSizing: 'border-box',
//                   opacity: loading ? 0.6 : 1
//                 }}
//                 onFocus={(e) => e.target.style.borderColor = '#667eea'}
//                 onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
//               />
//             </div>

//             {/* Password Input */}
//             <div style={{ marginBottom: '24px' }}>
//               <label style={{
//                 display: 'block',
//                 fontSize: '14px',
//                 fontWeight: '600',
//                 color: '#374151',
//                 marginBottom: '8px'
//               }}>
//                 Password
//               </label>
//               <div style={{ position: 'relative' }}>
//                 <input
//                   type={showPassword ? 'text' : 'password'}
//                   value={password}
//                   onChange={(e) => setPassword(e.target.value)}
//                   placeholder="Enter your password"
//                   required
//                   disabled={loading}
//                   style={{
//                     width: '100%',
//                     padding: '14px 48px 14px 16px',
//                     border: '2px solid #e5e7eb',
//                     borderRadius: '12px',
//                     fontSize: '16px',
//                     outline: 'none',
//                     transition: 'all 0.3s',
//                     boxSizing: 'border-box',
//                     opacity: loading ? 0.6 : 1
//                   }}
//                   onFocus={(e) => e.target.style.borderColor = '#667eea'}
//                   onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
//                 />
//                 <button
//                   type="button"
//                   onClick={() => setShowPassword(!showPassword)}
//                   disabled={loading}
//                   style={{
//                     position: 'absolute',
//                     right: '12px',
//                     top: '50%',
//                     transform: 'translateY(-50%)',
//                     background: 'none',
//                     border: 'none',
//                     cursor: loading ? 'not-allowed' : 'pointer',
//                     fontSize: '20px',
//                     padding: '4px',
//                     opacity: loading ? 0.6 : 1
//                   }}
//                 >
//                   {showPassword ? '👁️' : '👁️‍🗨️'}
//                 </button>
//               </div>
//             </div>

//             {/* Submit Button */}
//             <button
//               type="submit"
//               disabled={loading}
//               style={{
//                 width: '100%',
//                 padding: '16px',
//                 background: loading ? '#9ca3af' : 'linear-gradient(135deg, #667eea, #764ba2)',
//                 color: 'white',
//                 border: 'none',
//                 borderRadius: '12px',
//                 fontSize: '16px',
//                 fontWeight: '700',
//                 cursor: loading ? 'not-allowed' : 'pointer',
//                 transition: 'all 0.3s',
//                 boxShadow: loading ? 'none' : '0 4px 20px rgba(102, 126, 234, 0.4)',
//                 marginBottom: '24px'
//               }}
//               onMouseEnter={(e) => {
//                 if (!loading) e.currentTarget.style.transform = 'translateY(-2px)';
//               }}
//               onMouseLeave={(e) => {
//                 if (!loading) e.currentTarget.style.transform = 'translateY(0)';
//               }}
//             >
//               {loading ? (
//                 <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
//                   <span style={{ 
//                     display: 'inline-block',
//                     width: '16px',
//                     height: '16px',
//                     border: '3px solid rgba(255,255,255,0.3)',
//                     borderTopColor: 'white',
//                     borderRadius: '50%',
//                     animation: 'spin 0.8s linear infinite'
//                   }}></span>
//                   Signing in...
//                 </span>
//               ) : (
//                 'Sign In'
//               )}
//             </button>

//             {/* Sign Up Link */}
//             <p style={{
//               textAlign: 'center',
//               fontSize: '14px',
//               color: '#6b7280'
//             }}>
//               Don't have an account?{' '}
//               <Link
//                 to="/register"
//                 style={{
//                   color: '#667eea',
//                   textDecoration: 'none',
//                   fontWeight: '600'
//                 }}
//               >
//                 Sign up for free
//               </Link>
//             </p>
//           </form>
//         </div>

//         {/* Back to Home */}
//         <div style={{ textAlign: 'center', marginTop: '24px' }}>
//           <Link
//             to="/"
//             style={{
//               color: 'white',
//               textDecoration: 'none',
//               fontSize: '14px',
//               fontWeight: '500',
//               display: 'inline-flex',
//               alignItems: 'center',
//               gap: '6px'
//             }}
//           >
//             ← Back to Home
//           </Link>
//         </div>
//       </div>

//       {/* Animations */}
//       <style>{`
//         @keyframes float {
//           0%, 100% {
//             transform: translate(0, 0) rotate(0deg);
//           }
//           33% {
//             transform: translate(30px, -50px) rotate(120deg);
//           }
//           66% {
//             transform: translate(-20px, 30px) rotate(240deg);
//           }
//         }
        
//         @keyframes spin {
//           to { transform: rotate(360deg); }
//         }

//         @media (max-width: 640px) {
//           div[style*="padding: 48px"] {
//             padding: 32px 24px !important;
//           }
          
//           div[style*="fontSize: 36px"] {
//             font-size: 28px !important;
//           }
          
//           div[style*="fontSize: 40px"] {
//             font-size: 32px !important;
//           }
//         }
//       `}</style>
//     </div>
//   );
// };

// export default Login;



import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/reddit-auto', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const result = await login(email, password);

      if (result.success) {
        navigate('/reddit-auto', { replace: true });
      } else {
        setError(result.error || 'Login failed. Please check your credentials.');
      }
    } catch (err) {
      setError(err.message || 'An error occurred during login. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
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
          to { transform: rotate(360deg); }
        }

        @media (max-width: 640px) {
          .login-card {
            padding: 32px 24px !important;
          }
          
          .login-title {
            font-size: 28px !important;
          }
          
          .login-icon {
            font-size: 32px !important;
          }
        }
      `}</style>

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
          <div style={{ textAlign: 'center', marginBottom: '40px' }}>
            <Link to="/" className="login-title" style={{
              fontSize: '36px',
              fontWeight: '800',
              color: 'white',
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '16px'
            }}>
              <span className="login-icon" style={{ fontSize: '40px' }}>🚀</span>
              VelocityPost
            </Link>
            <p style={{
              color: 'rgba(255, 255, 255, 0.9)',
              fontSize: '18px',
              marginTop: '12px'
            }}>
              Welcome back! Sign in to your account
            </p>
          </div>

          <div className="login-card" style={{
            background: 'white',
            borderRadius: '24px',
            padding: '48px',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
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

            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '24px' }}>
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
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    border: '2px solid #e5e7eb',
                    borderRadius: '12px',
                    fontSize: '16px',
                    outline: 'none',
                    transition: 'all 0.3s',
                    boxSizing: 'border-box',
                    opacity: loading ? 0.6 : 1
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151',
                  marginBottom: '8px'
                }}>
                  Password
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                    disabled={loading}
                    style={{
                      width: '100%',
                      padding: '14px 48px 14px 16px',
                      border: '2px solid #e5e7eb',
                      borderRadius: '12px',
                      fontSize: '16px',
                      outline: 'none',
                      transition: 'all 0.3s',
                      boxSizing: 'border-box',
                      opacity: loading ? 0.6 : 1
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#667eea'}
                    onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    disabled={loading}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontSize: '20px',
                      padding: '4px',
                      opacity: loading ? 0.6 : 1
                    }}
                  >
                    {showPassword ? '👁️' : '👁️‍🗨️'}
                  </button>
                </div>
              </div>

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
                  <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                    <span style={{ 
                      display: 'inline-block',
                      width: '16px',
                      height: '16px',
                      border: '3px solid rgba(255,255,255,0.3)',
                      borderTopColor: 'white',
                      borderRadius: '50%',
                      animation: 'spin 0.8s linear infinite'
                    }}></span>
                    Signing in...
                  </span>
                ) : (
                  'Sign In'
                )}
              </button>

              <p style={{
                textAlign: 'center',
                fontSize: '14px',
                color: '#6b7280'
              }}>
                Don't have an account?{' '}
                <Link
                  to="/register"
                  style={{
                    color: '#667eea',
                    textDecoration: 'none',
                    fontWeight: '600'
                  }}
                >
                  Sign up for free
                </Link>
              </p>
            </form>
          </div>

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
      </div>
    </>
  );
};

export default Login;