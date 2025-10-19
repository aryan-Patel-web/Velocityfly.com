import React from 'react';
import { Link } from 'react-router-dom';

const About = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '1100px',
        margin: '0 auto'
      }}>
        {/* Header */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
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
            About VelocityPost
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '20px',
            lineHeight: '1.6',
            maxWidth: '800px'
          }}>
            We're on a mission to revolutionize social media management with AI-powered automation that saves time, boosts engagement, and helps businesses grow faster.
          </p>
        </div>

        {/* Mission & Vision */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '24px',
          marginBottom: '32px'
        }}>
          <div style={{
            background: 'white',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '24px',
              fontSize: '32px'
            }}>
              🎯
            </div>
            <h2 style={{
              fontSize: '28px',
              fontWeight: '800',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Our Mission
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              To empower businesses of all sizes with intelligent automation tools that make social media management effortless, efficient, and effective.
            </p>
          </div>

          <div style={{
            background: 'white',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              borderRadius: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '24px',
              fontSize: '32px'
            }}>
              🚀
            </div>
            <h2 style={{
              fontSize: '28px',
              fontWeight: '800',
              color: '#1f2937',
              marginBottom: '16px'
            }}>
              Our Vision
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: '16px',
              lineHeight: '1.8'
            }}>
              To become the world's leading AI-powered social media platform, helping millions of businesses connect with their audiences authentically and efficiently.
            </p>
          </div>
        </div>

        {/* Story */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '24px'
          }}>
            Our Story
          </h2>
          <div style={{
            color: '#374151',
            fontSize: '16px',
            lineHeight: '1.8'
          }}>
            <p style={{ marginBottom: '16px' }}>
              VelocityPost was founded in 2024 by a team of entrepreneurs and engineers who experienced firsthand the challenges of managing multiple social media accounts while running a business.
            </p>
            <p style={{ marginBottom: '16px' }}>
              We saw business owners spending hours every day creating content, scheduling posts, and trying to maintain a consistent presence across platforms. We knew there had to be a better way.
            </p>
            <p style={{ marginBottom: '16px' }}>
              Combining our expertise in artificial intelligence, social media marketing, and software development, we built VelocityPost—a platform that automates the tedious parts of social media management while maintaining authenticity and engagement.
            </p>
            <p>
              Today, we serve thousands of businesses worldwide, from solo entrepreneurs to enterprise teams, helping them save time and achieve better results on social media.
            </p>
          </div>
        </div>

        {/* Values */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '32px',
            textAlign: 'center'
          }}>
            Our Core Values
          </h2>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '24px'
          }}>
            {[
              {
                icon: '💡',
                title: 'Innovation',
                desc: 'We constantly push boundaries to deliver cutting-edge AI solutions'
              },
              {
                icon: '🤝',
                title: 'Customer First',
                desc: 'Your success is our success. We listen, adapt, and deliver'
              },
              {
                icon: '🔒',
                title: 'Security',
                desc: 'Your data privacy and security are our top priorities'
              },
              {
                icon: '⚡',
                title: 'Efficiency',
                desc: 'We help you do more with less time and effort'
              },
              {
                icon: '🎨',
                title: 'Quality',
                desc: 'We never compromise on the quality of our product'
              },
              {
                icon: '🌍',
                title: 'Accessibility',
                desc: 'Powerful tools accessible to businesses of all sizes'
              }
            ].map((value, idx) => (
              <div key={idx} style={{
                background: '#f9fafb',
                padding: '28px',
                borderRadius: '16px',
                textAlign: 'center',
                border: '2px solid #e5e7eb'
              }}>
                <div style={{
                  fontSize: '40px',
                  marginBottom: '16px'
                }}>
                  {value.icon}
                </div>
                <h3 style={{
                  fontSize: '20px',
                  fontWeight: '700',
                  color: '#1f2937',
                  marginBottom: '12px'
                }}>
                  {value.title}
                </h3>
                <p style={{
                  color: '#6b7280',
                  fontSize: '14px',
                  lineHeight: '1.6'
                }}>
                  {value.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Team */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          marginBottom: '32px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '16px',
            textAlign: 'center'
          }}>
            Meet Our Team
          </h2>
          <p style={{
            color: '#6b7280',
            fontSize: '16px',
            textAlign: 'center',
            marginBottom: '40px'
          }}>
            Passionate professionals dedicated to your success
          </p>
          
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '32px'
          }}>
            {[
              { name: 'Sarah Johnson', role: 'CEO & Co-Founder', emoji: '👩‍💼' },
              { name: 'Michael Chen', role: 'CTO & Co-Founder', emoji: '👨‍💻' },
              { name: 'Emily Rodriguez', role: 'Head of Product', emoji: '👩‍🎨' },
              { name: 'David Kim', role: 'Head of Engineering', emoji: '👨‍🔬' }
            ].map((member, idx) => (
              <div key={idx} style={{
                textAlign: 'center'
              }}>
                <div style={{
                  width: '120px',
                  height: '120px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  fontSize: '56px'
                }}>
                  {member.emoji}
                </div>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: '#1f2937',
                  marginBottom: '6px'
                }}>
                  {member.name}
                </h3>
                <p style={{
                  color: '#667eea',
                  fontSize: '14px',
                  fontWeight: '600'
                }}>
                  {member.role}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          borderRadius: '20px',
          padding: '48px',
          textAlign: 'center',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          color: 'white'
        }}>
          <h2 style={{
            fontSize: '36px',
            fontWeight: '800',
            marginBottom: '16px'
          }}>
            Join Us on Our Journey
          </h2>
          <p style={{
            fontSize: '18px',
            marginBottom: '32px',
            opacity: 0.95
          }}>
            Be part of the social media revolution. Start your free trial today.
          </p>
          <div style={{
            display: 'flex',
            gap: '16px',
            justifyContent: 'center',
            flexWrap: 'wrap'
          }}>
            <Link to="/register" style={{
              padding: '16px 32px',
              background: 'white',
              color: '#667eea',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              boxShadow: '0 4px 14px rgba(0, 0, 0, 0.2)'
            }}>
              Get Started Free
            </Link>
            <Link to="/contact" style={{
              padding: '16px 32px',
              background: 'rgba(255, 255, 255, 0.2)',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              border: '2px solid white'
            }}>
              Contact Sales
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
          
          h2[style*="fontSize: 32px"] {
            font-size: 24px !important;
          }

          div[style*="gridTemplateColumns: '1fr 1fr'"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))'"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))'"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
};

export default About;