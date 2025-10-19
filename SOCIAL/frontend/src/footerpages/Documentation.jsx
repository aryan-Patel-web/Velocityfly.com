import React from 'react';
import { Link } from 'react-router-dom';

const Documentation = () => {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px 20px'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
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
            Documentation
          </h1>
          
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto' }}>
            Complete guides and API references for developers
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
          {[
            { icon: '📚', title: 'Getting Started', desc: 'Quick start guides and tutorials' },
            { icon: '🔌', title: 'API Reference', desc: 'Complete REST API documentation' },
            { icon: '💻', title: 'SDKs & Libraries', desc: 'Official SDKs for multiple languages' },
            { icon: '🔐', title: 'Authentication', desc: 'OAuth 2.0 and API key setup' },
            { icon: '📊', title: 'Webhooks', desc: 'Real-time event notifications' },
            { icon: '🎨', title: 'UI Components', desc: 'Ready-to-use React components' }
          ].map((doc, idx) => (
            <a key={idx} href="#" style={{
              background: 'white',
              borderRadius: '20px',
              padding: '32px',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
              textDecoration: 'none',
              color: 'inherit',
              transition: '0.3s'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>{doc.icon}</div>
              <h3 style={{ fontSize: '24px', fontWeight: '800', color: '#1f2937', marginBottom: '8px' }}>{doc.title}</h3>
              <p style={{ color: '#6b7280', fontSize: '15px' }}>{doc.desc}</p>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Documentation;