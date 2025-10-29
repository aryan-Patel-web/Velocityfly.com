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
  
  // Core state
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Reddit connection state
  const [redditConnected, setRedditConnected] = useState(false);
  const [redditUsername, setRedditUsername] = useState('');
  
  // Scheduling state
  const [schedules, setSchedules] = useState([]);
  const [automationActive, setAutomationActive] = useState(false);
  const [newSchedule, setNewSchedule] = useState({
    time: '',
    subreddit: 'test',
    useAI: true
  });
  const [scheduledPosts, setScheduledPosts] = useState([]);
  
  // User profile state
  const [userProfile, setUserProfile] = useState({ 
    domain: 'tech', 
    businessType: 'AI automation platform', 
    businessDescription: 'We help businesses automate their Reddit presence', 
    targetAudience: 'tech_professionals', 
    contentStyle: 'engaging', 
    isConfigured: false 
  });
  
  // Post form state
  const [postForm, setPostForm] = useState({ 
    subreddit: 'test',
    title: '', 
    content: '', 
    language: 'en',
    contentType: 'text',
    isGenerating: false 
  });


    const [aiOptions, setAiOptions] = useState({
    topic: '',
    postType: 'discussion',
    tone: 'casual',
    length: 'medium'
  });
  const [humanScore, setHumanScore] = useState(null);

  // Questions state
  const [questionForm, setQuestionForm] = useState({
    subreddits: 'AskReddit,explainlikeimfive,NoStupidQuestions,india',
    keywords: 'help,how,what,why,study,learn',
    limit: 10
  });
  const [questions, setQuestions] = useState([]);
  
  // Performance state
  const [performanceData, setPerformanceData] = useState({ 
    postsToday: 0, 
    totalEngagement: 0, 
    successRate: 95,
    questionsFound: 0
  });

  // Notification system
  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: Date.now(), message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  // Check Reddit connection on mount




  useEffect(() => {
    if (!user?.email) return;
    
    const checkRedditConnection = async () => {
      // Check URL parameters first (OAuth callback)
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
        showNotification(`✅ Reddit connected! Welcome u/${username}!`, 'success');
        
        localStorage.setItem(`reddit_connected_${user.email}`, 'true');
        localStorage.setItem(`reddit_username_${user.email}`, username);
        
        window.history.replaceState({}, '', window.location.pathname); 
        return;
      }

      // Check localStorage
      const savedConnection = localStorage.getItem(`reddit_connected_${user.email}`);
      const savedUsername = localStorage.getItem(`reddit_username_${user.email}`);
      
      if (savedConnection === 'true' && savedUsername) {
        setRedditConnected(true);
        setRedditUsername(savedUsername);
        return;
      }

      // Check backend
      try {
        const response = await makeAuthenticatedRequest('/api/reddit/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setRedditConnected(true); 
          setRedditUsername(result.reddit_username || result.username);
          localStorage.setItem(`reddit_connected_${user.email}`, 'true');
          localStorage.setItem(`reddit_username_${user.email}`, result.reddit_username || result.username);
        }
      } catch (error) { 
        console.error('Failed to check Reddit connection:', error); 
      }

      // Load user profile
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
  }, [user, makeAuthenticatedRequest, updateUser]);

  // Connect Reddit account
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

  // Save user profile
  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem(`redditUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('✅ Profile saved successfully!', 'success');
    } catch (error) { 
      showNotification('Failed to save profile', 'error'); 
    }
  }, [userProfile, user?.email, showNotification]);





  // Generate AI content (FIXED - added subreddits)
const generateRedditContent = useCallback(async () => {
  if (!userProfile.isConfigured) { 
    showNotification('Please configure your profile first', 'error'); 
    return; 
  }

  try {
    setPostForm(prev => ({ ...prev, isGenerating: true }));
    showNotification('Generating human-like content from your profile...', 'info');
    
    const response = await makeAuthenticatedRequest('/api/reddit/generate-ai-post', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        post_type: aiOptions.postType,
        tone: aiOptions.tone,
        length: aiOptions.length,
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
        subreddit: result.subreddit || 'test',
        title: result.title || '',
        content: result.content || '',
        isGenerating: false
      }));
      
      setHumanScore(result.human_score || 85);
      showNotification(`✅ Generated! Human score: ${result.human_score || 85}/100`, 'success');
      
      if (result.human_score && result.human_score < 70) {
        showNotification('⚠️ Low score. Regenerating...', 'info');
        setTimeout(() => generateRedditContent(), 1000);
      }
    } else { 
      showNotification(result.error || 'Generation failed', 'error'); 
      setPostForm(prev => ({ ...prev, isGenerating: false }));
    }
  } catch (error) { 
    console.error('AI generation error:', error);
    showNotification('Generation failed: ' + error.message, 'error'); 
    setPostForm(prev => ({ ...prev, isGenerating: false }));
  }
}, [makeAuthenticatedRequest, showNotification, userProfile, aiOptions]);




  // Publish Reddit post
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
      
      const response = await makeAuthenticatedRequest('/api/automation/post-now', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: postForm.title,
          content: postForm.content,
          subreddit: postForm.subreddit,
          contentType: postForm.contentType
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification('✅ Posted to Reddit successfully!', 'success');
        setPostForm({ subreddit: 'test', title: '', content: '', language: 'en', contentType: 'text', isGenerating: false });
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        
        if (result.post_url) {
          setTimeout(() => window.open(result.post_url, '_blank'), 1000);
        }
      } else { 
        showNotification(result.error || 'Failed to post', 'error'); 
      }
    } catch (error) { 
      showNotification('Publishing failed: ' + error.message, 'error'); 
    } finally { 
      setLoading(false); 
    }
  }, [postForm, redditConnected, makeAuthenticatedRequest, showNotification]);

  // Find questions
  const findQuestions = useCallback(async () => {
    if (!redditConnected) {
      showNotification('Please connect Reddit first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Searching for questions...', 'info');
      
      const response = await makeAuthenticatedRequest(`/api/automation/questions?subreddits=${encodeURIComponent(questionForm.subreddits)}&keywords=${encodeURIComponent(questionForm.keywords)}&limit=${questionForm.limit}`);
      
      const result = await response.json();

      if (result.success) {
        setQuestions(result.questions || []);
        setPerformanceData(prev => ({ ...prev, questionsFound: result.questions?.length || 0 }));
        showNotification(`✅ Found ${result.questions?.length || 0} questions!`, 'success');
      } else {
        showNotification(result.error || 'Failed to find questions', 'error');
      }
    } catch (error) {
      showNotification('Search failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [questionForm, redditConnected, makeAuthenticatedRequest, showNotification]);

  // ============= SCHEDULING FUNCTIONS =============
  
  // Get minimum schedule time (3 minutes from now)
  const getMinScheduleTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 3);
    return now.toISOString().slice(0, 16);
  };

  // Get maximum schedule time (6 hours from now)
  const getMaxScheduleTime = () => {
    const max = new Date();
    max.setHours(max.getHours() + 6);
    return max.toISOString().slice(0, 16);
  };

  // Add schedule
  const addSchedule = useCallback(() => {
    if (!newSchedule.time) {
      showNotification('Please select a time', 'error');
      return;
    }

    if (schedules.length >= 5) {
      showNotification('Maximum 5 schedules per day', 'error');
      return;
    }

    const scheduleTime = new Date(newSchedule.time);
    const now = new Date();
    const minTime = new Date(now.getTime() + 3 * 60000);

    if (scheduleTime < minTime) {
      showNotification('Schedule time must be at least 3 minutes from now', 'error');
      return;
    }

    const newSched = {
      id: Date.now(),
      time: newSchedule.time,
      subreddit: newSchedule.subreddit,
      useAI: newSchedule.useAI,
      status: 'pending',
      createdAt: new Date().toISOString()
    };

    setSchedules(prev => [...prev, newSched]);
    showNotification('✅ Schedule added!', 'success');
    
    setNewSchedule({ time: '', subreddit: 'test', useAI: true });
  }, [newSchedule, schedules, showNotification]);

  // Remove schedule
  const removeSchedule = useCallback((scheduleId) => {
    setSchedules(prev => prev.filter(s => s.id !== scheduleId));
    showNotification('Schedule removed', 'info');
  }, [showNotification]);

  // Start automation
  const startAutomation = useCallback(async () => {
    if (schedules.length === 0) {
      showNotification('Please add at least one schedule', 'error');
      return;
    }

    if (!redditConnected) {
      showNotification('Please connect Reddit first', 'error');
      return;
    }

    if (!userProfile.isConfigured) {
      showNotification('Please complete your profile setup first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('🚀 Starting automation...', 'info');

      const response = await makeAuthenticatedRequest('/api/automation/setup/posting', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          language: 'en',
          content_style: userProfile.contentStyle,
          posts_per_day: schedules.length,
          posting_times: schedules.map(s => {
            const date = new Date(s.time);
            return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`;
          }),
          subreddits: schedules.map(s => s.subreddit),
          manual_time_entry: true,
          custom_post_count: true
        })
      });

      const result = await response.json();

      if (result.success) {
        setAutomationActive(true);
        showNotification('✅ Automation started! Posts will be published at scheduled times', 'success');
        monitorScheduledPosts();
      } else {
        showNotification(result.error || 'Failed to start automation', 'error');
      }
    } catch (error) {
      showNotification('Failed to start automation: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [schedules, redditConnected, userProfile, makeAuthenticatedRequest, showNotification]);

  // Stop automation
  const stopAutomation = useCallback(async () => {
    try {
      setLoading(true);
      
      const response = await makeAuthenticatedRequest('/api/automation/schedule/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: 'auto_posting',
          enabled: false
        })
      });

      const result = await response.json();

      if (result.success) {
        setAutomationActive(false);
        showNotification('⏸️ Automation stopped', 'info');
      } else {
        showNotification(result.error || 'Failed to stop automation', 'error');
      }
    } catch (error) {
      showNotification('Failed to stop automation: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  // Monitor scheduled posts
  const monitorScheduledPosts = useCallback(() => {
    const interval = setInterval(async () => {
      try {
        const response = await makeAuthenticatedRequest('/api/automation/stats');
        const result = await response.json();
        
        if (result.success) {
          setScheduledPosts(result.scheduled_posts || []);
          setPerformanceData(prev => ({
            ...prev,
            postsToday: result.posts_today || 0,
            totalEngagement: result.total_karma || 0
          }));
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [makeAuthenticatedRequest]);

  // Format time display
  const formatScheduleTime = (timeString) => {
    const date = new Date(timeString);
    const now = new Date();
    const diff = date - now;
    
    if (diff < 0) return 'Past';
    
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `in ${hours}h ${minutes % 60}m`;
    }
    return `in ${minutes}m`;
  };

  // ============= RENDER =============
  
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px',
      paddingTop: '80px'
    }}>
      {/* Notifications */}
      <div style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        maxWidth: '90vw'
      }}>
        {notifications.map(notif => (
          <div key={notif.id} style={{
            background: notif.type === 'success' ? '#d4edda' : notif.type === 'error' ? '#f8d7da' : '#d1ecf1',
            color: notif.type === 'success' ? '#155724' : notif.type === 'error' ? '#721c24' : '#0c5460',
            padding: '16px 24px',
            borderRadius: '12px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            fontWeight: '600',
            fontSize: '14px',
            animation: 'slideIn 0.3s ease-out',
            wordBreak: 'break-word'
          }}>
            {notif.message}
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto'
      }}>
        <div style={{
          background: 'rgba(255, 255, 255, 0.95)',
          borderRadius: '20px',
          padding: '20px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
          marginBottom: '20px'
        }}>
          <h1 style={{
            margin: '0 0 12px 0',
            color: '#FF4500',
            fontSize: 'clamp(24px, 5vw, 32px)',
            fontWeight: '700'
          }}>
            🤖 Reddit Automation
          </h1>
          <p style={{
            margin: 0,
            color: '#666',
            fontSize: 'clamp(14px, 2.5vw, 16px)'
          }}>
            Welcome, {user?.name || 'User'}! {redditConnected && `• Connected as u/${redditUsername}`}
          </p>
        </div>

        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '20px',
          flexWrap: 'wrap',
          overflowX: 'auto',
          padding: '4px'
        }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Setup' },
            { id: 'profile', icon: '👤', label: 'Profile' },
            { id: 'schedule', icon: '📅', label: 'Schedule' },
            { id: 'create', icon: '✍️', label: 'Create' },
            { id: 'questions', icon: '❓', label: 'Questions' },
            { id: 'analytics', icon: '📊', label: 'Analytics' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: 'clamp(10px, 2vw, 12px) clamp(16px, 3vw, 24px)',
                background: activeTab === tab.id ? 'linear-gradient(135deg, #FF4500, #FF8717)' : '#f5f5f5',
                color: activeTab === tab.id ? 'white' : '#333',
                border: 'none',
                borderRadius: '12px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: 'clamp(13px, 2.5vw, 15px)',
                whiteSpace: 'nowrap',
                transition: 'all 0.3s ease'
              }}
            >
              <span style={{ marginRight: '6px' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>

        {/* Setup Tab */}
        {activeTab === 'setup' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: 'clamp(20px, 4vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#FF4500',
              marginBottom: '24px',
              fontSize: 'clamp(22px, 4vw, 28px)',
              fontWeight: '700'
            }}>
              Reddit Connection Setup
            </h2>

            {!redditConnected ? (
              <div>
                <div style={{
                  background: '#fff3cd',
                  border: '1px solid #ffeaa7',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '24px'
                }}>
                  <p style={{ margin: 0, color: '#856404', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
                    ⚠️ Connect your Reddit account to start automating your posts
                  </p>
                </div>

                <button
                  onClick={handleRedditConnect}
                  disabled={loading}
                  style={{
                    background: loading ? '#ccc' : 'linear-gradient(135deg, #FF4500, #FF8717)',
                    padding: 'clamp(14px, 3vw, 18px) clamp(32px, 6vw, 48px)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: 'clamp(16px, 3vw, 18px)',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    width: '100%',
                    maxWidth: '400px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    margin: '0 auto 24px auto'
                  }}
                >
                  {loading ? '⏳ Connecting...' : '🤖 Connect Reddit Account'}
                </button>

                <div style={{
                  background: '#f8f9fa',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <h3 style={{
                    color: '#FF4500',
                    marginTop: 0,
                    marginBottom: '16px',
                    fontSize: 'clamp(16px, 3vw, 18px)'
                  }}>
                    What you'll get:
                  </h3>
                  <ul style={{
                    margin: 0,
                    paddingLeft: '24px',
                    color: '#333',
                    lineHeight: '1.8',
                    fontSize: 'clamp(13px, 2.5vw, 15px)'
                  }}>
                    <li>AI-powered content generation for Reddit</li>
                    <li>Auto-generate engaging posts and comments</li>
                    <li>Find and answer questions in your niche</li>
                    <li>Schedule and automate posts</li>
                    <li>Track performance analytics</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div style={{
                background: '#d4edda',
                border: '1px solid #c3e6cb',
                borderRadius: '12px',
                padding: '20px',
                textAlign: 'center'
              }}>
                <p style={{
                  margin: '0 0 12px 0',
                  color: '#155724',
                  fontSize: 'clamp(16px, 3vw, 18px)',
                  fontWeight: '600'
                }}>
                  ✅ Reddit Connected!
                </p>
                <p style={{
                  margin: 0,
                  color: '#155724',
                  fontSize: 'clamp(14px, 2.5vw, 16px)'
                }}>
                  You're logged in as <strong>u/{redditUsername}</strong>
                </p>
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: 'clamp(20px, 4vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#FF4500',
              marginBottom: '24px',
              fontSize: 'clamp(22px, 4vw, 28px)',
              fontWeight: '700'
            }}>
              👤 Your Profile
            </h2>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '20px',
              marginBottom: '24px'
            }}>
              {/* Domain Selection */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: 'clamp(14px, 2.5vw, 16px)'
                }}>
                  🎯 Domain
                </label>
                <select
                  value={userProfile.domain}
                  onChange={(e) => setUserProfile(prev => ({
                    ...prev,
                    domain: e.target.value,
                    businessType: DOMAIN_CONFIGS[e.target.value].sampleBusiness
                  }))}
                  style={{
                    width: '100%',
                    padding: 'clamp(12px, 2.5vw, 16px)',
                    borderRadius: '12px',
                    border: '2px solid #ddd',
                    fontSize: 'clamp(14px, 2.5vw, 16px)'
                  }}
                >
                  {Object.entries(DOMAIN_CONFIGS).map(([key, config]) => (
                    <option key={key} value={key}>
                      {config.icon} {config.description}
                    </option>
                  ))}
                </select>
              </div>

              {/* Business Type */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: 'clamp(14px, 2.5vw, 16px)'
                }}>
                  🏢 Business Type
                </label>
                <input
                  type="text"
                  value={userProfile.businessType}
                  onChange={(e) => setUserProfile(prev => ({...prev, businessType: e.target.value}))}
                  placeholder="e.g., AI automation platform"
                  style={{
                    width: '100%',
                    padding: 'clamp(12px, 2.5vw, 16px)',
                    borderRadius: '12px',
                    border: '2px solid #ddd',
                    fontSize: 'clamp(14px, 2.5vw, 16px)'
                  }}
                />
              </div>

              {/* Target Audience */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: 'clamp(14px, 2.5vw, 16px)'
                }}>
                  👥 Target Audience
                </label>
                <select
                  value={userProfile.targetAudience}
                  onChange={(e) => setUserProfile(prev => ({...prev, targetAudience: e.target.value}))}
                  style={{
                    width: '100%',
                    padding: 'clamp(12px, 2.5vw, 16px)',
                    borderRadius: '12px',
                    border: '2px solid #ddd',
                    fontSize: 'clamp(14px, 2.5vw, 16px)'
                  }}
                >
                  {Object.entries(TARGET_AUDIENCES).map(([key, audience]) => (
                    <option key={key} value={key}>
                      {audience.icon} {audience.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Content Style */}
              <div>
                <label style={{
                  display: 'block',
                  marginBottom: '8px',
                  color: '#333',
                  fontWeight: '600',
                  fontSize: 'clamp(14px, 2.5vw, 16px)'
                }}>
                  ✨ Content Style
                </label>
                <select
                  value={userProfile.contentStyle}
                  onChange={(e) => setUserProfile(prev => ({...prev, contentStyle: e.target.value}))}
                  style={{
                    width: '100%',
                    padding: 'clamp(12px, 2.5vw, 16px)',
                    borderRadius: '12px',
                    border: '2px solid #ddd',
                    fontSize: 'clamp(14px, 2.5vw, 16px)'
                  }}
                >
                  {Object.entries(CONTENT_STYLES).map(([key, label]) => (
                    <option key={key} value={key}>{label}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Business Description */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontWeight: '600',
                fontSize: 'clamp(14px, 2.5vw, 16px)'
              }}>
                📝 Business Description
              </label>
              <textarea
                value={userProfile.businessDescription}
                onChange={(e) => setUserProfile(prev => ({...prev, businessDescription: e.target.value}))}
                placeholder="Describe your business in detail..."
                rows={4}
                style={{
                  width: '100%',
                  padding: 'clamp(12px, 2.5vw, 16px)',
                  borderRadius: '12px',
                  border: '2px solid #ddd',
                  fontSize: 'clamp(14px, 2.5vw, 16px)',
                  resize: 'vertical',
                  fontFamily: 'inherit'
                }}
              />
            </div>

            <button
              onClick={saveUserProfile}
              style={{
                background: 'linear-gradient(135deg, #FF4500, #FF8717)',
                padding: 'clamp(14px, 3vw, 16px) clamp(32px, 6vw, 48px)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: 'clamp(16px, 3vw, 18px)',
                fontWeight: '700',
                cursor: 'pointer',
                width: '100%',
                maxWidth: '300px',
                display: 'block',
                margin: '0 auto'
              }}
            >
              💾 Save Profile
            </button>
          </div>
        )}

        {/* Schedule Tab */}
        {activeTab === 'schedule' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: 'clamp(20px, 4vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '24px',
              flexWrap: 'wrap',
              gap: '12px'
            }}>
              <h2 style={{
                color: '#FF4500',
                margin: 0,
                fontSize: 'clamp(22px, 4vw, 28px)',
                fontWeight: '700'
              }}>
                📅 Schedule Posts
              </h2>
              
              {automationActive && (
                <div style={{
                  background: '#d4edda',
                  color: '#155724',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  fontWeight: '600',
                  fontSize: 'clamp(13px, 2.5vw, 14px)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span style={{ fontSize: '20px' }}>🟢</span>
                  Automation Active
                </div>
              )}
            </div>

            {!redditConnected ? (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
                  ❌ Connect Reddit to schedule posts
                </p>
              </div>
            ) : (
              <>
                {/* Add New Schedule */}
                <div style={{
                  background: '#f8f9fa',
                  padding: '20px',
                  borderRadius: '12px',
                  marginBottom: '24px'
                }}>
                  <h3 style={{
                    color: '#FF4500',
                    marginTop: 0,
                    marginBottom: '16px',
                    fontSize: 'clamp(18px, 3vw, 20px)',
                    fontWeight: '600'
                  }}>
                    ➕ Add New Schedule
                  </h3>

                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '16px',
                    marginBottom: '16px'
                  }}>
                    <div>
                      <label style={{
                        display: 'block',
                        marginBottom: '8px',
                        color: '#333',
                        fontWeight: '600',
                        fontSize: 'clamp(13px, 2.5vw, 14px)'
                      }}>
                        📅 Schedule Time
                      </label>
                      <input
                        type="datetime-local"
                        min={getMinScheduleTime()}
                        max={getMaxScheduleTime()}
                        value={newSchedule.time}
                        onChange={(e) => setNewSchedule(prev => ({...prev, time: e.target.value}))}
                        style={{
                          width: '100%',
                          padding: '12px',
                          borderRadius: '8px',
                          border: '2px solid #ddd',
                          fontSize: 'clamp(13px, 2.5vw, 14px)'
                        }}
                      />
                      <small style={{ color: '#666', fontSize: 'clamp(11px, 2vw, 12px)' }}>
                        Min: 3 min from now • Max: 6 hours
                      </small>
                    </div>

                    <div>
                      <label style={{
                        display: 'block',
                        marginBottom: '8px',
                        color: '#333',
                        fontWeight: '600',
                        fontSize: 'clamp(13px, 2.5vw, 14px)'
                      }}>
                        📍 Subreddit
                      </label>
                      <input
                        type="text"
                        value={newSchedule.subreddit}
                        onChange={(e) => setNewSchedule(prev => ({...prev, subreddit: e.target.value}))}
                        placeholder="e.g. test"
                        style={{
                          width: '100%',
                          padding: '12px',
                          borderRadius: '8px',
                          border: '2px solid #ddd',
                          fontSize: 'clamp(13px, 2.5vw, 14px)'
                        }}
                      />
                    </div>

                    <div>
                      <label style={{
                        display: 'block',
                        marginBottom: '8px',
                        color: '#333',
                        fontWeight: '600',
                        fontSize: 'clamp(13px, 2.5vw, 14px)'
                      }}>
                        🤖 Content Source
                      </label>
                      <select
                        value={newSchedule.useAI}
                        onChange={(e) => setNewSchedule(prev => ({...prev, useAI: e.target.value === 'true'}))}
                        style={{
                          width: '100%',
                          padding: '12px',
                          borderRadius: '8px',
                          border: '2px solid #ddd',
                          fontSize: 'clamp(13px, 2.5vw, 14px)'
                        }}
                      >
                        <option value="true">AI Generated</option>
                        <option value="false">Manual</option>
                      </select>
                    </div>
                  </div>

                  <button
                    onClick={addSchedule}
                    disabled={!newSchedule.time || schedules.length >= 5}
                    style={{
                      background: schedules.length >= 5 ? '#ccc' : 'linear-gradient(135deg, #FF4500, #FF8717)',
                      padding: 'clamp(10px, 2vw, 12px) clamp(24px, 4vw, 32px)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: 'clamp(14px, 2.5vw, 16px)',
                      fontWeight: '600',
                      cursor: schedules.length >= 5 ? 'not-allowed' : 'pointer',
                      width: '100%',
                      maxWidth: '300px',
                      display: 'block',
                      margin: '0 auto'
                    }}
                  >
                    ➕ Add Schedule ({schedules.length}/5)
                  </button>
                </div>

                {/* Scheduled Posts List */}
                {schedules.length > 0 && (
                  <div style={{ marginBottom: '24px' }}>
                    <h3 style={{
                      color: '#FF4500',
                      marginBottom: '16px',
                      fontSize: 'clamp(18px, 3vw, 20px)',
                      fontWeight: '600'
                    }}>
                      📋 Scheduled Posts ({schedules.length})
                    </h3>

                    <div style={{
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px'
                    }}>
                      {schedules
                        .sort((a, b) => new Date(a.time) - new Date(b.time))
                        .map((schedule) => (
                        <div key={schedule.id} style={{
                          background: '#fff',
                          padding: '16px',
                          borderRadius: '12px',
                          border: '2px solid #ddd',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '12px'
                        }}>
                          <div style={{ flex: 1, minWidth: '200px' }}>
                            <div style={{
                              fontSize: 'clamp(14px, 2.5vw, 16px)',
                              fontWeight: '600',
                              color: '#333',
                              marginBottom: '8px'
                            }}>
                              🕐 {new Date(schedule.time).toLocaleString()}
                              <span style={{
                                marginLeft: '12px',
                                fontSize: 'clamp(12px, 2vw, 14px)',
                                color: '#FF4500',
                                fontWeight: '500'
                              }}>
                                {formatScheduleTime(schedule.time)}
                              </span>
                            </div>
                            <div style={{ fontSize: 'clamp(12px, 2vw, 14px)', color: '#666' }}>
                              📍 r/{schedule.subreddit} • {schedule.useAI ? '🤖 AI Generated' : '✍️ Manual'}
                            </div>
                          </div>

                          <button
                            onClick={() => removeSchedule(schedule.id)}
                            style={{
                              background: '#dc3545',
                              color: 'white',
                              border: 'none',
                              borderRadius: '8px',
                              padding: '8px 16px',
                              cursor: 'pointer',
                              fontWeight: '600',
                              fontSize: 'clamp(12px, 2vw, 14px)'
                            }}
                          >
                            🗑️ Remove
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Start/Stop Automation */}
                <div style={{
                  background: automationActive ? '#d4edda' : '#fff3cd',
                  padding: '20px',
                  borderRadius: '12px',
                  border: `2px solid ${automationActive ? '#c3e6cb' : '#ffeaa7'}`,
                  marginBottom: '24px'
                }}>
                  <h3 style={{
                    color: '#FF4500',
                    marginTop: 0,
                    marginBottom: '16px',
                    fontSize: 'clamp(18px, 3vw, 20px)',
                    fontWeight: '600'
                  }}>
                    {automationActive ? '⏸️ Automation Control' : '🚀 Ready to Start'}
                  </h3>

                  <p style={{
                    marginBottom: '16px',
                    color: '#333',
                    fontSize: 'clamp(13px, 2.5vw, 15px)'
                  }}>
                    {automationActive 
                      ? 'Automation is running. Posts will be published at scheduled times with AI-generated content.'
                      : `You have ${schedules.length} post${schedules.length !== 1 ? 's' : ''} scheduled. Click "Start Automation" to begin.`
                    }
                  </p>

                  {!automationActive ? (
                    <button
                      onClick={startAutomation}
                      disabled={loading || schedules.length === 0 || !userProfile.isConfigured}
                      style={{
                        background: (loading || schedules.length === 0 || !userProfile.isConfigured) 
                          ? '#ccc' 
                          : 'linear-gradient(135deg, #28a745, #20c997)',
                        padding: 'clamp(14px, 3vw, 16px) clamp(32px, 6vw, 48px)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        fontSize: 'clamp(16px, 3vw, 18px)',
                        fontWeight: '700',
                        cursor: (loading || schedules.length === 0 || !userProfile.isConfigured) 
                          ? 'not-allowed' 
                          : 'pointer',
                        width: '100%',
                        maxWidth: '400px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '12px',
                        margin: '0 auto'
                      }}
                    >
                      {loading ? '⏳ Starting...' : '🚀 Start Automation'}
                    </button>
                  ) : (
                    <button
                      onClick={stopAutomation}
                      disabled={loading}
                      style={{
                        background: loading ? '#ccc' : '#dc3545',
                        padding: 'clamp(14px, 3vw, 16px) clamp(32px, 6vw, 48px)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '12px',
                        fontSize: 'clamp(16px, 3vw, 18px)',
                        fontWeight: '700',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        width: '100%',
                        maxWidth: '400px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '12px',
                        margin: '0 auto'
                      }}
                    >
                      {loading ? '⏳ Stopping...' : '⏸️ Stop Automation'}
                    </button>
                  )}

                  {!userProfile.isConfigured && schedules.length > 0 && (
                    <p style={{
                      marginTop: '12px',
                      color: '#856404',
                      fontSize: 'clamp(12px, 2vw, 14px)',
                      fontWeight: '500',
                      textAlign: 'center'
                    }}>
                      ⚠️ Please complete your profile setup first
                    </p>
                  )}
                </div>

                {/* Active Schedule Status */}
                {automationActive && scheduledPosts.length > 0 && (
                  <div>
                    <h3 style={{
                      color: '#FF4500',
                      marginBottom: '16px',
                      fontSize: 'clamp(18px, 3vw, 20px)',
                      fontWeight: '600'
                    }}>
                      📊 Active Schedule Status
                    </h3>

                    <div style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                      gap: '16px'
                    }}>
                      {scheduledPosts.map((post, index) => (
                        <div key={index} style={{
                          background: post.status === 'posted' ? '#d4edda' : '#fff',
                          padding: '16px',
                          borderRadius: '12px',
                          border: '2px solid #ddd'
                        }}>
                          <div style={{
                            fontSize: 'clamp(12px, 2vw, 14px)',
                            fontWeight: '600',
                            color: '#333',
                            marginBottom: '8px'
                          }}>
                            {post.status === 'posted' ? '✅' : '⏳'} {post.time}
                          </div>
                          <div style={{ fontSize: 'clamp(11px, 2vw, 12px)', color: '#666' }}>
                            r/{post.subreddit}
                          </div>
                          {post.post_url && (
                            <a
                              href={post.post_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{
                                fontSize: 'clamp(11px, 2vw, 12px)',
                                color: '#FF4500',
                                textDecoration: 'none',
                                fontWeight: '600'
                              }}
                            >
                              View Post →
                            </a>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Quick Test Info */}
                <div style={{
                  marginTop: '24px',
                  background: '#e7f3ff',
                  padding: '20px',
                  borderRadius: '12px',
                  border: '2px solid #b3d9ff'
                }}>
                  <h4 style={{
                    color: '#0066cc',
                    marginTop: 0,
                    marginBottom: '12px',
                    fontSize: 'clamp(16px, 3vw, 18px)',
                    fontWeight: '600'
                  }}>
                    🧪 Quick Test Mode
                  </h4>
                  <p style={{
                    margin: 0,
                    color: '#333',
                    fontSize: 'clamp(12px, 2vw, 14px)',
                    lineHeight: '1.6'
                  }}>
                    Want to test scheduling? Set a time 3-5 minutes from now and click "Start Automation".
                    The system will generate AI content and post it automatically at the scheduled time.
                    You'll receive a notification when the post is published!
                  </p>
                </div>
              </>
            )}
          </div>
        )}








        
{/* Create Post Tab */}
{activeTab === 'create' && (
  <div style={{
    background: 'rgba(255, 255, 255, 0.95)',
    borderRadius: '20px',
    padding: 'clamp(20px, 4vw, 40px)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
  }}>
    <h2 style={{
      color: '#FF4500',
      marginBottom: '24px',
      fontSize: 'clamp(22px, 4vw, 28px)',
      fontWeight: '700'
    }}>
      ✍️ Create Reddit Post
    </h2>

    {!redditConnected ? (
      <div style={{
        background: '#f8d7da',
        border: '1px solid #f5c6cb',
        borderRadius: '12px',
        padding: '20px'
      }}>
        <p style={{ margin: 0, color: '#721c24', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
          ❌ Connect Reddit to create posts
        </p>
      </div>
    ) : (
      <form onSubmit={publishRedditPost}>
        <div style={{ marginBottom: '20px', background: 'linear-gradient(135deg, #667eea15, #764ba215)', borderRadius: '16px', padding: 'clamp(16px, 3vw, 24px)', border: '2px solid #667eea50' }}>
          <h3 style={{ color: '#667eea', marginBottom: '16px', fontSize: 'clamp(18px, 3vw, 22px)', fontWeight: '700' }}>🤖 AI Generator</h3>
          
          <p style={{ marginBottom: '12px', color: '#666', fontSize: 'clamp(13px, 2.5vw, 15px)', background: '#fff', padding: '10px', borderRadius: '8px', border: '1px solid #ddd' }}>
            Using your profile: <strong>{DOMAIN_CONFIGS[userProfile.domain]?.icon} {userProfile.businessType}</strong>
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '12px', marginBottom: '12px' }}>
            <select value={aiOptions.postType} onChange={(e) => setAiOptions(prev => ({...prev, postType: e.target.value}))} style={{ padding: 'clamp(10px, 2.5vw, 14px)', borderRadius: '10px', border: '2px solid #ddd', fontSize: 'clamp(13px, 2.5vw, 15px)' }}>
              <option value="discussion">💬 Discussion</option>
              <option value="question">❓ Question</option>
              <option value="story">📖 Story</option>
              <option value="review">⭐ Review</option>
              <option value="advice">💡 Advice</option>
            </select>

            <select value={aiOptions.tone} onChange={(e) => setAiOptions(prev => ({...prev, tone: e.target.value}))} style={{ padding: 'clamp(10px, 2.5vw, 14px)', borderRadius: '10px', border: '2px solid #ddd', fontSize: 'clamp(13px, 2.5vw, 15px)' }}>
              <option value="casual">😊 Casual</option>
              <option value="professional">👔 Professional</option>
              <option value="humorous">😄 Humorous</option>
              <option value="informative">📚 Informative</option>
            </select>

            <select value={aiOptions.length} onChange={(e) => setAiOptions(prev => ({...prev, length: e.target.value}))} style={{ padding: 'clamp(10px, 2.5vw, 14px)', borderRadius: '10px', border: '2px solid #ddd', fontSize: 'clamp(13px, 2.5vw, 15px)' }}>
              <option value="short">Short</option>
              <option value="medium">Medium</option>
              <option value="long">Long</option>
            </select>
          </div>

          {humanScore && (
            <div style={{ background: humanScore > 70 ? '#d4edda' : '#fff3cd', border: `2px solid ${humanScore > 70 ? '#28a745' : '#ffc107'}`, borderRadius: '10px', padding: '10px', marginBottom: '12px', fontSize: 'clamp(13px, 2.5vw, 15px)', fontWeight: '600' }}>
              🎯 Human Score: {humanScore}/100 {humanScore < 70 && '⚠️'}
            </div>
          )}
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>📍 Subreddit</label>
          <input
            type="text"
            value={postForm.subreddit}
            onChange={(e) => setPostForm(prev => ({...prev, subreddit: e.target.value}))}
            placeholder="e.g. test, learnprogramming"
            style={{ width: '100%', padding: 'clamp(12px, 2.5vw, 16px)', borderRadius: '12px', border: '2px solid #ddd', fontSize: 'clamp(14px, 2.5vw, 16px)' }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>📝 Title</label>
          <input
            type="text"
            value={postForm.title}
            onChange={(e) => setPostForm(prev => ({...prev, title: e.target.value}))}
            placeholder="Enter post title..."
            style={{ width: '100%', padding: 'clamp(12px, 2.5vw, 16px)', borderRadius: '12px', border: '2px solid #ddd', fontSize: 'clamp(14px, 2.5vw, 16px)' }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>💬 Content</label>
          <textarea
            value={postForm.content}
            onChange={(e) => setPostForm(prev => ({...prev, content: e.target.value}))}
            placeholder="Enter post content..."
            rows={6}
            style={{ width: '100%', padding: 'clamp(12px, 2.5vw, 16px)', borderRadius: '12px', border: '2px solid #ddd', fontSize: 'clamp(14px, 2.5vw, 16px)', resize: 'vertical', fontFamily: 'inherit' }}
          />
        </div>

        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>




<button
  type="button"
  onClick={generateRedditContent}
  disabled={postForm.isGenerating || !userProfile.isConfigured}
  style={{ flex: '1 1 200px', background: (postForm.isGenerating || !userProfile.isConfigured) ? '#ccc' : 'linear-gradient(135deg, #667eea, #764ba2)', padding: 'clamp(14px, 3vw, 16px) clamp(24px, 5vw, 32px)', color: 'white', border: 'none', borderRadius: '12px', fontSize: 'clamp(14px, 2.5vw, 16px)', fontWeight: '700', cursor: (postForm.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer' }}
>
  {postForm.isGenerating ? '⏳ Generating...' : '🤖 Generate post with (AI)'}
</button>





          <button
            type="submit"
            disabled={loading || !postForm.title || !postForm.content}
            style={{ flex: '1 1 200px', background: (loading || !postForm.title || !postForm.content) ? '#ccc' : 'linear-gradient(135deg, #FF4500, #FF8717)', padding: 'clamp(14px, 3vw, 16px) clamp(24px, 5vw, 32px)', color: 'white', border: 'none', borderRadius: '12px', fontSize: 'clamp(14px, 2.5vw, 16px)', fontWeight: '700', cursor: (loading || !postForm.title || !postForm.content) ? 'not-allowed' : 'pointer' }}
          >
            {loading ? '⏳ Publishing...' : '🚀 Publish to Reddit'}
          </button>
        </div>

        {!userProfile.isConfigured && (
          <p style={{ marginTop: '12px', color: '#856404', fontSize: 'clamp(12px, 2vw, 14px)', textAlign: 'center' }}>
            ⚠️ Complete your profile to use AI generation
          </p>
        )}
      </form>
    )}
  </div>
)}

{/* Questions Tab */}

















        {/* Questions Tab */}
        {activeTab === 'questions' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: 'clamp(20px, 4vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#FF4500',
              marginBottom: '24px',
              fontSize: 'clamp(22px, 4vw, 28px)',
              fontWeight: '700'
            }}>
              ❓ Find Questions
            </h2>

            {!redditConnected ? (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
                  ❌ Connect Reddit to find questions
                </p>
              </div>
            ) : (
              <div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '16px',
                  marginBottom: '20px'
                }}>
                  <div>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      color: '#333',
                      fontWeight: '600',
                      fontSize: 'clamp(14px, 2.5vw, 16px)'
                    }}>
                      📍 Subreddits (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={questionForm.subreddits}
                      onChange={(e) => setQuestionForm(prev => ({...prev, subreddits: e.target.value}))}
                      placeholder="AskReddit,explainlikeimfive"
                      style={{
                        width: '100%',
                        padding: '12px',
                        borderRadius: '12px',
                        border: '2px solid #ddd',
                        fontSize: 'clamp(14px, 2.5vw, 16px)'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      color: '#333',
                      fontWeight: '600',
                      fontSize: 'clamp(14px, 2.5vw, 16px)'
                    }}>
                      🔑 Keywords (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={questionForm.keywords}
                      onChange={(e) => setQuestionForm(prev => ({...prev, keywords: e.target.value}))}
                      placeholder="help,how,what,why"
                      style={{
                        width: '100%',
                        padding: '12px',
                        borderRadius: '12px',
                        border: '2px solid #ddd',
                        fontSize: 'clamp(14px, 2.5vw, 16px)'
                      }}
                    />
                  </div>

                  <div>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      color: '#333',
                      fontWeight: '600',
                      fontSize: 'clamp(14px, 2.5vw, 16px)'
                    }}>
                      🔢 Limit
                    </label>
                    <input
                      type="number"
                      value={questionForm.limit}
                      onChange={(e) => setQuestionForm(prev => ({...prev, limit: parseInt(e.target.value)}))}
                      min="1"
                      max="50"
                      style={{
                        width: '100%',
                        padding: '12px',
                        borderRadius: '12px',
                        border: '2px solid #ddd',
                        fontSize: 'clamp(14px, 2.5vw, 16px)'
                      }}
                    />
                  </div>
                </div>

                <button
                  onClick={findQuestions}
                  disabled={loading}
                  style={{
                    background: loading ? '#ccc' : 'linear-gradient(135deg, #FF4500, #FF8717)',
                    padding: 'clamp(14px, 3vw, 16px) clamp(32px, 6vw, 48px)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: 'clamp(16px, 3vw, 18px)',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    width: '100%',
                    maxWidth: '400px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '12px',
                    margin: '0 auto 24px auto'
                  }}
                >
                  {loading ? '⏳ Searching...' : '🔍 Find Questions'}
                </button>

                {questions.length > 0 && (
                  <div>
                    <h3 style={{
                      color: '#FF4500',
                      marginBottom: '16px',
                      fontSize: 'clamp(18px, 3vw, 22px)',
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
                            fontSize: 'clamp(16px, 3vw, 18px)',
                            fontWeight: '600',
                            wordBreak: 'break-word'
                          }}>
                            {question.title || 'Question ' + (index + 1)}
                          </h4>
                          <p style={{
                            margin: '0 0 12px 0',
                            color: '#666',
                            fontSize: 'clamp(12px, 2vw, 14px)'
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
                                fontSize: 'clamp(12px, 2vw, 14px)'
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
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: 'clamp(20px, 4vw, 40px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#FF4500',
              marginBottom: '24px',
              fontSize: 'clamp(22px, 4vw, 28px)',
              fontWeight: '700'
            }}>
              📊 Analytics & Performance
            </h2>

            {!redditConnected ? (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '12px',
                padding: '20px'
              }}>
                <p style={{ margin: 0, color: '#721c24', fontSize: 'clamp(14px, 2.5vw, 16px)' }}>
                  ❌ Connect Reddit to view analytics
                </p>
              </div>
            ) : (
              <>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                  gap: '20px',
                  marginBottom: '24px'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #FF4500, #FF8717)',
                    borderRadius: '16px',
                    padding: '24px',
                    color: 'white',
                    textAlign: 'center'
                  }}>
                    <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', fontWeight: 'bold', marginBottom: '12px' }}>
                      {performanceData.postsToday}
                    </div>
                    <div style={{ fontSize: 'clamp(14px, 2.5vw, 16px)', opacity: 0.9 }}>
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
                    <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', fontWeight: 'bold', marginBottom: '12px' }}>
                      {performanceData.totalEngagement}
                    </div>
                    <div style={{ fontSize: 'clamp(14px, 2.5vw, 16px)', opacity: 0.9 }}>
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
                    <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', fontWeight: 'bold', marginBottom: '12px' }}>
                      {performanceData.successRate}%
                    </div>
                    <div style={{ fontSize: 'clamp(14px, 2.5vw, 16px)', opacity: 0.9 }}>
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
                    <div style={{ fontSize: 'clamp(36px, 8vw, 48px)', fontWeight: 'bold', marginBottom: '12px' }}>
                      {performanceData.questionsFound}
                    </div>
                    <div style={{ fontSize: 'clamp(14px, 2.5vw, 16px)', opacity: 0.9 }}>
                      Questions Found
                    </div>
                  </div>
                </div>

                <div style={{
                  background: '#e8f5e8',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <h3 style={{
                    color: '#FF4500',
                    marginBottom: '16px',
                    fontSize: 'clamp(16px, 3vw, 18px)'
                  }}>
                    Tips for Better Engagement on Reddit
                  </h3>
                  <ul style={{
                    margin: 0,
                    paddingLeft: '24px',
                    color: '#333',
                    lineHeight: '1.8',
                    fontSize: 'clamp(13px, 2.5vw, 15px)'
                  }}>
                    <li>Post in relevant subreddits with active communities</li>
                    <li>Use descriptive, engaging titles</li>
                    <li>Provide value - don't just self-promote</li>
                    <li>Engage authentically with commenters</li>
                    <li>Follow subreddit rules and reddiquette</li>
                    <li>Post during peak activity hours</li>
                  </ul>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
};




export default RedditAutomation;