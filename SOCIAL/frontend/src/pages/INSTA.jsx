import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const POPULAR_HASHTAGS = { business: ['#entrepreneur', '#business', '#startup', '#success', '#motivation'], food: ['#foodie', '#delicious', '#foodporn', '#yummy', '#instafood'], fitness: ['#fitness', '#workout', '#health', '#gym', '#fitlife'], tech: ['#technology', '#innovation', '#coding', '#startup', '#ai'], lifestyle: ['#lifestyle', '#daily', '#inspiration', '#goals', '#mindset'] };

const CONTENT_TYPES = { carousel: 'Multi-image carousel post', single: 'Single image post', video: 'Video content', story: 'Instagram Story' };

const DOMAIN_CONFIGS = { education: { icon: '🎓', description: 'Educational services', sampleBusiness: 'JEE coaching institute' }, restaurant: { icon: '🍽️', description: 'Food & restaurants', sampleBusiness: 'Traditional Indian restaurant' }, tech: { icon: '💻', description: 'Technology & programming', sampleBusiness: 'AI automation platform' }, health: { icon: '💚', description: 'Health & wellness', sampleBusiness: 'Fitness coaching center' }, business: { icon: '💼', description: 'Business & entrepreneurship', sampleBusiness: 'Business consulting firm' } };

const TARGET_AUDIENCES = { 'indian_students': { label: 'Indian Students', icon: '🎓' }, 'food_lovers': { label: 'Food Lovers', icon: '🍕' }, 'tech_professionals': { label: 'Tech Professionals', icon: '💻' }, 'health_conscious': { label: 'Health Conscious', icon: '💚' }, 'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' }, 'general_users': { label: 'General Users', icon: '👥' } };

const CONTENT_STYLES = { 'engaging': 'Engaging & Interactive', 'informative': 'Informative & Educational', 'promotional': 'Promotional & Marketing', 'helpful': 'Helpful & Supportive', 'casual': 'Casual & Friendly', 'professional': 'Professional & Formal' };

const InstagramAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [instagramUsername, setInstagramUsername] = useState('');
  const [accountType, setAccountType] = useState('personal');
  
  const [userProfile, setUserProfile] = useState({ domain: 'tech', businessType: 'AI automation platform', businessDescription: 'We help businesses automate their Instagram presence', targetAudience: 'tech_professionals', contentStyle: 'engaging', isConfigured: false });
  
  const [postCreator, setPostCreator] = useState({ caption: '', hashtags: [], imagePrompt: '', generatedImage: '', contentType: 'single', isGeneratingContent: false, isGeneratingImage: false });
  
  const [automationConfig, setAutomationConfig] = useState({ enabled: false, postsPerDay: 2, postingTimes: [], hashtagStrategy: 'auto', contentMix: { carousel: 40, single: 40, video: 20 }, themes: [] });

  const [performanceData, setPerformanceData] = useState({ postsToday: 0, totalEngagement: 0, successRate: 95 });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 4000);
  }, []);

  useEffect(() => {
    if (!user?.email) return;
    
    const initKey = `instagram_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');

    const checkInstagramConnection = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const igConnected = urlParams.get('instagram_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) { showNotification(`Connection failed: ${error}`, 'error'); window.history.replaceState({}, '', window.location.pathname); return; }

      if (igConnected === 'true' && username) {
        setInstagramConnected(true); setInstagramUsername(username);
        updateUser({ instagram_connected: true, instagram_username: username });
        showNotification(`Instagram connected! Welcome @${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname); return;
      }

      try {
        const response = await makeAuthenticatedRequest('/api/instagram/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setInstagramConnected(true); setInstagramUsername(result.username);
          setAccountType(result.account_type || 'personal');
        }
      } catch (error) { console.error('Failed to check Instagram connection:', error); }

      try {
        const savedProfile = localStorage.getItem(`instagramUserProfile_${user.email}`);
        if (savedProfile) { const profile = JSON.parse(savedProfile); setUserProfile(profile); }
      } catch (error) { console.error('Error loading profile:', error); }
    };

    checkInstagramConnection();
  }, [user, makeAuthenticatedRequest, updateUser, showNotification]);

  const handleInstagramConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Instagram...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/oauth/instagram/authorize');
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else { showNotification(result.error || 'Failed to start Instagram authorization', 'error'); }
    } catch (error) { showNotification(`Connection failed: ${error.message}`, 'error'); } finally { setLoading(false); }
  }, [makeAuthenticatedRequest, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest('/api/instagram/connection-status');
      const result = await response.json();
      
      if (result.success && result.connected) {
        showNotification(`Instagram connection verified for @${result.username}!`, 'success');
      } else { showNotification('Instagram not connected', 'error'); }
    } catch (error) { showNotification('Test failed: ' + error.message, 'error'); } finally { setLoading(false); }
  }, [makeAuthenticatedRequest, showNotification]);

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem(`instagramUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) { showNotification('Failed to save profile', 'error'); }
  }, [userProfile, user?.email, showNotification]);

  const generateInstagramContent = useCallback(async () => {
    if (!userProfile.businessType) { showNotification('Please configure your profile first', 'error'); return; }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingContent: true }));
      showNotification('Generating Instagram content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        body: JSON.stringify({
          platform: 'instagram',
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setPostCreator(prev => ({
          ...prev,
          caption: result.content_preview || result.caption || result.content,
          imagePrompt: result.image_prompt || '',
          hashtags: result.hashtags || prev.hashtags
        }));
        showNotification(`Content generated! Human authenticity: ${result.human_score || 95}%`, 'success');
      } else { showNotification(result.error || 'Content generation failed', 'error'); }
    } catch (error) { showNotification('AI generation failed: ' + error.message, 'error'); } finally { setPostCreator(prev => ({ ...prev, isGeneratingContent: false })); }
  }, [makeAuthenticatedRequest, showNotification, userProfile]);

  const generateInstagramImage = useCallback(async () => {
    if (!postCreator.imagePrompt) { showNotification('Please add an image description first', 'error'); return; }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingImage: true }));
      showNotification('Generating image for Instagram post...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/ai/generate-image', {
        method: 'POST',
        body: JSON.stringify({
          prompt: postCreator.imagePrompt,
          platform: 'instagram',
          style: 'modern, engaging, high-quality'
        })
      });

      const result = await response.json();

      if (result.success) {
        setPostCreator(prev => ({ ...prev, generatedImage: result.image_url }));
        showNotification('Image generated successfully!', 'success');
      } else { showNotification(result.error || 'Image generation failed', 'error'); }
    } catch (error) { showNotification('Image generation failed: ' + error.message, 'error'); } finally { setPostCreator(prev => ({ ...prev, isGeneratingImage: false })); }
  }, [makeAuthenticatedRequest, showNotification, postCreator.imagePrompt]);

  const publishInstagramPost = useCallback(async () => {
    if (!postCreator.caption) { showNotification('Please add a caption to your post', 'error'); return; }
    if (!instagramConnected) { showNotification('Please connect your Instagram account first', 'error'); return; }

    try {
      setLoading(true);
      showNotification('Publishing to Instagram...', 'info');
      
      const fullCaption = `${postCreator.caption}\n\n${postCreator.hashtags.join(' ')}`;
      
      const response = await makeAuthenticatedRequest('/api/post/manual', {
        method: 'POST',
        body: JSON.stringify({
          platform: 'instagram',
          title: 'Instagram Post',
          content: fullCaption,
          image_url: postCreator.generatedImage
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification(`Posted successfully to @${instagramUsername}!`, 'success');
        if (result.post_url) { showNotification(`View post: ${result.post_url}`, 'info'); }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setPostCreator({ caption: '', hashtags: [], imagePrompt: '', generatedImage: '', contentType: 'single', isGeneratingContent: false, isGeneratingImage: false });
      } else { showNotification(result.error || 'Publishing failed', 'error'); }
    } catch (error) { showNotification('Publishing failed: ' + error.message, 'error'); } finally { setLoading(false); }
  }, [postCreator, instagramConnected, instagramUsername, makeAuthenticatedRequest, showNotification]);

  const addHashtag = (hashtag) => {
    if (hashtag && !postCreator.hashtags.includes(hashtag) && postCreator.hashtags.length < 30) {
      setPostCreator(prev => ({ ...prev, hashtags: [...prev.hashtags, hashtag] }));
    }
  };

  const removeHashtag = (hashtagToRemove) => {
    setPostCreator(prev => ({ ...prev, hashtags: prev.hashtags.filter(h => h !== hashtagToRemove) }));
  };

  const addTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    const testTime = now.toTimeString().slice(0, 5);
    if (!automationConfig.postingTimes.includes(testTime)) {
      setAutomationConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, testTime].sort() }));
      showNotification('Test time added (+5 minutes)', 'info');
    }
  };

  const removeTime = (time) => {
    setAutomationConfig(prev => ({ ...prev, postingTimes: prev.postingTimes.filter(t => t !== time) }));
  };

  const startAutomation = useCallback(async () => {
    if (!userProfile.isConfigured) { showNotification('Please configure your profile first', 'error'); setActiveTab('setup'); return; }
    if (!instagramConnected) { showNotification('Please connect your Instagram account first', 'error'); return; }

    try {
      setLoading(true);
      showNotification('Setting up Instagram automation...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/setup-auto-posting', {
        method: 'POST',
        body: JSON.stringify({
          platform: 'instagram',
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle,
          posts_per_day: automationConfig.postsPerDay,
          posting_times: automationConfig.postingTimes,
          hashtag_strategy: automationConfig.hashtagStrategy,
          content_mix: automationConfig.contentMix
        })
      });

      const result = await response.json();

      if (result.success) {
        setAutomationConfig(prev => ({ ...prev, enabled: true }));
        showNotification(`Instagram automation started for @${instagramUsername}!`, 'success');
      } else { showNotification(result.error || 'Automation setup failed', 'error'); }
    } catch (error) { showNotification('Setup failed: ' + error.message, 'error'); } finally { setLoading(false); }
  }, [instagramConnected, instagramUsername, userProfile, automationConfig, makeAuthenticatedRequest, showNotification]);

  return (
    <div className="ig-automation-container">
      
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
              <div className="spinner-outer"></div>
              <div className="spinner-inner"></div>
            </div>
            <p className="loading-text">Processing Instagram request...</p>
          </div>
        </div>
      )}

      {/* Sidebar Overlay for Mobile */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>}

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        
        <div className="sidebar-header">
          <div className="header-decoration-1"></div>
          <div className="header-decoration-2"></div>
          <div className="header-content">
            <div className="header-icon">📸</div>
            <h2 className="header-title">Instagram Studio</h2>
            <div className="header-subtitle">AI Content Creation Hub</div>
            <div className="header-user">👋 {user?.name}</div>
          </div>
        </div>

        {/* Connection Status - Positioned at Top */}
        <div className="connection-section">
          <h3 className="connection-title">CONNECTION STATUS</h3>
          <div className={`connection-card ${instagramConnected ? 'connected' : 'disconnected'}`}>
            {instagramConnected ? (
              <div className="connection-content">
                <div className="status-badge status-connected">
                  <div className="status-dot"></div>
                  <span>Connected</span>
                </div>
                {instagramUsername && <div className="username-badge">@{instagramUsername}</div>}
                <div className="account-type">Account: {accountType}</div>
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
                <p className="connection-message">Connect your Instagram account to start creating stunning AI-powered content</p>
                <button onClick={handleInstagramConnect} disabled={loading} className="connection-btn connect-btn">
                  {loading ? 'Connecting...' : '📸 Connect Instagram'}
                </button>
              </div>
            )}
          </div>
        </div>
        
        {/* Navigation */}
        <nav className="sidebar-nav">
          {[
            { id: 'setup', icon: '⚙️', label: 'Profile Setup', desc: 'Configure AI settings' },
            { id: 'connect', icon: '🔗', label: 'Connection', desc: 'Link Instagram account' },
            { id: 'create', icon: '🎨', label: 'Create Post', desc: 'AI content generation' },
            { id: 'automate', icon: '🤖', label: 'Automation', desc: 'Schedule & settings' },
            { id: 'analytics', icon: '📈', label: 'Analytics', desc: 'Performance insights' }
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
            <h1 className="main-title">Instagram Content Studio</h1>
            <p className="main-subtitle">Create stunning, AI-powered content for your Instagram audience</p>
          </div>
          
          {userProfile.isConfigured && instagramConnected && (
            <button 
              onClick={startAutomation} 
              disabled={loading || automationConfig.enabled} 
              className="start-automation-btn"
            >
              <span className="btn-icon">🚀</span>
              <span className="btn-text">{automationConfig.enabled ? 'Automation Active' : 'Start Automation'}</span>
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
                  <p className="section-desc">Configure your business profile to generate authentic, engaging Instagram content that resonates with your audience</p>
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
                      <div className="success-text">AI is ready for human-like content generation on Instagram.</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Connect Tab */}
            {activeTab === 'connect' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">🔗 Connection</div>
                  <h2 className="section-title">Instagram Connection</h2>
                </div>
                
                {instagramConnected ? (
                  <div className="connect-success">
                    <div className="success-icon-large">✅</div>
                    <h3 className="success-title-large">Instagram Connected Successfully!</h3>
                    <div className="connect-info-card">
                      <p className="connect-info">Connected Account: <strong>@{instagramUsername}</strong></p>
                      <p className="connect-info">Account Type: <strong>{accountType}</strong></p>
                    </div>
                  </div>
                ) : (
                  <div className="connect-prompt">
                    <div className="prompt-icon">📸</div>
                    <h3 className="prompt-title">Connect Your Instagram Account</h3>
                    <p className="prompt-text">Connect your Instagram account to start creating and scheduling authentic, AI-generated content that grows your following and engagement exponentially.</p>
                    <button onClick={handleInstagramConnect} disabled={loading} className="connect-btn-large">
                      {loading ? 'Connecting...' : '📸 Connect Instagram Account'}
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Create Tab */}
            {activeTab === 'create' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">🎨 Content Creator</div>
                  <h2 className="section-title">Instagram Content Creator</h2>
                  <p className="section-desc">Create stunning Instagram posts with AI-powered captions, hashtags, and image generation</p>
                </div>
                
                {!instagramConnected ? (
                  <div className="warning-box">
                    <div className="warning-icon">🔒</div>
                    <p className="warning-text">Please connect your Instagram account first to create content.</p>
                    <button onClick={() => setActiveTab('connect')} className="warning-btn">Go to Connection</button>
                  </div>
                ) : !userProfile.isConfigured ? (
                  <div className="warning-box">
                    <div className="warning-icon">⚙️</div>
                    <p className="warning-text">Please configure your profile first to generate content.</p>
                    <button onClick={() => setActiveTab('setup')} className="warning-btn">Go to Profile Setup</button>
                  </div>
                ) : (
                  <div>
                    <div className="content-type-section">
                      <div className="form-group">
                        <label className="form-label">Content Type</label>
                        <select value={postCreator.contentType} onChange={(e) => setPostCreator(prev => ({ ...prev, contentType: e.target.value }))} className="form-select">
                          {Object.entries(CONTENT_TYPES).map(([key, desc]) => (<option key={key} value={key}>{desc}</option>))}
                        </select>
                      </div>
                      <button onClick={generateInstagramContent} disabled={postCreator.isGeneratingContent} className="generate-btn">
                        <span className="btn-icon">✨</span>
                        <span className="btn-text">{postCreator.isGeneratingContent ? 'Generating...' : 'Generate Content'}</span>
                      </button>
                    </div>

                    <div className="create-grid">
                      <div className="create-left">
                        <div className="form-group">
                          <label className="form-label">Instagram Caption</label>
                          <textarea value={postCreator.caption} onChange={(e) => setPostCreator(prev => ({ ...prev, caption: e.target.value }))} placeholder="Write your Instagram caption here or generate with AI..." rows="8" className="form-textarea" />
                        </div>
                        
                        <div className="hashtags-section">
                          <label className="form-label">Hashtags ({postCreator.hashtags.length}/30)</label>
                          <div className="hashtags-container">
                            {postCreator.hashtags.map(hashtag => (
                              <span key={hashtag} className="hashtag-badge">
                                {hashtag}
                                <button onClick={() => removeHashtag(hashtag)} className="hashtag-remove">×</button>
                              </span>
                            ))}
                          </div>
                          
                          <div className="hashtag-suggestions">
                            {Object.entries(POPULAR_HASHTAGS).map(([category, tags]) => (
                              <div key={category} className="hashtag-category">
                                <div className="category-label">{category}:</div>
                                <div className="category-tags">
                                  {tags.map(tag => (
                                    <button key={tag} onClick={() => addHashtag(tag)} disabled={postCreator.hashtags.includes(tag) || postCreator.hashtags.length >= 30} className="tag-btn">
                                      {tag}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="create-right">
                        <div className="form-group">
                          <label className="form-label">Image Description</label>
                          <textarea value={postCreator.imagePrompt} onChange={(e) => setPostCreator(prev => ({ ...prev, imagePrompt: e.target.value }))} placeholder="Describe the image you want to generate..." rows="4" className="form-textarea" />
                        </div>
                        
                        <button onClick={generateInstagramImage} disabled={postCreator.isGeneratingImage || !postCreator.imagePrompt} className="image-btn">
                          <span className="btn-icon">🖼️</span>
                          <span className="btn-text">{postCreator.isGeneratingImage ? 'Generating Image...' : 'Generate Image'}</span>
                        </button>

                        {postCreator.generatedImage && (
                          <div className="generated-image-container">
                            <label className="form-label">Generated Image</label>
                            <img src={postCreator.generatedImage} alt="Generated" className="generated-image" />
                          </div>
                        )}

                        <button onClick={publishInstagramPost} disabled={loading || !postCreator.caption} className="publish-btn">
                          <span className="btn-icon">🚀</span>
                          <span className="btn-text">{loading ? 'Publishing...' : 'Publish to Instagram'}</span>
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Automate Tab */}
            {activeTab === 'automate' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">🤖 Automation</div>
                  <h2 className="section-title">Instagram Automation Settings</h2>
                  <p className="section-desc">Configure automated posting schedule and content strategy for Instagram</p>
                </div>
                
                {!userProfile.isConfigured ? (
                  <div className="warning-box">
                    <div className="warning-icon">⚙️</div>
                    <p className="warning-text">Please configure your profile first to set up automation.</p>
                    <button onClick={() => setActiveTab('setup')} className="warning-btn">Go to Profile Setup</button>
                  </div>
                ) : !instagramConnected ? (
                  <div className="warning-box">
                    <div className="warning-icon">🔒</div>
                    <p className="warning-text">Please connect your Instagram account first to set up automation.</p>
                    <button onClick={() => setActiveTab('connect')} className="warning-btn">Go to Connection</button>
                  </div>
                ) : (
                  <div className="automation-container">
                    <div className="automation-card">
                      <div className="automation-header">
                        <div className="automation-icon">📸</div>
                        <h3 className="automation-title">Instagram Auto-Posting</h3>
                      </div>
                      
                      <div className="form-group">
                        <label className="form-label">Posts Per Day</label>
                        <input type="number" min="1" max="3" value={automationConfig.postsPerDay} onChange={(e) => setAutomationConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} className="form-input-number" />
                        <div className="form-hint">Recommended: 1-2 posts per day for optimal engagement</div>
                      </div>

                      <div className="form-group">
                        <div className="times-header">
                          <label className="form-label">Posting Times</label>
                          <button type="button" onClick={addTime} className="add-time-btn">+ Add Test Time</button>
                        </div>
                        
                        <input type="time" onChange={(e) => { if (e.target.value && !automationConfig.postingTimes.includes(e.target.value)) { setAutomationConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); e.target.value = ''; } }} className="form-input" />

                        {automationConfig.postingTimes.length > 0 && (
                          <div className="times-list">
                            {automationConfig.postingTimes.map(time => (
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
                          <div className={`status-indicator ${automationConfig.enabled ? 'active' : 'inactive'}`}></div>
                          <span className="status-text">
                            {automationConfig.enabled ? (
                              <span>✓ Active - {automationConfig.postsPerDay} posts/day</span>
                            ) : (
                              <span>○ Inactive - Configure and start automation</span>
                            )}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Analytics Tab */}
            {activeTab === 'analytics' && (
              <div className="tab-pane">
                <div className="section-header">
                  <div className="section-badge">📈 Analytics</div>
                  <h2 className="section-title">Performance Analytics</h2>
                  <p className="section-desc">Track your Instagram automation performance and engagement metrics</p>
                </div>
                
                <div className="stats-grid">
                  <div className="stat-card stat-ig">
                    <div className="stat-header">
                      <div className="stat-icon-ig">📸</div>
                      <h3 className="stat-title">Instagram Connection</h3>
                    </div>
                    <div className={`stat-badge ${instagramConnected ? 'badge-success' : 'badge-error'}`}>
                      {instagramConnected ? '✓ Connected' : '○ Disconnected'}
                    </div>
                    {instagramUsername && <p className="stat-info">Account: <strong>@{instagramUsername}</strong></p>}
                    <p className="stat-info">Type: <strong>{accountType}</strong></p>
                  </div>

                  <div className="stat-card stat-ai">
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

                  <div className="stat-card stat-auto">
                    <div className="stat-header">
                      <div className="stat-icon-auto">⚡</div>
                      <h3 className="stat-title">Automation Status</h3>
                    </div>
                    <div className={`stat-badge ${automationConfig.enabled ? 'badge-success' : 'badge-error'}`}>
                      {automationConfig.enabled ? '✓ Active' : '○ Inactive'}
                    </div>
                    {automationConfig.enabled && (
                      <div className="stat-details">
                        <p className="stat-info">Posts/Day: <strong>{automationConfig.postsPerDay}</strong></p>
                        <p className="stat-info">Times: <strong>{automationConfig.postingTimes.length}</strong></p>
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

        .ig-automation-container {
          font-family: 'Inter', 'SF Pro Display', system-ui, -apple-system, sans-serif;
          min-height: 100vh;
          background: radial-gradient(circle at top right, #833ab4 0%, #fd1d1d 50%, #fcb045 100%);
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
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
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
          background: linear-gradient(135deg, #E4405F, #C13584);
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
          border-radius: 16px;
          backdrop-filter: blur(20px);
          color: white;
          font-weight: 600;
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          font-size: 15px;
          animation: slideInRight 0.4s ease-out;
          border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .notification-success {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.95), rgba(5, 150, 105, 0.95));
        }

        .notification-error {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.95), rgba(220, 38, 38, 0.95));
        }

        .notification-info {
          background: linear-gradient(135deg, rgba(59, 130, 246, 0.95), rgba(37, 99, 235, 0.95));
        }

        .notification-close {
          background: rgba(255, 255, 255, 0.25);
          border: none;
          color: white;
          font-size: 20px;
          cursor: pointer;
          padding: 4px 8px;
          border-radius: 8px;
          transition: all 0.2s;
          line-height: 1;
          font-weight: 700;
        }

        .notification-close:hover {
          background: rgba(255, 255, 255, 0.35);
        }

        /* Loading Overlay */
        .loading-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          backdrop-filter: blur(16px);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 9999;
          animation: fadeIn 0.3s ease-out;
        }

        .loading-content {
          background: linear-gradient(135deg, #ffffff, #f8f9fa);
          padding: 56px 72px;
          border-radius: 28px;
          text-align: center;
          box-shadow: 0 24px 72px rgba(0, 0, 0, 0.5);
          animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        .spinner-container {
          position: relative;
          width: 72px;
          height: 72px;
          margin: 0 auto;
        }

        .spinner-outer {
          position: absolute;
          width: 72px;
          height: 72px;
          border-radius: 50%;
          border: 6px solid transparent;
          border-top-color: #E4405F;
          border-right-color: #C13584;
          animation: spinGradient 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
        }

        .spinner-inner {
          position: absolute;
          width: 72px;
          height: 72px;
          border-radius: 50%;
          border: 6px solid transparent;
          border-bottom-color: #833ab4;
          border-left-color: #fcb045;
          animation: spinGradient 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite reverse;
          animation-delay: -0.6s;
        }

        .loading-text {
          margin-top: 28px;
          color: #1f2937;
          font-size: 18px;
          font-weight: 700;
          letter-spacing: -0.01em;
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
          backdrop-filter: blur(30px);
          height: 100vh;
          position: fixed;
          display: flex;
          flex-direction: column;
          box-shadow: 8px 0 48px rgba(0, 0, 0, 0.15);
          border-right: 1px solid rgba(255, 255, 255, 0.4);
          z-index: 1000;
          overflow-y: auto;
          transition: transform 0.3s ease;
        }

        .sidebar-header {
          padding: 32px 24px;
          background: linear-gradient(135deg, #E4405F, #C13584);
          position: relative;
          overflow: hidden;
        }

        .header-decoration-1 {
          position: absolute;
          top: -60%;
          left: -30%;
          width: 250px;
          height: 250px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(255, 255, 255, 0.15), transparent);
          filter: blur(50px);
        }

        .header-decoration-2 {
          position: absolute;
          bottom: -40%;
          right: -20%;
          width: 200px;
          height: 200px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(252, 176, 69, 0.2), transparent);
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
          animation: rotateIn 0.8s ease-out;
        }

        .header-title {
          font-size: 28px;
          font-weight: 900;
          color: white;
          margin-bottom: 6px;
          letter-spacing: -0.03em;
          text-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        }

        .header-subtitle {
          font-size: 14px;
          color: rgba(255, 255, 255, 0.95);
          font-weight: 600;
          letter-spacing: 0.02em;
        }

        .header-user {
          font-size: 13px;
          color: rgba(255, 255, 255, 0.9);
          margin-top: 12px;
          background: rgba(255, 255, 255, 0.2);
          padding: 8px 16px;
          border-radius: 24px;
          display: inline-block;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.3);
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
          position: relative;
          overflow: hidden;
        }

        .connection-card.connected {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(5, 150, 105, 0.08));
          border-color: rgba(16, 185, 129, 0.35);
        }

        .connection-card.disconnected {
          background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(220, 38, 38, 0.08));
          border-color: rgba(239, 68, 68, 0.35);
        }

        .connection-content {
          display: flex;
          flex-direction: column;
          gap: 12px;
          position: relative;
          z-index: 1;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 15px;
          font-weight: 800;
        }

        .status-connected {
          color: #047857;
        }

        .status-disconnected {
          color: #dc2626;
        }

        .status-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          animation: pulseGlow 2.5s ease-in-out infinite;
        }

        .status-connected .status-dot {
          background: #10b981;
          box-shadow: 0 0 0 5px rgba(16, 185, 129, 0.25);
        }

        .status-disconnected .status-dot {
          background: #ef4444;
        }

        .username-badge {
          font-size: 14px;
          color: #065f46;
          font-weight: 700;
          background: rgba(16, 185, 129, 0.2);
          padding: 10px 14px;
          border-radius: 12px;
          display: inline-block;
          border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .account-type {
          font-size: 13px;
          color: #059669;
          font-weight: 600;
          opacity: 0.9;
        }

        .connection-message {
          font-size: 13px;
          color: #7f1d1d;
          line-height: 1.6;
          font-weight: 500;
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
          letter-spacing: 0.02em;
        }

        .test-btn {
          background: linear-gradient(135deg, #10b981, #059669);
          box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
        }

        .connect-btn {
          background: linear-gradient(135deg, #E4405F, #C13584);
          box-shadow: 0 6px 16px rgba(228, 64, 95, 0.35);
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
          overflow-y: auto;
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
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          position: relative;
          overflow: hidden;
        }

        .nav-btn:hover {
          background: rgba(228, 64, 95, 0.08);
          transform: translateX(6px);
        }

        .nav-btn-active {
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          transform: translateX(8px) scale(1.02);
          box-shadow: 0 10px 28px rgba(228, 64, 95, 0.35);
        }

        .nav-btn-active::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(255, 255, 255, 0.1);
          animation: shimmer 2s infinite;
        }

        .nav-icon {
          font-size: 24px;
          transition: transform 0.4s;
          position: relative;
          z-index: 1;
        }

        .nav-btn-active .nav-icon {
          transform: rotate(10deg) scale(1.1);
        }

        .nav-content {
          flex: 1;
          position: relative;
          z-index: 1;
        }

        .nav-label {
          font-weight: 700;
          font-size: 16px;
          margin-bottom: 3px;
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
          backdrop-filter: blur(30px);
          border-bottom: 1px solid rgba(0, 0, 0, 0.08);
          display: flex;
          justify-content: space-between;
          align-items: center;
          position: sticky;
          top: 0;
          z-index: 50;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
        }

        .header-text {
          flex: 1;
        }

        .main-title {
          font-size: 36px;
          font-weight: 900;
          background: linear-gradient(135deg, #E4405F, #C13584, #833ab4);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          margin-bottom: 8px;
          letter-spacing: -0.03em;
        }

        .main-subtitle {
          font-size: 17px;
          color: #64748b;
          font-weight: 600;
        }

        .start-automation-btn {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 18px 36px;
          border: none;
          border-radius: 16px;
          font-size: 17px;
          font-weight: 800;
          cursor: pointer;
          color: white;
          box-shadow: 0 10px 28px rgba(228, 64, 95, 0.4);
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          letter-spacing: 0.01em;
        }

        .start-automation-btn:not(:disabled) {
          background: linear-gradient(135deg, #E4405F, #C13584);
        }

        .start-automation-btn:hover:not(:disabled) {
          transform: translateY(-3px) scale(1.02);
          box-shadow: 0 14px 36px rgba(228, 64, 95, 0.5);
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
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.12);
          max-width: 1400px;
          margin: 0 auto;
          position: relative;
          overflow: hidden;
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
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.12), rgba(118, 75, 162, 0.12));
          padding: 12px 24px;
          border-radius: 20px;
          margin-bottom: 16px;
          font-size: 14px;
          font-weight: 700;
          color: #667eea;
          border: 2px solid rgba(102, 126, 234, 0.2);
        }

        .section-title {
          font-size: 40px;
          font-weight: 900;
          color: #1f2937;
          margin-bottom: 16px;
          letter-spacing: -0.03em;
        }

        .section-desc {
          font-size: 17px;
          color: #64748b;
          max-width: 700px;
          margin: 0 auto;
          line-height: 1.7;
          font-weight: 500;
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
          font-size: 16px;
          font-weight: 800;
          color: #374151;
          margin-bottom: 12px;
          letter-spacing: -0.01em;
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
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .form-input:focus, .form-select:focus, .form-textarea:focus {
          border-color: #E4405F;
          box-shadow: 0 4px 16px rgba(228, 64, 95, 0.15);
        }

        .form-textarea {
          resize: vertical;
          line-height: 1.7;
        }

        .form-input-number {
          padding: 14px 18px;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          width: 140px;
          font-size: 20px;
          font-weight: 800;
          background: white;
          transition: all 0.3s;
          outline: none;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .form-input-number:focus {
          border-color: #E4405F;
        }

        .form-hint {
          font-size: 14px;
          color: #6b7280;
          margin-top: 10px;
          font-weight: 600;
        }

        .form-actions {
          text-align: center;
          margin-top: 40px;
        }

        .primary-btn, .generate-btn, .image-btn, .publish-btn {
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
          transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
          letter-spacing: 0.01em;
        }

        .primary-btn {
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          box-shadow: 0 8px 24px rgba(228, 64, 95, 0.4);
        }

        .generate-btn {
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          box-shadow: 0 8px 24px rgba(102, 126, 234, 0.35);
        }

        .image-btn {
          width: 100%;
          background: linear-gradient(135deg, #10b981, #059669);
          color: white;
          box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
          margin-bottom: 20px;
        }

        .publish-btn {
          width: 100%;
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          box-shadow: 0 8px 24px rgba(228, 64, 95, 0.4);
        }

        .primary-btn:hover:not(:disabled),
        .generate-btn:hover:not(:disabled),
        .image-btn:hover:not(:disabled),
        .publish-btn:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .primary-btn:disabled,
        .generate-btn:disabled,
        .image-btn:disabled,
        .publish-btn:disabled {
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
          animation: slideInFromBottom 0.6s ease-out;
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

        /* Connect Success/Prompt */
        .connect-success, .connect-prompt {
          text-align: center;
          padding: 40px;
        }

        .success-icon-large, .prompt-icon {
          font-size: 80px;
          margin-bottom: 20px;
        }

        .success-title-large, .prompt-title {
          font-size: 28px;
          font-weight: 800;
          margin-bottom: 24px;
        }

        .success-title-large {
          color: #10b981;
        }

        .prompt-title {
          color: #64748b;
        }

        .connect-info-card {
          background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
          padding: 24px;
          border-radius: 16px;
          margin-bottom: 32px;
          border: 2px solid rgba(16, 185, 129, 0.3);
        }

        .connect-info {
          font-size: 18px;
          color: #155724;
          margin-bottom: 8px;
          font-weight: 600;
        }

        .prompt-text {
          font-size: 16px;
          color: #64748b;
          margin-bottom: 32px;
          line-height: 1.8;
          max-width: 700px;
          margin-left: auto;
          margin-right: auto;
        }

        .connect-btn-large {
          padding: 20px 40px;
          border: none;
          border-radius: 16px;
          font-size: 18px;
          font-weight: 700;
          cursor: pointer;
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          box-shadow: 0 6px 20px rgba(228, 64, 95, 0.4);
          transition: all 0.3s ease;
        }

        .connect-btn-large:hover:not(:disabled) {
          transform: translateY(-2px);
        }

        .connect-btn-large:disabled {
          background: #bdc3c7;
          cursor: not-allowed;
        }

        /* Warning Box */
        .warning-box {
          text-align: center;
          padding: 56px;
          background: linear-gradient(135deg, rgba(251, 191, 36, 0.05), rgba(245, 158, 11, 0.05));
          border-radius: 24px;
          border: 2px dashed rgba(251, 191, 36, 0.3);
        }

        .warning-icon {
          font-size: 64px;
          margin-bottom: 24px;
        }

        .warning-text {
          font-size: 20px;
          color: #64748b;
          margin-bottom: 28px;
          font-weight: 600;
        }

        .warning-btn {
          padding: 16px 40px;
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          border: none;
          border-radius: 16px;
          font-size: 17px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s;
        }

        .warning-btn:hover {
          transform: translateY(-2px);
        }

        /* Content Type Section */
        .content-type-section {
          display: grid;
          grid-template-columns: 1fr auto;
          gap: 24px;
          margin-bottom: 32px;
          align-items: end;
        }

        /* Create Grid */
        .create-grid {
          display: grid;
          grid-template-columns: 1.2fr 1fr;
          gap: 32px;
        }

        /* Hashtags */
        .hashtags-section {
          margin-top: 20px;
        }

        .hashtags-container {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 12px;
          min-height: 50px;
          padding: 12px;
          border: 2px solid #e5e7eb;
          border-radius: 12px;
          background: white;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .hashtag-badge {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 8px 14px;
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          border-radius: 14px;
          font-size: 14px;
          font-weight: 700;
          transition: all 0.3s;
        }

        .hashtag-remove {
          background: rgba(255, 255, 255, 0.25);
          border: none;
          color: white;
          font-size: 18px;
          cursor: pointer;
          padding: 4px 8px;
          line-height: 1;
          border-radius: 8px;
          transition: all 0.2s;
          font-weight: 700;
        }

        .hashtag-remove:hover {
          background: rgba(255, 255, 255, 0.4);
        }

        .hashtag-suggestions {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }

        .hashtag-category {
          margin-bottom: 12px;
          width: 100%;
        }

        .category-label {
          font-size: 13px;
          color: #64748b;
          margin-bottom: 8px;
          font-weight: 800;
          text-transform: capitalize;
          letter-spacing: 0.02em;
        }

        .category-tags {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }

        .tag-btn {
          padding: 6px 12px;
          font-size: 13px;
          background: white;
          color: #374151;
          border: 2px solid #e5e7eb;
          border-radius: 10px;
          cursor: pointer;
          font-weight: 700;
          transition: all 0.2s;
        }

        .tag-btn:hover:not(:disabled) {
          background: #E4405F;
          color: white;
          border-color: #E4405F;
        }

        .tag-btn:disabled {
          background: #e5e7eb;
          color: #9ca3af;
          cursor: not-allowed;
        }

        /* Generated Image */
        .generated-image-container {
          margin-bottom: 20px;
        }

        .generated-image {
          width: 100%;
          border-radius: 12px;
          border: 2px solid #e5e7eb;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
          transition: all 0.3s;
        }

        .generated-image:hover {
          transform: scale(1.02);
        }

        /* Automation */
        .automation-container {
          max-width: 800px;
          margin: 0 auto;
        }

        .automation-card {
          padding: 40px;
          background: linear-gradient(135deg, rgba(228, 64, 95, 0.08), rgba(193, 53, 132, 0.08));
          border-radius: 24px;
          border: 3px solid rgba(228, 64, 95, 0.25);
          position: relative;
          overflow: hidden;
        }

        .automation-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 32px;
        }

        .automation-icon {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          background: linear-gradient(135deg, #E4405F, #C13584);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 28px;
          box-shadow: 0 8px 20px rgba(228, 64, 95, 0.3);
        }

        .automation-title {
          font-size: 24px;
          font-weight: 900;
          color: #1f2937;
        }

        .times-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .add-time-btn {
          padding: 12px 24px;
          font-size: 14px;
          background: linear-gradient(135deg, #E4405F, #C13584);
          color: white;
          border: none;
          border-radius: 12px;
          cursor: pointer;
          font-weight: 800;
          transition: all 0.3s;
          box-shadow: 0 6px 16px rgba(228, 64, 95, 0.35);
          letter-spacing: 0.02em;
        }

        .add-time-btn:hover {
          transform: translateY(-2px);
        }

        .times-list {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 16px;
        }

        .time-badge {
          display: inline-flex;
          align-items: center;
          gap: 10px;
          padding: 12px 18px;
          background: white;
          border: 2px solid rgba(228, 64, 95, 0.35);
          border-radius: 14px;
          color: #E4405F;
          font-size: 16px;
          font-weight: 800;
          transition: all 0.3s;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        }

        .time-remove {
          background: rgba(239, 68, 68, 0.15);
          border: none;
          color: #ef4444;
          font-size: 20px;
          cursor: pointer;
          padding: 6px 10px;
          line-height: 1;
          border-radius: 10px;
          transition: all 0.2s;
          font-weight: 800;
        }

        .time-remove:hover {
          background: rgba(239, 68, 68, 0.25);
        }

        .status-card {
          padding: 20px;
          background: white;
          border-radius: 16px;
          margin-top: 28px;
          border: 2px solid rgba(228, 64, 95, 0.2);
        }

        .status-title {
          font-size: 18px;
          font-weight: 800;
          color: #1f2937;
          margin-bottom: 12px;
        }

        .status-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status-indicator {
          width: 14px;
          height: 14px;
          border-radius: 50%;
          animation: pulseGlow 2.5s ease-in-out infinite;
        }

        .status-indicator.active {
          background: #10b981;
        }

        .status-indicator.inactive {
          background: #ef4444;
        }

        .status-text {
          font-size: 17px;
          color: #374151;
          font-weight: 700;
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
          padding: 28px;
          border: 2px solid;
          transition: all 0.4s;
          cursor: pointer;
          position: relative;
          overflow: hidden;
        }

        .stat-ig {
          border-color: rgba(228, 64, 95, 0.25);
          background: linear-gradient(135deg, rgba(228, 64, 95, 0.05), rgba(193, 53, 132, 0.05));
        }

        .stat-ai {
          border-color: rgba(102, 126, 234, 0.25);
          background: linear-gradient(135deg, rgba(102, 126, 234, 0.05), rgba(118, 75, 162, 0.05));
        }

        .stat-auto {
          border-color: rgba(79, 172, 254, 0.25);
          background: linear-gradient(135deg, rgba(79, 172, 254, 0.05), rgba(0, 242, 254, 0.05));
        }

        .stat-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
        }

        .stat-header {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
        }

        .stat-icon-ig, .stat-icon-ai, .stat-icon-auto {
          width: 48px;
          height: 48px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }

        .stat-icon-ig {
          background: linear-gradient(135deg, #E4405F, #C13584);
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
          background: linear-gradient(135deg, rgba(250, 112, 154, 0.05), rgba(254, 225, 64, 0.05));
          border-radius: 24px;
          border: 2px solid rgba(250, 112, 154, 0.2);
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
          letter-spacing: -0.02em;
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

        @keyframes spinGradient {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(0.95); }
        }

        @keyframes pulseGlow {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(0.98); }
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes bounceIn {
          0% { opacity: 0; transform: scale(0.3); }
          50% { opacity: 1; transform: scale(1.05); }
          70% { transform: scale(0.9); }
          100% { transform: scale(1); }
        }

        @keyframes rotateIn {
          0% { transform: rotate(-200deg) scale(0); opacity: 0; }
          100% { transform: rotate(0) scale(1); opacity: 1; }
        }

        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(100px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes slideInFromBottom {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }

        /* Responsive Design */
        @media (max-width: 1200px) {
          .form-grid {
            grid-template-columns: 1fr;
          }

          .create-grid {
            grid-template-columns: 1fr;
          }

          .content-type-section {
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

          .primary-btn, .generate-btn, .image-btn, .publish-btn {
            width: 100%;
            padding: 16px 32px;
            font-size: 16px;
          }

          .automation-card {
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

          .hashtag-suggestions {
            flex-direction: column;
          }

          .hashtag-category {
            width: 100%;
          }

          .loading-content {
            padding: 40px 50px;
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

          .loading-content {
            padding: 32px 40px;
          }

          .spinner-container {
            width: 56px;
            height: 56px;
          }

          .spinner-outer, .spinner-inner {
            width: 56px;
            height: 56px;
          }
        }
      `}</style>
    </div>
  );
};

export default InstagramAutomation;