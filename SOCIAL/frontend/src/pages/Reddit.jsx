import React, { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const Reddit = () => {
  // State management
  const [activeTab, setActiveTab] = useState('testing');
  const [connected, setConnected] = useState(false);
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [automationStatus, setAutomationStatus] = useState(null);
  
  // Form states
  const [postForm, setPostForm] = useState({
    subreddit: 'test',
    title: '',
    content: '',
    language: 'en',
    contentType: 'text'
  });
  
  const [autoPostForm, setAutoPostForm] = useState({
    domain: 'education',
    businessType: '',
    targetAudience: 'indian_students',
    contentStyle: 'engaging',
    language: 'en',
    numPosts: 1
  });
  
  const [questionForm, setQuestionForm] = useState({
    subreddits: 'AskReddit,explainlikeimfive,NoStupidQuestions,india',
    keywords: 'help,how,what,why,study,learn',
    limit: 10
  });
  
  const [domainForm, setDomainForm] = useState({
    domain: 'education',
    businessType: '',
    topic: 'study tips',
    language: 'en',
    contentStyle: 'engaging',
    targetAudience: 'students'
  });
  
  const [aiForm, setAiForm] = useState({
    platform: 'reddit',
    contentType: 'post',
    topic: '',
    tone: 'professional',
    language: 'en',
    targetAudience: '',
    domain: '',
    additionalContext: ''
  });

  const [questions, setQuestions] = useState([]);
  const [generatedContent, setGeneratedContent] = useState('');
  const [analytics, setAnalytics] = useState(null);

  const API_BASE = 'http://localhost:8000';

  // API call helper
  const makeApiRequest = async (endpoint, method = 'GET', data = null) => {
    try {
      const config = {
        method,
        url: `${API_BASE}${endpoint}`,
        headers: { 'Content-Type': 'application/json' },
        ...(data && { data })
      };
      
      const response = await axios(config);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || error.message || 'An error occurred';
      toast.error(message);
      return { success: false, error: message };
    }
  };

  // Initialize data
  useEffect(() => {
    checkConnection();
    checkAutomationStatus();
    checkSystemHealth();
  }, []);

  const checkSystemHealth = async () => {
    const response = await makeApiRequest('/health');
    if (response.success) {
      toast.success('System is healthy');
    }
  };

  const checkConnection = async () => {
    const response = await makeApiRequest('/api/reddit/connection-status');
    if (response.connected) {
      setConnected(true);
      setUsername(response.reddit_username);
    }
  };

  const checkAutomationStatus = async () => {
    const response = await makeApiRequest('/api/automation/status');
    setAutomationStatus(response);
  };

  const connectReddit = async () => {
    const response = await makeApiRequest('/api/oauth/reddit/authorize');
    if (response.success) {
      window.open(response.redirect_url, '_blank');
      toast.success('Reddit authorization opened in new tab');
    }
  };

  const simulateConnection = () => {
    setConnected(true);
    setUsername('test_user');
    toast.success('Simulated Reddit connection!');
  };

  const handleManualPost = async (e) => {
    e.preventDefault();
    if (!postForm.title || !postForm.content) {
      toast.error('Please enter both title and content');
      return;
    }

    setLoading(true);
    const response = await makeApiRequest('/api/reddit/post', 'POST', postForm);
    
    if (response.success) {
      toast.success('Post created successfully!');
      setPostForm({ subreddit: 'test', title: '', content: '', language: 'en', contentType: 'text' });
    }
    setLoading(false);
  };

  const generateAutoPost = async () => {
    if (!autoPostForm.businessType) {
      toast.error('Please enter your business type');
      return;
    }

    setLoading(true);
    for (let i = 0; i < autoPostForm.numPosts; i++) {
      const response = await makeApiRequest('/api/ai/generate-domain-content', 'POST', {
        domain: autoPostForm.domain,
        business_type: autoPostForm.businessType,
        target_audience: autoPostForm.targetAudience,
        language: autoPostForm.language,
        content_style: autoPostForm.contentStyle
      });

      if (response.success) {
        toast.success(`Content ${i + 1} generated successfully!`);
      }
    }
    setLoading(false);
  };

  const findQuestions = async () => {
    setLoading(true);
    const response = await makeApiRequest('/api/reddit/questions', 'GET', {
      subreddits: questionForm.subreddits,
      keywords: questionForm.keywords,
      limit: questionForm.limit
    });

    if (response.success) {
      setQuestions(response.questions || []);
      toast.success(`Found ${response.questions?.length || 0} questions`);
    }
    setLoading(false);
  };

  const generateDomainContent = async () => {
    if (!domainForm.businessType || !domainForm.topic) {
      toast.error('Please fill in business type and topic');
      return;
    }

    setLoading(true);
    const response = await makeApiRequest('/api/ai/generate-domain-content', 'POST', {
      domain: domainForm.domain,
      business_type: domainForm.businessType,
      target_audience: domainForm.targetAudience,
      language: domainForm.language,
      content_style: domainForm.contentStyle
    });

    if (response.success) {
      setGeneratedContent(`Title: ${response.title}\n\nContent: ${response.body}`);
      toast.success('Domain content generated!');
    }
    setLoading(false);
  };

  const generateAIContent = async () => {
    if (!aiForm.topic) {
      toast.error('Please enter a topic');
      return;
    }

    setLoading(true);
    const response = await makeApiRequest('/api/ai/generate-content', 'POST', aiForm);

    if (response.success) {
      setGeneratedContent(response.content);
      toast.success('AI content generated!');
    }
    setLoading(false);
  };

  const setupAutoPosting = async () => {
    const config = {
      domain: 'education',
      business_type: 'JEE coaching institute',
      target_audience: 'indian_students',
      subreddits: ['JEE', 'NEET', 'IndianStudents'],
      posts_per_day: 3,
      posting_times: ['09:00', '14:00', '19:00'],
      content_style: 'engaging'
    };

    const response = await makeApiRequest('/api/automation/setup-auto-posting', 'POST', config);
    if (response.success) {
      toast.success('Auto-posting enabled!');
      checkAutomationStatus();
    }
  };

  const setupAutoReplies = async () => {
    const config = {
      domain: 'education',
      expertise_level: 'intermediate',
      subreddits: ['JEE', 'NEET', 'IndianStudents'],
      keywords: ['help', 'advice', 'JEE', 'preparation'],
      max_replies_per_hour: 2,
      response_delay_minutes: 15
    };

    const response = await makeApiRequest('/api/automation/setup-auto-replies', 'POST', config);
    if (response.success) {
      toast.success('Auto-replies enabled!');
      checkAutomationStatus();
    }
  };

  const fetchAnalytics = async () => {
    const response = await makeApiRequest('/api/automation/performance-analytics');
    if (response.success) {
      setAnalytics(response.performance);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f9fafb', 
      fontFamily: 'system-ui, -apple-system, sans-serif' 
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 24px',
        marginBottom: '24px'
      }}>
        <h1 style={{
          fontSize: '32px',
          fontWeight: 'bold',
          color: '#111827',
          margin: 0,
          marginBottom: '8px'
        }}>
          Reddit Automation Platform
        </h1>
        <p style={{
          color: '#6b7280',
          margin: 0,
          fontSize: '16px'
        }}>
          Automate your Reddit presence with AI-powered content generation
        </p>
      </div>

      {/* Connection Status Bar */}
      <div style={{
        backgroundColor: 'white',
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        margin: '0 24px 24px 24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            backgroundColor: connected ? '#10b981' : '#ef4444'
          }}></div>
          <span style={{ fontWeight: '500', color: '#374151' }}>
            {connected ? `Connected as: ${username}` : 'Not connected to Reddit'}
          </span>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          {!connected && (
            <>
              <button
                onClick={connectReddit}
                style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Connect Reddit
              </button>
              <button
                onClick={simulateConnection}
                style={{
                  backgroundColor: '#6b7280',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '8px 16px',
                  cursor: 'pointer',
                  fontWeight: '500'
                }}
              >
                Simulate Connection
              </button>
            </>
          )}
        </div>
      </div>

      {/* Tab Navigation */}
      <div style={{
        margin: '0 24px',
        borderBottom: '1px solid #e5e7eb',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', gap: '32px' }}>
          {['testing', 'automation', 'questions', 'domain', 'ai', 'analytics'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                background: 'none',
                border: 'none',
                padding: '12px 0',
                fontSize: '16px',
                fontWeight: '500',
                color: activeTab === tab ? '#3b82f6' : '#6b7280',
                borderBottom: activeTab === tab ? '2px solid #3b82f6' : '2px solid transparent',
                cursor: 'pointer',
                textTransform: 'capitalize'
              }}
            >
              {tab === 'testing' ? 'Manual Testing' : 
               tab === 'automation' ? 'Auto Setup' :
               tab === 'questions' ? 'Question Monitor' :
               tab === 'domain' ? 'Domain Content' :
               tab === 'ai' ? 'AI Generator' : 'Analytics'}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div style={{ padding: '0 24px', maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Manual Testing Tab */}
        {activeTab === 'testing' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              Manual Reddit Post Testing
            </h2>
            
            <div style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '24px'
            }}>
              <form onSubmit={handleManualPost}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                      Subreddit
                    </label>
                    <select
                      value={postForm.subreddit}
                      onChange={(e) => setPostForm({...postForm, subreddit: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '14px'
                      }}
                    >
                      <option value="test">test</option>
                      <option value="india">india</option>
                      <option value="indiaspeaks">indiaspeaks</option>
                      <option value="bangalore">bangalore</option>
                      <option value="AskReddit">AskReddit</option>
                    </select>
                  </div>
                  
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                      Language
                    </label>
                    <select
                      value={postForm.language}
                      onChange={(e) => setPostForm({...postForm, language: e.target.value})}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        border: '1px solid #d1d5db',
                        borderRadius: '6px',
                        fontSize: '14px'
                      }}
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                    </select>
                  </div>
                </div>
                
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Post Title
                  </label>
                  <input
                    type="text"
                    value={postForm.title}
                    onChange={(e) => setPostForm({...postForm, title: e.target.value})}
                    placeholder="Enter your post title..."
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                    required
                  />
                </div>
                
                <div style={{ marginTop: '16px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Post Content
                  </label>
                  <textarea
                    value={postForm.content}
                    onChange={(e) => setPostForm({...postForm, content: e.target.value})}
                    placeholder="Enter your post content..."
                    rows={6}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px',
                      resize: 'vertical'
                    }}
                    required
                  />
                </div>
                
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '12px 24px',
                    marginTop: '24px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontWeight: '500',
                    fontSize: '16px'
                  }}
                >
                  {loading ? 'Posting...' : 'Post to Reddit'}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Automation Setup Tab */}
        {activeTab === 'automation' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              Automation Setup
            </h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '24px'
              }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
                  Auto-Posting
                </h3>
                <p style={{ color: '#6b7280', marginBottom: '16px', fontSize: '14px' }}>
                  Automatically post content 3 times daily based on your business domain
                </p>
                <button
                  onClick={setupAutoPosting}
                  style={{
                    backgroundColor: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '12px 24px',
                    cursor: 'pointer',
                    fontWeight: '500',
                    width: '100%'
                  }}
                >
                  Enable Auto-Posting
                </button>
              </div>
              
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '24px'
              }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
                  Auto-Replies
                </h3>
                <p style={{ color: '#6b7280', marginBottom: '16px', fontSize: '14px' }}>
                  Monitor questions and automatically provide helpful answers
                </p>
                <button
                  onClick={setupAutoReplies}
                  style={{
                    backgroundColor: '#8b5cf6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '12px 24px',
                    cursor: 'pointer',
                    fontWeight: '500',
                    width: '100%'
                  }}
                >
                  Enable Auto-Replies
                </button>
              </div>
            </div>
            
            {/* Automation Status */}
            {automationStatus && (
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '24px',
                marginTop: '24px'
              }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
                  Current Status
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <h4 style={{ fontWeight: '500', marginBottom: '8px', color: '#374151' }}>Auto-Posting</h4>
                    <span style={{
                      color: automationStatus.auto_posting?.enabled ? '#10b981' : '#6b7280',
                      fontSize: '14px'
                    }}>
                      {automationStatus.auto_posting?.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  <div>
                    <h4 style={{ fontWeight: '500', marginBottom: '8px', color: '#374151' }}>Auto-Replies</h4>
                    <span style={{
                      color: automationStatus.auto_replies?.enabled ? '#10b981' : '#6b7280',
                      fontSize: '14px'
                    }}>
                      {automationStatus.auto_replies?.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Question Monitor Tab */}
        {activeTab === 'questions' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              Reddit Question Monitor
            </h2>
            
            <div style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '24px',
              marginBottom: '24px'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Subreddits to Monitor
                  </label>
                  <input
                    type="text"
                    value={questionForm.subreddits}
                    onChange={(e) => setQuestionForm({...questionForm, subreddits: e.target.value})}
                    placeholder="Comma-separated subreddits"
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Filter Keywords
                  </label>
                  <input
                    type="text"
                    value={questionForm.keywords}
                    onChange={(e) => setQuestionForm({...questionForm, keywords: e.target.value})}
                    placeholder="Comma-separated keywords"
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                </div>
              </div>
              
              <button
                onClick={findQuestions}
                disabled={loading}
                style={{
                  backgroundColor: loading ? '#9ca3af' : '#f59e0b',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '12px 24px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: '500'
                }}
              >
                {loading ? 'Searching...' : 'Find Questions to Answer'}
              </button>
            </div>
            
            {/* Questions List */}
            {questions.length > 0 && (
              <div style={{ space: '16px' }}>
                {questions.map((question, index) => (
                  <div key={index} style={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    padding: '16px',
                    marginBottom: '16px'
                  }}>
                    <h4 style={{ fontWeight: '600', marginBottom: '8px', color: '#111827' }}>
                      Q{index + 1}: {question.title}
                    </h4>
                    <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '8px' }}>
                      r/{question.subreddit} • {question.score} upvotes • {question.num_comments} comments
                    </p>
                    <p style={{ color: '#374151', fontSize: '14px' }}>
                      {question.content?.substring(0, 200)}...
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Domain Content Tab */}
        {activeTab === 'domain' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              Domain-Specific Content Generation
            </h2>
            
            <div style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '24px'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Business Domain
                  </label>
                  <select
                    value={domainForm.domain}
                    onChange={(e) => setDomainForm({...domainForm, domain: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="education">Education</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="tech">Technology</option>
                    <option value="health">Health</option>
                    <option value="business">Business</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Content Topic
                  </label>
                  <input
                    type="text"
                    value={domainForm.topic}
                    onChange={(e) => setDomainForm({...domainForm, topic: e.target.value})}
                    placeholder="e.g., study tips, exam preparation"
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  />
                </div>
              </div>
              
              <div style={{ marginTop: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Business Type
                </label>
                <input
                  type="text"
                  value={domainForm.businessType}
                  onChange={(e) => setDomainForm({...domainForm, businessType: e.target.value})}
                  placeholder="e.g., IIT JEE coaching center in Delhi"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
              </div>
              
              <button
                onClick={generateDomainContent}
                disabled={loading}
                style={{
                  backgroundColor: loading ? '#9ca3af' : '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '12px 24px',
                  marginTop: '16px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: '500'
                }}
              >
                {loading ? 'Generating...' : 'Generate Domain Content'}
              </button>
              
              {generatedContent && (
                <div style={{ marginTop: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Generated Content
                  </label>
                  <textarea
                    value={generatedContent}
                    readOnly
                    rows={10}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px',
                      backgroundColor: '#f9fafb'
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Generator Tab */}
        {activeTab === 'ai' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              AI Content Generator
            </h2>
            
            <div style={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '24px'
            }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Platform
                  </label>
                  <select
                    value={aiForm.platform}
                    onChange={(e) => setAiForm({...aiForm, platform: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="reddit">Reddit</option>
                    <option value="twitter">Twitter</option>
                    <option value="stackoverflow">StackOverflow</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Content Type
                  </label>
                  <select
                    value={aiForm.contentType}
                    onChange={(e) => setAiForm({...aiForm, contentType: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="post">Post</option>
                    <option value="comment">Comment</option>
                    <option value="answer">Answer</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Tone
                  </label>
                  <select
                    value={aiForm.tone}
                    onChange={(e) => setAiForm({...aiForm, tone: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="friendly">Friendly</option>
                    <option value="informative">Informative</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Language
                  </label>
                  <select
                    value={aiForm.language}
                    onChange={(e) => setAiForm({...aiForm, language: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}
                  >
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                  </select>
                </div>
              </div>
              
              <div style={{ marginTop: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Topic
                </label>
                <input
                  type="text"
                  value={aiForm.topic}
                  onChange={(e) => setAiForm({...aiForm, topic: e.target.value})}
                  placeholder="Enter content topic..."
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
              </div>
              
              <div style={{ marginTop: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Target Audience
                </label>
                <input
                  type="text"
                  value={aiForm.targetAudience}
                  onChange={(e) => setAiForm({...aiForm, targetAudience: e.target.value})}
                  placeholder="e.g., Indian students, professionals"
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px'
                  }}
                />
              </div>
              
              <div style={{ marginTop: '16px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                  Additional Context
                </label>
                <textarea
                  value={aiForm.additionalContext}
                  onChange={(e) => setAiForm({...aiForm, additionalContext: e.target.value})}
                  placeholder="Any specific requirements..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #d1d5db',
                    borderRadius: '6px',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <button
                onClick={generateAIContent}
                disabled={loading}
                style={{
                  backgroundColor: loading ? '#9ca3af' : '#8b5cf6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '12px 24px',
                  marginTop: '16px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: '500'
                }}
              >
                {loading ? 'Generating...' : 'Generate AI Content'}
              </button>
              
              {generatedContent && (
                <div style={{ marginTop: '24px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#374151' }}>
                    Generated Content
                  </label>
                  <textarea
                    value={generatedContent}
                    readOnly
                    rows={8}
                    style={{
                      width: '100%',
                      padding: '12px',
                      border: '1px solid #d1d5db',
                      borderRadius: '6px',
                      fontSize: '14px',
                      backgroundColor: '#f9fafb'
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px', color: '#111827' }}>
              Analytics Dashboard
            </h2>
            
            <button
              onClick={fetchAnalytics}
              disabled={loading}
              style={{
                backgroundColor: loading ? '#9ca3af' : '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                padding: '12px 24px',
                marginBottom: '24px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: '500'
              }}
            >
              {loading ? 'Loading...' : 'Refresh Analytics'}
            </button>
            
            {/* Key Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '24px' }}>
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>
                  Posts Today
                </h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#3b82f6', margin: 0 }}>
                  {analytics?.auto_posts?.total_this_month || 12}
                </p>
                <p style={{ fontSize: '12px', color: '#10b981', margin: 0 }}>+3</p>
              </div>
              
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>
                  Auto Replies
                </h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981', margin: 0 }}>
                  {analytics?.auto_replies?.total_this_month || 8}
                </p>
                <p style={{ fontSize: '12px', color: '#10b981', margin: 0 }}>+2</p>
              </div>
              
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>
                  Karma Gained
                </h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b', margin: 0 }}>
                  {analytics?.engagement_metrics?.karma_gained || 456}
                </p>
                <p style={{ fontSize: '12px', color: '#10b981', margin: 0 }}>+45</p>
              </div>
              
              <div style={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '16px',
                textAlign: 'center'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: '500', color: '#6b7280', marginBottom: '8px' }}>
                  Success Rate
                </h3>
                <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#8b5cf6', margin: 0 }}>
                  {analytics?.auto_posts?.success_rate || 87}%
                </p>
                <p style={{ fontSize: '12px', color: '#10b981', margin: 0 }}>+5%</p>
              </div>
            </div>
            
            {/* Performance Details */}
            {analytics && (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                <div style={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '24px'
                }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
                    Best Performing Content
                  </h3>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {analytics.trending_performance?.most_engaging_topics?.map((topic, index) => (
                      <li key={index} style={{ 
                        padding: '8px 0', 
                        borderBottom: '1px solid #f3f4f6',
                        color: '#374151',
                        fontSize: '14px'
                      }}>
                        • {topic}
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div style={{
                  backgroundColor: 'white',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '24px'
                }}>
                  <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: '#111827' }}>
                    Optimal Subreddits
                  </h3>
                  <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {analytics.trending_performance?.optimal_subreddits?.map((subreddit, index) => (
                      <li key={index} style={{ 
                        padding: '8px 0', 
                        borderBottom: '1px solid #f3f4f6',
                        color: '#374151',
                        fontSize: '14px'
                      }}>
                        • {subreddit}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default RedditAUTO;