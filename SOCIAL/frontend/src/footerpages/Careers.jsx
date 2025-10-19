import React from 'react';
import { Link } from 'react-router-dom';

const Careers = () => {
  const jobs = [
    { title: 'Senior Full Stack Engineer', dept: 'Engineering', location: 'Remote', type: 'Full-time' },
    { title: 'Product Designer', dept: 'Design', location: 'San Francisco, CA', type: 'Full-time' },
    { title: 'Customer Success Manager', dept: 'Customer Success', location: 'Remote', type: 'Full-time' },
    { title: 'Marketing Manager', dept: 'Marketing', location: 'New York, NY', type: 'Full-time' },
    { title: 'Data Scientist', dept: 'AI/ML', location: 'Remote', type: 'Full-time' }
  ];

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '40px 20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ background: 'white', borderRadius: '20px', padding: '48px', marginBottom: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
          <Link to="/" style={{ color: '#667eea', textDecoration: 'none', fontSize: '14px', fontWeight: '600', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '20px' }}>← Back to Home</Link>
          <h1 style={{ fontSize: '48px', fontWeight: '900', background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '16px' }}>Join Our Team</h1>
          <p style={{ color: '#6b7280', fontSize: '20px', maxWidth: '800px', margin: '0 auto' }}>Help us build the future of social media automation</p>
        </div>

        <div style={{ background: 'white', borderRadius: '20px', padding: '40px', marginBottom: '24px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
          <h2 style={{ fontSize: '28px', fontWeight: '800', color: '#1f2937', marginBottom: '24px' }}>Open Positions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {jobs.map((job, idx) => (
              <div key={idx} style={{ padding: '24px', background: '#f9fafb', borderRadius: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                <div>
                  <h3 style={{ fontSize: '20px', fontWeight: '700', color: '#1f2937', marginBottom: '8px' }}>{job.title}</h3>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '14px', color: '#6b7280' }}>
                    <span>🏢 {job.dept}</span>
                    <span>📍 {job.location}</span>
                    <span>⏰ {job.type}</span>
                  </div>
                </div>
                <a href="#" style={{ padding: '12px 24px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', textDecoration: 'none', borderRadius: '8px', fontSize: '14px', fontWeight: '700' }}>Apply Now</a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Careers;