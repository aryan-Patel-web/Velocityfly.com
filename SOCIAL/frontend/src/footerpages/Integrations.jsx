import React from 'react';
import { Link } from 'react-router-dom';

const Integrations = () => {
  const integrations = [
    { name: 'Instagram', icon: '📸', status: 'Available' },
    { name: 'Facebook', icon: '📘', status: 'Available' },
    { name: 'Twitter/X', icon: '🐦', status: 'Available' },
    { name: 'LinkedIn', icon: '💼', status: 'Available' },
    { name: 'YouTube', icon: '📺', status: 'Available' },
    { name: 'TikTok', icon: '🎵', status: 'Available' },
    { name: 'Pinterest', icon: '📌', status: 'Available' },
    { name: 'Reddit', icon: '🔴', status: 'Available' },
    { name: 'WhatsApp', icon: '💬', status: 'Available' },
    { name: 'Telegram', icon: '✈️', status: 'Coming Soon' },
    { name: 'Snapchat', icon: '👻', status: 'Coming Soon' },
    { name: 'Discord', icon: '🎮', status: 'Coming Soon' }
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>Integrations</h1>
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto' }}>Connect all your favorite platforms in one place</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px' }}>
          {integrations.map((int, idx) => (
            <div key={idx} style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>{int.icon}</div>
              <h3 style={{ fontSize: '20px', fontWeight: '800', color: '#1f2937', marginBottom: '8px' }}>{int.name}</h3>
              <span style={{ display: 'inline-block', padding: '4px 12px', background: int.status === 'Available' ? '#d1fae5' : '#fef3c7', color: int.status === 'Available' ? '#065f46' : '#92400e', borderRadius: '8px', fontSize: '12px', fontWeight: '700' }}>{int.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Integrations;