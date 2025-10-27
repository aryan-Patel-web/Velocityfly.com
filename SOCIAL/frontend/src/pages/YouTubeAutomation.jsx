// import React, { useState, useEffect, useCallback } from 'react';
// import { useAuth } from '../quickpage/AuthContext';

// const YouTubeAutomation = () => {
//   const { user, token, isAuthenticated, debugAuth } = useAuth();
//   const [activeTab, setActiveTab] = useState('connect');
//   const [loading, setLoading] = useState(false);
//   const [status, setStatus] = useState(null);
//   const [error, setError] = useState('');
  
//   const [config, setConfig] = useState({
//     content_type: 'shorts',
//     upload_schedule: ['09:00', '15:00', '21:00'],
//     content_categories: ['Technology', 'Business', 'Education'],
//     auto_generate_titles: true,
//     auto_generate_descriptions: true,
//     auto_add_tags: true,
//     privacy_status: 'public',
//     shorts_per_day: 3,
//     videos_per_week: 2
//   });
  
//   const [contentData, setContentData] = useState({
//     content_type: 'shorts',
//     topic: '',
//     target_audience: 'general',
//     duration_seconds: 30,
//     style: 'engaging',
//     title: '',
//     description: '',
//     video_url: ''
//   });

//   const [generatedContent, setGeneratedContent] = useState(null);
//   const [analytics, setAnalytics] = useState(null);
//   // NEW: Thumbnail states
//   const [thumbnailOptions, setThumbnailOptions] = useState([]);
//   const [selectedThumbnail, setSelectedThumbnail] = useState(null);
//   const [generatingThumbnails, setGeneratingThumbnails] = useState(false);

//   const API_BASE = process.env.NODE_ENV === 'production' 
//     ? (import.meta.env.VITE_API_URL || 'https://velocitypost-984x.onrender.com')
//     : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

//   const getUserData = useCallback(() => {
//     if (user && user.user_id) {
//       return user;
//     }
    
//     const possibleKeys = ['user', 'cached_user', 'auth_user'];
//     for (const key of possibleKeys) {
//       try {
//         const storedUser = localStorage.getItem(key);
//         if (storedUser) {
//           const parsedUser = JSON.parse(storedUser);
//           if (parsedUser && parsedUser.user_id) {
//             return parsedUser;
//           }
//         }
//       } catch (error) {
//         console.warn(`Error parsing ${key} from localStorage:`, error);
//       }
//     }
    
//     return null;
//   }, [user]);

//   const generateContent = useCallback(async () => {
//     if (!token) {
//       setError('Authentication required');
//       return;
//     }

//     if (!contentData.topic) {
//       setError('Please enter a topic');
//       return;
//     }

//     setLoading(true);
//     setError('');
    
//     try {
//       const response = await fetch(`${API_BASE}/api/ai/generate-youtube-content`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`
//         },
//         body: JSON.stringify({
//           content_type: contentData.content_type,
//           topic: contentData.topic,
//           target_audience: contentData.target_audience,
//           duration_seconds: contentData.duration_seconds,
//           style: contentData.style
//         })
//       });
      
//       const result = await response.json();
      
//       if (result.success) {
//         setGeneratedContent(result);
//         setContentData(prev => ({
//           ...prev,
//           title: result.title || '',
//           description: result.description || ''
//         }));
//         setError('');
//       } else {
//         setError(result.error || result.message || 'Content generation failed');
//       }
//     } catch (error) {
//       setError('Content generation failed: ' + error.message);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, contentData, API_BASE]);





// const generateThumbnails = useCallback(async () => {
//   if (!contentData.video_url || !contentData.title) {
//     setError('Video URL and title required for thumbnail generation');
//     return;
//   }
  
//   setGeneratingThumbnails(true);
//   setError('');
  
//   try {
//     const response = await fetch(`${API_BASE}/api/ai/generate-thumbnails`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': `Bearer ${token}`
//       },
//       body: JSON.stringify({
//         video_url: contentData.video_url,
//         video_title: contentData.title,
//         style: 'indian'
//       })
//     });
    
//     const result = await response.json();
    
//     console.log('🎨 Thumbnail Generation Result:', result); // ← ADD THIS DEBUG LOG
    
//     if (result.success && result.thumbnails) {
//       setThumbnailOptions(result.thumbnails);
//       setSelectedThumbnail(result.thumbnails[0]); // Auto-select first
//       console.log('✅ Selected thumbnail:', result.thumbnails[0]); // ← ADD THIS
//       setError('');
//     } else {
//       setError(result.error || 'Thumbnail generation failed');
//     }
//   } catch (error) {
//     setError('Thumbnail generation failed: ' + error.message);
//   } finally {
//     setGeneratingThumbnails(false);
//   }
// }, [contentData.video_url, contentData.title, token, API_BASE]);







// const uploadVideo = useCallback(async () => {
//   if (!token) {
//     setError('Authentication required');
//     return;
//   }

//   if (!contentData.video_url || !contentData.title) {
//     setError('Please provide video URL and title');
//     return;
//   }

//   setLoading(true);
//   setError('');
  
//   try {
//     const userData = getUserData();
    
//     if (!userData || !userData.user_id) {
//       setError('User ID not found. Please log in again.');
//       return;
//     }
    
//     // ✅ VALIDATE THUMBNAIL
//     let thumbnailToSend = null;
//     if (selectedThumbnail?.url) {
//       // Make sure it's a valid data URL
//       if (selectedThumbnail.url.startsWith('data:image')) {
//         thumbnailToSend = selectedThumbnail.url;
//         console.log('📤 Uploading with thumbnail, size:', thumbnailToSend.length);
//       } else {
//         console.warn('⚠️ Invalid thumbnail format, skipping');
//       }
//     }
    
//     const uploadPayload = {
//       user_id: userData.user_id,
//       content_type: contentData.content_type,
//       title: contentData.title.trim(), // ✅ TRIM WHITESPACE
//       description: contentData.description.trim(),
//       video_url: contentData.video_url,
//       thumbnail_url: thumbnailToSend
//     };
    
//     console.log('📦 Upload payload:', {
//       ...uploadPayload,
//       thumbnail_url: thumbnailToSend ? `${thumbnailToSend.substring(0, 50)}... (${thumbnailToSend.length} chars)` : 'null'
//     });
    
//     const response = await fetch(`${API_BASE}/api/youtube/upload`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': `Bearer ${token}`,
//         'X-User-ID': userData.user_id
//       },
//       body: JSON.stringify(uploadPayload)
//     });
    
//     const result = await response.json();
    
//     if (result.success) {
//       const successMessage = result.thumbnail_uploaded 
//         ? `✅ Video uploaded successfully with custom thumbnail!\n\nURL: ${result.video_url}`
//         : `✅ Video uploaded successfully!\n\n⚠️ Thumbnail upload failed - you can add it manually later.\n\nURL: ${result.video_url}`;
      
//       alert(successMessage);
      
//       // Reset form
//       setContentData(prev => ({ 
//         ...prev, 
//         title: '', 
//         description: '', 
//         video_url: '' 
//       }));
//       setThumbnailOptions([]);
//       setSelectedThumbnail(null);
      
//       await fetchAutomationStatus();
//       if (analytics) fetchAnalytics();
//       setError('');
//     } else {
//       setError(result.error || result.message || 'Upload failed');
//     }
//   } catch (error) {
//     setError('Upload failed: ' + error.message);
//     console.error('Upload error:', error);
//   } finally {
//     setLoading(false);
//   }
// }, [token, contentData, selectedThumbnail, getUserData, API_BASE, fetchAutomationStatus, analytics, fetchAnalytics]);





// // Add these functions before your return statement

//   const generateCommunityPost = useCallback(async () => {
//     if (!token) {
//       setError('Authentication required');
//       return;
//     }

//     setLoading(true);
//     setError('');
    
//     try {
//       const response = await fetch(`${API_BASE}/api/ai/generate-community-post`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`
//         },
//         body: JSON.stringify({
//           post_type: contentData.post_type || 'text',
//           topic: contentData.topic || 'general',
//           target_audience: contentData.target_audience || 'general'
//         })
//       });
      
//       const result = await response.json();
      
//       if (result.success) {
//         setContentData(prev => ({
//           ...prev,
//           post_content: result.content || result.post_content || '',
//           option_0: result.options?.[0] || '',
//           option_1: result.options?.[1] || '',
//           option_2: result.options?.[2] || '',
//           option_3: result.options?.[3] || ''
//         }));
//         setError('');
//       } else {
//         setError(result.error || 'Failed to generate post');
//       }
//     } catch (error) {
//       setError('Post generation failed: ' + error.message);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, contentData.post_type, contentData.topic, contentData.target_audience, API_BASE]);







//   const publishCommunityPost = useCallback(async () => {
//     if (!token) {
//       setError('Authentication required');
//       return;
//     }

//     if (!contentData.post_content) {
//       setError('Please enter post content');
//       return;
//     }

//     setLoading(true);
//     setError('');
    
//     try {
//       const userData = getUserData();
      
//       if (!userData?.user_id) {
//         setError('User ID not found. Please log in again.');
//         return;
//       }
      
//       const postData = {
//         user_id: userData.user_id,
//         post_type: contentData.post_type || 'text',
//         content: contentData.post_content,
//         image_url: contentData.image_url || null,
//         options: [
//           contentData.option_0 || null,
//           contentData.option_1 || null,
//           contentData.option_2 || null,
//           contentData.option_3 || null
//         ].filter(Boolean),
//         correct_answer: contentData.correct_answer || null,
//         schedule_date: contentData.auto_schedule ? contentData.schedule_date : null,
//         schedule_time: contentData.auto_schedule ? contentData.schedule_time : null
//       };
      
//       const response = await fetch(`${API_BASE}/api/youtube/community-post`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`,
//           'X-User-ID': userData.user_id
//         },
//         body: JSON.stringify(postData)
//       });
      
//       const result = await response.json();
      
//       if (result.success) {
//         alert(`Community post ${contentData.auto_schedule ? 'scheduled' : 'published'} successfully!`);
//         setContentData(prev => ({ 
//           ...prev, 
//           post_content: '',
//           image_url: '',
//           option_0: '',
//           option_1: '',
//           option_2: '',
//           option_3: '',
//           auto_schedule: false,
//           schedule_date: '',
//           schedule_time: ''
//         }));
//         setError('');
//       } else {
//         setError(result.error || 'Failed to publish post');
//       }
//     } catch (error) {
//       setError('Publishing failed: ' + error.message);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, contentData, getUserData, API_BASE]);





//   const fetchAnalytics = useCallback(async () => {
//     if (!token) return;
    
//     try {
//       const userData = getUserData();
//       if (!userData?.user_id) return;
      
//       setLoading(true);
      
//       const response = await fetch(`${API_BASE}/api/youtube/analytics/${userData.user_id}?days=30`, {
//         headers: { 
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json',
//           'X-User-ID': userData.user_id
//         }
//       });
      
//       if (response.ok) {
//         const data = await response.json();
//         if (data.success) {
//           setAnalytics(data);
//         }
//       } else {
//         console.error('Analytics fetch failed:', response.status);
//       }
//     } catch (error) {
//       console.error('Analytics fetch failed:', error);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, getUserData, API_BASE]);

//   const fetchAutomationStatus = useCallback(async (retryCount = 0) => {
//     if (!token) {
//       console.log('No token available for status fetch');
//       return;
//     }
    
//     try {
//       const userData = getUserData();
      
//       if (!userData || !userData.user_id) {
//         console.error('No user_id found for status fetch');
//         setStatus({ youtube_connected: false });
//         return;
//       }
      
//       console.log('Fetching status for user_id:', userData.user_id);
      
//       const response = await fetch(`${API_BASE}/api/youtube/status/${userData.user_id}`, {
//         method: 'GET',
//         headers: { 
//           'Authorization': `Bearer ${token}`,
//           'Content-Type': 'application/json',
//           'X-User-ID': userData.user_id
//         }
//       });
      
//       if (response.ok) {
//         const data = await response.json();
//         if (data.success) {
//           setStatus(data);
//           if (data.youtube_automation?.config) {
//             setConfig(prev => ({ ...prev, ...data.youtube_automation.config }));
//           }
//         }
//       } else if (response.status === 404) {
//         setStatus({ youtube_connected: false });
//       } else if (response.status === 503 && retryCount < 3) {
//         console.log(`Service unavailable, retrying... (${retryCount + 1}/3)`);
//         setTimeout(() => fetchAutomationStatus(retryCount + 1), 2000);
//       } else {
//         throw new Error(`Status fetch failed: ${response.status}`);
//       }
//     } catch (error) {
//       console.error('Status fetch failed:', error);
//       setStatus({ youtube_connected: false });
//       if (retryCount === 0) {
//         setError('Failed to fetch YouTube connection status');
//       }
//     }
//   }, [token, getUserData, API_BASE]);






// const handleOAuthCallbackDirect = useCallback(async (code) => {
//   try {
//     setLoading(true);
//     setError('');
    
//     console.log('Processing OAuth callback with code:', code.substring(0, 20) + '...');
    
//     let userData = getUserData();
//     let currentToken = token;
    
//     if (!userData) {
//       const possibleTokenKeys = ['token', 'auth_token', 'access_token', 'authToken'];
//       for (const key of possibleTokenKeys) {
//         const storedToken = localStorage.getItem(key);
//         if (storedToken) {
//           currentToken = storedToken;
//           break;
//         }
//       }
//       userData = getUserData();
//     }
    
//     if (!userData || !userData.user_id) {
//       throw new Error('User authentication required. Please log in first.');
//     }
    
//     if (!currentToken) {
//       throw new Error('Authentication token not found. Please log in again.');
//     }
    
//     const currentOrigin = window.location.origin;
//     const redirectUri = `${currentOrigin}/youtube`;
    
//     console.log('Making OAuth callback request for user:', userData.user_id);
    
//     const response = await fetch(`${API_BASE}/api/youtube/oauth-callback`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': `Bearer ${currentToken}`,
//         'X-User-ID': userData.user_id
//       },
//       body: JSON.stringify({
//         user_id: userData.user_id,
//         code: code,
//         redirect_uri: redirectUri
//       })
//     });
    
//     if (!response.ok) {
//       const errorData = await response.json().catch(() => ({ error: 'Network error' }));
//       throw new Error(`OAuth callback failed: ${errorData.error || response.statusText}`);
//     }
    
//     const result = await response.json();
    
//     if (result.success) {
//       // Clear URL parameters AFTER successful processing
//       window.history.replaceState({}, document.title, window.location.pathname);
      
//       setError('');
//       setStatus(prev => ({ ...prev, youtube_connected: true, ...result }));
//       setActiveTab('setup');
      
//       await fetchAutomationStatus();
//       console.log('YouTube connected successfully - redirecting to setup');
//     } else {
//       throw new Error(result.error || result.message || 'YouTube connection failed');
//     }
//   } catch (error) {
//     // Clear URL on error too
//     window.history.replaceState({}, document.title, window.location.pathname);
//     console.error('OAuth callback error:', error);
//     setError(error.message);
//   } finally {
//     setLoading(false);
//   }
// }, [getUserData, token, API_BASE, fetchAutomationStatus]);






// useEffect(() => {
//   const urlParams = new URLSearchParams(window.location.search);
//   const code = urlParams.get('code');
//   const state = urlParams.get('state');
//   const error_param = urlParams.get('error');
  
//   console.log('YouTube useEffect - URL params:', { 
//     code: code ? code.substring(0, 20) + '...' : null, 
//     state, 
//     error: error_param,
//     fullURL: window.location.href
//   });
//   console.log('YouTube useEffect - Auth state:', { isAuthenticated, hasToken: !!token });
  
//   if (error_param) {
//     console.error('OAuth error detected:', error_param);
//     setError(`OAuth error: ${error_param}`);
//     window.history.replaceState({}, document.title, window.location.pathname);
//     return;
//   }
  
//   if (code && state === 'youtube_oauth') {
//     console.log('✅ OAuth callback detected - processing code:', code.substring(0, 20) + '...');
//     handleOAuthCallbackDirect(code);
//     return;
//   }
  
//   // Normal initialization
//   if (isAuthenticated && token) {
//     console.log('Normal initialization - fetching status');
//     fetchAutomationStatus();
//   } else {
//     console.log('Waiting for authentication...');
//   }
// }, [isAuthenticated, token, handleOAuthCallbackDirect]);



//   const generateOAuthUrl = useCallback(async () => {
//     if (!token) {
//       setError('Please login first');
//       return;
//     }

//     setLoading(true);
//     setError('');
    
//     try {
//       const userData = getUserData();
      
//       if (!userData || !userData.user_id) {
//         throw new Error('User ID not found. Please log in again.');
//       }

//       console.log('Generating OAuth URL for user_id:', userData.user_id);
      
//       const requestPayload = {
//         user_id: userData.user_id,
//         state: 'youtube_oauth',
//         redirect_uri: `${window.location.origin}/youtube`
//       };
      
//       const response = await fetch(`${API_BASE}/api/youtube/oauth-url`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`,
//           'X-User-ID': userData.user_id
//         },
//         body: JSON.stringify(requestPayload)
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json().catch(() => ({ error: 'Network error' }));
//         throw new Error(`HTTP ${response.status}: ${errorData.error || response.statusText}`);
//       }
      
//       const result = await response.json();
      
//       if (result.success && result.authorization_url) {
//         window.location.href = result.authorization_url;
//       } else {
//         throw new Error(result.error || result.message || 'Failed to generate OAuth URL');
//       }
//     } catch (error) {
//       console.error('OAuth URL generation failed:', error);
//       setError('Connection error: ' + error.message);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, getUserData, API_BASE]);

//   const setupYouTubeAutomation = useCallback(async () => {
//     if (!token) {
//       setError('Authentication required');
//       return;
//     }

//     setLoading(true);
//     setError('');
    
//     try {
//       const userData = getUserData();
      
//       if (!userData || !userData.user_id) {
//         throw new Error('User ID not found. Please log in again.');
//       }
      
//       const response = await fetch(`${API_BASE}/api/youtube/setup-automation`, {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//           'Authorization': `Bearer ${token}`,
//           'X-User-ID': userData.user_id
//         },
//         body: JSON.stringify({
//           user_id: userData.user_id,
//           config: config
//         })
//       });
      
//       if (!response.ok) {
//         const errorData = await response.json().catch(() => ({ error: 'Network error' }));
//         throw new Error(errorData.error || 'Setup failed');
//       }
      
//       const result = await response.json();
      
//       if (result.success) {
//         setError('');
//         await fetchAutomationStatus();
//         setActiveTab('dashboard');
//       } else {
//         throw new Error(result.error || result.message || 'Setup failed');
//       }
//     } catch (error) {
//       console.error('Automation setup failed:', error);
//       setError('Setup failed: ' + error.message);
//     } finally {
//       setLoading(false);
//     }
//   }, [token, getUserData, config, API_BASE, fetchAutomationStatus]);

//   const TabButton = ({ id, label, emoji, active, onClick }) => (
//     <button 
//       onClick={onClick} 
//       style={{ 
//         padding: '12px 24px', 
//         background: active ? '#FF0000' : 'transparent', 
//         color: active ? 'white' : '#FF0000', 
//         border: '2px solid #FF0000', 
//         borderRadius: '12px', 
//         cursor: 'pointer', 
//         fontWeight: '600', 
//         display: 'flex', 
//         alignItems: 'center', 
//         gap: '8px', 
//         fontSize: '14px',
//         transition: 'all 0.3s ease'
//       }}
//     >
//       <span>{emoji}</span>{label}
//     </button>
//   );

//   const StatusCard = ({ title, value, color = '#FF0000' }) => (
//     <div style={{ 
//       background: 'white', 
//       borderRadius: '12px', 
//       padding: '20px', 
//       textAlign: 'center', 
//       boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)', 
//       border: `2px solid ${color}` 
//     }}>
//       <div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>{value}</div>
//       <div style={{ fontSize: '14px', color: '#666' }}>{title}</div>
//     </div>
//   );

//   if (!isAuthenticated || !token) {
//     return (
//       <div style={{ 
//         minHeight: '100vh', 
//         background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', 
//         display: 'flex', 
//         alignItems: 'center', 
//         justifyContent: 'center', 
//         padding: '20px' 
//       }}>
//         <div style={{ 
//           background: 'rgba(255, 255, 255, 0.95)', 
//           borderRadius: '20px', 
//           padding: '40px', 
//           textAlign: 'center', 
//           maxWidth: '500px' 
//         }}>
//           <h2 style={{ color: '#FF0000', marginBottom: '16px' }}>Authentication Required</h2>
//           <p style={{ color: '#666', marginBottom: '20px' }}>
//             Please log in to access YouTube automation features.
//           </p>
//           <a 
//             href="/login" 
//             style={{ 
//               padding: '12px 24px', 
//               background: '#FF0000', 
//               color: 'white', 
//               textDecoration: 'none', 
//               borderRadius: '8px', 
//               fontWeight: '600' 
//             }}
//           >
//             Go to Login
//           </a>
//         </div>
//       </div>
//     );
//   }

//   return (

// <div style={{ 
//       minHeight: '100vh', 
//       background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', 
//       padding: '20px' 
//     }}>
//       <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
//         {/* Header */}
//         <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
//           <h1 style={{ 
//             fontSize: '48px', 
//             fontWeight: '700', 
//             marginBottom: '16px', 
//             display: 'flex', 
//             alignItems: 'center', 
//             justifyContent: 'center', 
//             gap: '16px' 
//           }}>
//             <span style={{ fontSize: '56px' }}>📺</span>YouTube Automation Studio
//           </h1>
//           <p style={{ 
//             fontSize: '20px', 
//             opacity: 0.9, 
//             maxWidth: '800px', 
//             margin: '0 auto' 
//           }}>
//             Automate your YouTube channel with AI-generated content, smart scheduling, and analytics tracking
//           </p>
//           {user && (
//             <p style={{ fontSize: '16px', opacity: 0.8, marginTop: '10px' }}>
//               Welcome, {user.name} ({user.email})
//             </p>
//           )}
//         </div>

//         {/* Error Display */}
//         {error && (
//           <div style={{ 
//             background: '#fee', 
//             border: '1px solid #fcc', 
//             borderRadius: '12px', 
//             padding: '16px', 
//             marginBottom: '20px', 
//             color: '#c33', 
//             textAlign: 'center' 
//           }}>
//             <strong>Error:</strong> {error}
//             <button 
//               onClick={() => setError('')} 
//               style={{ 
//                 marginLeft: '10px', 
//                 background: 'none', 
//                 border: 'none', 
//                 color: '#c33', 
//                 cursor: 'pointer', 
//                 fontSize: '16px' 
//               }}
//             >
//               ✕
//             </button>
//           </div>
//         )}

//         {/* Navigation Tabs */}
//         <div style={{ 
//           display: 'flex', 
//           justifyContent: 'center', 
//           gap: '16px', 
//           marginBottom: '40px', 
//           flexWrap: 'wrap' 
//         }}>
//           <TabButton 
//             id="connect" 
//             label="Connect YouTube" 
//             emoji="🔗" 
//             active={activeTab === 'connect'} 
//             onClick={() => setActiveTab('connect')} 
//           />
//           <TabButton 
//             id="setup" 
//             label="Setup Automation" 
//             emoji="⚙️" 
//             active={activeTab === 'setup'} 
//             onClick={() => setActiveTab('setup')} 
//           />
//           <TabButton 
//             id="content" 
//             label="Create Content" 
//             emoji="🎬" 
//             active={activeTab === 'content'} 
//             onClick={() => setActiveTab('content')} 
//           />
//           <TabButton 
//             id="dashboard" 
//             label="Dashboard" 
//             emoji="📊" 
//             active={activeTab === 'dashboard'} 
//             onClick={() => setActiveTab('dashboard')} 
//           />
//           <TabButton 
//             id="analytics" 
//             label="Analytics" 
//             emoji="📈" 
//             active={activeTab === 'analytics'} 
//             onClick={() => setActiveTab('analytics')} 
//           />
//         </div>

//         {/* Connect YouTube Tab */}
//         {activeTab === 'connect' && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
//           }}>
//             <h2 style={{ 
//               color: '#FF0000', 
//               marginBottom: '30px', 
//               fontSize: '28px', 
//               fontWeight: '700' 
//             }}>
//               Connect Your YouTube Channel
//             </h2>
            
//             <div style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
//               <div style={{ marginBottom: '30px' }}>
//                 <div style={{ fontSize: '64px', marginBottom: '20px' }}>📺</div>
//                 <h3 style={{ color: '#333', marginBottom: '16px' }}>
//                   {status?.youtube_connected ? 'YouTube Connected!' : 'Connect to Get Started'}
//                 </h3>
//                 <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '30px' }}>
//                   {status?.youtube_connected 
//                     ? 'Your YouTube channel is connected and ready for automation.' 
//                     : 'Connect your YouTube channel to start automating content creation and uploads.'}
//                 </p>
//               </div>

//               {status?.youtube_connected ? (
//                 <div style={{ 
//                   background: '#d4edda', 
//                   border: '1px solid #c3e6cb', 
//                   borderRadius: '8px', 
//                   padding: '16px', 
//                   marginBottom: '20px', 
//                   color: '#155724' 
//                 }}>
//                   <h4 style={{ margin: '0 0 8px 0' }}>✅ Connected Successfully</h4>
//                   <p style={{ margin: 0, fontSize: '14px' }}>
//                     Channel: {status.channel_info?.channel_name || 'YouTube Channel'}
//                   </p>
//                   <button 
//                     onClick={() => setActiveTab('setup')} 
//                     style={{ 
//                       marginTop: '12px', 
//                       padding: '8px 16px', 
//                       background: '#155724', 
//                       color: 'white', 
//                       border: 'none', 
//                       borderRadius: '6px', 
//                       cursor: 'pointer', 
//                       fontWeight: '600' 
//                     }}
//                   >
//                     Continue to Setup →
//                   </button>
//                 </div>
//               ) : (
//                 <button
//                   onClick={generateOAuthUrl}
//                   disabled={loading}
//                   style={{
//                     padding: '16px 32px',
//                     background: loading ? '#ccc' : '#FF0000',
//                     color: 'white',
//                     border: 'none',
//                     borderRadius: '12px',
//                     fontSize: '16px',
//                     fontWeight: '700',
//                     cursor: loading ? 'not-allowed' : 'pointer',
//                     transition: 'background 0.3s ease'
//                   }}
//                 >
//                   {loading ? '⏳ Connecting...' : '🔗 Connect YouTube Channel'}
//                 </button>
//               )}

//               <div style={{ 
//                 marginTop: '30px', 
//                 padding: '20px', 
//                 background: '#f8f9fa', 
//                 borderRadius: '12px', 
//                 fontSize: '14px', 
//                 color: '#666' 
//               }}>
//                 <h4 style={{ color: '#333', marginBottom: '12px' }}>📋 What happens next:</h4>
//                 <ol style={{ textAlign: 'left', paddingLeft: '20px' }}>
//                   <li>You'll be redirected to Google's secure authentication page</li>
//                   <li>Sign in to your Google account that owns the YouTube channel</li>
//                   <li>Grant permissions for YouTube channel management</li>
//                   <li>You'll be redirected back here with confirmation</li>
//                 </ol>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Setup Tab */}
//         {activeTab === 'setup' && status?.youtube_connected && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
//           }}>
//             <h2 style={{ 
//               color: '#FF0000', 
//               marginBottom: '30px', 
//               fontSize: '28px', 
//               fontWeight: '700' 
//             }}>
//               Setup YouTube Automation
//             </h2>
            
//             <div style={{ 
//               display: 'grid', 
//               gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
//               gap: '30px' 
//             }}>
//               <div>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Content Settings</h3>
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Content Type
//                   </label>
//                   <select 
//                     value={config.content_type} 
//                     onChange={(e) => setConfig(prev => ({...prev, content_type: e.target.value}))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px' 
//                     }}
//                   >
//                     <option value="shorts">YouTube Shorts</option>
//                     <option value="videos">Regular Videos</option>
//                     <option value="both">Both</option>
//                   </select>
//                 </div>
                
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Privacy Status
//                   </label>
//                   <select 
//                     value={config.privacy_status} 
//                     onChange={(e) => setConfig(prev => ({...prev, privacy_status: e.target.value}))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px' 
//                     }}
//                   >
//                     <option value="private">Private</option>
//                     <option value="unlisted">Unlisted</option>
//                     <option value="public">Public</option>
//                   </select>
//                 </div>

//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Content Categories
//                   </label>
//                   <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
//                     {['Technology', 'Business', 'Education', 'Entertainment', 'Gaming', 'Lifestyle', 'Health', 'Finance'].map(category => (
//                       <span 
//                         key={category}
//                         onClick={() => {
//                           setConfig(prev => ({
//                             ...prev,
//                             content_categories: prev.content_categories.includes(category) 
//                               ? prev.content_categories.filter(c => c !== category)
//                               : [...prev.content_categories, category]
//                           }));
//                         }}
//                         style={{ 
//                           background: config.content_categories.includes(category) ? '#FF0000' : '#f8f9fa', 
//                           color: config.content_categories.includes(category) ? 'white' : '#666',
//                           padding: '6px 12px', 
//                           borderRadius: '20px', 
//                           fontSize: '12px', 
//                           cursor: 'pointer',
//                           border: '1px solid #ddd',
//                           transition: 'all 0.3s ease'
//                         }}
//                       >
//                         {category}
//                       </span>
//                     ))}
//                   </div>
//                 </div>
//               </div>
              
//               <div>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Upload Schedule</h3>
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Upload Times
//                   </label>
//                   <div style={{ 
//                     display: 'flex', 
//                     flexWrap: 'wrap', 
//                     gap: '8px', 
//                     marginBottom: '12px' 
//                   }}>
//                     {config.upload_schedule.map((time, index) => (
//                       <span 
//                         key={index} 
//                         style={{ 
//                           background: '#FF0000', 
//                           color: 'white', 
//                           padding: '6px 12px', 
//                           borderRadius: '20px', 
//                           fontSize: '12px', 
//                           display: 'flex', 
//                           alignItems: 'center', 
//                           gap: '4px' 
//                         }}
//                       >
//                         {time}
//                         <button 
//                           onClick={() => setConfig(prev => ({
//                             ...prev, 
//                             upload_schedule: prev.upload_schedule.filter((_, i) => i !== index)
//                           }))}
//                           style={{ 
//                             background: 'none', 
//                             border: 'none', 
//                             color: 'white', 
//                             cursor: 'pointer', 
//                             fontSize: '12px', 
//                             padding: '0', 
//                             marginLeft: '4px' 
//                           }}
//                         >
//                           ×
//                         </button>
//                       </span>
//                     ))}
//                   </div>
//                   <div style={{ display: 'flex', gap: '8px' }}>
//                     <input 
//                       type="time" 
//                       id="newTime"
//                       style={{ 
//                         padding: '8px', 
//                         borderRadius: '4px', 
//                         border: '1px solid #ddd', 
//                         fontSize: '12px' 
//                       }}
//                     />
//                     <button 
//                       onClick={() => {
//                         const timeInput = document.getElementById('newTime');
//                         if (timeInput.value && !config.upload_schedule.includes(timeInput.value)) {
//                           setConfig(prev => ({
//                             ...prev, 
//                             upload_schedule: [...prev.upload_schedule, timeInput.value]
//                           }));
//                           timeInput.value = '';
//                         }
//                       }}
//                       style={{ 
//                         padding: '8px 12px', 
//                         background: '#28a745', 
//                         color: 'white', 
//                         border: 'none', 
//                         borderRadius: '4px', 
//                         fontSize: '12px', 
//                         cursor: 'pointer' 
//                       }}
//                     >
//                       Add Time
//                     </button>
//                   </div>
//                 </div>
                
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Shorts per Day
//                   </label>
//                   <input 
//                     type="number" 
//                     value={config.shorts_per_day} 
//                     onChange={(e) => setConfig(prev => ({
//                       ...prev, 
//                       shorts_per_day: parseInt(e.target.value) || 1
//                     }))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px' 
//                     }}
//                     min="1" max="10"
//                   />
//                 </div>

//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Videos per Week
//                   </label>
//                   <input 
//                     type="number" 
//                     value={config.videos_per_week} 
//                     onChange={(e) => setConfig(prev => ({
//                       ...prev, 
//                       videos_per_week: parseInt(e.target.value) || 1
//                     }))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px' 
//                     }}
//                     min="1" max="14"
//                   />
//                 </div>

//                 <div style={{ marginBottom: '20px' }}>
//                   <h4 style={{ color: '#333', marginBottom: '12px', fontSize: '16px' }}>
//                     Automation Features
//                   </h4>
//                   {[
//                     { key: 'auto_generate_titles', label: 'Auto-generate Titles' },
//                     { key: 'auto_generate_descriptions', label: 'Auto-generate Descriptions' },
//                     { key: 'auto_add_tags', label: 'Auto-add Tags' }
//                   ].map(feature => (
//                     <label 
//                       key={feature.key} 
//                       style={{ 
//                         display: 'flex', 
//                         alignItems: 'center', 
//                         gap: '8px', 
//                         marginBottom: '8px', 
//                         cursor: 'pointer' 
//                       }}
//                     >
//                       <input 
//                         type="checkbox" 
//                         checked={config[feature.key]} 
//                         onChange={(e) => setConfig(prev => ({
//                           ...prev, 
//                           [feature.key]: e.target.checked
//                         }))}
//                         style={{ width: '16px', height: '16px' }}
//                       />
//                       <span style={{ fontSize: '14px', color: '#333' }}>
//                         {feature.label}
//                       </span>
//                     </label>
//                   ))}
//                 </div>
//               </div>
//             </div>
            
//             <div style={{ textAlign: 'center', marginTop: '40px' }}>
//               <button 
//                 onClick={setupYouTubeAutomation}
//                 disabled={loading}
//                 style={{
//                   padding: '16px 32px',
//                   background: loading ? '#ccc' : '#FF0000',
//                   color: 'white',
//                   border: 'none',
//                   borderRadius: '12px',
//                   fontSize: '16px',
//                   fontWeight: '700',
//                   cursor: loading ? 'not-allowed' : 'pointer',
//                   transition: 'background 0.3s ease'
//                 }}
//               >
//                 {loading ? '⏳ Setting Up...' : '⚙️ Enable Automation'}
//               </button>
//             </div>
//           </div>
//         )}

//         {/* Content Creation Tab */}
//         {activeTab === 'content' && status?.youtube_connected && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
//           }}>
//             <h2 style={{ 
//               color: '#FF0000', 
//               marginBottom: '30px', 
//               fontSize: '28px', 
//               fontWeight: '700' 
//             }}>
//               Create & Upload Content
//             </h2>
            
//             <div style={{ 
//               display: 'grid', 
//               gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
//               gap: '40px' 
//             }}>
//               <div>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Generate Content with AI</h3>
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Content Type
//                   </label>
//                   <select 
//                     value={contentData.content_type} 
//                     onChange={(e) => setContentData(prev => ({...prev, content_type: e.target.value}))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '16px' 
//                     }}
//                   >
//                     <option value="shorts">YouTube Shorts</option>
//                     <option value="videos">Regular Videos</option>
//                   </select>
                  
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Topic
//                   </label>
//                   <input 
//                     type="text" 
//                     value={contentData.topic} 
//                     onChange={(e) => setContentData(prev => ({...prev, topic: e.target.value}))}
//                     placeholder="Enter your video topic..."
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '16px' 
//                     }}
//                   />
                  
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Target Audience
//                   </label>
//                   <select 
//                     value={contentData.target_audience} 
//                     onChange={(e) => setContentData(prev => ({...prev, target_audience: e.target.value}))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '16px' 
//                     }}
//                   >
//                     <option value="general">General Audience</option>
//                     <option value="teens">Teens (13-19)</option>
//                     <option value="young_adults">Young Adults (20-35)</option>
//                     <option value="adults">Adults (35+)</option>
//                     <option value="professionals">Professionals</option>
//                     <option value="students">Students</option>
//                   </select>
                  
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Style
//                   </label>
//                   <select 
//                     value={contentData.style} 
//                     onChange={(e) => setContentData(prev => ({...prev, style: e.target.value}))}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '20px' 
//                     }}
//                   >
//                     <option value="engaging">Engaging</option>
//                     <option value="educational">Educational</option>
//                     <option value="entertaining">Entertaining</option>
//                     <option value="professional">Professional</option>
//                     <option value="casual">Casual</option>
//                     <option value="trending">Trending</option>
//                   </select>
//                 </div>
                
//                 <button 
//                   onClick={generateContent}
//                   disabled={loading || !contentData.topic}
//                   style={{
//                     width: '100%',
//                     padding: '12px',
//                     background: loading || !contentData.topic ? '#ccc' : '#28a745',
//                     color: 'white',
//                     border: 'none',
//                     borderRadius: '8px',
//                     fontSize: '14px',
//                     fontWeight: '600',
//                     cursor: loading || !contentData.topic ? 'not-allowed' : 'pointer',
//                     marginBottom: '20px',
//                     transition: 'background 0.3s ease'
//                   }}
//                 >
//                   {loading ? 'Generating...' : 'Generate Content'}
//                 </button>
                
//                 {generatedContent && (
//                   <div style={{ 
//                     padding: '16px', 
//                     background: '#f8f9fa', 
//                     borderRadius: '8px', 
//                     border: '1px solid #ddd' 
//                   }}>
//                     <h4 style={{ color: '#333', marginBottom: '12px' }}>Generated Content:</h4>
//                     <div style={{ marginBottom: '12px' }}>
//                       <strong style={{ color: '#666' }}>Title:</strong>
//                       <p style={{ 
//                         fontSize: '14px', 
//                         color: '#333', 
//                         margin: '4px 0', 
//                         background: 'white', 
//                         padding: '8px', 
//                         borderRadius: '4px' 
//                       }}>
//                         {generatedContent.title}
//                       </p>
//                     </div>
//                     <div style={{ marginBottom: '12px' }}>
//                       <strong style={{ color: '#666' }}>Description:</strong>
//                       <p style={{ 
//                         fontSize: '14px', 
//                         color: '#333', 
//                         margin: '4px 0', 
//                         background: 'white', 
//                         padding: '8px', 
//                         borderRadius: '4px' 
//                       }}>
//                         {generatedContent.description}
//                       </p>
//                     </div>
//                     {generatedContent.tags && generatedContent.tags.length > 0 && (
//                       <div>
//                         <strong style={{ color: '#666' }}>Tags:</strong>
//                         <div style={{ 
//                           marginTop: '4px', 
//                           display: 'flex', 
//                           flexWrap: 'wrap', 
//                           gap: '4px' 
//                         }}>
//                           {generatedContent.tags.map((tag, index) => (
//                             <span 
//                               key={index} 
//                               style={{ 
//                                 background: '#007bff', 
//                                 color: 'white', 
//                                 padding: '2px 8px', 
//                                 borderRadius: '12px', 
//                                 fontSize: '12px' 
//                               }}
//                             >
//                               {tag}
//                             </span>
//                           ))}
//                         </div>
//                       </div>
//                     )}
//                   </div>
//                 )}
//               </div>
              
//               <div>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Upload Video</h3>
//                 <div style={{ marginBottom: '20px' }}>
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Video Title
//                   </label>
//                   <input 
//                     type="text" 
//                     value={contentData.title} 
//                     onChange={(e) => setContentData(prev => ({...prev, title: e.target.value}))}
//                     placeholder="Enter video title..."
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '16px' 
//                     }}
//                   />
                  
//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Video URL
//                   </label>
//                   <input 
//                     type="url" 
//                     value={contentData.video_url} 
//                     onChange={(e) => setContentData(prev => ({...prev, video_url: e.target.value}))}
//                     placeholder="https://example.com/video.mp4"
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       marginBottom: '16px' 
//                     }}
//                   />
                  



//                   <label style={{ 
//                     display: 'block', 
//                     marginBottom: '8px', 
//                     fontWeight: '600', 
//                     color: '#333' 
//                   }}>
//                     Description
//                   </label>
//                   <textarea 
//                     value={contentData.description} 
//                     onChange={(e) => setContentData(prev => ({...prev, description: e.target.value}))}
//                     placeholder="Enter video description..."
//                     rows={4}
//                     style={{ 
//                       width: '100%', 
//                       padding: '12px', 
//                       borderRadius: '8px', 
//                       border: '2px solid #ddd', 
//                       fontSize: '14px', 
//                       resize: 'vertical', 
//                       marginBottom: '20px' 
//                     }}
//                   />
//                 </div>




//                 {/* NEW: AI Thumbnail Generator */}
//                 <div style={{ marginBottom: '20px' }}>
//                   <button 
//                     onClick={generateThumbnails}
//                     disabled={generatingThumbnails || !contentData.video_url || !contentData.title}
//                     style={{
//                       width: '100%',
//                       padding: '12px',
//                       background: generatingThumbnails ? '#ccc' : '#FF6600',
//                       color: 'white',
//                       border: 'none',
//                       borderRadius: '8px',
//                       fontSize: '14px',
//                       fontWeight: '600',
//                       cursor: generatingThumbnails ? 'not-allowed' : 'pointer',
//                       marginBottom: '16px',
//                       transition: 'background 0.3s ease'
//                     }}
//                   >
//                     {generatingThumbnails ? '🎨 Generating Thumbnails...' : '🎨 Generate AI Thumbnails'}
//                   </button>
//                 </div>




// {/* Thumbnail Selection */}
// {thumbnailOptions.length > 0 && (
//   <div style={{ marginBottom: '20px' }}>
//     <h4 style={{ color: '#333', marginBottom: '12px', fontSize: '16px' }}>
//       🎨 Select Thumbnail:
//     </h4>
//     <div style={{ 
//       display: 'grid', 
//       gridTemplateColumns: '1fr 1fr 1fr', 
//       gap: '12px' 
//     }}>
//       {thumbnailOptions.map((thumb, index) => (
//         <div 
//           key={index}
//           onClick={() => {
//             setSelectedThumbnail(thumb);
//             console.log('✅ Thumbnail selected:', thumb.variation);
//           }}
//           style={{
//             border: selectedThumbnail?.variation === thumb.variation 
//               ? '3px solid #FF0000' 
//               : '2px solid #ddd',
//             borderRadius: '8px',
//             padding: '8px',
//             cursor: 'pointer',
//             position: 'relative',
//             transition: 'all 0.3s ease',
//             backgroundColor: selectedThumbnail?.variation === thumb.variation 
//               ? '#fff5f5' 
//               : 'white'
//           }}
//         >
//           <img 
//             src={thumb.url} 
//             alt={`Thumbnail ${index + 1}`}
//             style={{ 
//               width: '100%', 
//               borderRadius: '4px',
//               display: 'block'
//             }}
//           />
//           <div style={{ 
//             fontSize: '11px', 
//             marginTop: '8px',
//             display: 'flex',
//             justifyContent: 'space-between',
//             alignItems: 'center'
//           }}>
//             <span style={{ fontWeight: '600' }}>
//               {selectedThumbnail?.variation === thumb.variation ? '✓ ' : ''}
//               Option {thumb.variation}
//             </span>
//             <span style={{ 
//               background: thumb.ctr_score > 70 ? '#28a745' : '#ffc107',
//               color: 'white',
//               padding: '2px 6px',
//               borderRadius: '4px',
//               fontSize: '10px',
//               fontWeight: '600'
//             }}>
//               CTR: {thumb.ctr_score.toFixed(0)}%
//             </span>
//           </div>
//           <div style={{ 
//             fontSize: '10px', 
//             color: '#666',
//             marginTop: '4px',
//             overflow: 'hidden',
//             textOverflow: 'ellipsis',
//             whiteSpace: 'nowrap'
//           }}>
//             {thumb.text}
//           </div>
//         </div>
//       ))}
//     </div>
    
//     {/* Selected Thumbnail Indicator */}
//     {selectedThumbnail && (
//       <div style={{
//         marginTop: '12px',
//         padding: '12px',
//         background: '#d4edda',
//         border: '1px solid #c3e6cb',
//         borderRadius: '6px',
//         fontSize: '13px',
//         color: '#155724'
//       }}>
//         ✅ <strong>Selected:</strong> Option {selectedThumbnail.variation} - "{selectedThumbnail.text}"
//         <br />
//         <small>This thumbnail will be uploaded with your video</small>
//       </div>
//     )}
    
//     <div style={{
//       marginTop: '12px',
//       padding: '12px',
//       background: '#f8f9fa',
//       borderRadius: '6px',
//       fontSize: '12px',
//       color: '#666'
//     }}>
//       💡 <strong>Tip:</strong> Higher CTR score = better chance of getting clicks. 
//       Click a thumbnail to select it for your video.
//     </div>
//   </div>
// )}

// {/* Upload Button - SINGLE BUTTON ONLY */}
// <button 
//   onClick={uploadVideo}
//   disabled={loading || !contentData.title || !contentData.video_url}
//   style={{
//     width: '100%',
//     padding: '12px',
//     background: loading || !contentData.title || !contentData.video_url ? '#ccc' : '#FF0000',
//     color: 'white',
//     border: 'none',
//     borderRadius: '8px',
//     fontSize: '14px',
//     fontWeight: '600',
//     cursor: loading || !contentData.title || !contentData.video_url ? 'not-allowed' : 'pointer',
//     transition: 'background 0.3s ease'
//   }}
// >
//   {loading ? 'Uploading...' : 'Upload to YouTube'}
// </button>












//                 {/* ADD THE COMMUNITY POSTS SECTION HERE - AFTER UPLOAD BUTTON */}
                
//                 <div style={{ 
//                   marginTop: '40px', 
//                   paddingTop: '30px', 
//                   borderTop: '2px solid #f0f0f0' 
//                 }}>
//                   <h3 style={{ color: '#333', marginBottom: '20px' }}>📱 Community Posts</h3>
                  
//                   <div style={{ marginBottom: '20px' }}>
//                     <label style={{ 
//                       display: 'block', 
//                       marginBottom: '8px', 
//                       fontWeight: '600', 
//                       color: '#333' 
//                     }}>
//                       Post Type
//                     </label>
//                     <select 
//                       value={contentData.post_type || 'text'} 
//                       onChange={(e) => setContentData(prev => ({...prev, post_type: e.target.value}))}
//                       style={{ 
//                         width: '100%', 
//                         padding: '12px', 
//                         borderRadius: '8px', 
//                         border: '2px solid #ddd', 
//                         fontSize: '14px', 
//                         marginBottom: '16px' 
//                       }}
//                     >
//                       <option value="text">📝 Text Post</option>
//                       <option value="image">🖼️ Image Post</option>
//                       <option value="video">🎥 Video Post</option>
//                       <option value="text_poll">📊 Text Poll</option>
//                       <option value="image_poll">🖼️📊 Image Poll</option>
//                       <option value="quiz">🎯 Quiz</option>
//                     </select>
                    
//                     <label style={{ 
//                       display: 'block', 
//                       marginBottom: '8px', 
//                       fontWeight: '600', 
//                       color: '#333' 
//                     }}>
//                       What's on your mind?
//                     </label>
//                     <textarea 
//                       value={contentData.post_content || ''} 
//                       onChange={(e) => setContentData(prev => ({...prev, post_content: e.target.value}))}
//                       placeholder={
//                         contentData.post_type === 'quiz' ? "Enter your quiz question..." :
//                         contentData.post_type === 'text_poll' || contentData.post_type === 'image_poll' ? "Enter your poll question..." :
//                         "What's on your mind? Share your thoughts with your community..."
//                       }
//                       rows={3}
//                       style={{ 
//                         width: '100%', 
//                         padding: '12px', 
//                         borderRadius: '8px', 
//                         border: '2px solid #ddd', 
//                         fontSize: '14px', 
//                         resize: 'vertical', 
//                         marginBottom: '16px' 
//                       }}
//                     />

//                     {/* Image Upload for Image Posts/Polls */}
//                     {(contentData.post_type === 'image' || contentData.post_type === 'image_poll') && (
//                       <>
//                         <label style={{ 
//                           display: 'block', 
//                           marginBottom: '8px', 
//                           fontWeight: '600', 
//                           color: '#333' 
//                         }}>
//                           Image URL
//                         </label>
//                         <input 
//                           type="url" 
//                           value={contentData.image_url || ''} 
//                           onChange={(e) => setContentData(prev => ({...prev, image_url: e.target.value}))}
//                           placeholder="https://example.com/image.jpg"
//                           style={{ 
//                             width: '100%', 
//                             padding: '12px', 
//                             borderRadius: '8px', 
//                             border: '2px solid #ddd', 
//                             fontSize: '14px', 
//                             marginBottom: '16px' 
//                           }}
//                         />
//                       </>
//                     )}

//                     {/* Poll Options */}
//                     {(contentData.post_type === 'text_poll' || contentData.post_type === 'image_poll' || contentData.post_type === 'quiz') && (
//                       <div style={{ marginBottom: '16px' }}>
//                         <label style={{ 
//                           display: 'block', 
//                           marginBottom: '8px', 
//                           fontWeight: '600', 
//                           color: '#333' 
//                         }}>
//                           {contentData.post_type === 'quiz' ? 'Quiz Options' : 'Poll Options'}
//                         </label>
//                         {[0, 1, 2, 3].map(index => (
//                           <input 
//                             key={index}
//                             type="text" 
//                             value={contentData[`option_${index}`] || ''} 
//                             onChange={(e) => setContentData(prev => ({...prev, [`option_${index}`]: e.target.value}))}
//                             placeholder={`Option ${index + 1}${index === 0 || index === 1 ? ' (required)' : ' (optional)'}`}
//                             style={{ 
//                               width: '100%', 
//                               padding: '10px', 
//                               borderRadius: '6px', 
//                               border: '1px solid #ddd', 
//                               fontSize: '14px', 
//                               marginBottom: '8px' 
//                             }}
//                           />
//                         ))}
//                         {contentData.post_type === 'quiz' && (
//                           <>
//                             <label style={{ 
//                               display: 'block', 
//                               marginTop: '12px',
//                               marginBottom: '8px', 
//                               fontWeight: '600', 
//                               color: '#333' 
//                             }}>
//                               Correct Answer
//                             </label>
//                             <select 
//                               value={contentData.correct_answer || '0'} 
//                               onChange={(e) => setContentData(prev => ({...prev, correct_answer: e.target.value}))}
//                               style={{ 
//                                 width: '100%', 
//                                 padding: '10px', 
//                                 borderRadius: '6px', 
//                                 border: '1px solid #ddd', 
//                                 fontSize: '14px' 
//                               }}
//                             >
//                               <option value="0">Option 1</option>
//                               <option value="1">Option 2</option>
//                               <option value="2">Option 3</option>
//                               <option value="3">Option 4</option>
//                             </select>
//                           </>
//                         )}
//                       </div>
//                     )}

//                     {/* Auto-schedule Toggle */}
//                     <div style={{ 
//                       marginBottom: '20px',
//                       padding: '16px',
//                       background: '#f8f9fa',
//                       borderRadius: '8px',
//                       border: '1px solid #ddd'
//                     }}>
//                       <label style={{ 
//                         display: 'flex', 
//                         alignItems: 'center', 
//                         gap: '8px', 
//                         cursor: 'pointer',
//                         marginBottom: '12px'
//                       }}>
//                         <input 
//                           type="checkbox" 
//                           checked={contentData.auto_schedule || false} 
//                           onChange={(e) => setContentData(prev => ({...prev, auto_schedule: e.target.checked}))}
//                           style={{ width: '16px', height: '16px' }}
//                         />
//                         <span style={{ fontSize: '14px', fontWeight: '600', color: '#333' }}>
//                           🕒 Schedule for later
//                         </span>
//                       </label>
                      
//                       {contentData.auto_schedule && (
//                         <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
//                           <input 
//                             type="date" 
//                             value={contentData.schedule_date || ''} 
//                             onChange={(e) => setContentData(prev => ({...prev, schedule_date: e.target.value}))}
//                             min={new Date().toISOString().split('T')[0]}
//                             style={{ 
//                               padding: '8px', 
//                               borderRadius: '4px', 
//                               border: '1px solid #ddd', 
//                               fontSize: '12px' 
//                             }}
//                           />
//                           <input 
//                             type="time" 
//                             value={contentData.schedule_time || ''} 
//                             onChange={(e) => setContentData(prev => ({...prev, schedule_time: e.target.value}))}
//                             style={{ 
//                               padding: '8px', 
//                               borderRadius: '4px', 
//                               border: '1px solid #ddd', 
//                               fontSize: '12px' 
//                             }}
//                           />
//                         </div>
//                       )}
//                     </div>

//                     {/* AI Generate Post Button */}
//                     <button 
//                       onClick={generateCommunityPost}
//                       disabled={loading}
//                       style={{
//                         width: '100%',
//                         padding: '10px',
//                         background: loading ? '#ccc' : '#28a745',
//                         color: 'white',
//                         border: 'none',
//                         borderRadius: '6px',
//                         fontSize: '14px',
//                         fontWeight: '600',
//                         cursor: loading ? 'not-allowed' : 'pointer',
//                         marginBottom: '12px',
//                         transition: 'background 0.3s ease'
//                       }}
//                     >
//                       {loading ? '🤖 Generating...' : '🤖 AI Generate Post'}
//                     </button>

//                     {/* Publish Post Button */}
//                     <button 
//                       onClick={publishCommunityPost}
//                       disabled={loading || !contentData.post_content}
//                       style={{
//                         width: '100%',
//                         padding: '12px',
//                         background: loading || !contentData.post_content ? '#ccc' : '#FF0000',
//                         color: 'white',
//                         border: 'none',
//                         borderRadius: '8px',
//                         fontSize: '14px',
//                         fontWeight: '600',
//                         cursor: loading || !contentData.post_content ? 'not-allowed' : 'pointer',
//                         transition: 'background 0.3s ease'
//                       }}
//                     >
//                       {loading ? '📤 Publishing...' : 
//                        contentData.auto_schedule ? '🕒 Schedule Post' : '📤 Publish Post'}
//                     </button>
//                   </div>
//                 </div>


                



//                 <div style={{ 
//                   marginTop: '20px', 
//                   padding: '16px', 
//                   background: '#fff3cd', 
//                   border: '1px solid #ffeaa7', 
//                   borderRadius: '8px' 
//                 }}>
//                   <h4 style={{ 
//                     color: '#856404', 
//                     marginBottom: '8px', 
//                     fontSize: '14px' 
//                   }}>
//                     Upload Tips:
//                   </h4>
//                   <ul style={{ 
//                     fontSize: '12px', 
//                     color: '#856404', 
//                     paddingLeft: '16px', 
//                     margin: 0 
//                   }}>
//                     <li>Video URL should be a direct link to an MP4 file</li>
//                     <li>For YouTube Shorts: keep videos under 60 seconds</li>
//                     <li>Use engaging titles with relevant keywords</li>
//                     <li>Add detailed descriptions for better SEO</li>
//                   </ul>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Dashboard Tab */}
//         {activeTab === 'dashboard' && status?.youtube_connected && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
//           }}>
//             <h2 style={{ 
//               color: '#FF0000', 
//               marginBottom: '30px', 
//               fontSize: '28px', 
//               fontWeight: '700' 
//             }}>
//               Automation Dashboard
//             </h2>
            
//             <div style={{ 
//               display: 'grid', 
//               gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
//               gap: '20px', 
//               marginBottom: '40px' 
//             }}>
//               <StatusCard 
//                 title="Total Uploads" 
//                 value={status?.youtube_automation?.stats?.total_uploads || 0} 
//               />
//               <StatusCard 
//                 title="Successful Uploads" 
//                 value={status?.youtube_automation?.stats?.successful_uploads || 0} 
//                 color="#28a745" 
//               />
//               <StatusCard 
//                 title="Failed Uploads" 
//                 value={status?.youtube_automation?.stats?.failed_uploads || 0} 
//                 color="#dc3545" 
//               />
//               <StatusCard 
//                 title="Automation Status" 
//                 value={status?.youtube_automation?.enabled ? "Active" : "Inactive"} 
//                 color={status?.youtube_automation?.enabled ? "#28a745" : "#ffc107"} 
//               />
//             </div>

//             <div style={{ 
//               display: 'grid', 
//               gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
//               gap: '30px' 
//             }}>
//               <div style={{ 
//                 background: 'white', 
//                 borderRadius: '12px', 
//                 padding: '24px', 
//                 boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
//               }}>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Current Configuration</h3>
//                 <div style={{ fontSize: '14px', color: '#666', lineHeight: 1.6 }}>
//                   <p><strong>Content Type:</strong> {config.content_type}</p>
//                   <p><strong>Privacy Status:</strong> {config.privacy_status}</p>
//                   <p><strong>Shorts per Day:</strong> {config.shorts_per_day}</p>
//                   <p><strong>Videos per Week:</strong> {config.videos_per_week}</p>
//                   <p><strong>Upload Schedule:</strong> {config.upload_schedule.join(', ')}</p>
//                   <p><strong>Auto Features:</strong> 
//                     {config.auto_generate_titles && ' Titles,'}
//                     {config.auto_generate_descriptions && ' Descriptions,'}
//                     {config.auto_add_tags && ' Tags'}
//                   </p>
//                 </div>
//               </div>

//               <div style={{ 
//                 background: 'white', 
//                 borderRadius: '12px', 
//                 padding: '24px', 
//                 boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
//               }}>
//                 <h3 style={{ color: '#333', marginBottom: '20px' }}>Channel Information</h3>
//                 <div style={{ fontSize: '14px', color: '#666', lineHeight: 1.6 }}>
//                   <p><strong>Channel Name:</strong> {status?.channel_info?.channel_name || 'N/A'}</p>
//                   <p><strong>Subscribers:</strong> {status?.channel_info?.subscriber_count || '0'}</p>
//                   <p><strong>Total Videos:</strong> {status?.channel_info?.video_count || '0'}</p>
//                   <p><strong>Total Views:</strong> {status?.channel_info?.view_count || '0'}</p>
//                 </div>
                
//                 <div style={{ marginTop: '20px' }}>
//                   <button 
//                     onClick={() => setActiveTab('analytics')}
//                     style={{ 
//                       padding: '10px 16px', 
//                       background: '#007bff', 
//                       color: 'white', 
//                       border: 'none', 
//                       borderRadius: '6px', 
//                       cursor: 'pointer', 
//                       fontSize: '14px',
//                       transition: 'background 0.3s ease'
//                     }}
//                   >
//                     View Analytics
//                   </button>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Analytics Tab */}
//         {activeTab === 'analytics' && status?.youtube_connected && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
//           }}>
//             <div style={{ 
//               display: 'flex', 
//               justifyContent: 'space-between', 
//               alignItems: 'center', 
//               marginBottom: '30px' 
//             }}>
//               <h2 style={{ 
//                 color: '#FF0000', 
//                 fontSize: '28px', 
//                 fontWeight: '700', 
//                 margin: 0 
//               }}>
//                 Channel Analytics
//               </h2>
//               <button 
//                 onClick={fetchAnalytics}
//                 disabled={loading}
//                 style={{
//                   padding: '10px 16px',
//                   background: loading ? '#ccc' : '#007bff',
//                   color: 'white',
//                   border: 'none',
//                   borderRadius: '6px',
//                   cursor: loading ? 'not-allowed' : 'pointer',
//                   fontSize: '14px',
//                   transition: 'background 0.3s ease'
//                 }}
//               >
//                 {loading ? 'Loading...' : 'Refresh Analytics'}
//               </button>
//             </div>
            
//             {analytics ? (
//               <div>
//                 <div style={{ 
//                   display: 'grid', 
//                   gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
//                   gap: '20px', 
//                   marginBottom: '30px' 
//                 }}>
//                   <StatusCard 
//                     title="Total Subscribers" 
//                     value={analytics.channel_statistics?.subscriberCount || '0'} 
//                     color="#FF0000" 
//                   />
//                   <StatusCard 
//                     title="Total Views" 
//                     value={analytics.channel_statistics?.viewCount || '0'} 
//                     color="#28a745" 
//                   />
//                   <StatusCard 
//                     title="Total Videos" 
//                     value={analytics.channel_statistics?.videoCount || '0'} 
//                     color="#007bff" 
//                   />
//                   <StatusCard 
//                     title="Analysis Period" 
//                     value={`${analytics.period_days} days`} 
//                     color="#6f42c1" 
//                   />
//                 </div>

//                 <div style={{ 
//                   background: 'white', 
//                   borderRadius: '12px', 
//                   padding: '24px', 
//                   boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
//                 }}>
//                   <h3 style={{ color: '#333', marginBottom: '20px' }}>
//                     Recent Videos Performance
//                   </h3>
                  
//                   {analytics.recent_videos && analytics.recent_videos.length > 0 ? (
//                     <div style={{ overflowX: 'auto' }}>
//                       <table style={{ 
//                         width: '100%', 
//                         borderCollapse: 'collapse', 
//                         fontSize: '14px' 
//                       }}>
//                         <thead>
//                           <tr style={{ background: '#f8f9fa' }}>
//                             <th style={{ 
//                               padding: '12px', 
//                               textAlign: 'left', 
//                               borderBottom: '2px solid #dee2e6' 
//                             }}>
//                               Title
//                             </th>
//                             <th style={{ 
//                               padding: '12px', 
//                               textAlign: 'center', 
//                               borderBottom: '2px solid #dee2e6' 
//                             }}>
//                               Views
//                             </th>
//                             <th style={{ 
//                               padding: '12px', 
//                               textAlign: 'center', 
//                               borderBottom: '2px solid #dee2e6' 
//                             }}>
//                               Likes
//                             </th>
//                             <th style={{ 
//                               padding: '12px', 
//                               textAlign: 'center', 
//                               borderBottom: '2px solid #dee2e6' 
//                             }}>
//                               Comments
//                             </th>
//                             <th style={{ 
//                               padding: '12px', 
//                               textAlign: 'center', 
//                               borderBottom: '2px solid #dee2e6' 
//                             }}>
//                               Published
//                             </th>
//                           </tr>
//                         </thead>
//                         <tbody>
//                           {analytics.recent_videos.map((video, index) => (
//                             <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
//                               <td style={{ padding: '12px', maxWidth: '300px' }}>
//                                 <div style={{ 
//                                   fontWeight: '600', 
//                                   color: '#333', 
//                                   marginBottom: '4px' 
//                                 }}>
//                                   {video.title.length > 50 ? 
//                                     video.title.substring(0, 50) + '...' : 
//                                     video.title
//                                   }
//                                 </div>
//                                 <div style={{ fontSize: '12px', color: '#666' }}>
//                                   ID: {video.video_id}
//                                 </div>
//                               </td>
//                               <td style={{ padding: '12px', textAlign: 'center' }}>
//                                 <span style={{ 
//                                   background: '#e3f2fd', 
//                                   color: '#1976d2', 
//                                   padding: '4px 8px', 
//                                   borderRadius: '12px', 
//                                   fontSize: '12px', 
//                                   fontWeight: '600' 
//                                 }}>
//                                   {parseInt(video.view_count).toLocaleString()}
//                                 </span>
//                               </td>
//                               <td style={{ padding: '12px', textAlign: 'center' }}>
//                                 <span style={{ 
//                                   background: '#e8f5e8', 
//                                   color: '#2e7d2e', 
//                                   padding: '4px 8px', 
//                                   borderRadius: '12px', 
//                                   fontSize: '12px', 
//                                   fontWeight: '600' 
//                                 }}>
//                                   {parseInt(video.like_count).toLocaleString()}
//                                 </span>
//                               </td>
//                               <td style={{ padding: '12px', textAlign: 'center' }}>
//                                 <span style={{ 
//                                   background: '#fff3e0', 
//                                   color: '#f57c00', 
//                                   padding: '4px 8px', 
//                                   borderRadius: '12px', 
//                                   fontSize: '12px', 
//                                   fontWeight: '600' 
//                                 }}>
//                                   {parseInt(video.comment_count).toLocaleString()}
//                                 </span>
//                               </td>
//                               <td style={{ 
//                                 padding: '12px', 
//                                 textAlign: 'center', 
//                                 fontSize: '12px', 
//                                 color: '#666' 
//                               }}>
//                                 {new Date(video.published_at).toLocaleDateString()}
//                               </td>
//                             </tr>
//                           ))}
//                         </tbody>
//                       </table>
//                     </div>
//                   ) : (
//                     <div style={{ 
//                       textAlign: 'center', 
//                       padding: '40px', 
//                       color: '#666' 
//                     }}>
//                       <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
//                       <p>No recent videos found. Upload some content to see analytics here!</p>
//                     </div>
//                   )}
//                 </div>
//               </div>
//             ) : (
//               <div style={{ 
//                 textAlign: 'center', 
//                 padding: '60px', 
//                 color: '#666' 
//               }}>
//                 <div style={{ fontSize: '64px', marginBottom: '20px' }}>📈</div>
//                 <h3 style={{ color: '#333', marginBottom: '16px' }}>Analytics Not Loaded</h3>
//                 <p style={{ marginBottom: '20px' }}>
//                   Click "Refresh Analytics" to load your channel's performance data.
//                 </p>
//                 <button 
//                   onClick={fetchAnalytics}
//                   style={{ 
//                     padding: '12px 24px', 
//                     background: '#FF0000', 
//                     color: 'white', 
//                     border: 'none', 
//                     borderRadius: '8px', 
//                     cursor: 'pointer', 
//                     fontWeight: '600',
//                     transition: 'background 0.3s ease'
//                   }}
//                 >
//                   Load Analytics
//                 </button>
//               </div>
//             )}
//           </div>
//         )}

//         {/* Not Connected Message for other tabs */}
//         {activeTab !== 'connect' && !status?.youtube_connected && (
//           <div style={{ 
//             background: 'rgba(255, 255, 255, 0.95)', 
//             borderRadius: '20px', 
//             padding: '40px', 
//             boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', 
//             textAlign: 'center' 
//           }}>
//             <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔗</div>
//             <h3 style={{ color: '#FF0000', marginBottom: '20px' }}>
//               YouTube Not Connected
//             </h3>
//             <p style={{ color: '#666', marginBottom: '30px' }}>
//               Please connect your YouTube channel first to access this feature.
//             </p>
//             <button 
//               onClick={() => setActiveTab('connect')} 
//               style={{ 
//                 padding: '12px 24px', 
//                 background: '#FF0000', 
//                 color: 'white', 
//                 border: 'none', 
//                 borderRadius: '8px', 
//                 cursor: 'pointer', 
//                 fontWeight: '600',
//                 fontSize: '16px',
//                 transition: 'background 0.3s ease'
//               }}
//             >
//               Connect YouTube Channel
//             </button>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default YouTubeAutomation;









  

