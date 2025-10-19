import React from 'react';
import { Link } from 'react-router-dom';

const Status = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>System Status</h1>
          <p style={{ color: '#6b7280', fontSize: '20px' }}>All systems operational</p>
        </div>

        <div style={{ background: 'white', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '24px', background: '#d1fae5', borderRadius: '12px', marginBottom: '32px' }}>
            <div style={{ width: '48px', height: '48px', background: '#10b981', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>✓</div>
            <div>
              <div style={{ fontSize: '20px', fontWeight: '700', color: '#065f46', marginBottom: '4px' }}>All Systems Operational</div>
              <div style={{ fontSize: '14px', color: '#059669' }}>No issues detected • Uptime: 99.99%</div>
            </div>
          </div>

          {['API Services', 'Web Application', 'Mobile Apps', 'Database', 'AI Services', 'CDN'].map((service, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: idx < 5 ? '1px solid #e5e7eb' : 'none' }}>
              <span style={{ fontSize: '16px', fontWeight: '600', color: '#374151' }}>{service}</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ width: '8px', height: '8px', background: '#10b981', borderRadius: '50%' }}></div>
                <span style={{ fontSize: '14px', color: '#10b981', fontWeight: '600' }}>Operational</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Status;