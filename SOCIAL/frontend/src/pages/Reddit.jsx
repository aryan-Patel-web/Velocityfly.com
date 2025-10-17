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

const RedditAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  const [redditConnected, setRedditConnected] = useState(false);
  const [redditUsername, setRedditUsername] = useState('');
  
  const [userProfile, setUserProfile] = useState({ 
    domain: 'tech', 
    businessType: 'AI automation platform', 
    businessDescription: 'We help businesses automate their Reddit presence', 
    targetAudience: 'tech_professionals', 
    contentStyle: 'engaging', 
    isConfigured: false 
  });
  
  const [postForm, setPostForm] = useState({ 
    subreddit: 'test',
    title: '', 
    content: '', 
    language: 'en',
    contentType: 'text',
    isGenerating: false 
  });

  const [questionForm, setQuestionForm] = useState({
    subreddits: 'AskReddit,explainlikeimfive,NoStupidQuestions,india',
    keywords: 'help,how,what,why,study,learn',
    limit: 10
  });

  const [questions, setQuestions] = useState([]);
  
  const [performanceData, setPerformanceData] = useState({ 
    postsToday: 0, 
    totalEngagement: 0, 
    successRate: 95,
    questionsFound: 0
  });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: Date.now(), message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  useEffect(() => {
    if (!user?.email) return;
    
    const initKey = `reddit_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');

    const checkRedditConnection = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const redditConnected = urlParams.get('reddit_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) { 
        showNotification(`Connection failed: ${error}`, 'error'); 
        window.history.replaceState({}, '', window.location.pathname); 
        return; 
      }

      if (redditConnected === 'true' && username) {
        setRedditConnected(true); 
        setRedditUsername(username);
        updateUser({ reddit_connected: true, reddit_username: username });
        showNotification(`Reddit connected! Welcome u/${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname); 
        return;
      }

      try {
        const response = await makeAuthenticatedRequest('/api/reddit/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setRedditConnected(true); 
          setRedditUsername(result.reddit_username || result.username);
        }
      } catch (error) { 
        console.error('Failed to check Reddit connection:', error); 
      }

      try {
        const savedProfile = localStorage.getItem(`redditUserProfile_${user.email}`);
        if (savedProfile) { 
          const profile = JSON.parse(savedProfile); 
          setUserProfile(profile); 
        }
      } catch (error) { 
        console.error('Error loading profile:', error); 
      }
    };

    checkRedditConnection();
  }, [user, makeAuthenticatedRequest, updateUser, showNotification]);

  const handleRedditConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Reddit...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/oauth/reddit/authorize');
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else { 
        showNotification(result.error || 'Failed to start Reddit authorization', 'error'); 
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
      localStorage.setItem(`redditUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) { 
      showNotification('Failed to save profile', 'error'); 
    }
  }, [userProfile, user?.email, showNotification]);

  const generateRedditContent = useCallback(async () => {
    if (!userProfile.businessType) { 
      showNotification('Please configure your profile first', 'error'); 
      return; 
    }

    try {
      setPostForm(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating Reddit content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: 'reddit',
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setPostForm(prev => ({
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
      setPostForm(prev => ({ ...prev, isGenerating: false })); 
    }
  }, [makeAuthenticatedRequest, showNotification, userProfile]);

  const publishRedditPost = useCallback(async (e) => {
    e.preventDefault();
    if (!postForm.title || !postForm.content) { 
      showNotification('Please add both title and content', 'error'); 
      return; 
    }
    if (!redditConnected) { 
      showNotification('Please connect your Reddit account first', 'error'); 
      return; 
    }

    try {
      setLoading(true);
      showNotification('Publishing to Reddit...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/reddit/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subreddit: postForm.subreddit,
          title: postForm.title,
          content: postForm.content,
          language: postForm.language,
          contentType: postForm.contentType
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification('Posted successfully to r/' + postForm.subreddit + '!', 'success');
        if (result.post_url) { 
          showNotification(`View post: ${result.post_url}`, 'info'); 
        }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setPostForm({ 
          subreddit: 'test',
          title: '', 
          content: '', 
          language: 'en',
          contentType: 'text',
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
  }, [postForm, redditConnected, makeAuthenticatedRequest, showNotification]);

  const findQuestions = useCallback(async () => {
    if (!questionForm.subreddits || !questionForm.keywords) {
      showNotification('Please enter subreddits and keywords', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Searching for questions...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/reddit/questions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subreddits: questionForm.subreddits,
          keywords: questionForm.keywords,
          limit: questionForm.limit
        })
      });

      const result = await response.json();

      if (result.success) {
        setQuestions(result.questions || []);
        setPerformanceData(prev => ({ ...prev, questionsFound: result.questions?.length || 0 }));
        showNotification(`Found ${result.questions?.length || 0} questions!`, 'success');
      } else {
        showNotification(result.error || 'Search failed', 'error');
      }
    } catch (error) {
      showNotification('Search failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [questionForm, makeAuthenticatedRequest, showNotification]);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #FF4500 0%, #FF8717 100%)',
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
              background: 'linear-gradient(135deg, #FF4500, #FF8717)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent'
            }}>
              🤖 Reddit Automation
            </h1>
            <p style={{
              margin: '8px 0 0 0',
              color: '#666',
              fontSize: '16px'
            }}>
              {user?.name ? `Welcome, ${user.name}!` : 'Automate your Reddit presence'}
            </p>
          </div>

          {redditConnected && (
            <div style={{
              background: 'linear-gradient(135deg, #FF4500, #FF8717)',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '12px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              ✅ Connected: u/{redditUsername}
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
          { id: 'setup', label: '⚙️ Setup' },
          { id: 'profile', label: '👤 Profile' },
          { id: 'create', label: '✍️ Create Post' },
          { id: 'questions', label: '❓ Find Questions' },
          { id: 'analytics', label: '📊 Analytics' }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: '1',
              minWidth: '140px',
              padding: '16px 24px',
              background: activeTab === tab.id 
                ? 'linear-gradient(135deg, #FF4500, #FF8717)' 
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
              color: '#FF4500',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Reddit Connection Setup
            </h2>

            {!redditConnected ? (
              <div>
                <div style={{
                  background: '#fff3cd',
                  border: '1px solid #ffc107',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '30px'
                }}>
                  <p style={{ margin: 0, color: '#856404', fontSize: '16px' }}>
                    ⚠️ Connect your Reddit account to start automating your posts
                  </p>
                </div>

                <button
                  onClick={handleRedditConnect}
                  disabled={loading}
                  style={{
                    background: 'linear-gradient(135deg, #FF4500, #FF8717)',
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
                  {loading ? '⏳ Connecting...' : '🤖 Connect Reddit Account'}
                </button>

                <div style={{
                  marginTop: '40px',
                  padding: '24px',
                  background: '#f8f9fa',
                  borderRadius: '12px'
                }}>
                  <h3 style={{ color: '#FF4500', marginBottom: '16px' }}>
                    What you'll get:
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                    <li>AI-powered content generation for Reddit</li>
                    <li>Auto-generate engaging posts and comments</li>
                    <li>Find and answer questions in your niche</li>
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
                    ✅ Reddit connected successfully as u/{redditUsername}
                  </p>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '20px',
                  marginTop: '30px'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #FF4500, #FF8717)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '12px' }}>🤖</div>
                    <div style={{ fontSize: '18px', fontWeight: '600' }}>Ready to Post</div>
                    <div style={{ fontSize: '14px', opacity: 0.9, marginTop: '8px' }}>
                      Start creating amazing content
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #FF8717, #FFA500)',
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
              color: '#FF4500',
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
                background: 'linear-gradient(135deg, #FF4500, #FF8717)',
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
              color: '#FF4500',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Create Reddit Post
            </h2>

            {!redditConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Please connect Reddit first to create posts
                </p>
              </div>
            )}

            <form onSubmit={publishRedditPost}>
              <div style={{ marginBottom: '24px' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '12px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: '16px'
                }}>
                  Subreddit
                </label>
                <input
                  type="text"
                  value={postForm.subreddit}
                  onChange={(e) => setPostForm(prev => ({ ...prev, subreddit: e.target.value }))}
                  placeholder="e.g., test, AskReddit"
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
                  Post Title
                </label>
                <input
                  type="text"
                  value={postForm.title}
                  onChange={(e) => setPostForm(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="Enter your post title..."
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
                  value={postForm.content}
                  onChange={(e) => setPostForm(prev => ({ ...prev, content: e.target.value }))}
                  placeholder="Write your Reddit post..."
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
                  type="button"
                  onClick={generateRedditContent}
                  disabled={postForm.isGenerating || !userProfile.isConfigured}
                  style={{
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    padding: '16px 32px',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: (postForm.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    width: '100%',
                    justifyContent: 'center'
                  }}
                >
                  {postForm.isGenerating ? '⏳ Generating...' : '🤖 Generate Content with AI'}
                </button>
              </div>

              <button
                type="submit"
                disabled={loading || !postForm.title || !postForm.content || !redditConnected}
                style={{
                  background: 'linear-gradient(135deg, #FF4500, #FF8717)',
                  padding: '20px 48px',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '18px',
                  fontWeight: '700',
                  cursor: (loading || !postForm.title || !postForm.content || !redditConnected) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  margin: '0 auto'
                }}
              >
                {loading ? '⏳ Publishing...' : '📤 Publish to Reddit'}
              </button>
            </form>
          </div>
        )}

        {/* Find Questions Tab */}
        {activeTab === 'questions' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#FF4500',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Find Questions to Answer
            </h2>

            {!redditConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Please connect Reddit first to find questions
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
                Subreddits (comma-separated)
              </label>
              <input
                type="text"
                value={questionForm.subreddits}
                onChange={(e) => setQuestionForm(prev => ({ ...prev, subreddits: e.target.value }))}
                placeholder="e.g., AskReddit,explainlikeimfive,india"
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
                Keywords (comma-separated)
              </label>
              <input
                type="text"
                value={questionForm.keywords}
                onChange={(e) => setQuestionForm(prev => ({ ...prev, keywords: e.target.value }))}
                placeholder="e.g., help,how,what,why"
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
                Limit
              </label>
              <input
                type="number"
                value={questionForm.limit}
                onChange={(e) => setQuestionForm(prev => ({ ...prev, limit: parseInt(e.target.value) || 10 }))}
                min="1"
                max="50"
                style={{
                  width: '100%',
                  padding: '16px',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: '16px'
                }}
              />
            </div>

            <button
              onClick={findQuestions}
              disabled={loading || !redditConnected}
              style={{
                background: 'linear-gradient(135deg, #FF4500, #FF8717)',
                padding: '18px 48px',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '18px',
                fontWeight: '700',
                cursor: (loading || !redditConnected) ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                margin: '0 auto 30px auto'
              }}
            >
              {loading ? '⏳ Searching...' : '🔍 Find Questions'}
            </button>

            {questions.length > 0 && (
              <div style={{
                marginTop: '30px'
              }}>
                <h3 style={{
                  color: '#FF4500',
                  marginBottom: '20px',
                  fontSize: '22px',
                  fontWeight: '600'
                }}>
                  Found {questions.length} Questions:
                </h3>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '16px'
                }}>
                  {questions.map((question, index) => (
                    <div key={index} style={{
                      background: '#f8f9fa',
                      padding: '20px',
                      borderRadius: '12px',
                      border: '2px solid #ddd'
                    }}>
                      <h4 style={{
                        margin: '0 0 8px 0',
                        color: '#FF4500',
                        fontSize: '18px',
                        fontWeight: '600'
                      }}>
                        {question.title || 'Question ' + (index + 1)}
                      </h4>
                      <p style={{
                        margin: '0 0 12px 0',
                        color: '#666',
                        fontSize: '14px'
                      }}>
                        r/{question.subreddit || 'unknown'} • {question.score || 0} points
                      </p>
                      {question.url && (
                        <a
                          href={question.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: '#FF4500',
                            textDecoration: 'none',
                            fontWeight: '600',
                            fontSize: '14px'
                          }}
                        >
                          View on Reddit →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
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
              color: '#FF4500',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Analytics & Performance
            </h2>

            {!redditConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px',
                marginBottom: '30px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: '16px' }}>
                  ❌ Connect Reddit to view analytics
                </p>
              </div>
            )}

            {redditConnected && (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '20px'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #FF4500, #FF8717)',
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
                  background: 'linear-gradient(135deg, #FF8717, #FFA500)',
                  borderRadius: '16px',
                  padding: '24px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '12px' }}>
                    {performanceData.totalEngagement}
                  </div>
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    Total Karma
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

                <div style={{
                  background: 'linear-gradient(135deg, #00C851, #00A047)',
                  borderRadius: '16px',
                  padding: '24px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <div style={{ fontSize: '48px', fontWeight: 'bold', marginBottom: '12px' }}>
                    {performanceData.questionsFound}
                  </div>
                  <div style={{ fontSize: '16px', opacity: 0.9 }}>
                    Questions Found
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
              <h3 style={{ color: '#FF4500', marginBottom: '16px' }}>
                Tips for Better Engagement on Reddit
              </h3>
              <ul style={{ margin: 0, paddingLeft: '24px', color: '#333', lineHeight: '1.8' }}>
                <li>Post in relevant subreddits with active communities</li>
                <li>Use descriptive, engaging titles</li>
                <li>Provide value - don't just self-promote</li>
                <li>Engage authentically with commenters</li>
                <li>Follow subreddit rules and reddiquette</li>
                <li>Post during peak activity hours</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};



export default Reddit;