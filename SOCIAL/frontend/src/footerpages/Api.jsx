import React from 'react';
import { Link } from 'react-router-dom';

const API = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>API Platform</h1>
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto 32px' }}>Build powerful social media tools with our comprehensive API</p>
          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link to="/documentation" style={{ padding: '14px 28px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700' }}>View Documentation</Link>
            <Link to="/register" style={{ padding: '14px 28px', background: 'white', color: '#667eea', textDecoration: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', border: '2px solid #667eea' }}>Get API Key</Link>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
          {[
            { icon: '🚀', title: 'RESTful API', desc: 'Simple, consistent REST endpoints for all operations' },
            { icon: '📡', title: 'Webhooks', desc: 'Real-time event notifications for instant updates' },
            { icon: '🔐', title: 'OAuth 2.0', desc: 'Secure authentication and authorization' },
            { icon: '📊', title: 'Rate Limits', desc: 'Fair usage with generous rate limits' },
            { icon: '💻', title: 'SDKs', desc: 'Official libraries for Python, Node.js, Ruby, PHP' },
            { icon: '📝', title: 'Detailed Docs', desc: 'Complete API reference with examples' }
          ].map((feature, idx) => (
            <div key={idx} style={{ background: 'white', borderRadius: '20px', padding: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>{feature.icon}</div>
              <h3 style={{ fontSize: '22px', fontWeight: '800', color: '#1f2937', marginBottom: '8px' }}>{feature.title}</h3>
              <p style={{ color: '#6b7280', fontSize: '15px' }}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default API;