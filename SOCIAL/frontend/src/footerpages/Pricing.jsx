import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const Pricing = () => {
  const [billingCycle, setBillingCycle] = useState('monthly');

  const plans = [
    {
      name: 'Starter',
      icon: '🚀',
      description: 'Perfect for individuals and small teams getting started',
      monthlyPrice: 29,
      annualPrice: 24,
      features: [
        '3 social accounts',
        '30 posts per month',
        'AI content generation',
        'Basic analytics',
        'Email support',
        'Mobile app access'
      ],
      color: '#667eea',
      popular: false
    },
    {
      name: 'Professional',
      icon: '💼',
      description: 'Ideal for growing businesses and agencies',
      monthlyPrice: 79,
      annualPrice: 66,
      features: [
        '10 social accounts',
        '100 posts per month',
        'Advanced AI features',
        'Advanced analytics',
        'Priority support',
        'Team collaboration (5 users)',
        'Custom branding',
        'API access'
      ],
      color: '#10b981',
      popular: true
    },
    {
      name: 'Enterprise',
      icon: '🏢',
      description: 'For large teams with advanced needs',
      monthlyPrice: 199,
      annualPrice: 166,
      features: [
        'Unlimited social accounts',
        'Unlimited posts',
        'Full AI suite',
        'Custom analytics',
        'Dedicated support',
        'Unlimited team members',
        'White-label options',
        'Advanced API access',
        'Custom integrations',
        'SLA guarantee'
      ],
      color: '#f59e0b',
      popular: false
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
            Simple, Transparent Pricing
          </h1>
          
          <p style={{
            color: '#6b7280',
            fontSize: '20px',
            lineHeight: '1.6',
            maxWidth: '800px',
            margin: '0 auto 32px'
          }}>
            Choose the perfect plan for your business. Start free, upgrade anytime.
          </p>

          {/* Billing Toggle */}
          <div style={{
            display: 'inline-flex',
            background: '#f3f4f6',
            padding: '6px',
            borderRadius: '12px',
            gap: '4px'
          }}>
            <button
              onClick={() => setBillingCycle('monthly')}
              style={{
                padding: '12px 28px',
                background: billingCycle === 'monthly' ? 'white' : 'transparent',
                color: billingCycle === 'monthly' ? '#667eea' : '#6b7280',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: 'pointer',
                transition: '0.3s',
                boxShadow: billingCycle === 'monthly' ? '0 2px 8px rgba(0,0,0,0.1)' : 'none'
              }}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              style={{
                padding: '12px 28px',
                background: billingCycle === 'annual' ? 'white' : 'transparent',
                color: billingCycle === 'annual' ? '#667eea' : '#6b7280',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: 'pointer',
                transition: '0.3s',
                boxShadow: billingCycle === 'annual' ? '0 2px 8px rgba(0,0,0,0.1)' : 'none',
                position: 'relative'
              }}
            >
              Annual
              <span style={{
                position: 'absolute',
                top: '-8px',
                right: '-8px',
                background: '#10b981',
                color: 'white',
                padding: '2px 8px',
                borderRadius: '8px',
                fontSize: '11px',
                fontWeight: '700'
              }}>
                -20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '24px',
          marginBottom: '32px'
        }}>
          {plans.map((plan, idx) => (
            <div key={idx} style={{
              background: 'white',
              borderRadius: '20px',
              padding: '40px',
              boxShadow: plan.popular ? '0 12px 48px rgba(0, 0, 0, 0.3)' : '0 8px 32px rgba(0, 0, 0, 0.2)',
              position: 'relative',
              border: plan.popular ? '3px solid #10b981' : 'none',
              transform: plan.popular ? 'scale(1.05)' : 'scale(1)',
              transition: '0.3s'
            }}>
              {plan.popular && (
                <div style={{
                  position: 'absolute',
                  top: '-12px',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: '#10b981',
                  color: 'white',
                  padding: '6px 20px',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: '700'
                }}>
                  MOST POPULAR
                </div>
              )}

              <div style={{
                fontSize: '48px',
                marginBottom: '16px'
              }}>
                {plan.icon}
              </div>

              <h3 style={{
                fontSize: '28px',
                fontWeight: '800',
                color: '#1f2937',
                marginBottom: '8px'
              }}>
                {plan.name}
              </h3>

              <p style={{
                color: '#6b7280',
                fontSize: '15px',
                marginBottom: '24px',
                lineHeight: '1.5'
              }}>
                {plan.description}
              </p>

              <div style={{ marginBottom: '24px' }}>
                <div style={{
                  fontSize: '48px',
                  fontWeight: '900',
                  color: plan.color,
                  lineHeight: '1'
                }}>
                  ${billingCycle === 'monthly' ? plan.monthlyPrice : plan.annualPrice}
                  <span style={{
                    fontSize: '20px',
                    fontWeight: '600',
                    color: '#6b7280'
                  }}>
                    /month
                  </span>
                </div>
                {billingCycle === 'annual' && (
                  <div style={{
                    fontSize: '14px',
                    color: '#10b981',
                    fontWeight: '600',
                    marginTop: '8px'
                  }}>
                    Billed ${plan.annualPrice * 12}/year
                  </div>
                )}
              </div>

              <Link to="/register" style={{
                display: 'block',
                width: '100%',
                padding: '16px',
                background: plan.popular ? plan.color : 'transparent',
                color: plan.popular ? 'white' : plan.color,
                textDecoration: 'none',
                textAlign: 'center',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: '700',
                marginBottom: '24px',
                border: plan.popular ? 'none' : `2px solid ${plan.color}`,
                boxShadow: plan.popular ? '0 4px 14px rgba(0, 0, 0, 0.2)' : 'none',
                transition: '0.3s'
              }}>
                Start Free Trial
              </Link>

              <div style={{
                borderTop: '2px solid #f3f4f6',
                paddingTop: '24px'
              }}>
                {plan.features.map((feature, fidx) => (
                  <div key={fidx} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '12px',
                    color: '#374151',
                    fontSize: '15px'
                  }}>
                    <div style={{
                      width: '20px',
                      height: '20px',
                      background: plan.color,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: 'white',
                      fontSize: '12px',
                      fontWeight: '700',
                      flexShrink: 0
                    }}>
                      ✓
                    </div>
                    {feature}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* FAQ Section */}
        <div style={{
          background: 'white',
          borderRadius: '20px',
          padding: '48px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          marginBottom: '32px'
        }}>
          <h2 style={{
            fontSize: '32px',
            fontWeight: '800',
            color: '#1f2937',
            marginBottom: '32px',
            textAlign: 'center'
          }}>
            Frequently Asked Questions
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '32px'
          }}>
            {[
              {
                q: 'Can I change plans later?',
                a: 'Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.'
              },
              {
                q: 'Is there a free trial?',
                a: 'Absolutely! All plans include a 14-day free trial. No credit card required.'
              },
              {
                q: 'What payment methods do you accept?',
                a: 'We accept all major credit cards, PayPal, and bank transfers for annual plans.'
              },
              {
                q: 'Can I cancel anytime?',
                a: 'Yes, you can cancel your subscription at any time. No questions asked.'
              }
            ].map((faq, idx) => (
              <div key={idx}>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: '700',
                  color: '#667eea',
                  marginBottom: '8px'
                }}>
                  {faq.q}
                </h3>
                <p style={{
                  color: '#6b7280',
                  fontSize: '15px',
                  lineHeight: '1.6'
                }}>
                  {faq.a}
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
            fontSize: '32px',
            fontWeight: '800',
            marginBottom: '16px'
          }}>
            Need a Custom Plan?
          </h2>
          <p style={{
            fontSize: '18px',
            marginBottom: '24px',
            opacity: 0.95
          }}>
            Contact our sales team for enterprise solutions and volume discounts
          </p>
          <Link to="/contact" style={{
            display: 'inline-block',
            padding: '16px 32px',
            background: 'white',
            color: '#667eea',
            textDecoration: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: '700',
            boxShadow: '0 4px 14px rgba(0, 0, 0, 0.2)'
          }}>
            Contact Sales
          </Link>
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
          
          div[style*="gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))'"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="gridTemplateColumns: '1fr 1fr'"] {
            grid-template-columns: 1fr !important;
          }

          div[style*="transform: 'scale(1.05)'"] {
            transform: scale(1) !important;
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

export default Pricing;