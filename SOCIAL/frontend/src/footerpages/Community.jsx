import React from 'react';
import { Link } from 'react-router-dom';

const Community = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>Community</h1>
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto' }}>Connect with other VelocityPost users, share tips, and get support</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
          {[
            { icon: '💬', title: 'Discord Community', desc: 'Join 5,000+ members in our Discord server', btn: 'Join Discord' },
            { icon: '🐦', title: 'Twitter/X', desc: 'Follow us for updates and tips', btn: 'Follow @VelocityPost' },
            { icon: '📘', title: 'Facebook Group', desc: 'Connect with users on Facebook', btn: 'Join Group' },
            { icon: '💼', title: 'LinkedIn', desc: 'Professional networking and updates', btn: 'Follow on LinkedIn' },
            { icon: '📺', title: 'YouTube Channel', desc: 'Tutorials and feature demos', btn: 'Subscribe' },
            { icon: '📰', title: 'Newsletter', desc: 'Weekly tips and product updates', btn: 'Subscribe' }
          ].map((item, idx) => (
            <div key={idx} style={{ background: 'white', borderRadius: '20px', padding: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
              <div style={{ fontSize: '56px', marginBottom: '16px' }}>{item.icon}</div>
              <h3 style={{ fontSize: '24px', fontWeight: '800', color: '#1f2937', marginBottom: '12px' }}>{item.title}</h3>
              <p style={{ color: '#6b7280', fontSize: '15px', marginBottom: '20px' }}>{item.desc}</p>
              <a href="#" style={{ display: 'inline-block', padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', textDecoration: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700' }}>{item.btn}</a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Community;