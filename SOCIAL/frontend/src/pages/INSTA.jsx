import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const POPULAR_HASHTAGS = { 
  business: ['#entrepreneur', '#business', '#startup', '#success', '#motivation'], 
  food: ['#foodie', '#delicious', '#foodporn', '#yummy', '#instafood'], 
  fitness: ['#fitness', '#workout', '#health', '#gym', '#fitlife'], 
  tech: ['#technology', '#innovation', '#coding', '#startup', '#ai'], 
  lifestyle: ['#lifestyle', '#daily', '#inspiration', '#goals', '#mindset'] 
};

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

const InstagramAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [instagramUsername, setInstagramUsername] = useState('');
  const [accountType, setAccountType] = useState('personal');
  
  const [userProfile, setUserProfile] = useState({ 
    domain: 'tech', 
    businessType: 'AI automation platform', 
    businessDescription: 'We help businesses automate their Instagram presence', 
    targetAudience: 'tech_professionals', 
    contentStyle: 'engaging', 
    isConfigured: false 
  });
  
  const [postCreator, setPostCreator] = useState({ 
    caption: '', 
    hashtags: [], 
    imagePrompt: '', 
    generatedImage: '', 
    contentType: 'single', 
    isGeneratingContent: false, 
    isGeneratingImage: false 
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
    
    const initKey = `instagram_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');

    const checkInstagramConnection = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const igConnected = urlParams.get('instagram_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) { 
        showNotification(`Connection failed: ${error}`, 'error'); 
        window.history.replaceState({}, '', window.location.pathname); 
        return; 
      }

      if (igConnected === 'true' && username) {
        setInstagramConnected(true); 
        setInstagramUsername(username);
        updateUser({ instagram_connected: true, instagram_username: username });
        showNotification(`Instagram connected! Welcome @${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname); 
        return;
      }

      try {
        const response = await makeAuthenticatedRequest('/api/instagram/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setInstagramConnected(true); 
          setInstagramUsername(result.username);
          setAccountType(result.account_type || 'personal');
        }
      } catch (error) { 
        console.error('Failed to check Instagram connection:', error); 
      }

      try {
        const savedProfile = localStorage.getItem(`instagramUserProfile_${user.email}`);
        if (savedProfile) { 
          const profile = JSON.parse(savedProfile); 
          setUserProfile(profile); 
        }
      } catch (error) { 
        console.error('Error loading profile:', error); 
      }
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
      } else { 
        showNotification(result.error || 'Failed to start Instagram authorization', 'error'); 
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
      localStorage.setItem(`instagramUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) { 
      showNotification('Failed to save profile', 'error'); 
    }
  }, [userProfile, user?.email, showNotification]);

  const generateInstagramContent = useCallback(async () => {
    if (!userProfile.businessType) { 
      showNotification('Please configure your profile first', 'error'); 
      return; 
    }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingContent: true }));
      showNotification('Generating Instagram content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
      } else { 
        showNotification(result.error || 'Content generation failed', 'error'); 
      }
    } catch (error) { 
      showNotification('AI generation failed: ' + error.message, 'error'); 
    } finally { 
      setPostCreator(prev => ({ ...prev, isGeneratingContent: false })); 
    }
  }, [makeAuthenticatedRequest, showNotification, userProfile]);

  const generateInstagramImage = useCallback(async () => {
    if (!postCreator.imagePrompt) { 
      showNotification('Please add an image description first', 'error'); 
      return; 
    }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingImage: true }));
      showNotification('Generating image for Instagram post...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/ai/generate-image', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
      } else { 
        showNotification(result.error || 'Image generation failed', 'error'); 
      }
    } catch (error) { 
      showNotification('Image generation failed: ' + error.message, 'error'); 
    } finally { 
      setPostCreator(prev => ({ ...prev, isGeneratingImage: false })); 
    }
  }, [makeAuthenticatedRequest, showNotification, postCreator.imagePrompt]);

  const publishInstagramPost = useCallback(async () => {
    if (!postCreator.caption) { 
      showNotification('Please add a caption to your post', 'error'); 
      return; 
    }
    if (!instagramConnected) { 
      showNotification('Please connect your Instagram account first', 'error'); 
      return; 
    }

    try {
      setLoading(true);
      showNotification('Publishing to Instagram...', 'info');
      
      const fullCaption = `${postCreator.caption}\n\n${postCreator.hashtags.join(' ')}`;
      
      const response = await makeAuthenticatedRequest('/api/post/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
        if (result.post_url) { 
          showNotification(`View post: ${result.post_url}`, 'info'); 
        }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setPostCreator({ 
          caption: '', 
          hashtags: [], 
          imagePrompt: '', 
          generatedImage: '', 
          contentType: 'single', 
          isGeneratingContent: false, 
          isGeneratingImage: false 
        });
      } else { 
        showNotification(result.error || 'Publishing failed', 'error'); 
      }
    } catch (error) { 
      showNotification('Publishing failed: ' + error.message, 'error'); 
    } finally { 
      setLoading(false); 
    }
  }, [postCreator, instagramConnected, instagramUsername, makeAuthenticatedRequest, showNotification]);

  const addHashtag = (hashtag) => {
    if (hashtag && !postCreator.hashtags.includes(hashtag) && postCreator.hashtags.length < 30) {
      setPostCreator(prev => ({ ...prev, hashtags: [...prev.hashtags, hashtag] }));
    }
  };

  const removeHashtag = (hashtag) => {
    setPostCreator(prev => ({ ...prev, hashtags: prev.hashtags.filter(h => h !== hashtag) }));
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #833AB4 0%, #FD1D1D 50%, #F77737 100%)',
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
              background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              📸 Instagram Automation
            </h1>
            <p style={{
              margin: '8px 0 0 0',
              color: '#666',
              fontSize: '16px'
            }}>
              {user?.name ? `Welcome, ${user.name}!` : 'Manage your Instagram presence'}
            </p>
          </div>

          {instagramConnected && (
            <div style={{
              background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              ✅ Connected: @{instagramUsername}
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
                ? 'linear-gradient(135deg, #833AB4, #FD1D1D)' 
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
              color: '#833AB4',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Instagram Connection Setup
            </h2>

            {!instagramConnected ? (
              <div>
                <div style={{
                  background: '#fff3cd',
                  border: '1px solid #ffc107',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '30px'
                }}>
                  <p style={{ margin: 0, color: '#856404', fontSize: '16px' }}>
                    ⚠️ Connect your Instagram account to start automating your posts
                  </p>
                </div>

                <button
                  onClick={handleInstagramConnect}
                  disabled={loading}
                  style={{
                    background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
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
                  {loading ? '⏳ Connecting...' : '📸 Connect Instagram Account'}
                </button>

                <div style={{
                  marginTop: '40px',
                  padding: '24px',
                  background: '#f8f9fa',
                  borderRadius: '12px'
                }}>
                  <h3 style={{ color: '#833AB4', marginBottom: '16px' }}>
                    What you'll get:
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                    <li>AI-powered content generation</li>
                    <li>Auto-generate engaging captions and hashtags</li>
                    <li>Create stunning images with AI</li>
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
                    ✅ Instagram connected successfully as @{instagramUsername}
                  </p>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '20px',
                  marginTop: '30px'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>📸</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>Ready to Post</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Start creating amazing content
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #F77737, #FD1D1D)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>🤖</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>AI Powered</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Generate captions and images
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #833AB4, #833AB4)',
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
              color: '#833AB4',
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
                background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
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
              color: '#833AB4',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Create Instagram Post
            </h2>

            {!instagramConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Please connect Instagram first to create posts
                </p>
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
                Caption
              </label>
              <textarea
                value={postCreator.caption}
                onChange={(e) => setPostCreator(prev => ({ ...prev, caption: e.target.value }))}
                placeholder="Write your Instagram caption..."
                rows="6"
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
                onClick={generateInstagramContent}
                disabled={postCreator.isGeneratingContent || !userProfile.isConfigured}
                style={{
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  padding: '16px 32px',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: (postCreator.isGeneratingContent || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  width: '100%',
                  justifyContent: 'center'
                }}
              >
                {postCreator.isGeneratingContent ? '⏳ Generating...' : '🤖 Generate Caption with AI'}
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
                Image Description (for AI generation)
              </label>
              <input
                type="text"
                value={postCreator.imagePrompt}
                onChange={(e) => setPostCreator(prev => ({ ...prev, imagePrompt: e.target.value }))}
                placeholder="e.g., Modern workspace with laptop and coffee"
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
              <button
                onClick={generateInstagramImage}
                disabled={postCreator.isGeneratingImage || !postCreator.imagePrompt}
                style={{
                  background: 'linear-gradient(135deg, #F77737, #FD1D1D)',
                  padding: '16px 32px',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: (postCreator.isGeneratingImage || !postCreator.imagePrompt) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  width: '100%',
                  justifyContent: 'center'
                }}
              >
                {postCreator.isGeneratingImage ? '⏳ Creating Image...' : '🎨 Generate Image with AI'}
              </button>
            </div>

            {postCreator.generatedImage && (
              <div style={{
                marginBottom: '24px',
                textAlign: 'center'
              }}>
                <img
                  src={postCreator.generatedImage}
                  alt="Generated"
                  style={{
                    maxWidth: '100%',
                    maxHeight: '400px',
                    borderRadius: '12px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                />
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
                Hashtags ({postCreator.hashtags.length}/30)
              </label>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
                marginBottom: '16px'
              }}>
                {postCreator.hashtags.map((hashtag, index) => (
                  <span key={index} style={{
                    background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
                    color: 'white',
                    padding: '8px 16px',
                    borderRadius: '20px',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    {hashtag}
                    <button
                      onClick={() => removeHashtag(hashtag)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'white',
                        cursor: 'pointer',
                        fontSize: '16px',
                        padding: 0
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px'
              }}>
                {POPULAR_HASHTAGS[userProfile.domain]?.map((hashtag, index) => (
                  <button
                    key={index}
                    onClick={() => addHashtag(hashtag)}
                    disabled={postCreator.hashtags.includes(hashtag)}
                    style={{
                      background: postCreator.hashtags.includes(hashtag) ? '#ddd' : '#f8f9fa',
                      border: '2px solid #ddd',
                      padding: '8px 16px',
                      borderRadius: '20px',
                      fontSize: '14px',
                      cursor: postCreator.hashtags.includes(hashtag) ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {hashtag}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={publishInstagramPost}
              disabled={loading || !postCreator.caption || !instagramConnected}
              style={{
                background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
                padding: '20px 48px',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: '700',
                cursor: (loading || !postCreator.caption || !instagramConnected) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                margin: '0 auto'
              }}
            >
              {loading ? '⏳ Publishing...' : '📤 Publish to Instagram'}
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
              color: '#833AB4',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Analytics & Performance
            </h2>

            {!instagramConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Connect Instagram to view analytics
                </p>
              </div>
            )}

            {instagramConnected && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #833AB4, #FD1D1D)',
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
                  background: 'linear-gradient(135deg, #F77737, #FD1D1D)',
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
              <h3 style={{ color: '#833AB4', marginBottom: '16px' }}>
                Tips for Better Engagement
              </h3>
              <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                <li>Post consistently at optimal times</li>
                <li>Use relevant hashtags (10-15 per post)</li>
                <li>Engage with your audience through comments</li>
                <li>Use high-quality, eye-catching images</li>
                <li>Tell stories in your captions</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InstagramAutomation;