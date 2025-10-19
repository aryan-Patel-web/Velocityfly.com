import React from 'react';
import { Link } from 'react-router-dom';

const Blog = () => {
  const posts = [
    { title: '10 Social Media Trends for 2025', date: 'Jan 15, 2025', category: 'Trends', time: '5 min read' },
    { title: 'How AI is Transforming Content Creation', date: 'Jan 12, 2025', category: 'AI', time: '8 min read' },
    { title: 'Instagram Algorithm Updates You Need to Know', date: 'Jan 10, 2025', category: 'Instagram', time: '6 min read' },
    { title: 'Building an Effective Social Media Strategy', date: 'Jan 8, 2025', category: 'Strategy', time: '10 min read' },
    { title: 'The Power of Video Content on Social Media', date: 'Jan 5, 2025', category: 'Video', time: '7 min read' },
    { title: 'Automation Best Practices for Businesses', date: 'Jan 3, 2025', category: 'Automation', time: '9 min read' }
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>Blog</h1>
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto' }}>Insights, tips, and news about social media marketing and automation</p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '24px' }}>
          {posts.map((post, idx) => (
            <div key={idx} style={{ background: 'white', borderRadius: '20px', padding: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
              <div style={{ display: 'inline-block', padding: '6px 12px', background: '#667eea', color: 'white', borderRadius: '8px', fontSize: '12px', fontWeight: '700', marginBottom: '16px' }}>{post.category}</div>
              <h3 style={{ fontSize: '22px', fontWeight: '800', color: '#1f2937', marginBottom: '12px' }}>{post.title}</h3>
              <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#6b7280', marginBottom: '16px' }}>
                <span>📅 {post.date}</span>
                <span>⏱️ {post.time}</span>
              </div>
              <a href="#" style={{ color: '#667eea', textDecoration: 'none', fontWeight: '600', fontSize: '15px' }}>Read More →</a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Blog;