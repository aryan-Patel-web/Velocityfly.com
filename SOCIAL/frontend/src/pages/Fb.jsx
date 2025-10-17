import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://agentic-u5lx.onrender.com';

const DOMAIN_CONFIGS = { education: { icon: '🎓', description: 'Educational services', sampleBusiness: 'JEE coaching institute' }, restaurant: { icon: '🍽️', description: 'Food & restaurants', sampleBusiness: 'Traditional Indian restaurant' }, tech: { icon: '💻', description: 'Technology & programming', sampleBusiness: 'AI automation platform' }, health: { icon: '💚', description: 'Health & wellness', sampleBusiness: 'Fitness coaching center' }, business: { icon: '💼', description: 'Business & entrepreneurship', sampleBusiness: 'Business consulting firm' } };

const TARGET_AUDIENCES = { 'indian_students': { label: 'Indian Students', icon: '🎓' }, 'food_lovers': { label: 'Food Lovers', icon: '🍕' }, 'tech_professionals': { label: 'Tech Professionals', icon: '💻' }, 'health_conscious': { label: 'Health Conscious', icon: '💚' }, 'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' }, 'general_users': { label: 'General Users', icon: '👥' } };

const CONTENT_STYLES = { 'engaging': 'Engaging & Interactive', 'informative': 'Informative & Educational', 'promotional': 'Promotional & Marketing', 'helpful': 'Helpful & Supportive', 'casual': 'Casual & Friendly', 'professional': 'Professional & Formal' };

const FacebookAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  const [facebookConnected, setFacebookConnected] = useState(false);
  const [facebookUsername, setFacebookUsername] = useState('');
  const [facebookPages, setFacebookPages] = useState([]);
  
  const [userProfile, setUserProfile] = useState({ domain: 'tech', businessType: 'AI automation platform', businessDescription: 'We help businesses automate their social media presence', targetAudience: 'tech_professionals', contentStyle: 'engaging', isConfigured: false });
  
  const [manualPost, setManualPost] = useState({ platform: 'facebook', title: '', content: '', pageId: '', imageUrl: '', isGenerating: false });
  
  const [autoPostConfig, setAutoPostConfig] = useState({ enabled: false, postsPerDay: 3, postingTimes: [] });
  
  const [performanceData, setPerformanceData] = useState({ postsToday: 0, totalEngagement: 0, successRate: 95 });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  useEffect(() => {
    if (!user?.email) return;
    
    const initKey = `fb_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');
    
    const initApp = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const fbConnected = urlParams.get('facebook_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) {
        showNotification(`Connection failed: ${error}`, 'error');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      if (fbConnected === 'true' && username) {
        setFacebookConnected(true);
        setFacebookUsername(username);
        updateUser({ facebook_connected: true, facebook_username: username });
        showNotification(`Facebook connected! Welcome ${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      try {
        const response = await makeAuthenticatedRequest('/api/facebook/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setFacebookConnected(true);
          setFacebookUsername(result.username);
          setFacebookPages(result.pages || []);
        }
      } catch (error) {
        console.error('Failed to check Facebook connection:', error);
      }

      try {
        const savedProfile = localStorage.getItem('fbUserProfile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          setUserProfile(profile);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }
    };

    initApp();
  }, [user, makeAuthenticatedRequest, updateUser, showNotification]);

  const handleConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Facebook...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/oauth/facebook/authorize');
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else {
        showNotification(result.error || 'Failed to start Facebook authorization', 'error');
      }
    } catch (error) {
      showNotification(`Connection failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest('/api/facebook/connection-status');
      const result = await response.json();
      
      if (result.success && result.connected) {
        showNotification(`Facebook connection verified for ${result.username}!`, 'success');
      } else {
        showNotification('Facebook not connected', 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating human-like content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: 'facebook',
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setManualPost(prev => ({
          ...prev,
          title: result.post_details?.title || result.content_preview.split('\n')[0] || 'Generated Title',
          content: result.content_preview
        }));
        showNotification(`Human-like content generated using ${result.ai_service}!`, 'success');
      } else {
        showNotification(result.error || 'AI content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, makeAuthenticatedRequest, showNotification]);

  const handleManualPost = useCallback(async (e) => {
    e.preventDefault();
    
    if (!manualPost.title || !manualPost.content) {
      showNotification('Please enter both title and content', 'error');
      return;
    }

    if (!facebookConnected) {
      showNotification('Please connect your Facebook account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Posting to Facebook...', 'info');
      
      const postData = {
        platform: 'facebook',
        title: manualPost.title,
        content: manualPost.content,
        page_id: manualPost.pageId,
        image_url: manualPost.imageUrl
      };
      
      const response = await makeAuthenticatedRequest('/api/post/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        showNotification(`Post created successfully as ${facebookUsername}!`, 'success');
        if (result.post_url) {
          showNotification(`View post: ${result.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setManualPost({
          platform: 'facebook',
          title: '',
          content: '',
          pageId: '',
          imageUrl: '',
          isGenerating: false
        });
      } else {
        showNotification(result.error || 'Posting failed', 'error');
      }
    } catch (error) {
      showNotification('Posting failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [manualPost, makeAuthenticatedRequest, facebookConnected, facebookUsername, showNotification]);

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem('fbUserProfile', JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, showNotification]);

  const startAutomation = useCallback(async () => {
    if (!userProfile.isConfigured) {
      showNotification('Please configure your profile first', 'error');
      setActiveTab('setup');
      return;
    }

    if (!facebookConnected) {
      showNotification('Please connect your Facebook account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Setting up Facebook automation...', 'info');
      
      const config = {
        platform: 'facebook',
        domain: userProfile.domain,
        business_type: userProfile.businessType,
        business_description: userProfile.businessDescription,
        target_audience: userProfile.targetAudience,
        content_style: userProfile.contentStyle,
        posts_per_day: autoPostConfig.postsPerDay,
        posting_times: autoPostConfig.postingTimes
      };

      const response = await makeAuthenticatedRequest('/api/automation/setup-auto-posting', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAutoPostConfig(prev => ({ ...prev, enabled: true }));
        showNotification(`Facebook auto-posting started for ${facebookUsername}! Next post: ${result.next_post_time || 'scheduled'}`, 'success');
      } else {
        showNotification(result.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userProfile, facebookConnected, autoPostConfig, makeAuthenticatedRequest, facebookUsername, showNotification]);

  const addTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    const testTime = now.toTimeString().slice(0, 5);
    if (!autoPostConfig.postingTimes.includes(testTime)) {
      setAutoPostConfig(prev => ({
        ...prev,
        postingTimes: [...prev.postingTimes, testTime].sort()
      }));
      showNotification('Test time added for Facebook (+5 minutes)', 'info');
    }
  };

  const removeTime = (time) => {
    setAutoPostConfig(prev => ({
      ...prev,
      postingTimes: prev.postingTimes.filter(t => t !== time)
    }));
  };

  return (
    <div style={{ fontFamily: "'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif", minHeight: '100vh', background: 'linear-gradient(135deg, #1877f2 0%, #0c63e4 100%)', display: 'flex', position: 'relative', overflow: 'hidden' }}>
      
      {/* Animated Background Particles */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, opacity: 0.15, pointerEvents: 'none' }}>
        {[...Array(20)].map((_, i) => (
          <div key={i} style={{ position: 'absolute', width: `${Math.random() * 100 + 50}px`, height: `${Math.random() * 100 + 50}px`, borderRadius: '50%', background: 'rgba(255, 255, 255, 0.1)', top: `${Math.random() * 100}%`, left: `${Math.random() * 100}%`, animation: `float ${Math.random() * 10 + 10}s ease-in-out infinite`, animationDelay: `${Math.random() * 5}s` }} />
        ))}
      </div>

      {/* Notifications */}
      <div style={{ position: 'fixed', top: '24px', right: '24px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '12px', maxWidth: '420px' }}>
        {notifications.map(notification => (
          <div key={notification.id} style={{ padding: '18px 24px', borderRadius: '16px', backdropFilter: 'blur(20px)', color: 'white', fontWeight: '600', boxShadow: '0 12px 40px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)', background: notification.type === 'success' ? 'linear-gradient(135deg, #10b981, #059669)' : notification.type === 'error' ? 'linear-gradient(135deg, #ef4444, #dc2626)' : 'linear-gradient(135deg, #3b82f6, #2563eb)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', fontSize: '15px', animation: 'slideInRight 0.4s ease-out', transform: 'translateX(0)' }}>
            <span>{notification.message}</span>
            <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))} style={{ background: 'rgba(255, 255, 255, 0.2)', border: 'none', color: 'white', fontSize: '20px', cursor: 'pointer', padding: '4px 8px', borderRadius: '8px', transition: 'all 0.2s', lineHeight: 1 }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'} onMouseLeave={e => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'}>×</button>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.75)', backdropFilter: 'blur(12px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999, animation: 'fadeIn 0.3s ease-out' }}>
          <div style={{ background: 'white', padding: '48px 60px', borderRadius: '24px', textAlign: 'center', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)', animation: 'scaleIn 0.3s ease-out' }}>
            <div style={{ position: 'relative', width: '64px', height: '64px', margin: '0 auto' }}>
              <div style={{ border: '5px solid #f3f4f6', borderRadius: '50%', width: '64px', height: '64px', position: 'absolute' }}></div>
              <div style={{ border: '5px solid #1877f2', borderTop: '5px solid transparent', borderRadius: '50%', width: '64px', height: '64px', animation: 'spin 1s linear infinite', position: 'absolute' }}></div>
            </div>
            <p style={{ marginTop: '24px', color: '#1f2937', fontSize: '17px', fontWeight: '600', letterSpacing: '-0.01em' }}>Processing Facebook request...</p>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div style={{ width: '340px', background: 'rgba(255, 255, 255, 0.98)', backdropFilter: 'blur(20px)', height: '100vh', position: 'fixed', display: 'flex', flexDirection: 'column', boxShadow: '6px 0 40px rgba(0, 0, 0, 0.12)', borderRight: '1px solid rgba(255, 255, 255, 0.3)', zIndex: 100 }}>
        
        <div style={{ padding: '40px 32px', borderBottom: '1px solid rgba(0, 0, 0, 0.08)', background: 'linear-gradient(135deg, #1877f2, #0c63e4)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: '-50%', right: '-20%', width: '200px', height: '200px', borderRadius: '50%', background: 'rgba(255, 255, 255, 0.1)', filter: 'blur(40px)' }}></div>
          <div style={{ position: 'relative', zIndex: 1 }}>
            <div style={{ fontSize: '48px', marginBottom: '16px', textAlign: 'center' }}>📘</div>
            <h2 style={{ fontSize: '28px', fontWeight: '800', color: 'white', margin: 0, marginBottom: '8px', textAlign: 'center', letterSpacing: '-0.02em' }}>Facebook Studio</h2>
            <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.95)', fontWeight: '500', textAlign: 'center' }}>AI-Powered Social Media</div>
            <div style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.85)', marginTop: '8px', textAlign: 'center', background: 'rgba(255, 255, 255, 0.15)', padding: '6px 12px', borderRadius: '20px', display: 'inline-block', width: '100%' }}>👋 {user?.name}</div>
          </div>
        </div>
        
        <nav style={{ flex: 1, padding: '24px 20px', overflowY: 'auto' }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Profile Setup', desc: 'Configure AI settings', gradient: 'linear-gradient(135deg, #667eea, #764ba2)' },
            { id: 'manual', icon: '✍️', label: 'Manual Post', desc: 'Create & post now', gradient: 'linear-gradient(135deg, #f093fb, #f5576c)' },
            { id: 'schedule', icon: '📅', label: 'Auto Schedule', desc: 'Set posting times', gradient: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
            { id: 'status', icon: '📊', label: 'Analytics', desc: 'Performance metrics', gradient: 'linear-gradient(135deg, #43e97b, #38f9d7)' }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '16px', padding: '18px 20px', border: 'none', background: activeTab === tab.id ? tab.gradient : 'transparent', color: activeTab === tab.id ? 'white' : '#64748b', textAlign: 'left', borderRadius: '16px', cursor: 'pointer', marginBottom: '10px', fontSize: '15px', transform: activeTab === tab.id ? 'translateX(8px)' : 'translateX(0)', boxShadow: activeTab === tab.id ? '0 8px 24px rgba(24, 119, 242, 0.35)' : 'none', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', fontWeight: activeTab === tab.id ? '600' : '500' }} onMouseEnter={e => { if (activeTab !== tab.id) { e.currentTarget.style.background = 'rgba(24, 119, 242, 0.06)'; e.currentTarget.style.transform = 'translateX(4px)'; } }} onMouseLeave={e => { if (activeTab !== tab.id) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.transform = 'translateX(0)'; } }}>
              <span style={{ fontSize: '24px', transition: 'transform 0.3s' }}>{tab.icon}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', fontSize: '15px', marginBottom: '2px' }}>{tab.label}</div>
                <div style={{ fontSize: '12px', opacity: 0.85 }}>{tab.desc}</div>
              </div>
            </button>
          ))}
        </nav>

        {/* Connection Status */}
        <div style={{ padding: '24px 20px', borderTop: '1px solid rgba(0, 0, 0, 0.06)' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '700', color: '#64748b', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Connection Status</h3>
          <div style={{ padding: '20px', background: facebookConnected ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05))' : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05))', borderRadius: '16px', border: `2px solid ${facebookConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`, position: 'relative', overflow: 'hidden' }}>
            {facebookConnected ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#10b981', boxShadow: '0 0 0 4px rgba(16, 185, 129, 0.2)', animation: 'pulse 2s ease-in-out infinite' }}></div>
                  <span style={{ fontSize: '15px', fontWeight: '700', color: '#047857' }}>Connected</span>
                </div>
                {facebookUsername && <div style={{ fontSize: '14px', color: '#065f46', marginBottom: '16px', fontWeight: '600', background: 'rgba(16, 185, 129, 0.15)', padding: '8px 12px', borderRadius: '10px', display: 'inline-block' }}>@{facebookUsername}</div>}
                {facebookPages && facebookPages.length > 0 && (
                  <div style={{ marginBottom: '16px' }}>
                    <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '8px', fontWeight: '600' }}>{facebookPages.length} Pages Connected:</div>
                    {facebookPages.slice(0, 2).map(page => (
                      <div key={page.id} style={{ fontSize: '11px', color: '#4b5563', margin: '4px 0', background: 'rgba(59, 130, 246, 0.1)', padding: '4px 10px', borderRadius: '12px', display: 'inline-block', marginRight: '6px', fontWeight: '500' }}>📄 {page.name}</div>
                    ))}
                    {facebookPages.length > 2 && <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>+{facebookPages.length - 2} more</div>}
                  </div>
                )}
                <button onClick={testConnection} disabled={loading} style={{ width: '100%', padding: '12px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #10b981, #059669)', color: 'white', border: 'none', borderRadius: '12px', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.3s', boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)' }} onMouseEnter={e => !loading && (e.currentTarget.style.transform = 'translateY(-2px)')} onMouseLeave={e => !loading && (e.currentTarget.style.transform = 'translateY(0)')}>
                  {loading ? 'Testing...' : '✓ Test Connection'}
                </button>
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#ef4444', animation: 'pulse 2s ease-in-out infinite' }}></div>
                  <span style={{ fontSize: '15px', fontWeight: '700', color: '#dc2626' }}>Not Connected</span>
                </div>
                <p style={{ fontSize: '13px', color: '#7f1d1d', marginBottom: '16px', lineHeight: 1.5 }}>Connect your Facebook account to start automating your social media presence</p>
                <button onClick={handleConnect} disabled={loading} style={{ width: '100%', padding: '12px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #1877f2, #0c63e4)', color: 'white', border: 'none', borderRadius: '12px', cursor: loading ? 'not-allowed' : 'pointer', transition: 'all 0.3s', boxShadow: '0 4px 12px rgba(24, 119, 242, 0.3)' }} onMouseEnter={e => !loading && (e.currentTarget.style.transform = 'translateY(-2px)')} onMouseLeave={e => !loading && (e.currentTarget.style.transform = 'translateY(0)')}>
                  {loading ? 'Connecting...' : '📘 Connect Facebook'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: '340px', minHeight: '100vh', position: 'relative', zIndex: 1 }}>
        
        <header style={{ padding: '40px 48px', background: 'rgba(255, 255, 255, 0.98)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(0, 0, 0, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 50, boxShadow: '0 4px 16px rgba(0, 0, 0, 0.04)' }}>
          <div>
            <h1 style={{ fontSize: '36px', fontWeight: '800', background: 'linear-gradient(135deg, #1877f2, #0c63e4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '8px', letterSpacing: '-0.02em' }}>Facebook Automation</h1>
            <p style={{ fontSize: '17px', color: '#64748b', margin: 0, fontWeight: '500' }}>AI-powered content creation and scheduling for Facebook</p>
          </div>
          
          <div style={{ display: 'flex', gap: '16px' }}>
            {userProfile.isConfigured && (
              <button onClick={startAutomation} disabled={loading || !facebookConnected} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 32px', border: 'none', borderRadius: '14px', fontSize: '16px', fontWeight: '700', cursor: loading || !facebookConnected ? 'not-allowed' : 'pointer', background: loading || !facebookConnected ? 'linear-gradient(135deg, #cbd5e1, #94a3b8)' : 'linear-gradient(135deg, #1877f2, #0c63e4)', color: 'white', boxShadow: '0 8px 24px rgba(24, 119, 242, 0.35)', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }} onMouseEnter={e => { if (!loading && facebookConnected) e.currentTarget.style.transform = 'translateY(-2px)'; }} onMouseLeave={e => { if (!loading && facebookConnected) e.currentTarget.style.transform = 'translateY(0)'; }}>
                <span style={{ fontSize: '20px' }}>🚀</span>
                <span>Start Automation</span>
              </button>
            )}
          </div>
        </header>

        {/* Tab Content */}
        <div style={{ padding: '48px' }}>
          <div style={{ background: 'white', borderRadius: '28px', padding: '48px', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.08), 0 0 1px rgba(0, 0, 0, 0.05)', maxWidth: '1400px', margin: '0 auto', position: 'relative', overflow: 'hidden' }}>
            
            <div style={{ position: 'absolute', top: '-100px', right: '-100px', width: '300px', height: '300px', borderRadius: '50%', background: 'linear-gradient(135deg, rgba(24, 119, 242, 0.05), rgba(12, 99, 228, 0.05))', filter: 'blur(60px)', pointerEvents: 'none' }}></div>
            
            {/* Setup Tab */}
            {activeTab === 'setup' && (
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ textAlign: 'center', marginBottom: '48px' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))', padding: '12px 24px', borderRadius: '20px', marginBottom: '16px' }}>
                    <span style={{ fontSize: '24px' }}>⚙️</span>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#667eea', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Configuration</span>
                  </div>
                  <h2 style={{ fontSize: '40px', fontWeight: '800', color: '#1f2937', marginBottom: '16px', letterSpacing: '-0.02em' }}>AI Profile Configuration</h2>
                  <p style={{ fontSize: '17px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>Configure your business profile to generate authentic, engaging Facebook content</p>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '28px', marginBottom: '28px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Business Domain</label>
                    <select value={userProfile.domain} onChange={(e) => { const domain = e.target.value; const config = DOMAIN_CONFIGS[domain]; setUserProfile(prev => ({ ...prev, domain, businessType: config?.sampleBusiness || prev.businessType })); }} style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', cursor: 'pointer', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'}>
                      {Object.entries(DOMAIN_CONFIGS).map(([key, config]) => (
                        <option key={key} value={key}>{config.icon} {config.description}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Content Style</label>
                    <select value={userProfile.contentStyle} onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))} style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', cursor: 'pointer', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'}>
                      {Object.entries(CONTENT_STYLES).map(([key, style]) => (
                        <option key={key} value={key}>{style}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ marginBottom: '28px' }}>
                  <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Business Type</label>
                  <input type="text" value={userProfile.businessType} onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))} placeholder={DOMAIN_CONFIGS[userProfile.domain]?.sampleBusiness} style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                </div>

                <div style={{ marginBottom: '28px' }}>
                  <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Business Description</label>
                  <textarea value={userProfile.businessDescription} onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))} placeholder="Describe your business, services, and unique value proposition..." rows="4" style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.6, transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                </div>

                <div style={{ marginBottom: '40px' }}>
                  <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Target Audience</label>
                  <select value={userProfile.targetAudience} onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))} style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', cursor: 'pointer', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'}>
                    {Object.entries(TARGET_AUDIENCES).map(([key, option]) => (
                      <option key={key} value={key}>{option.icon} {option.label}</option>
                    ))}
                  </select>
                </div>

                <div style={{ textAlign: 'center' }}>
                  <button onClick={saveUserProfile} disabled={!userProfile.businessType} style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '20px 48px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: userProfile.businessType ? 'pointer' : 'not-allowed', background: userProfile.businessType ? 'linear-gradient(135deg, #1877f2, #0c63e4)' : 'linear-gradient(135deg, #cbd5e1, #94a3b8)', color: 'white', boxShadow: userProfile.businessType ? '0 8px 24px rgba(24, 119, 242, 0.35)' : 'none', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }} onMouseEnter={e => userProfile.businessType && (e.currentTarget.style.transform = 'translateY(-2px)')} onMouseLeave={e => userProfile.businessType && (e.currentTarget.style.transform = 'translateY(0)')}>
                    <span style={{ fontSize: '20px' }}>✅</span>
                    <span>Save Configuration</span>
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div style={{ marginTop: '32px', padding: '24px', background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05))', borderRadius: '20px', border: '2px solid rgba(16, 185, 129, 0.3)', animation: 'fadeInUp 0.5s ease-out' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                      <span style={{ fontSize: '28px' }}>✓</span>
                      <span style={{ color: '#065f46', fontWeight: '700', fontSize: '20px' }}>Profile Configured Successfully!</span>
                    </div>
                    <div style={{ color: '#059669', fontSize: '16px', marginLeft: '40px' }}>AI is ready for human-like content generation on Facebook.</div>
                  </div>
                )}
              </div>
            )}

            {/* Manual Post Tab */}
            {activeTab === 'manual' && (
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ textAlign: 'center', marginBottom: '48px' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', background: 'linear-gradient(135deg, rgba(245, 87, 108, 0.1), rgba(240, 147, 251, 0.1))', padding: '12px 24px', borderRadius: '20px', marginBottom: '16px' }}>
                    <span style={{ fontSize: '24px' }}>✍️</span>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#f5576c', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Content Creation</span>
                  </div>
                  <h2 style={{ fontSize: '40px', fontWeight: '800', color: '#1f2937', marginBottom: '16px', letterSpacing: '-0.02em' }}>Create & Post with AI</h2>
                  <p style={{ fontSize: '17px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>Generate human-like content with AI and publish directly to Facebook</p>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '32px' }}>
                  <button onClick={generateContent} disabled={manualPost.isGenerating || !userProfile.isConfigured} style={{ padding: '18px 36px', border: 'none', borderRadius: '16px', fontSize: '17px', fontWeight: '700', cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer', background: (manualPost.isGenerating || !userProfile.isConfigured) ? 'linear-gradient(135deg, #cbd5e1, #94a3b8)' : 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', boxShadow: (manualPost.isGenerating || !userProfile.isConfigured) ? 'none' : '0 8px 24px rgba(102, 126, 234, 0.35)', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)', display: 'flex', alignItems: 'center', gap: '12px' }} onMouseEnter={e => { if (!manualPost.isGenerating && userProfile.isConfigured) e.currentTarget.style.transform = 'translateY(-2px)'; }} onMouseLeave={e => { if (!manualPost.isGenerating && userProfile.isConfigured) e.currentTarget.style.transform = 'translateY(0)'; }}>
                    <span style={{ fontSize: '22px' }}>🤖</span>
                    <span>{manualPost.isGenerating ? 'Generating...' : 'Generate AI Content'}</span>
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ marginBottom: '28px' }}>
                    <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Post Title</label>
                    <input type="text" value={manualPost.title} onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))} placeholder="Enter your post title..." required style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                  </div>

                  <div style={{ marginBottom: '28px' }}>
                    <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Post Content</label>
                    <textarea value={manualPost.content} onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))} placeholder="Enter your post content or generate with AI..." rows="10" required style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.6, transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                  </div>

                  {facebookPages.length > 0 && (
                    <div style={{ marginBottom: '28px' }}>
                      <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Facebook Page (Optional)</label>
                      <select value={manualPost.pageId} onChange={(e) => setManualPost(prev => ({ ...prev, pageId: e.target.value }))} style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', cursor: 'pointer', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'}>
                        <option value="">Select a page</option>
                        {facebookPages.map(page => (
                          <option key={page.id} value={page.id}>{page.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div style={{ marginBottom: '40px' }}>
                    <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', color: '#374151', marginBottom: '12px', letterSpacing: '-0.01em' }}>Image URL (Optional)</label>
                    <input type="url" value={manualPost.imageUrl} onChange={(e) => setManualPost(prev => ({ ...prev, imageUrl: e.target.value }))} placeholder="https://example.com/image.jpg" style={{ width: '100%', padding: '16px 20px', border: '2px solid #e5e7eb', borderRadius: '14px', fontSize: '16px', background: 'white', fontWeight: '500', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <button type="submit" disabled={loading || !facebookConnected || !manualPost.title || !manualPost.content} style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '20px 48px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: (loading || !facebookConnected || !manualPost.title || !manualPost.content) ? 'not-allowed' : 'pointer', background: (loading || !facebookConnected || !manualPost.title || !manualPost.content) ? 'linear-gradient(135deg, #cbd5e1, #94a3b8)' : 'linear-gradient(135deg, #10b981, #059669)', color: 'white', boxShadow: (loading || !facebookConnected || !manualPost.title || !manualPost.content) ? 'none' : '0 8px 24px rgba(16, 185, 129, 0.35)', transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)' }} onMouseEnter={e => { if (!loading && facebookConnected && manualPost.title && manualPost.content) e.currentTarget.style.transform = 'translateY(-2px)'; }} onMouseLeave={e => { if (!loading && facebookConnected && manualPost.title && manualPost.content) e.currentTarget.style.transform = 'translateY(0)'; }}>
                      <span style={{ fontSize: '22px' }}>🚀</span>
                      <span>{loading ? 'Posting...' : 'Post to Facebook'}</span>
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Schedule Tab */}
            {activeTab === 'schedule' && (
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ textAlign: 'center', marginBottom: '48px' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', background: 'linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(0, 242, 254, 0.1))', padding: '12px 24px', borderRadius: '20px', marginBottom: '16px' }}>
                    <span style={{ fontSize: '24px' }}>📅</span>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#4facfe', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Automation</span>
                  </div>
                  <h2 style={{ fontSize: '40px', fontWeight: '800', color: '#1f2937', marginBottom: '16px', letterSpacing: '-0.02em' }}>Auto-Post Schedule</h2>
                  <p style={{ fontSize: '17px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>Configure automated posting times for your Facebook content</p>
                </div>
                
                <div style={{ maxWidth: '700px', margin: '0 auto' }}>
                  <div style={{ padding: '40px', background: 'linear-gradient(135deg, rgba(24, 119, 242, 0.05), rgba(12, 99, 228, 0.05))', borderRadius: '24px', border: '2px solid rgba(24, 119, 242, 0.2)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                      <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'linear-gradient(135deg, #1877f2, #0c63e4)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '28px' }}>📘</div>
                      <h3 style={{ margin: 0, color: '#1f2937', fontSize: '24px', fontWeight: '700' }}>Facebook Schedule</h3>
                    </div>
                    
                    <div style={{ marginBottom: '28px' }}>
                      <label style={{ display: 'block', fontSize: '15px', fontWeight: '700', marginBottom: '12px', color: '#374151' }}>Posts Per Day</label>
                      <input type="number" min="1" max="5" value={autoPostConfig.postsPerDay} onChange={(e) => setAutoPostConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} style={{ padding: '14px 18px', border: '2px solid #e5e7eb', borderRadius: '12px', width: '120px', fontSize: '18px', fontWeight: '700', background: 'white', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />
                      <div style={{ fontSize: '13px', color: '#6b7280', marginTop: '8px', fontWeight: '500' }}>Recommended: 2-3 posts per day for optimal engagement</div>
                    </div>

                    <div style={{ marginBottom: '28px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <label style={{ fontSize: '15px', fontWeight: '700', color: '#374151' }}>Posting Times</label>
                        <button type="button" onClick={addTime} style={{ padding: '10px 20px', fontSize: '13px', background: 'linear-gradient(135deg, #1877f2, #0c63e4)', color: 'white', border: 'none', borderRadius: '10px', cursor: 'pointer', fontWeight: '700', transition: 'all 0.3s', boxShadow: '0 4px 12px rgba(24, 119, 242, 0.3)' }} onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'} onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}>+ Add Test Time</button>
                      </div>
                      
                      <input type="time" onChange={(e) => { if (e.target.value && !autoPostConfig.postingTimes.includes(e.target.value)) { setAutoPostConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); e.target.value = ''; } }} style={{ padding: '14px 16px', border: '2px solid #e5e7eb', borderRadius: '12px', fontSize: '16px', marginBottom: '16px', width: '100%', background: 'white', fontWeight: '500', transition: 'all 0.3s', outline: 'none' }} onFocus={e => e.target.style.borderColor = '#1877f2'} onBlur={e => e.target.style.borderColor = '#e5e7eb'} />

                      {autoPostConfig.postingTimes.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                          {autoPostConfig.postingTimes.map(time => (
                            <span key={time} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 16px', background: 'white', border: '2px solid rgba(24, 119, 242, 0.3)', borderRadius: '12px', color: '#1877f2', fontSize: '15px', fontWeight: '700', transition: 'all 0.3s' }}>
                              🕒 {time}
                              <button onClick={() => removeTime(time)} style={{ background: 'rgba(239, 68, 68, 0.1)', border: 'none', color: '#ef4444', fontSize: '18px', cursor: 'pointer', padding: '4px 8px', lineHeight: 1, borderRadius: '8px', transition: 'all 0.2s', fontWeight: '700' }} onMouseEnter={e => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)'} onMouseLeave={e => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}>×</button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div style={{ padding: '20px', background: 'white', borderRadius: '16px', marginTop: '28px', border: '2px solid rgba(24, 119, 242, 0.15)' }}>
                      <h4 style={{ margin: '0 0 12px 0', color: '#1f2937', fontSize: '17px', fontWeight: '700' }}>Automation Status</h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: autoPostConfig.enabled ? '#10b981' : '#ef4444', animation: 'pulse 2s ease-in-out infinite' }}></div>
                        <span style={{ fontSize: '16px', color: '#374151', fontWeight: '600' }}>
                          {autoPostConfig.enabled ? (
                            <span style={{ color: '#059669' }}>✓ Active - {autoPostConfig.postsPerDay} posts/day</span>
                          ) : (
                            <span style={{ color: '#dc2626' }}>○ Inactive - Configure and start automation</span>
                          )}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Status Tab */}
            {activeTab === 'status' && (
              <div style={{ position: 'relative', zIndex: 1 }}>
                <div style={{ textAlign: 'center', marginBottom: '48px' }}>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', background: 'linear-gradient(135deg, rgba(67, 233, 123, 0.1), rgba(56, 249, 215, 0.1))', padding: '12px 24px', borderRadius: '20px', marginBottom: '16px' }}>
                    <span style={{ fontSize: '24px' }}>📊</span>
                    <span style={{ fontSize: '14px', fontWeight: '700', color: '#43e97b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Analytics</span>
                  </div>
                  <h2 style={{ fontSize: '40px', fontWeight: '800', color: '#1f2937', marginBottom: '16px', letterSpacing: '-0.02em' }}>Performance Analytics</h2>
                  <p style={{ fontSize: '17px', color: '#64748b', maxWidth: '600px', margin: '0 auto' }}>Track your Facebook automation performance and engagement metrics</p>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '28px', marginBottom: '48px' }}>
                  <div style={{ background: 'linear-gradient(135deg, rgba(24, 119, 242, 0.05), rgba(12, 99, 228, 0.05))', borderRadius: '20px', padding: '32px', border: '2px solid rgba(24, 119, 242, 0.2)', transition: 'all 0.3s', cursor: 'pointer' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(24, 119, 242, 0.2)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                      <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'linear-gradient(135deg, #1877f2, #0c63e4)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>📘</div>
                      <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>Facebook Connection</h3>
                    </div>
                    <div style={{ display: 'inline-block', padding: '8px 16px', borderRadius: '10px', fontSize: '14px', fontWeight: '700', background: facebookConnected ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: facebookConnected ? '#059669' : '#dc2626', marginBottom: '12px' }}>
                      {facebookConnected ? '✓ Connected' : '○ Disconnected'}
                    </div>
                    {facebookUsername && <p style={{ margin: '12px 0 0 0', color: '#64748b', fontSize: '16px', fontWeight: '500' }}>Account: <strong style={{ color: '#1f2937' }}>{facebookUsername}</strong></p>}
                    {facebookPages.length > 0 && <p style={{ margin: '8px 0 0 0', color: '#64748b', fontSize: '14px' }}>{facebookPages.length} pages available</p>}
                  </div>

                  <div style={{ background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05))', borderRadius: '20px', padding: '32px', border: '2px solid rgba(102, 126, 234, 0.2)', transition: 'all 0.3s', cursor: 'pointer' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(102, 126, 234, 0.2)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                      <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'linear-gradient(135deg, #667eea, #764ba2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>🤖</div>
                      <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>AI Profile Status</h3>
                    </div>
                    <div style={{ display: 'inline-block', padding: '8px 16px', borderRadius: '10px', fontSize: '14px', fontWeight: '700', background: userProfile.isConfigured ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: userProfile.isConfigured ? '#059669' : '#dc2626', marginBottom: '12px' }}>
                      {userProfile.isConfigured ? '✓ Configured' : '○ Not Configured'}
                    </div>
                    {userProfile.isConfigured && (
                      <div style={{ marginTop: '12px' }}>
                        <p style={{ margin: '6px 0', color: '#64748b', fontSize: '15px' }}>Domain: <strong style={{ color: '#1f2937' }}>{userProfile.domain}</strong></p>
                        <p style={{ margin: '6px 0', color: '#64748b', fontSize: '15px' }}>Style: <strong style={{ color: '#1f2937' }}>{userProfile.contentStyle}</strong></p>
                      </div>
                    )}
                  </div>

                  <div style={{ background: 'linear-gradient(135deg, rgba(79, 172, 254, 0.05), rgba(0, 242, 254, 0.05))', borderRadius: '20px', padding: '32px', border: '2px solid rgba(79, 172, 254, 0.2)', transition: 'all 0.3s', cursor: 'pointer' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 12px 32px rgba(79, 172, 254, 0.2)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                      <div style={{ width: '48px', height: '48px', borderRadius: '14px', background: 'linear-gradient(135deg, #4facfe, #00f2fe)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px' }}>⚡</div>
                      <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#1f2937' }}>Automation Status</h3>
                    </div>
                    <div style={{ display: 'inline-block', padding: '8px 16px', borderRadius: '10px', fontSize: '14px', fontWeight: '700', background: autoPostConfig.enabled ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: autoPostConfig.enabled ? '#059669' : '#dc2626', marginBottom: '12px' }}>
                      {autoPostConfig.enabled ? '✓ Active' : '○ Inactive'}
                    </div>
                    {autoPostConfig.enabled && (
                      <div style={{ marginTop: '12px' }}>
                        <p style={{ margin: '6px 0', color: '#64748b', fontSize: '15px' }}>Posts/Day: <strong style={{ color: '#1f2937' }}>{autoPostConfig.postsPerDay}</strong></p>
                        <p style={{ margin: '6px 0', color: '#64748b', fontSize: '15px' }}>Scheduled Times: <strong style={{ color: '#1f2937' }}>{autoPostConfig.postingTimes.length}</strong></p>
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ padding: '48px', background: 'linear-gradient(135deg, rgba(67, 233, 123, 0.05), rgba(56, 249, 215, 0.05))', borderRadius: '24px', border: '2px solid rgba(67, 233, 123, 0.2)' }}>
                  <h3 style={{ margin: '0 0 40px 0', fontSize: '28px', fontWeight: '800', color: '#1f2937', textAlign: 'center', letterSpacing: '-0.01em' }}>📈 Performance Metrics</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '24px' }}>
                    {[
                      { value: performanceData.postsToday, label: 'Posts Today', icon: '📝', color: '#10b981', gradient: 'linear-gradient(135deg, #10b981, #059669)' },
                      { value: performanceData.totalEngagement, label: 'Total Engagement', icon: '💬', color: '#3b82f6', gradient: 'linear-gradient(135deg, #3b82f6, #2563eb)' },
                      { value: `${performanceData.successRate}%`, label: 'Success Rate', icon: '✓', color: '#f59e0b', gradient: 'linear-gradient(135deg, #f59e0b, #d97706)' }
                    ].map((metric, i) => (
                      <div key={i} style={{ padding: '32px 24px', background: 'white', borderRadius: '20px', textAlign: 'center', border: '2px solid rgba(0, 0, 0, 0.05)', transition: 'all 0.3s', cursor: 'pointer' }} onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-6px)'; e.currentTarget.style.boxShadow = '0 16px 40px rgba(0, 0, 0, 0.1)'; }} onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}>
                        <div style={{ fontSize: '40px', marginBottom: '12px' }}>{metric.icon}</div>
                        <div style={{ fontSize: '48px', fontWeight: '800', marginBottom: '12px', background: metric.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.02em' }}>{metric.value}</div>
                        <div style={{ fontSize: '15px', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{metric.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.05); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(0.95); }
        }
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes scaleIn {
          from { opacity: 0; transform: scale(0.9); }
          to { opacity: 1; transform: scale(1); }
        }
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(100px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  );
};

export default FacebookAutomation;