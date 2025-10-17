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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
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
    <div className="fb-automation-container">
      
      {/* Mobile Menu Toggle */}
      <button 
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

      {/* Notifications */}
      <div className="notifications-container">
        {notifications.map(notification => (
          <div key={notification.id} className={`notification notification-${notification.type}`}>
            <span>{notification.message}</span>
            <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))} className="notification-close">×</button>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-content">
            <div className="spinner-container">
              <div className="spinner-bg"></div>
              <div className="spinner"></div>
            </div>
            <p className="loading-text">Processing Facebook request...</p>
          </div>
        </div>
      )}

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>}

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        
        <div className="sidebar-header">
          <div className="header-decoration"></div>
          <div className="header-content">
            <div className="header-icon">📘</div>
            <h2 className="header-title">Facebook Studio</h2>
            <div className="header-subtitle">AI-Powered Social Media</div>
            <div className="header-user">👋 {user?.name}</div>
          </div>
        </div>

        {/* Connection Status - Positioned at Top */}
        <div className="connection-section">
          <h3 className="connection-title">CONNECTION STATUS</h3>
          <div className={`connection-card ${facebookConnected ? 'connected' : 'disconnected'}`}>
            {facebookConnected ? (
              <div className="connection-content">
                <div className="status-badge status-connected">
                  <div className="status-dot"></div>
                  <span>Connected</span>
                </div>
                {facebookUsername && <div className="username-badge">@{facebookUsername}</div>}
                {facebookPages && facebookPages.length > 0 && (
                  <div className="pages-info">
                    <div className="pages-count">{facebookPages.length} Pages Connected</div>
                    {facebookPages.slice(0, 2).map(page => (
                      <div key={page.id} className="page-badge">📄 {page.name}</div>
                    ))}
                    {facebookPages.length > 2 && <div className="pages-more">+{facebookPages.length - 2} more</div>}
                  </div>
                )}
                <button onClick={testConnection} disabled={loading} className="connection-btn test-btn">
                  {loading ? 'Testing...' : '✓ Test Connection'}
                </button>
              </div>
            ) : (
              <div className="connection-content">
                <div className="status-badge status-disconnected">
                  <div className="status-dot"></div>
                  <span>Not Connected</span>
                </div>
                <p className="connection-message">Connect your Facebook account to start automating your social media presence</p>
                <button onClick={handleConnect} disabled={loading} className="connection-btn connect-btn">
                  {loading ? 'Connecting...' : '📘 Connect Facebook'}
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="sidebar-nav">
          {[
            { id: 'setup', icon: '⚙️', label: 'Profile Setup', desc: 'Configure AI settings' },
            { id: 'manual', icon: '✍️', label: 'Manual Post', desc: 'Create & post now' },
            { id: 'schedule', icon: '📅', label: 'Auto Schedule', desc: 'Set posting times' },
            { id: 'status', icon: '📊', label: 'Analytics', desc: 'Performance metrics' }
          ].map(tab => (
            <button 
              key={tab.id} 
              onClick={() => { 
                setActiveTab(tab.id); 
                if (window.innerWidth < 768) setSidebarOpen(false); 
              }} 
              className={`nav-btn ${activeTab === tab.id ? 'nav-btn-active' : ''}`}
            >
              <span className="nav-icon">{tab.icon}</span>
              <div className="nav-content">
                <div className="nav-label">{tab.label}</div>
                <div className="nav-desc">{tab.desc}</div>
              </div>
            </button>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        
        <header className="main-header">
          <div className="header-text">
            <h1 className="main-title">Facebook Automation</h1>
            <p className="main-subtitle">AI-powered content creation and scheduling for Facebook</p>
          </div>
          
          {userProfile.isConfigured && (
            <button 
              onClick={startAutomation} 
              disabled={loading || !facebookConnected} 
              className="start-automation-btn"
            >
              <span className="btn-icon">🚀</span>
              <span className="btn-text">Start Automation</span>
            </button>
          )}
        </header>

        {/* Tab Content */}
        <div className="tab-container">
          <div className="tab-content">
            
            {/* Setup Tab */}
            {activeTab === 'setup' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">⚙️ Configuration</div>
                  <h2 className="section-title">AI Profile Configuration</h2>
                  <p className="section-desc">Configure your business profile to generate authentic, engaging Facebook content</p>
                </div>
                
                <div className="form-grid">
                  <div className="form-group">
                    <label className="form-label">Business Domain</label>
                    <select value={userProfile.domain} onChange={(e) => { const domain = e.target.value; const config = DOMAIN_CONFIGS[domain]; setUserProfile(prev => ({ ...prev, domain, businessType: config?.sampleBusiness || prev.businessType })); }} className="form-select">
                      {Object.entries(DOMAIN_CONFIGS).map(([key, config]) => (
                        <option key={key} value={key}>{config.icon} {config.description}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Content Style</label>
                    <select value={userProfile.contentStyle} onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))} className="form-select">
                      {Object.entries(CONTENT_STYLES).map(([key, style]) => (
                        <option key={key} value={key}>{style}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Business Type</label>
                  <input type="text" value={userProfile.businessType} onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))} placeholder={DOMAIN_CONFIGS[userProfile.domain]?.sampleBusiness} className="form-input" />
                </div>

                <div className="form-group">
                  <label className="form-label">Business Description</label>
                  <textarea value={userProfile.businessDescription} onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))} placeholder="Describe your business, services, and unique value proposition..." rows="4" className="form-textarea" />
                </div>

                <div className="form-group">
                  <label className="form-label">Target Audience</label>
                  <select value={userProfile.targetAudience} onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))} className="form-select">
                    {Object.entries(TARGET_AUDIENCES).map(([key, option]) => (
                      <option key={key} value={key}>{option.icon} {option.label}</option>
                    ))}
                  </select>
                </div>

                <div className="form-actions">
                  <button onClick={saveUserProfile} disabled={!userProfile.businessType} className="primary-btn">
                    <span className="btn-icon">✅</span>
                    <span className="btn-text">Save Configuration</span>
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div className="success-message">
                    <div className="success-icon">✓</div>
                    <div className="success-content">
                      <div className="success-title">Profile Configured Successfully!</div>
                      <div className="success-text">AI is ready for human-like content generation on Facebook.</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Manual Post Tab */}
            {activeTab === 'manual' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">✍️ Content Creation</div>
                  <h2 className="section-title">Create & Post with AI</h2>
                  <p className="section-desc">Generate human-like content with AI and publish directly to Facebook</p>
                </div>
                
                <div className="generate-section">
                  <button onClick={generateContent} disabled={manualPost.isGenerating || !userProfile.isConfigured} className="generate-btn">
                    <span className="btn-icon">🤖</span>
                    <span className="btn-text">{manualPost.isGenerating ? 'Generating...' : 'Generate AI Content'}</span>
                  </button>
                </div>

                <form onSubmit={handleManualPost} className="post-form">
                  <div className="form-group">
                    <label className="form-label">Post Title</label>
                    <input type="text" value={manualPost.title} onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))} placeholder="Enter your post title..." required className="form-input" />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Post Content</label>
                    <textarea value={manualPost.content} onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))} placeholder="Enter your post content or generate with AI..." rows="10" required className="form-textarea" />
                  </div>

                  {facebookPages.length > 0 && (
                    <div className="form-group">
                      <label className="form-label">Facebook Page (Optional)</label>
                      <select value={manualPost.pageId} onChange={(e) => setManualPost(prev => ({ ...prev, pageId: e.target.value }))} className="form-select">
                        <option value="">Select a page</option>
                        {facebookPages.map(page => (
                          <option key={page.id} value={page.id}>{page.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="form-group">
                    <label className="form-label">Image URL (Optional)</label>
                    <input type="url" value={manualPost.imageUrl} onChange={(e) => setManualPost(prev => ({ ...prev, imageUrl: e.target.value }))} placeholder="https://example.com/image.jpg" className="form-input" />
                  </div>

                  <div className="form-actions">
                    <button type="submit" disabled={loading || !facebookConnected || !manualPost.title || !manualPost.content} className="submit-btn">
                      <span className="btn-icon">🚀</span>
                      <span className="btn-text">{loading ? 'Posting...' : 'Post to Facebook'}</span>
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Schedule Tab */}
            {activeTab === 'schedule' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">📅 Automation</div>
                  <h2 className="section-title">Auto-Post Schedule</h2>
                  <p className="section-desc">Configure automated posting times for your Facebook content</p>
                </div>
                
                <div className="schedule-container">
                  <div className="schedule-card">
                    <div className="schedule-header">
                      <div className="schedule-icon">📘</div>
                      <h3 className="schedule-title">Facebook Schedule</h3>
                    </div>
                    
                    <div className="form-group">
                      <label className="form-label">Posts Per Day</label>
                      <input type="number" min="1" max="5" value={autoPostConfig.postsPerDay} onChange={(e) => setAutoPostConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} className="form-input-number" />
                      <div className="form-hint">Recommended: 2-3 posts per day for optimal engagement</div>
                    </div>

                    <div className="form-group">
                      <div className="times-header">
                        <label className="form-label">Posting Times</label>
                        <button type="button" onClick={addTime} className="add-time-btn">+ Add Test Time</button>
                      </div>
                      
                      <input type="time" onChange={(e) => { if (e.target.value && !autoPostConfig.postingTimes.includes(e.target.value)) { setAutoPostConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); e.target.value = ''; } }} className="form-input" />

                      {autoPostConfig.postingTimes.length > 0 && (
                        <div className="times-list">
                          {autoPostConfig.postingTimes.map(time => (
                            <span key={time} className="time-badge">
                              🕒 {time}
                              <button onClick={() => removeTime(time)} className="time-remove">×</button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="status-card">
                      <h4 className="status-title">Automation Status</h4>
                      <div className="status-info">
                        <div className={`status-indicator ${autoPostConfig.enabled ? 'active' : 'inactive'}`}></div>
                        <span className="status-text">
                          {autoPostConfig.enabled ? (
                            <span>✓ Active - {autoPostConfig.postsPerDay} posts/day</span>
                          ) : (
                            <span>○ Inactive - Configure and start automation</span>
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
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">📊 Analytics</div>
                  <h2 className="section-title">Performance Analytics</h2>
                  <p className="section-desc">Track your Facebook automation performance and engagement metrics</p>
                </div>
                
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-header">
                      <div className="stat-icon-fb">📘</div>
                      <h3 className="stat-title">Facebook Connection</h3>
                    </div>
                    <div className={`stat-badge ${facebookConnected ? 'badge-success' : 'badge-error'}`}>
                      {facebookConnected ? '✓ Connected' : '○ Disconnected'}
                    </div>
                    {facebookUsername && <p className="stat-info">Account: <strong>{facebookUsername}</strong></p>}
                    {facebookPages.length > 0 && <p className="stat-info">{facebookPages.length} pages available</p>}
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <div className="stat-icon-ai">🤖</div>
                      <h3 className="stat-title">AI Profile Status</h3>
                    </div>
                    <div className={`stat-badge ${userProfile.isConfigured ? 'badge-success' : 'badge-error'}`}>
                      {userProfile.isConfigured ? '✓ Configured' : '○ Not Configured'}
                    </div>
                    {userProfile.isConfigured && (
                      <div className="stat-details">
                        <p className="stat-info">Domain: <strong>{userProfile.domain}</strong></p>
                        <p className="stat-info">Style: <strong>{userProfile.contentStyle}</strong></p>
                      </div>
                    )}
                  </div>

                  <div className="stat-card">
                    <div className="stat-header">
                      <div className="stat-icon-auto">⚡</div>
                      <h3 className="stat-title">Automation Status</h3>
                    </div>
                    <div className={`stat-badge ${autoPostConfig.enabled ? 'badge-success' : 'badge-error'}`}>
                      {autoPostConfig.enabled ? '✓ Active' : '○ Inactive'}
                    </div>
                    {autoPostConfig.enabled && (
                      <div className="stat-details">
                        <p className="stat-info">Posts/Day: <strong>{autoPostConfig.postsPerDay}</strong></p>
                        <p className="stat-info">Scheduled Times: <strong>{autoPostConfig.postingTimes.length}</strong></p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="metrics-section">
                  <h3 className="metrics-title">📈 Performance Metrics</h3>
                  <div className="metrics-grid">
                    {[
                      { value: performanceData.postsToday, label: 'Posts Today', icon: '📝', color: '#10b981' },
                      { value: performanceData.totalEngagement, label: 'Total Engagement', icon: '💬', color: '#3b82f6' },
                      { value: `${performanceData.successRate}%`, label: 'Success Rate', icon: '✓', color: '#f59e0b' }
                    ].map((metric, i) => (
                      <div key={i} className="metric-card">
                        <div className="metric-icon">{metric.icon}</div>
                        <div className="metric-value" style={{ color: metric.color }}>{metric.value}</div>
                        <div className="metric-label">{metric.label}</div>
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
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }

        .fb-automation-container {
          font-family: 'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif;
          min-height: 100vh;
          background: linear-gradient(135deg, #1877f2 0%, #0c63e4 100%);
          position: relative;
        }

        /* Mobile Menu Button */
        .mobile-menu-btn {
          display: none;
          position: fixed;
          top: 20px;
          left: 20px;
          z-index: 1001;
          background: white;
          border: none;
          border-radius: 12px;
          padding: 12px;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          flex-direction: column;
          gap: 4px;
          width: 48px;
          height: 48px;
          align-items: center;
          justify-content: center;
        }

        .mobile-menu-btn span {
          width: 24px;
          height: 3px;
          background: #1877f2;
          border-radius: 2px;
          transition: all 0.3s;
        }

        /* Notifications */
        .notifications-container {
          position: fixed;
          top: 24px;
          right: 24px;
          z-index: 10000;
          display: flex;
          flex-direction: column;
          gap: 12px;
          max-width: 420px;
        }

        .notification {
          padding: 18px 24px;
          borderRadius: 16px;
          backdrop-filter: blur(20px);
          color: white;
          font-weight: 600;
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          fontSize: 15px;
          animation: slideInRight 0.4s ease-out;
        }

        .notification-success {
          background: linear-gradient(135deg, #10b981, #059669);
        }

        .notification-error {
          background: linear-gradient(135deg, #ef4444, #dc2626);
        }

        .notification-info {
          background: linear-gradient(135deg, #3b82f6, #2563eb);
        }

        .notification-close {
          background: rgba(255, 255, 255, 0.2);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 8px;
          transition: all 0.2s;
          line-height: 1;
        }

        .notification-close:hover {
          background: rgba(255, 255, 255, 0.3);
        }

        /* Loading Overlay */
        .loading-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.75);
          backdrop-filter: blur(12px);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
          animation: fadeIn 0.3s ease-out;
        }

        .loading-content {
          background: white;
          padding: 48px 60px;
          border-radius: 24px;
          text-align: center;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
          animation: scaleIn 0.3s ease-out;
        }

        .spinner-container {
          position: relative;
          width: 64px;
          height: 64px;
          margin: 0 auto;
        }

        .spinner-bg {
          border: 5px solid #f3f4f6;
          border-radius: 50%;
          width: 64px;
          height: 64px;
          position: absolute;
        }

        .spinner {
          border: 5px solid #1877f2;
          border-top: 5px solid transparent;
          border-radius: 50%;
          width: 64px;
          height: 64px;
          animation: spin 1s linear infinite;
          position: absolute;
        }

        .loading-text {
          margin-top: 24px;
          color: #1f2937;
          font-size: 17px;
          font-weight: 600;
        }

        /* Sidebar */
        .sidebar-overlay {
          display: none;
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 999;
        }

        .sidebar {
          width: 340px;
          background: rgba(255, 255, 255, 0.98);
          backdrop-filter: blur(20px);
          height: 100vh;
          position: fixed;
          display: flex;
          flex-direction: column;
          box-shadow: 6px 0 40px rgba(0, 0, 0, 0.12);
          z-index: 1000;
          overflow-y: auto;
          transition: transform 0.3s ease;
        }

        .sidebar-header {
          padding: 32px 24px;
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          position: relative;
          overflow: hidden;
        }

        .header-decoration {
          position: absolute;
          top: -50%;
          right: -20%;
          width: 200px;
          height: 200px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.1);
          filter: blur(40px);
        }

        .header-content {
          position: relative;
          z-index: 1;
          text-align: center;
        }

        .header-icon {
          font-size: 48px;
          margin-bottom: 12px;
        }

        .header-title {
          font-size: 28px;
          font-weight: 800;
          color: white;
          margin-bottom: 6px;
        }

        .header-subtitle {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.95);
          font-weight: 500;
        }

        .header-user {
          font-size: 13px;
          color: rgba(255, 255, 255, 0.85);
          margin-top: 8px;
          background: rgba(255, 255, 255, 0.15);
          padding: 6px 12px;
          border-radius: 20px;
          display: inline-block;
        }

        /* Connection Section */
        .connection-section {
          padding: 20px;
          background: white;
          border-bottom: 1px solid rgba(0, 0, 0, 0.06);
        }

        .connection-title {
          font-size: 12px;
          font-weight: 800;
          color: #64748b;
          margin-bottom: 12px;
          letter-spacing: 0.08em;
        }

        .connection-card {
          padding: 20px;
          border-radius: 16px;
          border: 2px solid;
        }

        .connection-card.connected {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
          border-color: rgba(16, 185, 129, 0.3);
        }

        .connection-card.disconnected {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.05));
          border-color: rgba(239, 68, 68, 0.3);
        }

        .connection-content {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 15px;
          font-weight: 700;
        }

        .status-connected {
          color: #047857;
        }

        .status-disconnected {
          color: #dc2626;
        }

        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }

        .status-connected .status-dot {
          background: #10b981;
          box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.2);
        }

        .status-disconnected .status-dot {
          background: #ef4444;
        }

        .username-badge {
          font-size: 14px;
          color: #065f46;
          font-weight: 700;
          background: rgba(16, 185, 129, 0.15);
          padding: 8px 12px;
          border-radius: 10px;
          display: inline-block;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .pages-info {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .pages-count {
          font-size: 12px;
          color: #6b7280;
          font-weight: 600;
        }

        .page-badge {
          font-size: 11px;
          color: #4b5563;
          background: rgba(59, 130, 246, 0.1);
          padding: 4px 10px;
          border-radius: 12px;
          display: inline-block;
          margin-right: 6px;
          font-weight: 500;
        }

        .pages-more {
          font-size: 11px;
          color: #6b7280;
        }

        .connection-message {
          font-size: 13px;
          color: #7f1d1d;
          line-height: 1.5;
        }

        .connection-btn {
          width: 100%;
          padding: 12px;
          font-size: 14px;
          font-weight: 700;
          color: white;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .test-btn {
          background: linear-gradient(135deg, #10b981, #059669);
          box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        .connect-btn {
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          box-shadow: 0 4px 12px rgba(24, 119, 242, 0.3);
        }

        .connection-btn:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .connection-btn:disabled {
          background: #d1d5db;
          cursor: not-allowed;
          box-shadow: none;
        }

        /* Navigation */
        .sidebar-nav {
          flex: 1;
          padding: 20px;
        }

        .nav-btn {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 18px 20px;
          border: none;
          background: transparent;
          color: #64748b;
          text-align: left;
          border-radius: 16px;
          cursor: pointer;
          margin-bottom: 10px;
          font-size: 15px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .nav-btn:hover {
          background: rgba(24, 119, 242, 0.06);
          transform: translateX(4px);
        }

        .nav-btn-active {
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          color: white;
          transform: translateX(8px);
          box-shadow: 0 8px 24px rgba(24, 119, 242, 0.35);
        }

        .nav-icon {
          font-size: 24px;
        }

        .nav-content {
          flex: 1;
        }

        .nav-label {
          font-weight: 600;
          font-size: 15px;
          margin-bottom: 2px;
        }

        .nav-desc {
          font-size: 12px;
          opacity: 0.85;
        }

        /* Main Content */
        .main-content {
          margin-left: 340px;
          min-height: 100vh;
          position: relative;
        }

        .main-header {
          padding: 40px 48px;
          background: rgba(255, 255, 255, 0.98);
          backdrop-filter: blur(20px);
          border-bottom: 1px solid rgba(0, 0, 0, 0.08);
          display: flex;
          justify-content: space-between;
          align-items: center;
          position: sticky;
          top: 0;
          z-index: 50;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
        }

        .header-text {
          flex: 1;
        }

        .main-title {
          font-size: 36px;
          font-weight: 800;
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 8px;
        }

        .main-subtitle {
          font-size: 17px;
          color: #64748b;
          font-weight: 500;
        }

        .start-automation-btn {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px 32px;
          border: none;
          border-radius: 14px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          color: white;
          box-shadow: 0 8px 24px rgba(24, 119, 242, 0.35);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .start-automation-btn:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .start-automation-btn:disabled {
          background: linear-gradient(135deg, #cbd5e1, #94a3b8);
          cursor: not-allowed;
        }

        .btn-icon {
          font-size: 20px;
        }

        /* Tab Container */
        .tab-container {
          padding: 48px;
        }

        .tab-content {
          background: white;
          border-radius: 28px;
          padding: 48px;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
          max-width: 1400px;
          margin: 0 auto;
          position: relative;
        }

        /* Section Header */
        .section-header {
          text-align: center;
          margin-bottom: 48px;
        }

        .section-badge {
          display: inline-flex;
          align-items: center;
          gap: 12px;
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
          padding: 12px 24px;
          border-radius: 20px;
          margin-bottom: 16px;
          font-size: 14px;
          font-weight: 700;
          color: #667eea;
        }

        .section-title {
          font-size: 40px;
          font-weight: 800;
          color: #1f2937;
          margin-bottom: 16px;
        }

        .section-desc {
          font-size: 17px;
          color: #64748b;
          max-width: 600px;
          margin: 0 auto;
        }

        /* Forms */
        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 28px;
          margin-bottom: 28px;
        }

        .form-group {
          margin-bottom: 28px;
        }

        .form-label {
          display: block;
          font-size: 15px;
          font-weight: 700;
          color: #374151;
          margin-bottom: 12px;
        }

        .form-input, .form-select, .form-textarea {
          width: 100%;
          padding: 16px 20px;
          border: 2px solid #e5e7eb;
          border-radius: 14px;
          font-size: 16px;
          background: white;
          font-weight: 500;
          transition: all 0.3s;
          outline: none;
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
          border-color: #1877f2;
        }

        .form-textarea {
          resize: vertical;
          line-height: 1.6;
        }

        .form-input-number {
          padding: 14px 18px;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          width: 120px;
          font-size: 18px;
          font-weight: 700;
          background: white;
          transition: all 0.3s;
          outline: none;
        }

        .form-input-number:focus {
          border-color: #1877f2;
        }

        .form-hint {
          font-size: 13px;
          color: #6b7280;
          margin-top: 8px;
          font-weight: 500;
        }

        .form-actions {
          text-align: center;
          margin-top: 40px;
        }

        .primary-btn, .submit-btn, .generate-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 12px;
          padding: 20px 48px;
          border: none;
          border-radius: 16px;
          font-size: 18px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .primary-btn {
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          color: white;
          box-shadow: 0 8px 24px rgba(24, 119, 242, 0.35);
        }

        .submit-btn {
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          box-shadow: 0 8px 24px rgba(16, 185, 129, 0.35);
        }

        .generate-btn {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
        }

        .primary-btn:hover:not(:disabled),
        .submit-btn:hover:not(:disabled),
        .generate-btn:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .primary-btn:disabled,
        .submit-btn:disabled,
        .generate-btn:disabled {
          background: linear-gradient(135deg, #cbd5e1, #94a3b8);
          cursor: not-allowed;
          box-shadow: none;
        }

        /* Success Message */
        .success-message {
          margin-top: 32px;
          padding: 24px;
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
          border-radius: 20px;
          border: 2px solid rgba(16, 185, 129, 0.3);
          display: flex;
          align-items: center;
          gap: 16px;
          animation: fadeInUp 0.5s ease-out;
        }

        .success-icon {
          font-size: 28px;
          color: #10b981;
        }

        .success-content {
          flex: 1;
        }

        .success-title {
          color: #065f46;
          font-weight: 700;
          font-size: 20px;
          margin-bottom: 6px;
        }

        .success-text {
          color: #059669;
          font-size: 16px;
        }

        /* Generate Section */
        .generate-section {
          display: flex;
          justify-content: flex-end;
          margin-bottom: 32px;
        }

        /* Schedule */
        .schedule-container {
          max-width: 700px;
          margin: 0 auto;
        }

        .schedule-card {
          padding: 40px;
          background: linear-gradient(135deg, rgba(24, 119, 242, 0.05), rgba(12, 99, 228, 0.05));
          border-radius: 24px;
          border: 2px solid rgba(24, 119, 242, 0.2);
        }

        .schedule-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 32px;
        }

        .schedule-icon {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
        }

        .schedule-title {
          font-size: 24px;
          font-weight: 700;
          color: #1f2937;
        }

        .times-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .add-time-btn {
          padding: 10px 20px;
          font-size: 13px;
          background: linear-gradient(135deg, #1877f2, #0c63e4);
          color: white;
          border: none;
          border-radius: 10px;
          cursor: pointer;
          font-weight: 700;
          transition: all 0.3s;
          box-shadow: 0 4px 12px rgba(24, 119, 242, 0.3);
        }

        .add-time-btn:hover {
          transform: translateY(-2px);
        }

        .times-list {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 16px;
        }

        .time-badge {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 10px 16px;
          background: white;
          border: 2px solid rgba(24, 119, 242, 0.3);
          border-radius: 12px;
          color: #1877f2;
          font-size: 15px;
          font-weight: 700;
        }

        .time-remove {
          background: rgba(239, 68, 68, 0.1);
          border: none;
          color: #ef4444;
          font-size: 18px;
          cursor: pointer;
          padding: 4px 8px;
          line-height: 1;
          border-radius: 8px;
          transition: all 0.2s;
          font-weight: 700;
        }

        .time-remove:hover {
          background: rgba(239, 68, 68, 0.2);
        }

        .status-card {
          padding: 20px;
          background: white;
          border-radius: 16px;
          margin-top: 28px;
          border: 2px solid rgba(24, 119, 242, 0.15);
        }

        .status-title {
          font-size: 17px;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 12px;
        }

        .status-info {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .status-indicator {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          animation: pulse 2s ease-in-out infinite;
        }

        .status-indicator.active {
          background: #10b981;
        }

        .status-indicator.inactive {
          background: #ef4444;
        }

        .status-text {
          font-size: 16px;
          color: #374151;
          font-weight: 600;
        }

        /* Stats Grid */
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
          gap: 28px;
          margin-bottom: 48px;
        }

        .stat-card {
          background: white;
          border-radius: 20px;
          padding: 32px;
          border: 2px solid;
          transition: all 0.3s;
          cursor: pointer;
        }

        .stat-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
        }

        .stat-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .stat-icon-fb, .stat-icon-ai, .stat-icon-auto {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }

        .stat-icon-fb {
          background: linear-gradient(135deg, #1877f2, #0c63e4);
        }

        .stat-icon-ai {
          background: linear-gradient(135deg, #667eea, #764ba2);
        }

        .stat-icon-auto {
          background: linear-gradient(135deg, #4facfe, #00f2fe);
        }

        .stat-title {
          font-size: 18px;
          font-weight: 700;
          color: #1f2937;
        }

        .stat-badge {
          display: inline-block;
          padding: 8px 16px;
          border-radius: 10px;
          font-size: 14px;
          font-weight: 700;
          margin-bottom: 12px;
        }

        .badge-success {
          background: rgba(16, 185, 129, 0.15);
          color: #059669;
        }

        .badge-error {
          background: rgba(239, 68, 68, 0.15);
          color: #dc2626;
        }

        .stat-info {
          margin: 6px 0;
          color: #64748b;
          font-size: 15px;
        }

        .stat-info strong {
          color: #1f2937;
        }

        .stat-details {
          margin-top: 12px;
        }

        /* Metrics */
        .metrics-section {
          padding: 48px;
          background: linear-gradient(135deg, rgba(67, 233, 123, 0.05), rgba(56, 249, 215, 0.05));
          border-radius: 24px;
          border: 2px solid rgba(67, 233, 123, 0.2);
        }

        .metrics-title {
          font-size: 28px;
          font-weight: 800;
          color: #1f2937;
          text-align: center;
          margin-bottom: 40px;
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 24px;
        }

        .metric-card {
          padding: 32px 24px;
          background: white;
          border-radius: 20px;
          text-align: center;
          border: 2px solid rgba(0, 0, 0, 0.05);
          transition: all 0.3s;
          cursor: pointer;
        }

        .metric-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
        }

        .metric-icon {
          font-size: 40px;
          margin-bottom: 12px;
        }

        .metric-value {
          font-size: 48px;
          font-weight: 800;
          margin-bottom: 12px;
        }

        .metric-label {
          font-size: 15px;
          color: #64748b;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        /* Animations */
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
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

        /* Responsive Design */
        @media (max-width: 1200px) {
          .form-grid {
            grid-template-columns: 1fr;
          }

          .stats-grid {
            grid-template-columns: 1fr;
          }

          .metrics-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 768px) {
          .mobile-menu-btn {
            display: flex;
          }

          .sidebar {
            transform: translateX(-100%);
          }

          .sidebar-open {
            transform: translateX(0);
          }

          .sidebar-overlay {
            display: block;
          }

          .main-content {
            margin-left: 0;
          }

          .main-header {
            padding: 20px;
            flex-direction: column;
            gap: 16px;
            align-items: flex-start;
          }

          .main-title {
            font-size: 24px;
          }

          .main-subtitle {
            font-size: 14px;
          }

          .start-automation-btn {
            width: 100%;
            justify-content: center;
          }

          .tab-container {
            padding: 20px;
          }

          .tab-content {
            padding: 24px;
            border-radius: 20px;
          }

          .section-title {
            font-size: 28px;
          }

          .section-desc {
            font-size: 15px;
          }

          .notifications-container {
            right: 16px;
            left: 16px;
            max-width: none;
          }

          .notification {
            padding: 14px 18px;
            font-size: 14px;
          }

          .form-actions {
            margin-top: 24px;
          }

          .primary-btn, .submit-btn, .generate-btn {
            width: 100%;
            padding: 16px 32px;
            font-size: 16px;
          }

          .generate-section {
            justify-content: stretch;
          }

          .generate-btn {
            width: 100%;
          }

          .schedule-card {
            padding: 24px;
          }

          .metrics-section {
            padding: 24px;
          }

          .metrics-title {
            font-size: 22px;
          }

          .metric-value {
            font-size: 36px;
          }
        }

        @media (max-width: 480px) {
          .sidebar {
            width: 280px;
          }

          .header-icon {
            font-size: 36px;
          }

          .header-title {
            font-size: 22px;
          }

          .connection-section {
            padding: 16px;
          }

          .sidebar-nav {
            padding: 16px;
          }

          .nav-btn {
            padding: 14px 16px;
          }

          .main-header {
            padding: 16px;
          }

          .main-title {
            font-size: 20px;
          }

          .tab-content {
            padding: 20px;
          }

          .section-title {
            font-size: 24px;
          }

          .time-badge {
            font-size: 13px;
            padding: 8px 12px;
          }
        }
      `}</style>
    </div>
  );
};

export default FacebookAutomation;