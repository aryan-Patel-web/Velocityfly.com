import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const DOMAIN_CONFIGS = { 
  education: { icon: '🎓', description: 'Educational services', sampleBusiness: 'JEE coaching institute' }, 
  restaurant: { icon: '🍽️', description: 'Food & restaurants', sampleBusiness: 'Traditional Indian restaurant' }, 
  tech: { icon: '💻', description: 'Technology & programming', sampleBusiness: 'AI automation platform' }, 
  health: { icon: '💚', description: 'Health & wellness', sampleBusiness: 'Fitness coaching center' }, 
  business: { icon: '💼', description: 'Business & entrepreneurship', sampleBusiness: 'Business consulting firm' } 
};

const TARGET_AUDIENCES = { 
  'indian_students': { label: 'Indian Students', icon: '🎓' }, 
  'food_lovers': { label: 'Food Lovers', icon: '🍕' }, 
  'tech_professionals': { label: 'Tech Professionals', icon: '💻' }, 
  'health_conscious': { label: 'Health Conscious', icon: '💚' }, 
  'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' }, 
  'general_users': { label: 'General Users', icon: '👥' } 
};

const CONTENT_STYLES = { 
  'engaging': 'Engaging & Interactive', 
  'informative': 'Informative & Educational', 
  'promotional': 'Promotional & Marketing', 
  'helpful': 'Helpful & Supportive', 
  'casual': 'Casual & Friendly', 
  'professional': 'Professional & Formal' 
};

const FacebookAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  const [facebookConnected, setFacebookConnected] = useState(false);
  const [facebookUsername, setFacebookUsername] = useState('');
  const [facebookPages, setFacebookPages] = useState([]);
  
  const [userProfile, setUserProfile] = useState({ 
    domain: 'tech', 
    businessType: 'AI automation platform', 
    businessDescription: 'We help businesses automate their social media presence', 
    targetAudience: 'tech_professionals', 
    contentStyle: 'engaging', 
    isConfigured: false 
  });
  
  const [manualPost, setManualPost] = useState({ 
    platform: 'facebook', 
    title: '', 
    content: '', 
    pageId: '', 
    imageUrl: '', 
    isGenerating: false 
  });
  
  const [performanceData, setPerformanceData] = useState({ 
    postsToday: 0, 
    totalEngagement: 0, 
    successRate: 95 
  });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: Date.now(), message, type };
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
        const savedProfile = localStorage.getItem(`fbUserProfile_${user.email}`);
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

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem(`fbUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, user?.email, showNotification]);

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating Facebook content with AI...', 'info');
      
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
          title: result.title || '',
          content: result.content_preview || result.content || ''
        }));
        showNotification(`Content generated! Human authenticity: ${result.human_score || 95}%`, 'success');
      } else {
        showNotification(result.error || 'Content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [makeAuthenticatedRequest, showNotification, userProfile]);

  const publishPost = useCallback(async () => {
    if (!manualPost.content) {
      showNotification('Please add content to your post', 'error');
      return;
    }
    if (!facebookConnected) {
      showNotification('Please connect your Facebook account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Publishing to Facebook...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/post/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: 'facebook',
          title: manualPost.title,
          content: manualPost.content,
          page_id: manualPost.pageId,
          image_url: manualPost.imageUrl
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification('Posted successfully to Facebook!', 'success');
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
        showNotification(result.error || 'Publishing failed', 'error');
      }
    } catch (error) {
      showNotification('Publishing failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [manualPost, facebookConnected, makeAuthenticatedRequest, showNotification]);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1877F2 0%, #42B72A 100%)',
      padding: '20px'
    }}>
      {/* Notifications */}
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        maxWidth: '400px'
      }}>
        {notifications.map(notif => (
          <div key={notif.id} style={{
            background: notif.type === 'success' ? '#00C851' : notif.type === 'error' ? '#ff4444' : '#33b5e5',
            color: 'white',
            padding: '16px 20px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            fontSize: '15px',
            fontWeight: '500'
          }}>
            {notif.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '20px',
        padding: '30px',
        marginBottom: '20px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '20px'
        }}>
          <div>
            <h1 style={{
              margin: 0,
              fontSize: '32px',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #1877F2, #42B72A)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              📘 Facebook Automation
            </h1>
            <p style={{
              margin: '8px 0 0 0',
              color: '#666',
              fontSize: '16px'
            }}>
              {user?.name ? `Welcome, ${user.name}!` : 'Manage your Facebook presence'}
            </p>
          </div>

          {facebookConnected && (
            <div style={{
              background: 'linear-gradient(135deg, #1877F2, #42B72A)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              ✅ Connected: {facebookUsername}
            </div>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        borderRadius: '20px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
        display: 'flex',
        gap: '10px',
        flexWrap: 'wrap'
      }}>
        {[
          { id: 'setup', label: '⚙️ Setup', icon: '⚙️' },
          { id: 'profile', label: '👤 Profile', icon: '👤' },
          { id: 'create', label: '✍️ Create Post', icon: '✍️' },
          { id: 'analytics', label: '📊 Analytics', icon: '📊' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: '1',
              minWidth: '150px',
              padding: '16px 24px',
              background: activeTab === tab.id 
                ? 'linear-gradient(135deg, #1877F2, #42B72A)' 
                : 'transparent',
              color: activeTab === tab.id ? 'white' : '#666',
              border: activeTab === tab.id ? 'none' : '2px solid #ddd',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div>
        {/* Setup Tab */}
        {activeTab === 'setup' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#1877F2',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Facebook Connection Setup
            </h2>

            {!facebookConnected ? (
              <div>
                <div style={{
                  background: '#fff3cd',
                  border: '1px solid #ffc107',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '30px'
                }}>
                  <p style={{ margin: 0, color: '#856404', fontSize: '16px' }}>
                    ⚠️ Connect your Facebook account to start automating your posts
                  </p>
                </div>

                <button
                  onClick={handleConnect}
                  disabled={loading}
                  style={{
                    background: 'linear-gradient(135deg, #1877F2, #42B72A)',
                    padding: '18px 48px',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '18px',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    margin: '0 auto'
                  }}
                >
                  {loading ? '⏳ Connecting...' : '📘 Connect Facebook Account'}
                </button>

                <div style={{
                  marginTop: '40px',
                  padding: '24px',
                  background: '#f8f9fa',
                  borderRadius: '12px'
                }}>
                  <h3 style={{ color: '#1877F2', marginBottom: '16px' }}>
                    What you'll get:
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                    <li>AI-powered content generation for Facebook</li>
                    <li>Auto-generate engaging posts</li>
                    <li>Post to multiple Facebook pages</li>
                    <li>Schedule and automate posts</li>
                    <li>Track performance analytics</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div>
                <div style={{
                  background: '#d4edda',
                  border: '1px solid #c3e6cb',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '20px'
                }}>
                  <p style={{ margin: 0, color: '#155724', fontSize: '16px' }}>
                    ✅ Facebook connected successfully as {facebookUsername}
                  </p>
                </div>

                {facebookPages.length > 0 && (
                  <div style={{
                    background: '#e7f3ff',
                    border: '1px solid #b3d4fc',
                    borderRadius: '12px',
                    padding: '20px',
                    marginBottom: '20px'
                  }}>
                    <p style={{ margin: '0 0 12px 0', color: '#004085', fontWeight: '600' }}>
                      📄 Your Facebook Pages ({facebookPages.length}):
                    </p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {facebookPages.map((page, index) => (
                        <div key={index} style={{
                          background: 'white',
                          padding: '12px',
                          borderRadius: '8px',
                          color: '#333'
                        }}>
                          {page.name}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '20px',
                  marginTop: '30px'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #1877F2, #42B72A)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>📘</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>Ready to Post</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Start creating amazing content
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #42B72A, #00C851)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>🤖</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>AI Powered</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Generate posts automatically
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>📊</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>Analytics</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Track your performance
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#1877F2',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Configure Your Profile
            </h2>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Business Domain
              </label>
              <select
                value={userProfile.domain}
                onChange={(e) => setUserProfile(prev => ({ ...prev, domain: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px',
                  background: 'white'
                }}
              >
                {Object.entries(DOMAIN_CONFIGS).map(([key, config]) => (
                  <option key={key} value={key}>
                    {config.icon} {config.description}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Business Type
              </label>
              <input
                type="text"
                value={userProfile.businessType}
                onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))}
                placeholder="e.g., AI automation platform"
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Business Description
              </label>
              <textarea
                value={userProfile.businessDescription}
                onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))}
                placeholder="Describe your business..."
                rows="4"
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Target Audience
              </label>
              <select
                value={userProfile.targetAudience}
                onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px',
                  background: 'white'
                }}
              >
                {Object.entries(TARGET_AUDIENCES).map(([key, audience]) => (
                  <option key={key} value={key}>
                    {audience.icon} {audience.label}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ marginBottom: '32px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Content Style
              </label>
              <select
                value={userProfile.contentStyle}
                onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px',
                  background: 'white'
                }}
              >
                {Object.entries(CONTENT_STYLES).map(([key, style]) => (
                  <option key={key} value={key}>
                    {style}
                  </option>
                ))}
              </select>
            </div>

            <button
              onClick={saveUserProfile}
              style={{
                background: 'linear-gradient(135deg, #1877F2, #42B72A)',
                padding: '18px 48px',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: '700',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                margin: '0 auto'
              }}
            >
              💾 Save Profile
            </button>
          </div>
        )}

        {/* Create Post Tab */}
        {activeTab === 'create' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#1877F2',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Create Facebook Post
            </h2>

            {!facebookConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Please connect Facebook first to create posts
                </p>
              </div>
            )}

            {facebookPages.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '12px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: '16px'
                }}>
                  Select Facebook Page
                </label>
                <select
                  value={manualPost.pageId}
                  onChange={(e) => setManualPost(prev => ({ ...prev, pageId: e.target.value }))}
                  style={{
                    width: '100%',
                    padding: '16px',
                    borderRadius: '12px',
                    border: '2px solid #ddd',
                    fontSize: '16px',
                    background: 'white'
                  }}
                >
                  <option value="">Choose a page...</option>
                  {facebookPages.map((page, index) => (
                    <option key={index} value={page.id}>
                      {page.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Post Title (Optional)
              </label>
              <input
                type="text"
                value={manualPost.title}
                onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Add a title for your post..."
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Post Content
              </label>
              <textarea
                value={manualPost.content}
                onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))}
                placeholder="What's on your mind?"
                rows="8"
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
              />
            </div>

            <div style={{ marginBottom: '24px' }}>
              <button
                onClick={generateContent}
                disabled={manualPost.isGenerating || !userProfile.isConfigured}
                style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  padding: '16px 32px',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  width: '100%',
                  justifyContent: 'center'
                }}
              >
                {manualPost.isGenerating ? '⏳ Generating...' : '🤖 Generate Content with AI'}
              </button>
            </div>

            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '12px',
                color: '#333',
                fontWeight: '600',
                fontSize: '16px'
              }}>
                Image URL (Optional)
              </label>
              <input
                type="text"
                value={manualPost.imageUrl}
                onChange={(e) => setManualPost(prev => ({ ...prev, imageUrl: e.target.value }))}
                placeholder="https://example.com/image.jpg"
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px'
                }}
              />
            </div>

            {manualPost.imageUrl && (
              <div style={{
                marginBottom: '24px',
                textAlign: 'center'
              }}>
                <img
                  src={manualPost.imageUrl}
                  alt="Preview"
                  style={{
                    maxWidth: '100%',
                    maxHeight: '400px',
                    borderRadius: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            )}

            <button
              onClick={publishPost}
              disabled={loading || !manualPost.content || !facebookConnected}
              style={{
                background: 'linear-gradient(135deg, #1877F2, #42B72A)',
                padding: '20px 48px',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: '700',
                cursor: (loading || !manualPost.content || !facebookConnected) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                margin: '0 auto'
              }}
            >
              {loading ? '⏳ Publishing...' : '📤 Publish to Facebook'}
            </button>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#1877F2',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Analytics & Performance
            </h2>

            {!facebookConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Connect Facebook to view analytics
                </p>
              </div>
            )}

            {facebookConnected && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #1877F2, #42B72A)',
                  borderRadius: '16px',
                  padding: '24px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '12px' }}>
                    {performanceData.postsToday}
                  </div>
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    Posts Today
                  </div>
                </div>

                <div style={{
                  background: 'linear-gradient(135deg, #42B72A, #00C851)',
                  borderRadius: '16px',
                  padding: '24px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '12px' }}>
                    {performanceData.totalEngagement}
                  </div>
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    Total Engagement
                  </div>
                </div>

                <div style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  borderRadius: '16px',
                  padding: '24px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '12px' }}>
                    {performanceData.successRate}%
                  </div>
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    Success Rate
                  </div>
                </div>
              </div>
            )}

            <div style={{
              marginTop: '30px',
              background: '#e8f5e8',
              borderRadius: '12px',
              padding: '24px'
            }}>
              <h3 style={{ color: '#1877F2', marginBottom: '16px' }}>
                Tips for Better Engagement
              </h3>
              <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                <li>Post at peak times when your audience is active</li>
                <li>Use compelling visuals and videos</li>
                <li>Ask questions to encourage engagement</li>
                <li>Respond to comments promptly</li>
                <li>Share valuable and relevant content</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FacebookAutomation;