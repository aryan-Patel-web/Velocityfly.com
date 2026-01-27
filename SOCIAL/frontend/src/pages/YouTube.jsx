import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const YouTubeAutomation = () => {
  const [videoPreview, setVideoPreview] = useState(null);
  const { user, token, isAuthenticated, debugAuth } = useAuth();
  const [activeTab, setActiveTab] = useState('connect');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');
  
  const [config, setConfig] = useState({
    content_type: 'shorts',
    upload_schedule: ['09:00', '15:00', '21:00'],
    content_categories: ['Technology', 'Business', 'Education'],
    auto_generate_titles: true,
    auto_generate_descriptions: true,
    auto_add_tags: true,
    privacy_status: 'public',
    shorts_per_day: 3,
    videos_per_week: 2
  });
  
  const [contentData, setContentData] = useState({
    content_type: 'shorts',
    topic: '',
    target_audience: 'general',
    duration_seconds: 30,
    style: 'engaging',
    language: 'english',
    title: '',
    description: '',
    video_url: ''
  });

  const [generatedContent, setGeneratedContent] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [thumbnailOptions, setThumbnailOptions] = useState([]);
  const [selectedThumbnail, setSelectedThumbnail] = useState(null);
  const [generatingThumbnails, setGeneratingThumbnails] = useState(false);
  const [uploadMode, setUploadMode] = useState('new');
  const [existingVideoUrl, setExistingVideoUrl] = useState('');
  const [thumbnails, setThumbnails] = useState([]);
  const [showDisconnectModal, setShowDisconnectModal] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [disconnectError, setDisconnectError] = useState(null);
  const [scheduleMode, setScheduleMode] = useState(false);
  const [scheduledPosts, setScheduledPosts] = useState([]);
  
  // ✅ COMMENTS & VIDEOS STATE - KEEP ONLY ONCE
  const [comments, setComments] = useState([]);
  const [selectedVideoId, setSelectedVideoId] = useState('');
  const [userVideos, setUserVideos] = useState([]); // ✅ KEEP THIS ONE
  const [selectedVideos, setSelectedVideos] = useState([]); // ✅ ADD THIS
  const [replyText, setReplyText] = useState('');
  const [loadingVideos, setLoadingVideos] = useState(false);
  const [videoComments, setVideoComments] = useState({});
  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editText, setEditText] = useState('');
  
  const [autoReplyEnabled, setAutoReplyEnabled] = useState(false);
  const [autoReplyConfig, setAutoReplyConfig] = useState({
    reply_style: 'friendly',
    reply_delay_minutes: 5,
    custom_prompt: '',
    languages: ['english', 'hindi'],
    filter_spam: true,
    max_replies_per_hour: 10
  });



// Add these to your existing useState declarations
const [chinaConfig, setChinaConfig] = useState({
  niche: 'funny',
  show_captions: true,
  num_videos: 1
});
const [chinaGenerating, setChinaGenerating] = useState(false);
const [chinaProgress, setChinaProgress] = useState(0);
const [chinaResult, setChinaResult] = useState(null);
const [chinaNiches, setChinaNiches] = useState({});



// MrBeast Viral Shorts Generator State
const [mrBeastConfig, setMrBeastConfig] = useState({
  youtube_url: '',
  target_duration: 30,
  voice_type: 'male_energetic',
  num_videos: 3
});
const [mrBeastGenerating, setMrBeastGenerating] = useState(false);
const [mrBeastProgress, setMrBeastProgress] = useState(0);
const [mrBeastResult, setMrBeastResult] = useState(null);




  // Viral Pixel States
// At the TOP of your component (with other useState)
const [viralPixelConfig, setViralPixelConfig] = useState({
  niche: '',
  language: 'hindi',
  hd_quality: true,
  show_captions: true,
  channel_name: 'The LLM Labs'
});
const [viralPixelGenerating, setViralPixelGenerating] = useState(false);
const [viralPixelProgress, setViralPixelProgress] = useState(0);
const [viralPixelResult, setViralPixelResult] = useState(null);

  // Automation States
  const [automationEnabled, setAutomationEnabled] = useState(false);
  const [automationConfig, setAutomationConfig] = useState({
    max_posts_per_day: 200,
    upload_times: ['07:00', '13:00', '18:00'],
    base_url: 'https://www.flipkart.com',
    search_query: '',
    auto_scrape: true,
    auto_generate_video: true,
    auto_upload: true
  });
  const [testScheduleTime, setTestScheduleTime] = useState('');
  const [showTestScheduler, setShowTestScheduler] = useState(false);
  const [automationLogs, setAutomationLogs] = useState([]);
  const [loadingLogs, setLoadingLogs] = useState(false);

  // URL Management States
  const [scrapeUrl, setScrapeUrl] = useState('');
  const [savedUrl, setSavedUrl] = useState(null);
  const [urlStats, setUrlStats] = useState({ total: 0, processed: 0 });

  // Schedule Slots
  const [scheduleSlots, setScheduleSlots] = useState([
    { id: 1, video_url: '', title: '', description: '', date: '', time: '' },
    { id: 2, video_url: '', title: '', description: '', date: '', time: '' },
    { id: 3, video_url: '', title: '', description: '', date: '', time: '' }
  ]);
  
  // Slideshow States
  const [slideshowMode, setSlideshowMode] = useState(false);
  const [uploadedImages, setUploadedImages] = useState([]);
  const [slideshowConfig, setSlideshowConfig] = useState({
    duration_per_image: 2,
    transition: 'fade',
    music_style: 'upbeat',
    add_text: true,
    platforms: ['youtube_shorts']
  });
  const [generatedSlideshow, setGeneratedSlideshow] = useState(null);
  const [generatingSlideshow, setGeneratingSlideshow] = useState(false);
  const [uploadMethod, setUploadMethod] = useState('url');
  const [imageUrls, setImageUrls] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [videoUploadMode, setVideoUploadMode] = useState('new');
  const [existingVideoId, setExistingVideoId] = useState('');
  const [slideshowTab, setSlideshowTab] = useState('manual');
  const [productUrl, setProductUrl] = useState('');
  const [scrapedProduct, setScrapedProduct] = useState(null);
  const [slideshowTitle, setSlideshowTitle] = useState('');
  const [slideshowDescription, setSlideshowDescription] = useState('');
  const [slideshowResult, setSlideshowResult] = useState(null);
  const [addThumbnailOverlay, setAddThumbnailOverlay] = useState(true);
  const [customThumbnailPrompt, setCustomThumbnailPrompt] = useState('');

  const API_BASE = process.env.NODE_ENV === 'production' 
    ? (import.meta.env.VITE_API_URL || 'https://velocityfly.onrender.com')
    : (import.meta.env.VITE_API_URL || 'http://localhost:8000');

  const DEFAULT_IMAGE_URLS = `https://picsum.photos/1080/1920?random=1
https://picsum.photos/1080/1920?random=2
https://picsum.photos/1080/1920?random=3
https://picsum.photos/1080/1920?random=4`;

  // ... rest of your component code


// Line 62-114: getUserData (stays here)
const getUserData = useCallback(() => {
  if (user && user.user_id) {
    return user;
  }
  
  const possibleKeys = ['user', 'cached_user', 'auth_user'];
  for (const key of possibleKeys) {
    try {
      const storedUser = localStorage.getItem(key);
      if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        if (parsedUser && parsedUser.user_id) {
          return parsedUser;
        }
      }
    } catch (error) {
      console.warn(`Error parsing ${key} from localStorage:`, error);
    }
  }
  
  return null;
}, [user]);



/////// testing


const fetchAutomationStatus = useCallback(async (retryCount = 0) => {
  if (!token) {
    console.log('No token available for status fetch');
    return;
  }
  
  try {
    const userData = getUserData();
    
    if (!userData || !userData.user_id) {
      console.error('No user_id found for status fetch');
      setStatus({ youtube_connected: false });
      return;
    }
    
    console.log('Fetching status for user_id:', userData.user_id);
    
    const response = await fetch(`${API_BASE}/api/youtube/status/${userData.user_id}`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-User-ID': userData.user_id
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setStatus(data);
        if (data.youtube_automation?.config) {
          setConfig(prev => ({ ...prev, ...data.youtube_automation.config }));
        }
      }
    } else if (response.status === 404) {
      setStatus({ youtube_connected: false });
    } else if (response.status === 503 && retryCount < 3) {
      console.log(`Service unavailable, retrying... (${retryCount + 1}/3)`);
      setTimeout(() => fetchAutomationStatus(retryCount + 1), 2000);
    } else {
      throw new Error(`Status fetch failed: ${response.status}`);
    }
  } catch (error) {
    console.error('Status fetch failed:', error);
    setStatus({ youtube_connected: false });
    if (retryCount === 0) {
      setError('Failed to fetch YouTube connection status');
    }
  }
}, [token, getUserData, API_BASE]);


const fetchAnalytics = useCallback(async () => {
  if (!token) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    setLoading(true);
    
    const response = await fetch(`${API_BASE}/api/youtube/analytics/${userData.user_id}?days=30`, {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-User-ID': userData.user_id
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setAnalytics(data);
      }
    } else {
      console.error('Analytics fetch failed:', response.status);
    }
  } catch (error) {
    console.error('Analytics fetch failed:', error);
  } finally {
    setLoading(false);
  }
}, [token, getUserData, API_BASE]);




const fetchScheduledPosts = useCallback(async () => {
  if (!token) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/scheduled-posts/${userData.user_id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setScheduledPosts(data.scheduled_posts);
      }
    }
  } catch (error) {
    console.error('Failed to fetch scheduled posts:', error);
  }
}, [token, getUserData, API_BASE]);

  const generateContent = useCallback(async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    if (!contentData.topic) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/ai/generate-youtube-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
body: JSON.stringify({
  content_type: contentData.content_type,
  topic: contentData.topic,
  target_audience: contentData.target_audience,
  duration_seconds: contentData.duration_seconds,
  style: contentData.style,
  language: contentData.language || 'english',  // NEW
  region: 'india'  // NEW
})
      });
      
  const result = await response.json();

      if (!response.ok) {
  alert('❌ Failed: ' + (result.error || 'Unknown error'));
  return;
}

     if (result.success) {
      
      // if (result.success) {
        setGeneratedContent(result);
        setContentData(prev => ({
          ...prev,
          title: result.title || '',
          description: result.description || ''
        }));
        setError('');
      } else {
        setError(result.error || result.message || 'Content generation failed');
      }
    } catch (error) {
      setError('Content generation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [token, contentData, API_BASE]);






const uploadVideo = useCallback(async () => {
  if (!token) {
    setError('Authentication required');
    return;
  }

  if (!contentData.video_url || !contentData.title) {
    setError('Please provide video URL and title');
    return;
  }

  setLoading(true);
  setError('');
  
  try {
    const userData = getUserData();
    
    if (!userData || !userData.user_id) {
      setError('User ID not found. Please log in again.');
      return;
    }
    
    // ✅ VALIDATE THUMBNAIL
// Make sure thumbnail is being sent correctly
let thumbnailToSend = null;
if (selectedThumbnail?.url) {
  if (selectedThumbnail.url.startsWith('data:image')) {
    thumbnailToSend = selectedThumbnail.url;
    console.log('📤 Thumbnail size:', thumbnailToSend.length, 'chars');
    console.log('📤 Thumbnail preview:', thumbnailToSend.substring(0, 100));
  } else {
    console.warn('⚠️ Invalid thumbnail format:', selectedThumbnail.url.substring(0, 50));
  }
}
    
    const uploadPayload = {
      user_id: userData.user_id,
      content_type: contentData.content_type,
      title: contentData.title.trim(), // ✅ TRIM WHITESPACE
      description: contentData.description.trim(),
      video_url: contentData.video_url,
      thumbnail_url: thumbnailToSend
    };
    
    console.log('📦 Upload payload:', {
      ...uploadPayload,
      thumbnail_url: thumbnailToSend ? `${thumbnailToSend.substring(0, 50)}... (${thumbnailToSend.length} chars)` : 'null'
    });
    
    const response = await fetch(`${API_BASE}/api/youtube/upload`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-User-ID': userData.user_id
      },
      body: JSON.stringify(uploadPayload)
    });
    
    const result = await response.json();
    
    if (result.success) {
      const successMessage = result.thumbnail_uploaded 
        ? `✅ Video uploaded successfully with custom thumbnail!\n\nURL: ${result.video_url}`
        : `✅ Video uploaded successfully!\n\n⚠️ Thumbnail upload failed - you can add it manually later.\n\nURL: ${result.video_url}`;
      
      alert(successMessage);
      
      // Reset form
      setContentData(prev => ({ 
        ...prev, 
        title: '', 
        description: '', 
        video_url: '' 
      }));
      setThumbnailOptions([]);
      setSelectedThumbnail(null);
      
      await fetchAutomationStatus();
      if (analytics) fetchAnalytics();
      setError('');
    } else {
      setError(result.error || result.message || 'Upload failed');
    }
  } catch (error) {
    setError('Upload failed: ' + error.message);
    console.error('Upload error:', error);
  } finally {
    setLoading(false);
  }
}, [token, contentData, selectedThumbnail, getUserData, API_BASE, fetchAutomationStatus, analytics, fetchAnalytics]);

const scheduleVideos = useCallback(async () => {
  if (!token) {
    setError('Authentication required');
    return;
  }
  
  const userData = getUserData();
  if (!userData?.user_id) {
    setError('User ID not found');
    return;
  }
  
  setLoading(true);
  setError('');
  
  try {
    // Filter valid slots (must have video_url, title, date, time)
    const validSlots = scheduleSlots.filter(slot => 
      slot.video_url && slot.title && slot.date && slot.time
    );
    
    if (validSlots.length === 0) {
      setError('Please fill at least one schedule slot completely');
      setLoading(false);
      return;
    }
    
    // Schedule each video
    const results = await Promise.all(
      validSlots.map(slot => 
        fetch(`${API_BASE}/api/youtube/schedule-video`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            user_id: userData.user_id,
            schedule_date: slot.date,
            schedule_time: slot.time,
            video_data: {
              title: slot.title,
              description: slot.description || '',
              video_url: slot.video_url,
              content_type: contentData.content_type,
              thumbnail_url: selectedThumbnail?.url
            }
          })
        }).then(r => r.json())
      )
    );
    
    const successCount = results.filter(r => r.success).length;
    
    alert(`✅ ${successCount} video(s) scheduled successfully!`);
    
    // Reset schedule slots
    setScheduleSlots([
      { id: 1, video_url: '', title: '', description: '', date: '', time: '' },
      { id: 2, video_url: '', title: '', description: '', date: '', time: '' },
      { id: 3, video_url: '', title: '', description: '', date: '', time: '' }
    ]);
    
    // Refresh scheduled posts list
    await fetchScheduledPosts();
    
  } catch (error) {
    setError('Scheduling failed: ' + error.message);
  } finally {
    setLoading(false);
  }
}, [token, scheduleSlots, contentData.content_type, selectedThumbnail, getUserData, API_BASE, fetchScheduledPosts]);

const deleteScheduledPost = useCallback(async (postId) => {
  if (!confirm('Delete this scheduled post?')) return;
  
  try {
    const response = await fetch(`${API_BASE}/api/youtube/scheduled-post/${postId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      alert('Scheduled post deleted');
      await fetchScheduledPosts();
    }
  } catch (error) {
    console.error('Delete failed:', error);
  }
}, [token, API_BASE, fetchScheduledPosts]);


const fetchUserVideos = useCallback(async () => {
  if (!token) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    setLoadingVideos(true);
    
    const response = await fetch(`${API_BASE}/api/youtube/user-videos/${userData.user_id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setUserVideos(data.videos);
      }
    }
  } catch (error) {
    console.error('Failed to fetch videos:', error);
  } finally {
    setLoadingVideos(false);
  }
}, [token, API_BASE, getUserData]);

const fetchVideoComments = useCallback(async (videoId) => {
  if (!token) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/comments/${userData.user_id}?video_id=${videoId}&max_results=20`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setVideoComments(prev => ({
          ...prev,
          [videoId]: data.comments
        }));
      }
    }
  } catch (error) {
    console.error('Failed to fetch video comments:', error);
  }
}, [token, API_BASE, getUserData]);

const startAutoReplyForSelectedVideos = useCallback(async () => {
  if (selectedVideos.length === 0) {
    alert('Please select at least one video for auto-reply');
    return;
  }
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/start-auto-reply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        selected_videos: selectedVideos,
        config: {
          ...autoReplyConfig,
          timezone: 'Asia/Kolkata' // IST timezone
        }
      })
    });
    
    if (response.ok) {
      setAutoReplyEnabled(true);
      alert(`✅ Auto-reply started for ${selectedVideos.length} video(s)!`);
    }
  } catch (error) {
    console.error('Failed to start auto replies:', error);
  }
}, [token, API_BASE, autoReplyConfig, selectedVideos, getUserData]);



// Comments management functions
const fetchComments = useCallback(async (videoId = '') => {
  if (!token) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    setLoading(true);
    
    const url = videoId 
      ? `${API_BASE}/api/youtube/comments/${userData.user_id}?video_id=${videoId}`
      : `${API_BASE}/api/youtube/comments/${userData.user_id}`;
    
    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setComments(data.comments);
      }
    }
  } catch (error) {
    console.error('Failed to fetch comments:', error);
  } finally {
    setLoading(false);
  }
}, [token, API_BASE]);

const replyToComment = useCallback(async (commentId, replyText) => {
  if (!token || !replyText.trim()) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/reply-comment`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        comment_id: commentId,
        reply_text: replyText
      })
    });
    
    if (response.ok) {
      alert('Reply posted successfully!');
      setReplyText('');
      await fetchComments(selectedVideoId);
    }
  } catch (error) {
    console.error('Reply failed:', error);
    alert('Failed to post reply');
  }
}, [token, API_BASE, selectedVideoId, fetchComments]);








// const generateAutoReply = useCallback(async (commentText, commentId) => {
//   if (!token) return;
  
//   try {
//     const userData = getUserData();
//     if (!userData?.user_id) return;
    
//     const response = await fetch(`${API_BASE}/api/youtube/generate-auto-reply`, {
//       method: 'POST',
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': `Bearer ${token}`
//       },
//       body: JSON.stringify({
//         user_id: userData.user_id,
//         comment_text: commentText,
//         reply_style: autoReplyConfig.reply_style
//       })
//     });
    
//     const result = await response.json();
    
//     if (result.success) {
//       // Auto-post the reply
//       await replyToComment(commentId, result.reply);
//     }
//   } catch (error) {
//     console.error('Auto reply failed:', error);
//   }
// }, [token, API_BASE, autoReplyConfig.reply_style, replyToComment]);


const generateAutoReply = useCallback(async (commentText, commentId, videoTitle = '') => {
  if (!token) return;
  

  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    console.log('🤖 Generating smart reply for:', commentText);
    
    // Use NEW smart auto-reply endpoint
    const response = await fetch(`${API_BASE}/api/youtube/smart-auto-reply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        comment_text: commentText,
        video_title: videoTitle || contentData.title || '',
        video_description: contentData.description || '',
        reply_style: autoReplyConfig.reply_style
      })
    });
    
    const result = await response.json();
    console.log('📥 Smart reply result:', result);
    
    if (result.success && result.reply) {
      // Auto-post the smart reply
      await replyToComment(commentId, result.reply);
      
      // Show notification
      alert(`✅ Smart reply posted!\n\nIntent: ${result.intent}\nReply: ${result.reply.substring(0, 100)}...`);
    } else {
      console.error('Smart reply failed:', result.error);
    }
  } catch (error) {
    console.error('❌ Auto reply failed:', error);
  }
}, [token, API_BASE, autoReplyConfig.reply_style, replyToComment, contentData.title, contentData.description]);



const startAutomatedReplies = useCallback(async () => {
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/start-auto-reply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        config: autoReplyConfig
      })
    });
    
    if (response.ok) {
      setAutoReplyEnabled(true);
      alert('✅ Automated replies started! Comments will be replied to automatically.');
    }
  } catch (error) {
    console.error('Failed to start auto replies:', error);
  }
}, [token, API_BASE, autoReplyConfig, getUserData]);

const stopAutomatedReplies = useCallback(async () => {
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    const response = await fetch(`${API_BASE}/api/youtube/stop-auto-reply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userData.user_id
      })
    });
    
    if (response.ok) {
      setAutoReplyEnabled(false);
      alert('⏹️ Automated replies stopped.');
    }
  } catch (error) {
    console.error('Failed to stop auto replies:', error);
  }
}, [token, API_BASE, getUserData]);

const deleteComment = useCallback(async (commentId) => {
  if (!confirm('Delete this comment/reply?')) return;
  
  try {
    const userData = getUserData();
    if (!userData?.user_id) return;
    
    // Check if it's our reply or original comment
    const isReply = commentId.includes('reply');
    const endpoint = isReply 
      ? `${API_BASE}/api/youtube/delete-reply/${commentId}?user_id=${userData.user_id}`
      : `${API_BASE}/api/youtube/delete-comment/${commentId}?user_id=${userData.user_id}`;
    
    const response = await fetch(endpoint, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (response.ok) {
      alert(isReply ? 'Reply deleted' : 'Comment deleted');
      await fetchComments(selectedVideoId);
    }
  } catch (error) {
    console.error('Delete failed:', error);
  }
}, [token, API_BASE, selectedVideoId, fetchComments, getUserData]);
// Add these functions before your return statement

  const generateCommunityPost = useCallback(async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/ai/generate-community-post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          post_type: contentData.post_type || 'text',
          topic: contentData.topic || 'general',
          target_audience: contentData.target_audience || 'general'
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setContentData(prev => ({
          ...prev,
          post_content: result.content || result.post_content || '',
          option_0: result.options?.[0] || '',
          option_1: result.options?.[1] || '',
          option_2: result.options?.[2] || '',
          option_3: result.options?.[3] || ''
        }));
        setError('');
      } else {
        setError(result.error || 'Failed to generate post');
      }
    } catch (error) {
      setError('Post generation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [token, contentData.post_type, contentData.topic, contentData.target_audience, API_BASE]);







  const publishCommunityPost = useCallback(async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    if (!contentData.post_content) {
      setError('Please enter post content');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const userData = getUserData();
      
      if (!userData?.user_id) {
        setError('User ID not found. Please log in again.');
        return;
      }
      
      const postData = {
        user_id: userData.user_id,
        post_type: contentData.post_type || 'text',
        content: contentData.post_content,
        image_url: contentData.image_url || null,
        options: [
          contentData.option_0 || null,
          contentData.option_1 || null,
          contentData.option_2 || null,
          contentData.option_3 || null
        ].filter(Boolean),
        correct_answer: contentData.correct_answer || null,
        schedule_date: contentData.auto_schedule ? contentData.schedule_date : null,
        schedule_time: contentData.auto_schedule ? contentData.schedule_time : null
      };
      
      const response = await fetch(`${API_BASE}/api/youtube/community-post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userData.user_id
        },
        body: JSON.stringify(postData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Community post ${contentData.auto_schedule ? 'scheduled' : 'published'} successfully!`);
        setContentData(prev => ({ 
          ...prev, 
          post_content: '',
          image_url: '',
          option_0: '',
          option_1: '',
          option_2: '',
          option_3: '',
          auto_schedule: false,
          schedule_date: '',
          schedule_time: ''
        }));
        setError('');
      } else {
        setError(result.error || 'Failed to publish post');
      }
    } catch (error) {
      setError('Publishing failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [token, contentData, getUserData, API_BASE]);

















const handleOAuthCallbackDirect = useCallback(async (code) => {
  try {
    setLoading(true);
    setError('');
    
    console.log('Processing OAuth callback with code:', code.substring(0, 20) + '...');
    
    let userData = getUserData();
    let currentToken = token;
    
    if (!userData) {
      const possibleTokenKeys = ['token', 'auth_token', 'access_token', 'authToken'];
      for (const key of possibleTokenKeys) {
        const storedToken = localStorage.getItem(key);
        if (storedToken) {
          currentToken = storedToken;
          break;
        }
      }
      userData = getUserData();
    }
    
    if (!userData || !userData.user_id) {
      throw new Error('User authentication required. Please log in first.');
    }
    
    if (!currentToken) {
      throw new Error('Authentication token not found. Please log in again.');
    }
    
    const currentOrigin = window.location.origin;
    const redirectUri = `${currentOrigin}/youtube`;
    
    console.log('Making OAuth callback request for user:', userData.user_id);
    
    const response = await fetch(`${API_BASE}/api/youtube/oauth-callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${currentToken}`,
        'X-User-ID': userData.user_id
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        code: code,
        redirect_uri: redirectUri
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Network error' }));
      throw new Error(`OAuth callback failed: ${errorData.error || response.statusText}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      // Clear URL parameters AFTER successful processing
      window.history.replaceState({}, document.title, window.location.pathname);
      
      setError('');
      setStatus(prev => ({ ...prev, youtube_connected: true, ...result }));
      setActiveTab('setup');
      
      await fetchAutomationStatus();
      console.log('YouTube connected successfully - redirecting to setup');
    } else {
      throw new Error(result.error || result.message || 'YouTube connection failed');
    }
  } catch (error) {
    // Clear URL on error too
    window.history.replaceState({}, document.title, window.location.pathname);
    console.error('OAuth callback error:', error);
    setError(error.message);
  } finally {
    setLoading(false);
  }
}, [getUserData, token, API_BASE, fetchAutomationStatus]);


// ✅ Disconnect YouTube Handler
const handleDisconnectYouTube = async () => {
  setDisconnecting(true);
  setDisconnectError(null);

  try {
    const userId = localStorage.getItem('user_id');
    const token = localStorage.getItem('token');

    if (!userId) {
      throw new Error('User ID not found. Please log in again.');
    }

    console.log('🔴 Disconnecting YouTube for user:', userId);

    const response = await axios.post(
      `${API_URL}/api/youtube/disconnect/${userId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    console.log('✅ Disconnect response:', response.data);

    if (response.data.success) {
      // Show success message
      alert(`✅ ${response.data.message}\n\n${response.data.action || ''}`);
      
      // Close modal
      setShowDisconnectModal(false);
      
      // Refresh status
      await fetchYouTubeStatus();
      
      // Reset to connect tab
      setActiveTab('connect');
      
      console.log('✅ YouTube disconnected successfully');
    } else {
      throw new Error(response.data.error || 'Disconnect failed');
    }
  } catch (error) {
    console.error('❌ Disconnect error:', error);
    
    const errorMessage = error.response?.data?.detail 
      || error.response?.data?.error 
      || error.message 
      || 'Failed to disconnect YouTube';
    
    setDisconnectError(errorMessage);
  } finally {
    setDisconnecting(false);
  }
};



useEffect(() => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  const state = urlParams.get('state');
  const error_param = urlParams.get('error');
  
  console.log('YouTube useEffect - URL params:', { 
    code: code ? code.substring(0, 20) + '...' : null, 
    state, 
    error: error_param,
    fullURL: window.location.href
  });
  console.log('YouTube useEffect - Auth state:', { isAuthenticated, hasToken: !!token });
  
  if (error_param) {
    console.error('OAuth error detected:', error_param);
    setError(`OAuth error: ${error_param}`);
    window.history.replaceState({}, document.title, window.location.pathname);
    return;
  }
  
  if (code && state === 'youtube_oauth') {
    console.log('✅ OAuth callback detected - processing code:', code.substring(0, 20) + '...');
    handleOAuthCallbackDirect(code);
    return;
  }
  
  // Normal initialization
  if (isAuthenticated && token) {
    console.log('Normal initialization - fetching status');
    fetchAutomationStatus();
    fetchScheduledPosts();  // NEW: Load scheduled posts
  } else {
    console.log('Waiting for authentication...');
  }
}, [isAuthenticated, token, handleOAuthCallbackDirect]);

// }, [isAuthenticated, token, handleOAuthCallbackDirect]);
// NEW: Load saved automation config
useEffect(() => {
  const loadAutomationConfig = async () => {
    if (!user?.user_id || !token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/automation/config/${user.user_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.config) {
          setAutomationConfig(data.config);
          setAutomationEnabled(data.config.enabled || false);
          
          // If has base_url and search_query, set as savedUrl too
          if (data.config.base_url && data.config.search_query) {
            setSavedUrl(`${data.config.base_url} | Search: ${data.config.search_query}`);
          }
        }
      }
    } catch (error) {
      console.error('Failed to load automation config:', error);
    }
  };
  
  loadAutomationConfig();
}, [user, token]);


// ✅ VIRAL PIXEL useEffect (Add this with your other useEffects)
useEffect(() => {
  // Load available niches from backend (optional - if your API supports it)
  // You can remove this if you're using hardcoded niches
  const loadViralPixelData = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/viral-pixel/niches`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await response.json();
      if (data.success) {
        console.log('Viral Pixel niches loaded successfully');
      }
    } catch (error) {
      console.error('Failed to load Viral Pixel niches:', error);
    }
  };

  if (status?.youtube_connected) {
    loadViralPixelData();
  }
}, [API_BASE, token, status]);

// ✅ Load automation config on mount
useEffect(() => {
  const loadAutomationConfig = async () => {
    if (!user?.user_id || !token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/automation/config/${user.user_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.config) {
          setAutomationConfig(prev => ({
            ...prev,
            ...data.config
          }));
          setAutomationEnabled(data.config.enabled || false);
          console.log('✅ Loaded automation config:', data.config);
        }
      }
    } catch (error) {
      console.error('Failed to load automation config:', error);
    }
  };
  
  loadAutomationConfig();
}, [user, token]);

// ✅ Load automation config on mount
useEffect(() => {
  const loadAutomationConfig = async () => {
    if (!user?.user_id || !token) return;
    
    try {
      console.log('📥 Loading automation config...');
      
      const response = await fetch(`${API_BASE}/api/automation/config/${user.user_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success && data.config) {
          console.log('✅ Config loaded:', data.config);
          
          setAutomationConfig({
            base_url: data.config.base_url || 'https://www.flipkart.com',
            search_query: data.config.search_query || '',
            upload_times: Array.isArray(data.config.upload_times) ? data.config.upload_times : ['07:00', '13:00', '18:00'],
            max_posts_per_day: data.config.max_posts_per_day || 200,
            auto_scrape: data.config.auto_scrape !== false,
            auto_generate_video: data.config.auto_generate_video !== false,
            auto_upload: data.config.auto_upload !== false
          });
          
          setAutomationEnabled(data.config.enabled === true);
        }
      }
    } catch (error) {
      console.error('Failed to load automation config:', error);
    }
  };
  
  loadAutomationConfig();
}, [user, token]);

// ✅ Load activity logs
useEffect(() => {
  const loadLogs = async () => {
    if (!user?.user_id || !token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/automation/logs/${user.user_id}?limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAutomationLogs(data.logs || []);
        }
      }
    } catch (error) {
      console.error('Failed to load logs:', error);
    }
  };
  
  loadLogs();
  
  // Refresh logs every 30 seconds
  const interval = setInterval(loadLogs, 30000);
  return () => clearInterval(interval);
}, [user, token]);

// ✅ NEW: Load saved URL on component mount
useEffect(() => {
  const loadSavedUrl = async () => {
    if (!user?.user_id) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/automation/get-url/${user.user_id}`);
      const data = await response.json();
      
      if (data.success && data.url) {
        setSavedUrl(data.url);
        setUrlStats({
          total: data.total_products || 0,
          processed: data.products_processed || 0
        });
      }
    } catch (error) {
      console.error('Failed to load saved URL:', error);
    }
  };
  
  loadSavedUrl();
}, [user]);


// PART 2: ADD THIS useEffect TO FETCH NICHES (after other useEffects)
// ============================================================================

useEffect(() => {
  // Fetch available niches on component mount
  const fetchNiches = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/china/niches`);
      const data = await response.json();
      
      if (data.success) {
        setChinaNiches(data.niches);
        console.log('✅ China niches loaded:', Object.keys(data.niches).length);
      }
    } catch (error) {
      console.error('Failed to fetch niches:', error);
    }
  };
  
  fetchNiches();
}, []);

  // const generateOAuthUrl = useCallback(async () => {

  const generateOAuthUrl = useCallback(async () => {
    if (!token) {
      setError('Please login first');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const userData = getUserData();
      
      if (!userData || !userData.user_id) {
        throw new Error('User ID not found. Please log in again.');
      }

      console.log('Generating OAuth URL for user_id:', userData.user_id);
      
      const requestPayload = {
        user_id: userData.user_id,
        state: 'youtube_oauth',
        redirect_uri: `${window.location.origin}/youtube`
      };
      
      const response = await fetch(`${API_BASE}/api/youtube/oauth-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userData.user_id
        },
        body: JSON.stringify(requestPayload)
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Network error' }));
        throw new Error(`HTTP ${response.status}: ${errorData.error || response.statusText}`);
      }
      
      const result = await response.json();
      
      if (result.success && result.authorization_url) {
        window.location.href = result.authorization_url;
      } else {
        throw new Error(result.error || result.message || 'Failed to generate OAuth URL');
      }
    } catch (error) {
      console.error('OAuth URL generation failed:', error);
      setError('Connection error: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [token, getUserData, API_BASE]);

  const setupYouTubeAutomation = useCallback(async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const userData = getUserData();
      
      if (!userData || !userData.user_id) {
        throw new Error('User ID not found. Please log in again.');
      }
      
      const response = await fetch(`${API_BASE}/api/youtube/setup-automation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
          'X-User-ID': userData.user_id
        },
        body: JSON.stringify({
          user_id: userData.user_id,
          config: config
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Network error' }));
        throw new Error(errorData.error || 'Setup failed');
      }
      
      const result = await response.json();
      
      if (result.success) {
        setError('');
        await fetchAutomationStatus();
        setActiveTab('dashboard');
      } else {
        throw new Error(result.error || result.message || 'Setup failed');
      }
    } catch (error) {
      console.error('Automation setup failed:', error);
      setError('Setup failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  }, [token, getUserData, config, API_BASE, fetchAutomationStatus]);

  const TabButton = ({ id, label, emoji, active, onClick }) => (
    <button 
      onClick={onClick} 
      style={{ 
        padding: '12px 24px', 
        background: active ? '#FF0000' : 'transparent', 
        color: active ? 'white' : '#FF0000', 
        border: '2px solid #FF0000', 
        borderRadius: '12px', 
        cursor: 'pointer', 
        fontWeight: '600', 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px', 
        fontSize: '14px',
        transition: 'all 0.3s ease'
      }}
    >
      <span>{emoji}</span>{label}
    </button>
  );

  const StatusCard = ({ title, value, color = '#FF0000' }) => (
    <div style={{ 
      background: 'white', 
      borderRadius: '12px', 
      padding: '20px', 
      textAlign: 'center', 
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)', 
      border: `2px solid ${color}` 
    }}>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>{value}</div>
      <div style={{ fontSize: '14px', color: '#666' }}>{title}</div>
    </div>
  );

  if (!isAuthenticated || !token) {
    return (
      <div style={{ 
        minHeight: '100vh', 
        background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        padding: '20px' 
      }}>
        <div style={{ 
          background: 'rgba(255, 255, 255, 0.95)', 
          borderRadius: '20px', 
          padding: '40px', 
          textAlign: 'center', 
          maxWidth: '500px' 
        }}>
          <h2 style={{ color: '#FF0000', marginBottom: '16px' }}>Authentication Required</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Please log in to access YouTube automation features.
          </p>
          <a 
            href="/login" 
            style={{ 
              padding: '12px 24px', 
              background: '#FF0000', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: '8px', 
              fontWeight: '600' 
            }}
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (




<div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', 
      padding: '20px' 
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
          <h1 style={{ 
            fontSize: '48px', 
            fontWeight: '700', 
            marginBottom: '16px', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            gap: '16px' 
          }}>
            <span style={{ fontSize: '56px' }}>📺</span>YouTube Automation Studio
          </h1>
          <p style={{ 
            fontSize: '20px', 
            opacity: 0.9, 
            maxWidth: '800px', 
            margin: '0 auto' 
          }}>
            Automate your YouTube channel with AI-generated content, smart scheduling, and analytics tracking
          </p>
          {user && (
            <p style={{ fontSize: '16px', opacity: 0.8, marginTop: '10px' }}>
              Welcome, {user.name} ({user.email})
            </p>
          )}
        </div>

        {/* Error Display */}
        {error && (
          <div style={{ 
            background: '#fee', 
            border: '1px solid #fcc', 
            borderRadius: '12px', 
            padding: '16px', 
            marginBottom: '20px', 
            color: '#c33', 
            textAlign: 'center' 
          }}>
            <strong>Error:</strong> {error}
            <button 
              onClick={() => setError('')} 
              style={{ 
                marginLeft: '10px', 
                background: 'none', 
                border: 'none', 
                color: '#c33', 
                cursor: 'pointer', 
                fontSize: '16px' 
              }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Navigation Tabs */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: '16px', 
          marginBottom: '40px', 
          flexWrap: 'wrap' 
        }}>
          <TabButton 
            id="connect" 
            label="Connect YouTube" 
            emoji="🔗" 
            active={activeTab === 'connect'} 
            onClick={() => setActiveTab('connect')} 
          />
          <TabButton 
            id="setup" 
            label="Setup Automation" 
            emoji="⚙️" 
            active={activeTab === 'setup'} 
            onClick={() => setActiveTab('setup')} 
          />
          <TabButton 
            id="content" 
            label="Create Content" 
            emoji="🎬" 
            active={activeTab === 'content'} 
            onClick={() => setActiveTab('content')} 
          />
          <TabButton 
            id="dashboard" 
            label="Dashboard" 
            emoji="📊" 
            active={activeTab === 'dashboard'} 
            onClick={() => setActiveTab('dashboard')} 
          />
          <TabButton 
            id="analytics" 
            label="Analytics" 
            emoji="📈" 
            active={activeTab === 'analytics'} 
            onClick={() => setActiveTab('analytics')} 
          />

          <TabButton 
  id="comments" 
  label="Comments" 
  emoji="💬" 
  active={activeTab === 'comments'} 
  onClick={() => setActiveTab('comments')} 
/>
<TabButton 
  id="slideshow" 
  label="Image Slideshow" 
  emoji="🎬" 
  active={activeTab === 'slideshow'} 
  onClick={() => setActiveTab('slideshow')} 
/>

<TabButton 
  id="automation" 
  label="Automation" 
  emoji="🤖" 
  active={activeTab === 'automation'} 
  onClick={() => setActiveTab('automation')} 
/>


{/* <TabButton 
  id="viral-pixabay" 
  label="Viral Pixel" 
  emoji="🎬" 
  active={activeTab === 'viral-pixel'} 
  onClick={() => setActiveTab('viral-pixel')} 
/> */}

<button 
  onClick={() => setActiveTab('viral-pixel')}
  style={{
    padding: '12px 24px',
    background: activeTab === 'viral-pixel' 
      ? 'linear-gradient(135deg, #667eea, #764ba2)' 
      : 'white',
    color: activeTab === 'viral-pixel' ? 'white' : '#333',
    border: activeTab === 'viral-pixel' ? 'none' : '2px solid #e0e0e0',
    borderRadius: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    boxShadow: activeTab === 'viral-pixel' 
      ? '0 4px 15px rgba(102,126,234,0.4)' 
      : '0 2px 8px rgba(0,0,0,0.1)'
  }}
>
  <span style={{ fontSize: '20px' }}>🎬</span>
  Viral Pixel
</button>

<button 
  onClick={() => setActiveTab('mrbeast-shorts')}
  style={{
    padding: '12px 24px',
    background: activeTab === 'mrbeast-shorts' 
      ? 'linear-gradient(135deg, #f093fb, #f5576c)' 
      : 'white',
    color: activeTab === 'mrbeast-shorts' ? 'white' : '#333',
    border: activeTab === 'mrbeast-shorts' ? 'none' : '2px solid #e0e0e0',
    borderRadius: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    boxShadow: activeTab === 'mrbeast-shorts' 
      ? '0 4px 15px rgba(240,147,251,0.4)' 
      : '0 2px 8px rgba(0,0,0,0.1)'
  }}
>
  <span style={{ fontSize: '20px' }}>🔥</span>
  MrBeast Shorts
</button>




<button 
  onClick={() => setActiveTab('china-automation')}
  style={{
    padding: '12px 24px',
    background: activeTab === 'china-automation' 
      ? 'linear-gradient(135deg, #FF6B6B, #FF8E53)' 
      : 'white',
    color: activeTab === 'china-automation' ? 'white' : '#333',
    border: activeTab === 'china-automation' ? 'none' : '2px solid #e0e0e0',
    borderRadius: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    boxShadow: activeTab === 'china-automation' 
      ? '0 4px 15px rgba(255,107,107,0.4)' 
      : '0 2px 8px rgba(0,0,0,0.1)'
  }}
>
  <span style={{ fontSize: '20px' }}>🇨🇳</span>
  China Videos
</button>



</div>

 {/* Connect YouTube Tab */}

{/* Connect YouTube Tab */}
{activeTab === 'connect' && (
  <div style={{ 
    background: 'rgba(255, 255, 255, 0.95)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
  }}>
    <h2 style={{ 
      color: '#FF0000', 
      marginBottom: '30px', 
      fontSize: '28px', 
      fontWeight: '700' 
    }}>
      Connect Your YouTube Channel
    </h2>
    
    <div style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ marginBottom: '30px' }}>
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>📺</div>
        <h3 style={{ color: '#333', marginBottom: '16px' }}>
          {status?.youtube_connected ? 'YouTube Connected!' : 'Connect to Get Started'}
        </h3>
        <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '30px' }}>
          {status?.youtube_connected 
            ? 'Your YouTube channel is connected and ready for automation.' 
            : 'Connect your YouTube channel to start automating content creation and uploads.'}
        </p>
      </div>

      {status?.youtube_connected ? (
        <div>
          {/* ✅ CONNECTED STATE */}
          <div style={{ 
            background: '#d4edda', 
            border: '2px solid #28a745', 
            borderRadius: '12px', 
            padding: '24px', 
            marginBottom: '20px', 
            color: '#155724' 
          }}>
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>✅</div>
            <h4 style={{ margin: '0 0 12px 0', fontSize: '20px', fontWeight: '700' }}>
              Connected Successfully
            </h4>
            <p style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: '600' }}>
              Channel: <span style={{ color: '#0a3622' }}>
                {status.channel_info?.channel_name || 'YouTube Channel'}
              </span>
            </p>
            <p style={{ margin: 0, fontSize: '13px', color: '#155724' }}>
              ✓ Ready for automation • ✓ Uploads enabled • ✓ API active
            </p>
            
            {/* Action Buttons */}
            <div style={{ 
              display: 'flex', 
              gap: '12px', 
              marginTop: '20px',
              justifyContent: 'center',
              flexWrap: 'wrap'
            }}>
              <button 
                onClick={() => setActiveTab('setup')} 
                style={{ 
                  padding: '12px 24px', 
                  background: '#28a745', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '8px', 
                  cursor: 'pointer', 
                  fontWeight: '600',
                  fontSize: '15px',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#218838'}
                onMouseOut={(e) => e.currentTarget.style.background = '#28a745'}
              >
                Continue to Setup →
              </button>
              
              {/* 🔴 DISCONNECT BUTTON */}
              <button 
                onClick={() => setShowDisconnectModal(true)}
                style={{ 
                  padding: '12px 24px', 
                  background: '#dc3545', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '8px', 
                  cursor: 'pointer', 
                  fontWeight: '600',
                  fontSize: '15px',
                  transition: 'all 0.3s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#c82333'}
                onMouseOut={(e) => e.currentTarget.style.background = '#dc3545'}
              >
                🔴 Disconnect
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div>
          {/* ❌ NOT CONNECTED STATE */}
          <button
            onClick={generateOAuthUrl}
            disabled={loading}
            style={{
              padding: '16px 32px',
              background: loading ? '#ccc' : '#FF0000',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: '700',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'background 0.3s ease'
            }}
          >
            {loading ? '⏳ Connecting...' : '🔗 Connect YouTube Channel'}
          </button>
        </div>
      )}

      <div style={{ 
        marginTop: '30px', 
        padding: '20px', 
        background: '#f8f9fa', 
        borderRadius: '12px', 
        fontSize: '14px', 
        color: '#666' 
      }}>
        <h4 style={{ color: '#333', marginBottom: '12px' }}>📋 What happens next:</h4>
        <ol style={{ textAlign: 'left', paddingLeft: '20px', lineHeight: '1.8' }}>
          <li>You'll be redirected to Google's secure authentication page</li>
          <li>Sign in to your Google account that owns the YouTube channel</li>
          <li>Grant permissions for YouTube channel management</li>
          <li>You'll be redirected back here with confirmation</li>
        </ol>
      </div>
    </div>
  </div>
)}

{/* 🔴 DISCONNECT CONFIRMATION MODAL */}
{showDisconnectModal && (
  <div
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999,
      backdropFilter: 'blur(4px)'
    }}
    onClick={() => !disconnecting && setShowDisconnectModal(false)}
  >
    <div
      style={{
        background: 'white',
        padding: '40px',
        borderRadius: '20px',
        maxWidth: '550px',
        width: '90%',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)'
      }}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Warning Icon */}
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <div style={{ fontSize: '72px', lineHeight: 1 }}>⚠️</div>
      </div>

      {/* Title */}
      <h2 style={{ 
        textAlign: 'center', 
        marginBottom: '20px', 
        color: '#dc3545',
        fontSize: '24px',
        fontWeight: '700'
      }}>
        Disconnect YouTube Account?
      </h2>

      {/* Channel Info */}
      <div style={{
        background: 'linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%)',
        padding: '20px',
        borderRadius: '12px',
        marginBottom: '24px',
        border: '2px solid #ffc107',
        textAlign: 'center'
      }}>
        <p style={{ 
          margin: 0, 
          fontWeight: '700', 
          color: '#856404',
          fontSize: '16px'
        }}>
          📺 Channel: {status?.channel_info?.channel_name || 'Your Channel'}
        </p>
      </div>

      {/* Warning Text */}
      <div style={{ 
        marginBottom: '28px', 
        color: '#495057', 
        lineHeight: '1.7',
        fontSize: '15px'
      }}>
        <p style={{ fontWeight: '700', marginBottom: '12px', color: '#212529' }}>
          This action will:
        </p>
        <ul style={{ 
          paddingLeft: '24px', 
          margin: '0 0 16px 0',
          listStyleType: 'none'
        }}>
          <li style={{ marginBottom: '8px' }}>
            <span style={{ color: '#28a745', marginRight: '8px' }}>✓</span>
            Revoke YouTube access tokens
          </li>
          <li style={{ marginBottom: '8px' }}>
            <span style={{ color: '#28a745', marginRight: '8px' }}>✓</span>
            Stop all active automations
          </li>
          <li style={{ marginBottom: '8px' }}>
            <span style={{ color: '#28a745', marginRight: '8px' }}>✓</span>
            Delete scheduled posts
          </li>
          <li style={{ marginBottom: '8px' }}>
            <span style={{ color: '#28a745', marginRight: '8px' }}>✓</span>
            Remove channel connection
          </li>
        </ul>
        <div style={{ 
          background: '#f8d7da', 
          border: '1px solid #f5c6cb',
          borderRadius: '8px',
          padding: '12px',
          marginTop: '16px'
        }}>
          <p style={{ 
            color: '#721c24', 
            fontWeight: '700', 
            margin: 0,
            fontSize: '14px'
          }}>
            ⚠️ You can reconnect anytime with fresh tokens
          </p>
        </div>
      </div>

      {/* Error Display */}
      {disconnectError && (
        <div style={{
          background: '#f8d7da',
          color: '#721c24',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '20px',
          fontSize: '14px',
          border: '1px solid #f5c6cb'
        }}>
          <strong>❌ Error:</strong> {disconnectError}
        </div>
      )}

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <button
          onClick={() => setShowDisconnectModal(false)}
          disabled={disconnecting}
          style={{
            flex: 1,
            padding: '14px',
            borderRadius: '10px',
            border: '2px solid #dee2e6',
            background: 'white',
            cursor: disconnecting ? 'not-allowed' : 'pointer',
            fontSize: '15px',
            fontWeight: '700',
            color: '#495057',
            transition: 'all 0.2s ease'
          }}
        >
          Cancel
        </button>
        <button
          onClick={handleDisconnectYouTube}
          disabled={disconnecting}
          style={{
            flex: 1,
            padding: '14px',
            borderRadius: '10px',
            border: 'none',
            background: disconnecting 
              ? 'linear-gradient(135deg, #6c757d 0%, #495057 100%)' 
              : 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)',
            color: 'white',
            cursor: disconnecting ? 'not-allowed' : 'pointer',
            fontSize: '15px',
            fontWeight: '700',
            transition: 'all 0.2s ease',
            boxShadow: disconnecting ? 'none' : '0 4px 12px rgba(220, 53, 69, 0.3)'
          }}
        >
          {disconnecting ? '⏳ Disconnecting...' : '🔴 Yes, Disconnect'}
        </button>
      </div>
    </div>
  </div>
)}






        {/* Setup Tab */}
        {activeTab === 'setup' && status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
          }}>
            <h2 style={{ 
              color: '#FF0000', 
              marginBottom: '30px', 
              fontSize: '28px', 
              fontWeight: '700' 
            }}>
              Setup YouTube Automation
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '30px' 
            }}>
              <div>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>Content Settings</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Content Type
                  </label>
                  <select 
                    value={config.content_type} 
                    onChange={(e) => setConfig(prev => ({...prev, content_type: e.target.value}))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px' 
                    }}
                  >
                    <option value="shorts">YouTube Shorts</option>
                    <option value="videos">Regular Videos</option>
                    <option value="both">Both</option>
                  </select>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Privacy Status
                  </label>
                  <select 
                    value={config.privacy_status} 
                    onChange={(e) => setConfig(prev => ({...prev, privacy_status: e.target.value}))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px' 
                    }}
                  >
                    <option value="private">Private</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="public">Public</option>
                  </select>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Content Categories
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {['Technology', 'Business', 'Education', 'Entertainment', 'Gaming', 'Lifestyle', 'Health', 'Finance'].map(category => (
                      <span 
                        key={category}
                        onClick={() => {
                          setConfig(prev => ({
                            ...prev,
                            content_categories: prev.content_categories.includes(category) 
                              ? prev.content_categories.filter(c => c !== category)
                              : [...prev.content_categories, category]
                          }));
                        }}
                        style={{ 
                          background: config.content_categories.includes(category) ? '#FF0000' : '#f8f9fa', 
                          color: config.content_categories.includes(category) ? 'white' : '#666',
                          padding: '6px 12px', 
                          borderRadius: '20px', 
                          fontSize: '12px', 
                          cursor: 'pointer',
                          border: '1px solid #ddd',
                          transition: 'all 0.3s ease'
                        }}
                      >
                        {category}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
              
              <div>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>Upload Schedule</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Upload Times
                  </label>
                  <div style={{ 
                    display: 'flex', 
                    flexWrap: 'wrap', 
                    gap: '8px', 
                    marginBottom: '12px' 
                  }}>
                    {config.upload_schedule.map((time, index) => (
                      <span 
                        key={index} 
                        style={{ 
                          background: '#FF0000', 
                          color: 'white', 
                          padding: '6px 12px', 
                          borderRadius: '20px', 
                          fontSize: '12px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '4px' 
                        }}
                      >
                        {time}
                        <button 
                          onClick={() => setConfig(prev => ({
                            ...prev, 
                            upload_schedule: prev.upload_schedule.filter((_, i) => i !== index)
                          }))}
                          style={{ 
                            background: 'none', 
                            border: 'none', 
                            color: 'white', 
                            cursor: 'pointer', 
                            fontSize: '12px', 
                            padding: '0', 
                            marginLeft: '4px' 
                          }}
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <input 
                      type="time" 
                      id="newTime"
                      style={{ 
                        padding: '8px', 
                        borderRadius: '4px', 
                        border: '1px solid #ddd', 
                        fontSize: '12px' 
                      }}
                    />
                    <button 
                      onClick={() => {
                        const timeInput = document.getElementById('newTime');
                        if (timeInput.value && !config.upload_schedule.includes(timeInput.value)) {
                          setConfig(prev => ({
                            ...prev, 
                            upload_schedule: [...prev.upload_schedule, timeInput.value]
                          }));
                          timeInput.value = '';
                        }
                      }}
                      style={{ 
                        padding: '8px 12px', 
                        background: '#28a745', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px', 
                        fontSize: '12px', 
                        cursor: 'pointer' 
                      }}
                    >
                      Add Time
                    </button>
                  </div>
                </div>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Shorts per Day
                  </label>
                  <input 
                    type="number" 
                    value={config.shorts_per_day} 
                    onChange={(e) => setConfig(prev => ({
                      ...prev, 
                      shorts_per_day: parseInt(e.target.value) || 1
                    }))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px' 
                    }}
                    min="1" max="10"
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Videos per Week
                  </label>
                  <input 
                    type="number" 
                    value={config.videos_per_week} 
                    onChange={(e) => setConfig(prev => ({
                      ...prev, 
                      videos_per_week: parseInt(e.target.value) || 1
                    }))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px' 
                    }}
                    min="1" max="14"
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ color: '#333', marginBottom: '12px', fontSize: '16px' }}>
                    Automation Features
                  </h4>
                  {[
                    { key: 'auto_generate_titles', label: 'Auto-generate Titles' },
                    { key: 'auto_generate_descriptions', label: 'Auto-generate Descriptions' },
                    { key: 'auto_add_tags', label: 'Auto-add Tags' }
                  ].map(feature => (
                    <label 
                      key={feature.key} 
                      style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        marginBottom: '8px', 
                        cursor: 'pointer' 
                      }}
                    >
                      <input 
                        type="checkbox" 
                        checked={config[feature.key]} 
                        onChange={(e) => setConfig(prev => ({
                          ...prev, 
                          [feature.key]: e.target.checked
                        }))}
                        style={{ width: '16px', height: '16px' }}
                      />
                      <span style={{ fontSize: '14px', color: '#333' }}>
                        {feature.label}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
            
            <div style={{ textAlign: 'center', marginTop: '40px' }}>
              <button 
                onClick={setupYouTubeAutomation}
                disabled={loading}
                style={{
                  padding: '16px 32px',
                  background: loading ? '#ccc' : '#FF0000',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '700',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  transition: 'background 0.3s ease'
                }}
              >
                {loading ? '⏳ Setting Up...' : '⚙️ Enable Automation'}
              </button>
            </div>
          </div>
        )}

        {/* Content Creation Tab */}
        {activeTab === 'content' && status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
          }}>
            <h2 style={{ 
              color: '#FF0000', 
              marginBottom: '30px', 
              fontSize: '28px', 
              fontWeight: '700' 
            }}>
              Create & Upload Content
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
              gap: '40px' 
            }}>
              <div>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>Generate Content with AI</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Content Type
                  </label>
                  <select 
                    value={contentData.content_type} 
                    onChange={(e) => setContentData(prev => ({...prev, content_type: e.target.value}))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px', 
                      marginBottom: '16px' 
                    }}
                  >
                    <option value="shorts">YouTube Shorts</option>
                    <option value="videos">Regular Videos</option>
                  </select>
                  
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Topic
                  </label>
                  <input 
                    type="text" 
                    value={contentData.topic} 
                    onChange={(e) => setContentData(prev => ({...prev, topic: e.target.value}))}
                    placeholder="Enter your video topic..."
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px', 
                      marginBottom: '16px' 
                    }}
                  />
                  
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Target Audience
                  </label>
                  <select 
                    value={contentData.target_audience} 
                    onChange={(e) => setContentData(prev => ({...prev, target_audience: e.target.value}))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px', 
                      marginBottom: '16px' 
                    }}
                  >
                    <option value="general">General Audience</option>
                    <option value="teens">Teens (13-19)</option>
                    <option value="young_adults">Young Adults (20-35)</option>
                    <option value="adults">Adults (35+)</option>
                    <option value="professionals">Professionals</option>
                    <option value="students">Students</option>
                  </select>
                  
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '8px', 
                    fontWeight: '600', 
                    color: '#333' 
                  }}>
                    Style
                  </label>
                  <select 
                    value={contentData.style} 
                    onChange={(e) => setContentData(prev => ({...prev, style: e.target.value}))}
                    style={{ 
                      width: '100%', 
                      padding: '12px', 
                      borderRadius: '8px', 
                      border: '2px solid #ddd', 
                      fontSize: '14px', 
                      marginBottom: '20px' 
                    }}
                  >
                    <option value="engaging">Engaging</option>
                    <option value="educational">Educational</option>
                    <option value="entertaining">Entertaining</option>
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="trending">Trending</option>
                  </select>

                  {/* Language Selector - ADD THIS */}
<label style={{ 
  display: 'block', 
  marginBottom: '8px', 
  fontWeight: '600', 
  color: '#333' 
}}>
  Content Language 🌐
</label>
<select 
  value={contentData.language || 'english'} 
  onChange={(e) => setContentData(prev => ({...prev, language: e.target.value}))}
  style={{ 
    width: '100%', 
    padding: '12px', 
    borderRadius: '8px', 
    border: '2px solid #ddd', 
    fontSize: '14px', 
    marginBottom: '20px' 
  }}
>
  <option value="english">English</option>
  <option value="hindi">हिन्दी (Hindi)</option>
  <option value="hinglish">Hinglish (हिन्दी + English)</option>
  <option value="tamil">தமிழ் (Tamil)</option>
  <option value="telugu">తెలుగు (Telugu)</option>
  <option value="bengali">বাংলা (Bengali)</option>
  <option value="marathi">मराठी (Marathi)</option>
  <option value="gujarati">ગુજરાતી (Gujarati)</option>
  <option value="malayalam">മലയാളം (Malayalam)</option>
  <option value="kannada">ಕನ್ನಡ (Kannada)</option>
  <option value="punjabi">ਪੰਜਾਬੀ (Punjabi)</option>
  <option value="assamese">অসমীয়া (Assamese)</option>
</select>
                </div>
                
                <button 
                  onClick={generateContent}
                  disabled={loading || !contentData.topic}
                  style={{
                    width: '100%',
                    padding: '12px',
                    background: loading || !contentData.topic ? '#ccc' : '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '600',
                    cursor: loading || !contentData.topic ? 'not-allowed' : 'pointer',
                    marginBottom: '20px',
                    transition: 'background 0.3s ease'
                  }}
                >
                  {loading ? 'Generating...' : 'Generate Content'}
                </button>
                
                {generatedContent && (
                  <div style={{ 
                    padding: '16px', 
                    background: '#f8f9fa', 
                    borderRadius: '8px', 
                    border: '1px solid #ddd' 
                  }}>
                    <h4 style={{ color: '#333', marginBottom: '12px' }}>Generated Content:</h4>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#666' }}>Title:</strong>
                      <p style={{ 
                        fontSize: '14px', 
                        color: '#333', 
                        margin: '4px 0', 
                        background: 'white', 
                        padding: '8px', 
                        borderRadius: '4px' 
                      }}>
                        {generatedContent.title}
                      </p>
                    </div>
                    <div style={{ marginBottom: '12px' }}>
                      <strong style={{ color: '#666' }}>Description:</strong>
                      <p style={{ 
                        fontSize: '14px', 
                        color: '#333', 
                        margin: '4px 0', 
                        background: 'white', 
                        padding: '8px', 
                        borderRadius: '4px' 
                      }}>
                        {generatedContent.description}
                      </p>
                    </div>
                    {generatedContent.tags && generatedContent.tags.length > 0 && (
                      <div>
                        <strong style={{ color: '#666' }}>Tags:</strong>
                        <div style={{ 
                          marginTop: '4px', 
                          display: 'flex', 
                          flexWrap: 'wrap', 
                          gap: '4px' 
                        }}>
                          {generatedContent.tags.map((tag, index) => (
                            <span 
                              key={index} 
                              style={{ 
                                background: '#007bff', 
                                color: 'white', 
                                padding: '2px 8px', 
                                borderRadius: '12px', 
                                fontSize: '12px' 
                              }}
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              







<div>
  <h3 style={{ color: '#333', marginBottom: '20px' }}>Upload Video</h3>
  <div style={{ marginBottom: '20px' }}>
    <label style={{ 
      display: 'block', 
      marginBottom: '8px', 
      fontWeight: '600', 
      color: '#333' 
    }}>
      Video Title
    </label>
    <input 
      type="text" 
      value={contentData.title} 
      onChange={(e) => setContentData(prev => ({...prev, title: e.target.value}))}
      placeholder="Enter video title..."
      style={{ 
        width: '100%', 
        padding: '12px', 
        borderRadius: '8px', 
        border: '2px solid #ddd', 
        fontSize: '14px', 
        marginBottom: '16px' 
      }}
    />
    
    <label style={{ 
      display: 'block', 
      marginBottom: '8px', 
      fontWeight: '600', 
      color: '#333' 
    }}>
      Video URL
    </label>
    <input 
      type="url" 
      value={contentData.video_url} 
      onChange={(e) => setContentData(prev => ({...prev, video_url: e.target.value}))}
      placeholder="https://example.com/video.mp4"
      style={{ 
        width: '100%', 
        padding: '12px', 
        borderRadius: '8px', 
        border: '2px solid #ddd', 
        fontSize: '14px', 
        marginBottom: '16px' 
      }}
    />



{/* Video Source Options */}
<div style={{
  marginTop: '16px',
  padding: '16px',
  background: '#f8f9fa',
  borderRadius: '8px',
  border: '1px solid #dee2e6'
}}>
  <div style={{
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
    alignItems: 'center'
  }}>
    {/* Manual File Upload */}
    <label style={{
      padding: '12px 20px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      borderRadius: '8px',
      cursor: 'pointer',
      fontSize: '14px',
      fontWeight: '600',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      transition: 'transform 0.2s',
      boxShadow: '0 4px 6px rgba(102, 126, 234, 0.4)'
    }}
    onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
    onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      📂 Upload Video File
      <input
        type="file"
        accept="video/mp4,video/avi,video/mov,video/*"
        style={{ display: 'none' }}
        onChange={async (e) => {
          const file = e.target.files?.[0];
          if (!file) return;
          
          // Validate file size (500MB max)
          const maxSize = 500 * 1024 * 1024;
          if (file.size > maxSize) {
            alert(`❌ File too large! Maximum size is 500MB.\nYour file: ${(file.size / 1024 / 1024).toFixed(2)}MB`);
            return;
          }
          
          setLoading(true);
          setUploadProgress(0);
          
          try {
            const formData = new FormData();
            formData.append('video', file);
            formData.append('user_id', user.user_id);
            
            // Use XMLHttpRequest for progress tracking
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
              if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                setUploadProgress(percent);
              }
            });
            
            // Handle completion
            xhr.addEventListener('load', () => {
              if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                  setContentData(prev => ({
                    ...prev,
                    video_url: response.video_url
                  }));
                  alert(`✅ Video uploaded successfully!\n\nSize: ${(response.file_size / 1024 / 1024).toFixed(2)}MB\n\nNext: Click "🎨 Generate Thumbnails"`);
                } else {
                  alert('❌ Upload failed: ' + (response.message || 'Unknown error'));
                }
              } else {
                alert(`❌ Upload failed: ${xhr.statusText}`);
              }
              setLoading(false);
              setUploadProgress(0);
            });
            
            // Handle errors
            xhr.addEventListener('error', () => {
              alert('❌ Upload failed: Network error');
              setLoading(false);
              setUploadProgress(0);
            });
            
            // Send request
            xhr.open('POST', `${API_BASE}/api/youtube/upload-video-file`);
            xhr.setRequestHeader('Authorization', `Bearer ${localStorage.getItem('token')}`);
            xhr.send(formData);
            
          } catch (error) {
            console.error('Upload error:', error);
            alert('❌ Upload failed: ' + error.message);
            setLoading(false);
            setUploadProgress(0);
          }
        }}
      />
    </label>

    {/* Upload Progress Bar */}
    {uploadProgress > 0 && (
      <div style={{
        flex: '1 1 300px',
        background: '#e9ecef',
        borderRadius: '20px',
        height: '32px',
        position: 'relative',
        overflow: 'hidden',
        boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <div style={{
          width: `${uploadProgress}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #4CAF50, #8BC34A)',
          transition: 'width 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{
            color: 'white',
            fontWeight: '700',
            fontSize: '14px',
            textShadow: '0 1px 2px rgba(0,0,0,0.3)'
          }}>
            {uploadProgress}%
          </span>
        </div>
      </div>
    )}
  </div>

  {/* Supported Formats Info */}
  <div style={{
    marginTop: '12px',
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
    fontSize: '12px',
    color: '#6c757d'
  }}>
    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      ✅ <strong>.mp4 URL</strong>
    </span>
    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      ✅ <strong>Google Drive</strong>
    </span>
    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      ✅ <strong>Manual Upload</strong>
    </span>
    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
      ✅ <strong>Max: 500MB</strong>
    </span>
  </div>
</div>





    <label style={{ 
      display: 'block', 
      marginBottom: '8px', 
      fontWeight: '600', 
      color: '#333' 
    }}>
      Description
    </label>
    <textarea 
      value={contentData.description} 
      onChange={(e) => setContentData(prev => ({...prev, description: e.target.value}))}
      placeholder="Enter video description..."
      rows={4}
      style={{ 
        width: '100%', 
        padding: '12px', 
        borderRadius: '8px', 
        border: '2px solid #ddd', 
        fontSize: '14px', 
        resize: 'vertical', 
        marginBottom: '20px' 
      }}
    />
  </div>





{/* NEW: Upload Mode Toggle */}
{/* Upload Mode Selection */}
<div style={{
  marginTop: '24px',
  padding: '20px',
  background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
  borderRadius: '12px',
  border: '2px solid #667eea'
}}>
  <h4 style={{
    marginBottom: '16px',
    color: '#667eea',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px'
  }}>
    <span>📹</span> Video Upload Mode
  </h4>
  



<div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
  {/* NEW VIDEO MODE */}
  <button
    onClick={() => {
      setUploadMode('new');
      setExistingVideoUrl('');
      setContentData(prev => ({
        ...prev,
        video_url: '',
        title: '',
        description: ''
      }));
      setThumbnails([]);
      setSelectedThumbnail(null);
    }}
    style={{
      flex: 1,
      padding: '14px',
      background: uploadMode === 'new' ? '#667eea' : 'white',
      color: uploadMode === 'new' ? 'white' : '#667eea',
      border: '2px solid #667eea',
      borderRadius: '8px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s',
      fontSize: '14px'
    }}
  >
    🆕 Upload New Video
  </button>
    


<button
  onClick={() => {
    setUploadMode('update');
    setExistingVideoUrl('');  // ✅ ADDED: Reset YouTube URL input
    setContentData(prev => ({ 
      ...prev, 
      video_url: '',
      title: '',
      description: ''
    }));
    setThumbnails([]);
    setSelectedThumbnail(null);
  }}
  style={{
    flex: 1,
    padding: '14px',
    background: uploadMode === 'update' ? '#667eea' : 'white',
    color: uploadMode === 'update' ? 'white' : '#667eea',
    border: '2px solid #667eea',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.3s',
    fontSize: '14px'
  }}
>
  🔄 Update Existing Thumbnail
</button>
  </div>

  {/* Update Mode - YouTube URL Input */}
  {uploadMode === 'update' && (
    <div style={{
      padding: '16px',
      background: 'white',
      borderRadius: '8px',
      border: '1px solid #dee2e6'
    }}>
      <label style={{
        display: 'block',
        marginBottom: '8px',
        fontWeight: '600',
        color: '#495057',
        fontSize: '14px'
      }}>
        📺 Your YouTube Video URL:
      </label>
      <input
        type="text"
        value={existingVideoUrl}
        onChange={(e) => setExistingVideoUrl(e.target.value)}
        placeholder="https://youtube.com/watch?v=YOUR_VIDEO_ID"
        style={{
          width: '100%',
          padding: '12px',
          borderRadius: '6px',
          border: '2px solid #ced4da',
          fontSize: '14px',
          outline: 'none',
          transition: 'border-color 0.3s'
        }}
        onFocus={(e) => e.target.style.borderColor = '#667eea'}
        onBlur={(e) => e.target.style.borderColor = '#ced4da'}
      />
      
      <button
        onClick={async () => {
          if (!existingVideoUrl.trim()) {
            alert('⚠️ Please paste your YouTube video URL');
            return;
          }
          
          setLoading(true);
          try {
            const response = await fetch(`${API_BASE}/api/youtube/fetch-video-info`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
              body: JSON.stringify({
                user_id: user.user_id,
                video_url: existingVideoUrl
              })
            });
            
            const result = await response.json();
            



if (result.success) {
  setContentData(prev => ({
    ...prev,
    title: result.title,
    description: result.description,
    video_url: existingVideoUrl  // ✅ This is the YouTube URL
  }));
  
  setUploadMode('update');  // ✅ CRITICAL: Set mode to 'update'
  
  console.log('✅ Video info loaded');
  console.log('📹 Mode set to: update');


              alert(`✅ Video info loaded!\n\nTitle: ${result.title}\n\nNext: Click "🎨 Generate Thumbnails"`);
            } else {
              alert('❌ Error: ' + (result.message || result.error || 'Failed to fetch video info'));
            }
          } catch (error) {
            console.error('Fetch error:', error);
            alert('❌ Network error: ' + error.message);
          } finally {
            setLoading(false);
          }
        }}
        disabled={loading || !existingVideoUrl.trim()}
        style={{
          marginTop: '12px',
          width: '100%',
          padding: '12px',
          background: loading || !existingVideoUrl.trim() ? '#ccc' : '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: loading || !existingVideoUrl.trim() ? 'not-allowed' : 'pointer',
          fontWeight: '600',
          fontSize: '14px'
        }}
      >
        {loading ? '⏳ Loading...' : '🔍 Fetch Video Info'}
      </button>
    </div>
  )}
</div>













{/* relgfjeo'rg */}
{/* Manual Thumbnail Upload */}
{/* ✅ MANUAL THUMBNAIL UPLOAD FROM GALLERY */}
{/* ============================================ */}
{/* THUMBNAIL GENERATION OPTIONS - ALL 3 METHODS */}
{/* ============================================ */}

{/* OPTION 1: Manual Thumbnail Upload */}
<div style={{marginTop: '20px'}}>
  <h4 style={{
    marginBottom: '12px',
    color: '#FF6B6B',
    fontSize: '16px',
    fontWeight: '700',
    display: 'flex',
    alignItems: 'center',
    gap: '8px'
  }}>
    <span>🖼️</span> Option 1: Upload Custom Thumbnail from Gallery
  </h4>
  
  <label style={{
    display: 'block',
    width: '100%',
    padding: '14px',
    background: 'linear-gradient(135deg, #FF6B6B, #FF8E53)',
    color: 'white',
    textAlign: 'center',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: '700',
    fontSize: '15px',
    transition: 'transform 0.2s',
    border: 'none'
  }}
  onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
  onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
  >
    🖼️ Upload Your Own Image
    <input
      type="file"
      accept="image/*"
      style={{ display: 'none' }}
      onChange={async (e) => {
        const file = e.target.files?.[0];
        if (!file) return;
        
        setLoading(true);
        try {
          const formData = new FormData();
          formData.append('image', file);
          formData.append('user_id', user.user_id);
          
          const response = await fetch(`${API_BASE}/api/youtube/upload-thumbnail-image`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
          });
          
          const result = await response.json();
          
          if (result.success) {
            // Add to thumbnails array
            const customThumbnail = {
              id: 'custom_upload',
              url: result.thumbnail_url,
              style: 'Custom Upload',
              ctr_optimized: false
            };
            
            setThumbnails([customThumbnail]);
            setSelectedThumbnail(customThumbnail);
            
            alert('✅ Custom thumbnail uploaded and resized to 1280x720!');
          } else {
            alert('❌ Upload failed: ' + (result.error || 'Unknown error'));
          }
        } catch (error) {
          alert('❌ Upload error: ' + error.message);
        } finally {
          setLoading(false);
        }
      }}
    />
  </label>
  <div style={{
    marginTop: '8px',
    fontSize: '12px',
    color: '#666',
    textAlign: 'center'
  }}>
    Upload your own thumbnail • Auto-resized to 1280x720 • PNG/JPG supported
  </div>
</div>

{/* Divider */}
<div style={{
  margin: '24px 0',
  height: '2px',
  background: 'linear-gradient(to right, #FF6B6B, #FF8E53)',
  borderRadius: '2px'
}}></div>

{/* OPTION 2: AI Generated Thumbnails */}
<div style={{
  padding: '20px',
  background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
  borderRadius: '12px',
  border: '2px solid #667eea'
}}>
  <h4 style={{
    marginBottom: '16px',
    color: '#667eea',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
    fontWeight: '700'
  }}>
    <span>🤖</span> Option 2: AI Generated Thumbnails
  </h4>

  <div style={{
    padding: '12px',
    background: '#fff',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '13px',
    color: '#555'
  }}>
    💡 <strong>AI Magic:</strong> Generate 3 unique thumbnail designs with custom styles. Perfect for eye-catching thumbnails!
  </div>

  {/* Custom Prompt Input */}
  <div style={{ marginBottom: '16px' }}>
    <label style={{
      display: 'block',
      marginBottom: '8px',
      fontWeight: '600',
      color: '#495057',
      fontSize: '14px'
    }}>
      🎨 Custom Style (Optional):
    </label>
    <input
      type="text"
      value={customThumbnailPrompt}
      onChange={(e) => setCustomThumbnailPrompt(e.target.value)}
      placeholder="e.g., futuristic, neon colors, cyberpunk, minimalist, vibrant..."
      style={{
        width: '100%',
        padding: '10px',
        borderRadius: '6px',
        border: '2px solid #ced4da',
        fontSize: '14px'
      }}
    />
    <div style={{
      marginTop: '6px',
      fontSize: '12px',
      color: '#666'
    }}>
      💡 Leave empty for default styles, or add keywords like "cinematic", "colorful", "dark mode"
    </div>
  </div>

  {/* Overlay Toggle */}
  <div style={{
    marginBottom: '16px',
    padding: '14px',
    background: 'white',
    borderRadius: '8px',
    border: '2px solid #ffc107'
  }}>
    <label style={{
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      cursor: 'pointer',
      fontSize: '14px',
      fontWeight: '600'
    }}>
      <input
        type="checkbox"
        checked={addThumbnailOverlay}
        onChange={(e) => setAddThumbnailOverlay(e.target.checked)}
        style={{
          width: '20px',
          height: '20px',
          cursor: 'pointer',
          accentColor: '#ffc107'
        }}
      />
      <span>📝 Add Yellow Text Overlay (Bottom Center)</span>
    </label>
    <div style={{
      marginTop: '8px',
      fontSize: '12px',
      color: '#666',
      marginLeft: '30px',
      padding: '8px',
      background: addThumbnailOverlay ? '#fff3cd' : '#f8f9fa',
      borderRadius: '6px',
      border: addThumbnailOverlay ? '1px solid #ffc107' : '1px solid #dee2e6'
    }}>
      {addThumbnailOverlay 
        ? '✅ Your title will appear on a yellow box at the bottom' 
        : '❌ Pure AI-generated image without text'}
    </div>
  </div>

  {/* Generate AI Thumbnails Button */}
  <button
    onClick={async () => {
      // Validation
      if (!contentData.title?.trim()) {
        alert('⚠️ Please enter a video title first!');
        return;
      }
      
      setGeneratingThumbnails(true);
      setThumbnails([]);
      setSelectedThumbnail(null);
      
      try {
        console.log('🤖 Starting AI thumbnail generation...');
        console.log('Title:', contentData.title);
        console.log('Overlay:', addThumbnailOverlay);
        console.log('Custom Prompt:', customThumbnailPrompt);
        
        const response = await fetch(`${API_BASE}/api/youtube/generate-ai-thumbnails`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            user_id: user.user_id,
            title: contentData.title,
            description: contentData.description || '',
            add_overlay: addThumbnailOverlay,
            custom_prompt: customThumbnailPrompt
          })
        });
        
        const result = await response.json();
        console.log('🎨 AI Thumbnail response:', result);
        
        if (result.success && result.thumbnails?.length > 0) {
          setThumbnails(result.thumbnails);
          alert(`✅ Generated ${result.thumbnails.length} AI thumbnails!\n\n🎨 3 unique designs created!\nScroll right to see all options.`);
        } else {
          alert('❌ AI generation failed: ' + (result.message || result.error || 'Unknown error'));
        }
        
      } catch (error) {
        console.error('❌ AI Thumbnail error:', error);
        alert('❌ AI Thumbnail generation failed:\n' + error.message);
      } finally {
        setGeneratingThumbnails(false);
      }
    }}
    disabled={generatingThumbnails || !contentData.title}
    style={{
      width: '100%',
      padding: '16px',
      background: (generatingThumbnails || !contentData.title) 
        ? '#ccc' 
        : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      fontSize: '16px',
      fontWeight: '700',
      cursor: (generatingThumbnails || !contentData.title) 
        ? 'not-allowed' 
        : 'pointer',
      boxShadow: (generatingThumbnails || !contentData.title) 
        ? 'none' 
        : '0 4px 15px rgba(102, 126, 234, 0.4)',
      transition: 'all 0.3s',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px'
    }}
  >
    {generatingThumbnails ? (
      <>
        <span className="spinner" style={{
          border: '3px solid rgba(255,255,255,0.3)',
          borderTop: '3px solid white',
          borderRadius: '50%',
          width: '22px',
          height: '22px',
          animation: 'spin 1s linear infinite'
        }} />
        Generating AI Thumbnails...
      </>
    ) : (
      <>
        <span style={{ fontSize: '20px' }}>🤖</span>
        <span>Generate AI Thumbnails (3 Designs)</span>
      </>
    )}
  </button>

  {/* Info Box */}
  <div style={{
    marginTop: '12px',
    padding: '10px',
    background: '#e7f3ff',
    borderRadius: '6px',
    fontSize: '12px',
    color: '#004085',
    border: '1px solid #bee5eb'
  }}>
    ℹ️ <strong>How it works:</strong> AI creates 3 unique thumbnail designs based on your title. Each has a different style (cinematic, vibrant, minimalist).
  </div>
</div>

{/* Divider */}
<div style={{
  margin: '24px 0',
  height: '2px',
  background: 'linear-gradient(to right, #667eea, #764ba2)',
  borderRadius: '2px'
}}></div>

{/* OPTION 3: Frame Extraction from Video */}
<div style={{
  padding: '20px',
  background: 'linear-gradient(135deg, #007bff15 0%, #0056b315 100%)',
  borderRadius: '12px',
  border: '2px solid #007bff'
}}>
  <h4 style={{
    marginBottom: '16px',
    color: '#007bff',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
    fontWeight: '700'
  }}>
    <span>🎬</span> Option 3: Extract Frames from Video
  </h4>

  <div style={{
    padding: '12px',
    background: '#fff',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '13px',
    color: '#555'
  }}>
    📹 <strong>Video Frames:</strong> Extract key frames from your video and add text overlay automatically.
  </div>

  {/* Generate Frame Thumbnails Button */}
  <button
    onClick={async () => {
      // Validation
      if (!contentData.title?.trim()) {
        alert('⚠️ Please enter a video title first!');
        return;
      }
      
      if (!contentData.video_url?.trim()) {
        alert('⚠️ Please provide a video URL or upload a file first!');
        return;
      }
      
      setGeneratingThumbnails(true);
      setThumbnails([]);
      setSelectedThumbnail(null);
      
      try {
        console.log('🎬 Starting frame thumbnail generation...');
        console.log('Video URL:', contentData.video_url);
        console.log('Title:', contentData.title);
        
        const response = await fetch(`${API_BASE}/api/youtube/generate-thumbnails`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            user_id: user.user_id,
            video_url: contentData.video_url,
            title: contentData.title,
            description: contentData.description || ''
          })
        });
        
        const result = await response.json();
        console.log('Frame thumbnail response:', result);
        
        if (result.success && result.thumbnails?.length > 0) {
          setThumbnails(result.thumbnails);
          alert(`✅ Generated ${result.thumbnails.length} frame thumbnails!\n\nSelect one and click "Upload to YouTube"`);
        } else {
          alert('❌ No thumbnails generated. Error: ' + (result.message || 'Unknown error'));
        }
        
      } catch (error) {
        console.error('Frame thumbnail generation error:', error);
        alert('❌ Frame thumbnail generation failed:\n' + error.message);
      } finally {
        setGeneratingThumbnails(false);
      }
    }}
    disabled={generatingThumbnails || !contentData.title || !contentData.video_url}
    style={{
      width: '100%',
      padding: '16px',
      background: (generatingThumbnails || !contentData.title || !contentData.video_url) 
        ? '#ccc' 
        : 'linear-gradient(135deg, #007bff 0%, #0056b3 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      fontSize: '16px',
      fontWeight: '700',
      cursor: (generatingThumbnails || !contentData.title || !contentData.video_url) 
        ? 'not-allowed' 
        : 'pointer',
      boxShadow: (generatingThumbnails || !contentData.title || !contentData.video_url)
        ? 'none'
        : '0 4px 15px rgba(0, 123, 255, 0.4)',
      transition: 'all 0.3s',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px'
    }}
  >
    {generatingThumbnails ? (
      <>
        <span className="spinner" style={{
          border: '3px solid rgba(255,255,255,0.3)',
          borderTop: '3px solid white',
          borderRadius: '50%',
          width: '20px',
          height: '20px',
          animation: 'spin 1s linear infinite'
        }} />
        Extracting Frames...
      </>
    ) : (
      <>
        <span style={{ fontSize: '20px' }}>🎬</span>
        <span>Extract Frame Thumbnails with Overlay</span>
      </>
    )}
  </button>

  {/* Info Box */}
  <div style={{
    marginTop: '12px',
    padding: '10px',
    background: '#e7f3ff',
    borderRadius: '6px',
    fontSize: '12px',
    color: '#004085',
    border: '1px solid #bee5eb'
  }}>
    ℹ️ <strong>How it works:</strong> Extracts 3 key frames from your video at different timestamps. Adds text overlay with your title. CTR optimized!
  </div>
</div>

{/* Add spinner animation */}
<style>{`
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`}</style>




{/* Display Generated Thumbnails */}
{/* ✅ DISPLAY GENERATED THUMBNAILS - KEEP THIS */}
{/* ============================================ */}
{/* ============================================ */}
{/* UNIFIED THUMBNAIL DISPLAY (Frame + AI + Manual) */}
{/* ============================================ */}
{thumbnails.length > 0 && (
  <div style={{
    marginTop: '24px',
    padding: '20px',
    background: 'linear-gradient(135deg, #fff5f5 0%, #f0f9ff 100%)',
    borderRadius: '12px',
    border: '3px solid #28a745',
    boxShadow: '0 4px 12px rgba(40, 167, 69, 0.2)'
  }}>
    <h4 style={{
      marginBottom: '16px',
      color: '#28a745',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      fontSize: '18px',
      fontWeight: '700'
    }}>
      ✅ Select Your Thumbnail ({thumbnails.length} options available)
    </h4>
    
    {/* Horizontal Scrollable Container */}
    <div style={{
      display: 'flex',
      gap: '16px',
      overflowX: 'auto',
      paddingBottom: '16px',
      scrollBehavior: 'smooth',
      scrollbarWidth: 'thin',
      scrollbarColor: '#28a745 #e9ecef',
      WebkitOverflowScrolling: 'touch'
    }}>
      {thumbnails.map((thumb, index) => (
        <div
          key={thumb.id}
          onClick={() => {
            setSelectedThumbnail(thumb);
            console.log('✅ Thumbnail selected:', thumb.id, thumb);
          }}
          style={{
            minWidth: '280px',
            maxWidth: '280px',
            border: selectedThumbnail?.id === thumb.id 
              ? '4px solid #28a745' 
              : '2px solid #dee2e6',
            borderRadius: '12px',
            overflow: 'hidden',
            cursor: 'pointer',
            transition: 'all 0.3s',
            background: 'white',
            transform: selectedThumbnail?.id === thumb.id ? 'scale(1.05)' : 'scale(1)',
            boxShadow: selectedThumbnail?.id === thumb.id 
              ? '0 8px 24px rgba(40, 167, 69, 0.4)' 
              : '0 2px 8px rgba(0,0,0,0.1)',
            flexShrink: 0
          }}
        >
          <img 
            src={thumb.url} 
            alt={`Thumbnail ${index + 1}`}
            style={{
              width: '100%',
              height: '157px',
              objectFit: 'cover',
              display: 'block'
            }}
          />
          <div style={{
            padding: '12px',
            textAlign: 'center',
            background: selectedThumbnail?.id === thumb.id 
              ? 'linear-gradient(135deg, #28a745, #20c997)' 
              : 'white',
            color: selectedThumbnail?.id === thumb.id ? 'white' : '#333'
          }}>
            {/* Title/Selection Status */}
            <div style={{
              fontWeight: '700',
              fontSize: '14px',
              marginBottom: '6px'
            }}>
              {selectedThumbnail?.id === thumb.id ? '✅ SELECTED' : `Option ${index + 1}`}
            </div>
            
            {/* Thumbnail Type Badge */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              marginBottom: '4px',
              flexWrap: 'wrap'
            }}>
              {/* AI Generated Badge */}
              {thumb.has_overlay !== undefined && (
                <span style={{
                  fontSize: '10px',
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: selectedThumbnail?.id === thumb.id ? 'rgba(255,255,255,0.3)' : '#667eea',
                  color: 'white',
                  fontWeight: '600'
                }}>
                  🤖 AI Generated
                </span>
              )}
              
              {/* Frame Extraction Badge */}
              {thumb.ctr_optimized !== undefined && !thumb.has_overlay && (
                <span style={{
                  fontSize: '10px',
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: selectedThumbnail?.id === thumb.id ? 'rgba(255,255,255,0.3)' : '#007bff',
                  color: 'white',
                  fontWeight: '600'
                }}>
                  🎬 Frame Extract
                </span>
              )}
              
              {/* Manual Upload Badge */}
              {thumb.id === 'custom_upload' && (
                <span style={{
                  fontSize: '10px',
                  padding: '3px 8px',
                  borderRadius: '12px',
                  background: selectedThumbnail?.id === thumb.id ? 'rgba(255,255,255,0.3)' : '#FF6B6B',
                  color: 'white',
                  fontWeight: '600'
                }}>
                  🖼️ Custom Upload
                </span>
              )}
            </div>
            
            {/* Style/Details */}
            <div style={{
              fontSize: '11px',
              opacity: 0.9,
              marginBottom: '4px'
            }}>
              {thumb.style && <div>{thumb.style}</div>}
              {thumb.variation && <div>Variation {thumb.variation}</div>}
            </div>
            
            {/* Overlay Status */}
            {thumb.has_overlay !== undefined && (
              <div style={{
                fontSize: '10px',
                opacity: 0.85,
                marginTop: '4px'
              }}>
                {thumb.has_overlay ? '📝 With Text Overlay' : '🖼️ Pure Image'}
              </div>
            )}
            
            {/* CTR Score for Frame Thumbnails */}
            {thumb.ctr_optimized && thumb.ctr_score && (
              <div style={{
                fontSize: '10px',
                marginTop: '4px',
                padding: '2px 6px',
                background: selectedThumbnail?.id === thumb.id 
                  ? 'rgba(255,255,255,0.3)' 
                  : (thumb.ctr_score > 70 ? '#28a745' : '#ffc107'),
                color: 'white',
                borderRadius: '4px',
                display: 'inline-block',
                fontWeight: '600'
              }}>
                CTR: {thumb.ctr_score.toFixed(0)}%
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
    
    {/* Scroll Indicator */}
    {thumbnails.length > 3 && (
      <div style={{
        textAlign: 'center',
        marginTop: '12px',
        fontSize: '12px',
        color: '#666',
        fontWeight: '600'
      }}>
        ← Scroll horizontally to see all {thumbnails.length} thumbnails →
      </div>
    )}
    
    {/* Selection Info */}
    {selectedThumbnail && (
      <div style={{
        marginTop: '16px',
        padding: '14px',
        background: 'linear-gradient(135deg, #d4edda, #c3f0d2)',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#155724',
        border: '2px solid #28a745',
        fontWeight: '600'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <span style={{ fontSize: '18px' }}>✅</span>
          <strong>Selected Thumbnail:</strong>
        </div>
        <div style={{ fontSize: '13px', marginLeft: '26px' }}>
          {/* Thumbnail Type */}
          {selectedThumbnail.has_overlay !== undefined && (
            <div>🤖 AI Generated • {selectedThumbnail.has_overlay ? 'With overlay' : 'No overlay'}</div>
          )}
          {selectedThumbnail.ctr_optimized && (
            <div>🎬 Frame Extracted • CTR Score: {selectedThumbnail.ctr_score?.toFixed(0)}%</div>
          )}
          {selectedThumbnail.id === 'custom_upload' && (
            <div>🖼️ Your Custom Upload</div>
          )}
          
          {/* Style Info */}
          {selectedThumbnail.style && (
            <div style={{ marginTop: '4px', opacity: 0.9 }}>
              Style: {selectedThumbnail.style}
            </div>
          )}
          
          <div style={{ marginTop: '8px', fontSize: '12px', opacity: 0.85 }}>
            This thumbnail will be uploaded with your video to YouTube
          </div>
        </div>
      </div>
    )}
    
    {/* Tips Box */}
    <div style={{
      marginTop: '12px',
      padding: '12px',
      background: 'rgba(255, 255, 255, 0.9)',
      borderRadius: '8px',
      fontSize: '12px',
      color: '#666',
      border: '1px solid #dee2e6'
    }}>
      <div style={{ fontWeight: '600', marginBottom: '6px', color: '#333' }}>
        💡 Pro Tips:
      </div>
      <ul style={{ margin: '0', paddingLeft: '20px', lineHeight: '1.6' }}>
        <li>Scroll right → to see all thumbnail options</li>
        <li>🤖 AI thumbnails offer unique creative designs</li>
        <li>🎬 Frame thumbnails show actual video content</li>
        <li>🖼️ Custom uploads give you full control</li>
        <li>Click any thumbnail to select it, then upload below!</li>
      </ul>
    </div>
  </div>
)}

{/* Final Upload/Update Button */}
{selectedThumbnail && (
  <button
    onClick={async () => {
      if (!selectedThumbnail) {
        alert('⚠️ Please select a thumbnail first!');
        return;
      }
      
      setLoading(true);
      
      try {
        const uploadData = {
          user_id: user.user_id,
          title: contentData.title,
          description: contentData.description || '',
          video_url: contentData.video_url,
          thumbnail_url: selectedThumbnail?.url || null,
          privacy_status: 'public',
          tags: contentData.tags || [],
          video_mode: uploadMode,
          content_type: contentData.content_type || 'shorts'
        };

        console.log('📤 Upload Data:', uploadData);
        console.log('📤 Upload Mode:', uploadMode);
        
        const response = await fetch(`${API_BASE}/api/youtube/upload`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(uploadData)
        });
        
        const result = await response.json();
        
        if (result.success) {
          if (uploadMode === 'update') {
            alert(`✅ Thumbnail updated successfully!\n\nYour video thumbnail has been changed.`);
          } else {
            alert(`✅ Video uploaded successfully!\n\nVideo ID: ${result.video_id || 'N/A'}\n\nCheck your YouTube channel!`);
          }
          
          // Reset form
          setContentData({
            title: '',
            description: '',
            video_url: '',
            tags: []
          });
          setThumbnails([]);
          setSelectedThumbnail(null);
          setExistingVideoUrl('');
          
        } else {
          alert('❌ Upload failed:\n' + (result.message || result.error || 'Unknown error'));
        }
        
      } catch (error) {
        console.error('Upload error:', error);
        alert('❌ Upload failed:\n' + error.message);
      } finally {
        setLoading(false);
      }
    }}
    disabled={loading || !selectedThumbnail}
    style={{
      width: '100%',
      padding: '18px',
      background: loading || !selectedThumbnail 
        ? '#ccc' 
        : uploadMode === 'update'
        ? 'linear-gradient(135deg, #FF6B6B, #FF8E53)'
        : 'linear-gradient(135deg, #56CCF2, #2F80ED)',
      color: 'white',
      border: 'none',
      borderRadius: '10px',
      fontSize: '17px',
      fontWeight: '700',
      cursor: loading || !selectedThumbnail ? 'not-allowed' : 'pointer',
      marginTop: '20px',
      boxShadow: '0 6px 20px rgba(47, 128, 237, 0.4)',
      transition: 'all 0.3s'
    }}
  >
    {loading ? '⏳ Processing...' : 
     uploadMode === 'update' ? '🔄 Update Thumbnail on YouTube' : 
     '📤 Upload Video to YouTube'}
  </button>
)}


{/* Upload Button - SINGLE BUTTON ONLY */}
{/* <button 
  onClick={uploadVideo}
  disabled={loading || !contentData.title || !contentData.video_url}
  style={{
    width: '100%',
    padding: '12px',
    background: loading || !contentData.title || !contentData.video_url ? '#ccc' : '#FF0000',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: loading || !contentData.title || !contentData.video_url ? 'not-allowed' : 'pointer',
    transition: 'background 0.3s ease'
  }}
>
  {loading ? 'Uploading...' : 'Upload to YouTube'}
</button> */}

{/* 👆 REPLACE THE ABOVE BUTTON WITH THIS NEW VERSION 👇 */}

<button 
  onClick={async () => {
    if (!contentData.title || !contentData.video_url) {
      alert('Please provide title and video');
      return;
    }
    
    await uploadVideo();
  }}
  disabled={loading || !contentData.title || !contentData.video_url}
  style={{
    width: '100%',
    padding: '14px',
    background: loading || !contentData.title || !contentData.video_url ? '#ccc' : '#FF0000',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '15px',
    fontWeight: '600',
    cursor: loading || !contentData.title || !contentData.video_url ? 'not-allowed' : 'pointer',
    transition: 'all 0.3s ease'
  }}
>
  {loading ? '⏳ Processing...' : 
   videoUploadMode === 'update' ? '🔄 Update Thumbnail Only' : 
   '📤 Upload to YouTube'}
</button>








{/* NEW: Schedule Mode Toggle */}
{/* IMPROVED: Unified Upload/Schedule Section */}
<div style={{ marginTop: '30px', paddingTop: '30px', borderTop: '2px solid #f0f0f0' }}>
  <div style={{ 
    display: 'flex', 
    gap: '12px', 
    marginBottom: '24px' 
  }}>
    {/* Upload Now Button */}
    <button 
      onClick={uploadVideo}
      disabled={loading || !contentData.title || !contentData.video_url}
      style={{
        flex: 1,
        padding: '14px',
        background: loading || !contentData.title || !contentData.video_url ? '#ccc' : '#FF0000',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        fontSize: '15px',
        fontWeight: '600',
        cursor: loading || !contentData.title || !contentData.video_url ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      {loading ? 'Uploading...' : 'Upload to YouTube Now'}
    </button>
    
    {/* OR Separator */}
    <div style={{ 
      display: 'flex', 
      alignItems: 'center', 
      color: '#999',
      fontSize: '14px',
      fontWeight: '600'
    }}>
      OR
    </div>
    
    {/* Schedule Button */}
    <button
      onClick={() => setScheduleMode(!scheduleMode)}
      disabled={!contentData.title || !contentData.video_url}
      style={{
        flex: 1,
        padding: '14px',
        background: scheduleMode ? '#28a745' : (!contentData.title || !contentData.video_url ? '#ccc' : '#f0f0f0'),
        color: scheduleMode ? 'white' : (!contentData.title || !contentData.video_url ? '#999' : '#333'),
        border: scheduleMode ? 'none' : '2px solid #ddd',
        borderRadius: '8px',
        fontSize: '15px',
        fontWeight: '600',
        cursor: !contentData.title || !contentData.video_url ? 'not-allowed' : 'pointer',
        transition: 'all 0.3s ease'
      }}
    >
      {scheduleMode ? 'Scheduling Active' : 'Schedule for Later'}
    </button>
  </div>

  {scheduleMode && (
    <div style={{
      background: '#f8f9fa',
      padding: '20px',
      borderRadius: '12px',
      border: '2px solid #28a745'
    }}>
      <h4 style={{ color: '#28a745', marginBottom: '16px', fontSize: '16px' }}>
        Schedule Upload Times
      </h4>
      
      <div style={{
        background: 'white',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
        fontSize: '13px',
        color: '#666',
        border: '1px solid #ddd'
      }}>
        <strong>Ready to schedule:</strong> {contentData.title}
        <br />
        <small>Video will upload automatically at selected times</small>
      </div>
      
      {scheduleSlots.map((slot, index) => (
        <div key={slot.id} style={{
          background: 'white',
          padding: '16px',
          borderRadius: '8px',
          marginBottom: '12px',
          border: '2px solid #e0e0e0'
        }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between',
            marginBottom: '12px'
          }}>
            <span style={{ fontWeight: '600', color: '#28a745', fontSize: '14px' }}>
              Upload Time {index + 1}
            </span>
            {slot.date && slot.time && (
              <button
                onClick={() => {
                  const newSlots = [...scheduleSlots];
                  newSlots[index] = { id: slot.id, date: '', time: '' };
                  setScheduleSlots(newSlots);
                }}
                style={{
                  padding: '4px 8px',
                  background: '#dc3545',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  fontSize: '11px',
                  cursor: 'pointer'
                }}
              >
                Clear
              </button>
            )}
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '12px', 
                color: '#666',
                marginBottom: '4px',
                fontWeight: '500'
              }}>
                Date
              </label>
              <input
                type="date"
                value={slot.date}
                min={new Date().toISOString().split('T')[0]}
                onChange={(e) => {
                  const newSlots = [...scheduleSlots];
                  newSlots[index].date = e.target.value;
                  setScheduleSlots(newSlots);
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '6px',
                  border: '1px solid #ddd',
                  fontSize: '13px'
                }}
              />
            </div>
            
            <div>
              <label style={{ 
                display: 'block', 
                fontSize: '12px', 
                color: '#666',
                marginBottom: '4px',
                fontWeight: '500'
              }}>
                Time
              </label>
              <input
                type="time"
                value={slot.time}
                onChange={(e) => {
                  const newSlots = [...scheduleSlots];
                  newSlots[index].time = e.target.value;
                  setScheduleSlots(newSlots);
                }}
                style={{
                  width: '100%',
                  padding: '10px',
                  borderRadius: '6px',
                  border: '1px solid #ddd',
                  fontSize: '13px'
                }}
              />
            </div>
          </div>
          
          {slot.date && slot.time && (
            <div style={{
              marginTop: '8px',
              padding: '8px',
              background: '#d4edda',
              borderRadius: '4px',
              fontSize: '12px',
              color: '#155724'
            }}>
              Will upload: {new Date(`${slot.date}T${slot.time}`).toLocaleString()}
            </div>
          )}
        </div>
      ))}
      
      <div style={{
        background: '#fff3cd',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
        border: '1px solid #ffc107'
      }}>
        <div style={{ fontSize: '12px', fontWeight: '600', color: '#856404', marginBottom: '8px' }}>
          Quick Test (3-minute intervals)
        </div>
        <button
          onClick={() => {
            const now = new Date();
            const newSlots = [
              { id: 1, date: now.toISOString().split('T')[0], time: new Date(now.getTime() + 3 * 60000).toTimeString().slice(0, 5) },
              { id: 2, date: now.toISOString().split('T')[0], time: new Date(now.getTime() + 6 * 60000).toTimeString().slice(0, 5) },
              { id: 3, date: now.toISOString().split('T')[0], time: new Date(now.getTime() + 9 * 60000).toTimeString().slice(0, 5) }
            ];
            setScheduleSlots(newSlots);
          }}
          style={{
            padding: '8px 16px',
            background: '#ffc107',
            color: '#000',
            border: 'none',
            borderRadius: '6px',
            fontSize: '12px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          Set Test Times (Now +3min, +6min, +9min)
        </button>
      </div>
      


      
      <button








onClick={async () => {
  const validSlots = scheduleSlots.filter(s => s.date && s.time);
  
  if (validSlots.length === 0) {
    alert('Please set at least one date and time for scheduling');
    return;
  }
  
  if (!contentData.title?.trim() || !contentData.video_url?.trim()) {
    alert('Please enter video title and URL first');
    return;
  }
  
  setLoading(true);
  setError('');
  
  try {
    const userData = getUserData();
    
    if (!userData?.user_id) {
      throw new Error('User ID not found');
    }
    
    console.log('Sending schedule requests...');
    
    const results = await Promise.all(
      validSlots.map(async (slot, index) => {
        // ✅ CONVERT IST TO UTC
        const istDateTime = new Date(`${slot.date}T${slot.time}:00+05:30`); // IST timezone
        const utcDate = istDateTime.toISOString().split('T')[0]; // YYYY-MM-DD
        const utcTime = istDateTime.toISOString().split('T')[1].substring(0, 5); // HH:MM
        
        console.log(`Slot ${index + 1}:`);
        console.log(`  IST: ${slot.date} ${slot.time}`);
        console.log(`  UTC: ${utcDate} ${utcTime}`);
        
        const payload = {
          user_id: userData.user_id,
          schedule_date: utcDate,  // ← Send UTC date
          schedule_time: utcTime,  // ← Send UTC time
          video_data: {
            title: contentData.title.trim(),
            description: contentData.description.trim(),
            video_url: contentData.video_url.trim(),
            content_type: contentData.content_type,
            thumbnail_url: selectedThumbnail?.url || null
          }
        };
        
        console.log(`Schedule payload ${index + 1}:`, payload);
        
        const response = await fetch(`${API_BASE}/api/youtube/schedule-video`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        console.log(`Schedule response ${index + 1}:`, result);
        
        return result;
      })
    );
    
    const successCount = results.filter(r => r.success).length;
    
    if (successCount > 0) {
      alert(`✅ ${successCount} upload(s) scheduled successfully!\n\nNote: Times are converted to UTC for server processing.`);
      
      setScheduleSlots([
        { id: 1, date: '', time: '' },
        { id: 2, date: '', time: '' },
        { id: 3, date: '', time: '' }
      ]);
      
      setScheduleMode(false);
      await fetchScheduledPosts();
    } else {
      alert('All scheduling attempts failed. Check browser console.');
      console.error('All failed. Results:', results);
    }
    
  } catch (error) {
    console.error('Scheduling error:', error);
    alert('Scheduling failed: ' + error.message);
    setError('Scheduling failed: ' + error.message);
  } finally {
    setLoading(false);
  }
}}




        disabled={loading || scheduleSlots.filter(s => s.date && s.time).length === 0}
        style={{
          width: '100%',
          padding: '14px',
          background: loading || scheduleSlots.filter(s => s.date && s.time).length === 0 ? '#ccc' : '#28a745',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '15px',
          fontWeight: '600',
          cursor: loading || scheduleSlots.filter(s => s.date && s.time).length === 0 ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Scheduling...' : `Schedule ${scheduleSlots.filter(s => s.date && s.time).length} Upload(s)`}
      </button>
    </div>
  )}
  
  {scheduledPosts.length > 0 && (
    <div style={{ marginTop: '24px' }}>
      <h4 style={{ color: '#333', marginBottom: '12px', fontSize: '15px' }}>
        Scheduled Uploads
      </h4>
      {scheduledPosts.map(post => (
        <div key={post.id} style={{
          background: 'white',
          padding: '12px',
          borderRadius: '8px',
          marginBottom: '8px',
          border: '1px solid #ddd',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: '600', fontSize: '13px', marginBottom: '4px' }}>
              {post.title}
            </div>
            <div style={{ fontSize: '11px', color: '#666' }}>
              {new Date(post.scheduled_for).toLocaleString()}
              {' '}
              <span style={{
                color: post.status === 'published' ? '#28a745' : 
                       post.status === 'failed' ? '#dc3545' : '#ffc107',
                fontWeight: '600'
              }}>
                {post.status.toUpperCase()}
              </span>
            </div>
          </div>
          {post.status === 'scheduled' && (
            <button
              onClick={() => deleteScheduledPost(post.id)}
              style={{
                padding: '6px 12px',
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                fontSize: '11px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
          )}
        </div>
      ))}
    </div>
  )}
</div>








                {/* ADD THE COMMUNITY POSTS SECTION HERE - AFTER UPLOAD BUTTON */}
                
                <div style={{ 
                  marginTop: '40px', 
                  paddingTop: '30px', 
                  borderTop: '2px solid #f0f0f0' 
                }}>
                  <h3 style={{ color: '#333', marginBottom: '20px' }}>📱 Community Posts</h3>
                  
                  <div style={{ marginBottom: '20px' }}>
                    <label style={{ 
                      display: 'block', 
                      marginBottom: '8px', 
                      fontWeight: '600', 
                      color: '#333' 
                    }}>
                      Post Type
                    </label>
                    <select 
                      value={contentData.post_type || 'text'} 
                      onChange={(e) => setContentData(prev => ({...prev, post_type: e.target.value}))}
                      style={{ 
                        width: '100%', 
                        padding: '12px', 
                        borderRadius: '8px', 
                        border: '2px solid #ddd', 
                        fontSize: '14px', 
                        marginBottom: '16px' 
                      }}
                    >
                      <option value="text">📝 Text Post</option>
                      <option value="image">🖼️ Image Post</option>
                      <option value="video">🎥 Video Post</option>
                      <option value="text_poll">📊 Text Poll</option>
                      <option value="image_poll">🖼️📊 Image Poll</option>
                      <option value="quiz">🎯 Quiz</option>
                    </select>
                    
                    <label style={{ 
                      display: 'block', 
                      marginBottom: '8px', 
                      fontWeight: '600', 
                      color: '#333' 
                    }}>
                      What's on your mind?
                    </label>
                    <textarea 
                      value={contentData.post_content || ''} 
                      onChange={(e) => setContentData(prev => ({...prev, post_content: e.target.value}))}
                      placeholder={
                        contentData.post_type === 'quiz' ? "Enter your quiz question..." :
                        contentData.post_type === 'text_poll' || contentData.post_type === 'image_poll' ? "Enter your poll question..." :
                        "What's on your mind? Share your thoughts with your community..."
                      }
                      rows={3}
                      style={{ 
                        width: '100%', 
                        padding: '12px', 
                        borderRadius: '8px', 
                        border: '2px solid #ddd', 
                        fontSize: '14px', 
                        resize: 'vertical', 
                        marginBottom: '16px' 
                      }}
                    />

                    {/* Image Upload for Image Posts/Polls */}
                    {(contentData.post_type === 'image' || contentData.post_type === 'image_poll') && (
                      <>
                        <label style={{ 
                          display: 'block', 
                          marginBottom: '8px', 
                          fontWeight: '600', 
                          color: '#333' 
                        }}>
                          Image URL
                        </label>
                        <input 
                          type="url" 
                          value={contentData.image_url || ''} 
                          onChange={(e) => setContentData(prev => ({...prev, image_url: e.target.value}))}
                          placeholder="https://example.com/image.jpg"
                          style={{ 
                            width: '100%', 
                            padding: '12px', 
                            borderRadius: '8px', 
                            border: '2px solid #ddd', 
                            fontSize: '14px', 
                            marginBottom: '16px' 
                          }}
                        />
                      </>
                    )}

                    {/* Poll Options */}
                    {(contentData.post_type === 'text_poll' || contentData.post_type === 'image_poll' || contentData.post_type === 'quiz') && (
                      <div style={{ marginBottom: '16px' }}>
                        <label style={{ 
                          display: 'block', 
                          marginBottom: '8px', 
                          fontWeight: '600', 
                          color: '#333' 
                        }}>
                          {contentData.post_type === 'quiz' ? 'Quiz Options' : 'Poll Options'}
                        </label>
                        {[0, 1, 2, 3].map(index => (
                          <input 
                            key={index}
                            type="text" 
                            value={contentData[`option_${index}`] || ''} 
                            onChange={(e) => setContentData(prev => ({...prev, [`option_${index}`]: e.target.value}))}
                            placeholder={`Option ${index + 1}${index === 0 || index === 1 ? ' (required)' : ' (optional)'}`}
                            style={{ 
                              width: '100%', 
                              padding: '10px', 
                              borderRadius: '6px', 
                              border: '1px solid #ddd', 
                              fontSize: '14px', 
                              marginBottom: '8px' 
                            }}
                          />
                        ))}
                        {contentData.post_type === 'quiz' && (
                          <>
                            <label style={{ 
                              display: 'block', 
                              marginTop: '12px',
                              marginBottom: '8px', 
                              fontWeight: '600', 
                              color: '#333' 
                            }}>
                              Correct Answer
                            </label>
                            <select 
                              value={contentData.correct_answer || '0'} 
                              onChange={(e) => setContentData(prev => ({...prev, correct_answer: e.target.value}))}
                              style={{ 
                                width: '100%', 
                                padding: '10px', 
                                borderRadius: '6px', 
                                border: '1px solid #ddd', 
                                fontSize: '14px' 
                              }}
                            >
                              <option value="0">Option 1</option>
                              <option value="1">Option 2</option>
                              <option value="2">Option 3</option>
                              <option value="3">Option 4</option>
                            </select>
                          </>
                        )}
                      </div>
                    )}

                    {/* Auto-schedule Toggle */}
                    <div style={{ 
                      marginBottom: '20px',
                      padding: '16px',
                      background: '#f8f9fa',
                      borderRadius: '8px',
                      border: '1px solid #ddd'
                    }}>
                      <label style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '8px', 
                        cursor: 'pointer',
                        marginBottom: '12px'
                      }}>
                        <input 
                          type="checkbox" 
                          checked={contentData.auto_schedule || false} 
                          onChange={(e) => setContentData(prev => ({...prev, auto_schedule: e.target.checked}))}
                          style={{ width: '16px', height: '16px' }}
                        />
                        <span style={{ fontSize: '14px', fontWeight: '600', color: '#333' }}>
                          🕒 Schedule for later
                        </span>
                      </label>
                      
                      {contentData.auto_schedule && (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                          <input 
                            type="date" 
                            value={contentData.schedule_date || ''} 
                            onChange={(e) => setContentData(prev => ({...prev, schedule_date: e.target.value}))}
                            min={new Date().toISOString().split('T')[0]}
                            style={{ 
                              padding: '8px', 
                              borderRadius: '4px', 
                              border: '1px solid #ddd', 
                              fontSize: '12px' 
                            }}
                          />
                          <input 
                            type="time" 
                            value={contentData.schedule_time || ''} 
                            onChange={(e) => setContentData(prev => ({...prev, schedule_time: e.target.value}))}
                            style={{ 
                              padding: '8px', 
                              borderRadius: '4px', 
                              border: '1px solid #ddd', 
                              fontSize: '12px' 
                            }}
                          />
                        </div>
                      )}
                    </div>

                    {/* AI Generate Post Button */}
                    <button 
                      onClick={generateCommunityPost}
                      disabled={loading}
                      style={{
                        width: '100%',
                        padding: '10px',
                        background: loading ? '#ccc' : '#28a745',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        marginBottom: '12px',
                        transition: 'background 0.3s ease'
                      }}
                    >
                      {loading ? '🤖 Generating...' : '🤖 AI Generate Post'}
                    </button>

                    {/* Publish Post Button */}
                    <button 
                      onClick={publishCommunityPost}
                      disabled={loading || !contentData.post_content}
                      style={{
                        width: '100%',
                        padding: '12px',
                        background: loading || !contentData.post_content ? '#ccc' : '#FF0000',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: loading || !contentData.post_content ? 'not-allowed' : 'pointer',
                        transition: 'background 0.3s ease'
                      }}
                    >
                      {loading ? '📤 Publishing...' : 
                       contentData.auto_schedule ? '🕒 Schedule Post' : '📤 Publish Post'}
                    </button>
                  </div>
                </div>


                



                <div style={{ 
                  marginTop: '20px', 
                  padding: '16px', 
                  background: '#fff3cd', 
                  border: '1px solid #ffeaa7', 
                  borderRadius: '8px' 
                }}>
                  <h4 style={{ 
                    color: '#856404', 
                    marginBottom: '8px', 
                    fontSize: '14px' 
                  }}>
                    Upload Tips:
                  </h4>
                  <ul style={{ 
                    fontSize: '12px', 
                    color: '#856404', 
                    paddingLeft: '16px', 
                    margin: 0 
                  }}>
                    <li>Video URL should be a direct link to an MP4 file</li>
                    <li>For YouTube Shorts: keep videos under 60 seconds</li>
                    <li>Use engaging titles with relevant keywords</li>
                    <li>Add detailed descriptions for better SEO</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
          }}>
            <h2 style={{ 
              color: '#FF0000', 
              marginBottom: '30px', 
              fontSize: '28px', 
              fontWeight: '700' 
            }}>
              Automation Dashboard
            </h2>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
              gap: '20px', 
              marginBottom: '40px' 
            }}>
              <StatusCard 
                title="Total Uploads" 
                value={status?.youtube_automation?.stats?.total_uploads || 0} 
              />
              <StatusCard 
                title="Successful Uploads" 
                value={status?.youtube_automation?.stats?.successful_uploads || 0} 
                color="#28a745" 
              />
              <StatusCard 
                title="Failed Uploads" 
                value={status?.youtube_automation?.stats?.failed_uploads || 0} 
                color="#dc3545" 
              />
              <StatusCard 
                title="Automation Status" 
                value={status?.youtube_automation?.enabled ? "Active" : "Inactive"} 
                color={status?.youtube_automation?.enabled ? "#28a745" : "#ffc107"} 
              />
            </div>

            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
              gap: '30px' 
            }}>
              <div style={{ 
                background: 'white', 
                borderRadius: '12px', 
                padding: '24px', 
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
              }}>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>Current Configuration</h3>
                <div style={{ fontSize: '14px', color: '#666', lineHeight: 1.6 }}>
                  <p><strong>Content Type:</strong> {config.content_type}</p>
                  <p><strong>Privacy Status:</strong> {config.privacy_status}</p>
                  <p><strong>Shorts per Day:</strong> {config.shorts_per_day}</p>
                  <p><strong>Videos per Week:</strong> {config.videos_per_week}</p>
                  <p><strong>Upload Schedule:</strong> {config.upload_schedule.join(', ')}</p>
                  <p><strong>Auto Features:</strong> 
                    {config.auto_generate_titles && ' Titles,'}
                    {config.auto_generate_descriptions && ' Descriptions,'}
                    {config.auto_add_tags && ' Tags'}
                  </p>
                </div>
              </div>

              <div style={{ 
                background: 'white', 
                borderRadius: '12px', 
                padding: '24px', 
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
              }}>
                <h3 style={{ color: '#333', marginBottom: '20px' }}>Channel Information</h3>
                <div style={{ fontSize: '14px', color: '#666', lineHeight: 1.6 }}>
                  <p><strong>Channel Name:</strong> {status?.channel_info?.channel_name || 'N/A'}</p>
                  <p><strong>Subscribers:</strong> {status?.channel_info?.subscriber_count || '0'}</p>
                  <p><strong>Total Videos:</strong> {status?.channel_info?.video_count || '0'}</p>
                  <p><strong>Total Views:</strong> {status?.channel_info?.view_count || '0'}</p>
                </div>
                
                <div style={{ marginTop: '20px' }}>
                  <button 
                    onClick={() => setActiveTab('analytics')}
                    style={{ 
                      padding: '10px 16px', 
                      background: '#007bff', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '6px', 
                      cursor: 'pointer', 
                      fontSize: '14px',
                      transition: 'background 0.3s ease'
                    }}
                  >
                    View Analytics
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '30px' 
            }}>
              <h2 style={{ 
                color: '#FF0000', 
                fontSize: '28px', 
                fontWeight: '700', 
                margin: 0 
              }}>
                Channel Analytics
              </h2>
              <button 
                onClick={fetchAnalytics}
                disabled={loading}
                style={{
                  padding: '10px 16px',
                  background: loading ? '#ccc' : '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  transition: 'background 0.3s ease'
                }}
              >
                {loading ? 'Loading...' : 'Refresh Analytics'}
              </button>
            </div>
            
            {analytics ? (
              <div>
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                  gap: '20px', 
                  marginBottom: '30px' 
                }}>
                  <StatusCard 
                    title="Total Subscribers" 
                    value={analytics.channel_statistics?.subscriberCount || '0'} 
                    color="#FF0000" 
                  />
                  <StatusCard 
                    title="Total Views" 
                    value={analytics.channel_statistics?.viewCount || '0'} 
                    color="#28a745" 
                  />
                  <StatusCard 
                    title="Total Videos" 
                    value={analytics.channel_statistics?.videoCount || '0'} 
                    color="#007bff" 
                  />
                  <StatusCard 
                    title="Analysis Period" 
                    value={`${analytics.period_days} days`} 
                    color="#6f42c1" 
                  />
                </div>

                <div style={{ 
                  background: 'white', 
                  borderRadius: '12px', 
                  padding: '24px', 
                  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' 
                }}>
                  <h3 style={{ color: '#333', marginBottom: '20px' }}>
                    Recent Videos Performance
                  </h3>
                  
                  {analytics.recent_videos && analytics.recent_videos.length > 0 ? (
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ 
                        width: '100%', 
                        borderCollapse: 'collapse', 
                        fontSize: '14px' 
                      }}>
                        <thead>
                          <tr style={{ background: '#f8f9fa' }}>
                            <th style={{ 
                              padding: '12px', 
                              textAlign: 'left', 
                              borderBottom: '2px solid #dee2e6' 
                            }}>
                              Title
                            </th>
                            <th style={{ 
                              padding: '12px', 
                              textAlign: 'center', 
                              borderBottom: '2px solid #dee2e6' 
                            }}>
                              Views
                            </th>
                            <th style={{ 
                              padding: '12px', 
                              textAlign: 'center', 
                              borderBottom: '2px solid #dee2e6' 
                            }}>
                              Likes
                            </th>
                            <th style={{ 
                              padding: '12px', 
                              textAlign: 'center', 
                              borderBottom: '2px solid #dee2e6' 
                            }}>
                              Comments
                            </th>
                            <th style={{ 
                              padding: '12px', 
                              textAlign: 'center', 
                              borderBottom: '2px solid #dee2e6' 
                            }}>
                              Published
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {analytics.recent_videos.map((video, index) => (
                            <tr key={index} style={{ borderBottom: '1px solid #dee2e6' }}>
                              <td style={{ padding: '12px', maxWidth: '300px' }}>
                                <div style={{ 
                                  fontWeight: '600', 
                                  color: '#333', 
                                  marginBottom: '4px' 
                                }}>
                                  {video.title.length > 50 ? 
                                    video.title.substring(0, 50) + '...' : 
                                    video.title
                                  }
                                </div>
                                <div style={{ fontSize: '12px', color: '#666' }}>
                                  ID: {video.video_id}
                                </div>
                              </td>
                              <td style={{ padding: '12px', textAlign: 'center' }}>
                                <span style={{ 
                                  background: '#e3f2fd', 
                                  color: '#1976d2', 
                                  padding: '4px 8px', 
                                  borderRadius: '12px', 
                                  fontSize: '12px', 
                                  fontWeight: '600' 
                                }}>
                                  {parseInt(video.view_count).toLocaleString()}
                                </span>
                              </td>
                              <td style={{ padding: '12px', textAlign: 'center' }}>
                                <span style={{ 
                                  background: '#e8f5e8', 
                                  color: '#2e7d2e', 
                                  padding: '4px 8px', 
                                  borderRadius: '12px', 
                                  fontSize: '12px', 
                                  fontWeight: '600' 
                                }}>
                                  {parseInt(video.like_count).toLocaleString()}
                                </span>
                              </td>
                              <td style={{ padding: '12px', textAlign: 'center' }}>
                                <span style={{ 
                                  background: '#fff3e0', 
                                  color: '#f57c00', 
                                  padding: '4px 8px', 
                                  borderRadius: '12px', 
                                  fontSize: '12px', 
                                  fontWeight: '600' 
                                }}>
                                  {parseInt(video.comment_count).toLocaleString()}
                                </span>
                              </td>
                              <td style={{ 
                                padding: '12px', 
                                textAlign: 'center', 
                                fontSize: '12px', 
                                color: '#666' 
                              }}>
                                {new Date(video.published_at).toLocaleDateString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div style={{ 
                      textAlign: 'center', 
                      padding: '40px', 
                      color: '#666' 
                    }}>
                      <div style={{ fontSize: '48px', marginBottom: '16px' }}>📊</div>
                      <p>No recent videos found. Upload some content to see analytics here!</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div style={{ 
                textAlign: 'center', 
                padding: '60px', 
                color: '#666' 
              }}>
                <div style={{ fontSize: '64px', marginBottom: '20px' }}>📈</div>
                <h3 style={{ color: '#333', marginBottom: '16px' }}>Analytics Not Loaded</h3>
                <p style={{ marginBottom: '20px' }}>
                  Click "Refresh Analytics" to load your channel's performance data.
                </p>
                <button 
                  onClick={fetchAnalytics}
                  style={{ 
                    padding: '12px 24px', 
                    background: '#FF0000', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '8px', 
                    cursor: 'pointer', 
                    fontWeight: '600',
                    transition: 'background 0.3s ease'
                  }}
                >
                  Load Analytics
                </button>
              </div>
            )}
          </div>
        )}






{/* Comments Management Tab */}
        {activeTab === 'comments' && status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
          }}>
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center', 
              marginBottom: '30px' 
            }}>
              <h2 style={{ 
                color: '#FF0000', 
                fontSize: '28px', 
                fontWeight: '700', 
                margin: 0 
              }}>
                💬 Comments Management
              </h2>
              
              <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                <button 
                  onClick={fetchUserVideos}
                  disabled={loadingVideos}
                  style={{
                    padding: '10px 16px',
                    background: loadingVideos ? '#ccc' : '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loadingVideos ? 'not-allowed' : 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {loadingVideos ? 'Loading...' : 'Load My Videos'}
                </button>
                
                {autoReplyEnabled ? (
                  <button
                    onClick={stopAutomatedReplies}
                    style={{
                      padding: '10px 16px',
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}
                  >
                    ⏹️ Stop Auto-Reply
                  </button>
                ) : (
                  <button
                    onClick={startAutoReplyForSelectedVideos}
                    disabled={selectedVideos.length === 0}
                    style={{
                      padding: '10px 16px',
                      background: selectedVideos.length === 0 ? '#ccc' : '#28a745',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: selectedVideos.length === 0 ? 'not-allowed' : 'pointer',
                      fontSize: '14px',
                      fontWeight: '600'
                    }}
                  >
                    🤖 Start Auto-Reply ({selectedVideos.length} videos)
                  </button>
                )}
              </div>
            </div>

            {/* Video Selection Panel */}
            {userVideos.length > 0 && (
              <div style={{
                background: '#f8f9fa',
                padding: '20px',
                borderRadius: '12px',
                marginBottom: '30px',
                border: '2px solid #007bff'
              }}>
                <h3 style={{ color: '#007bff', marginBottom: '16px' }}>📹 Select Videos for Auto-Reply</h3>
                
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                  gap: '12px',
                  maxHeight: '400px',
                  overflowY: 'auto'
                }}>
                  {userVideos.map((video, index) => (
                    <div 
                      key={video.video_id}
                      onClick={() => {
                        const isSelected = selectedVideos.includes(video.video_id);
                        if (isSelected) {
                          setSelectedVideos(prev => prev.filter(id => id !== video.video_id));
                        } else {
                          setSelectedVideos(prev => [...prev, video.video_id]);
                          fetchVideoComments(video.video_id);
                        }
                      }}
                      style={{
                        padding: '12px',
                        background: selectedVideos.includes(video.video_id) ? '#d4edda' : 'white',
                        border: selectedVideos.includes(video.video_id) ? '2px solid #28a745' : '1px solid #ddd',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        transition: 'all 0.3s ease'
                      }}
                    >
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        marginBottom: '8px'
                      }}>
                        <input
                          type="checkbox"
                          checked={selectedVideos.includes(video.video_id)}
                          onChange={() => {}}
                          style={{ width: '16px', height: '16px' }}
                        />
                        <span style={{
                          fontWeight: '600',
                          fontSize: '13px',
                          color: selectedVideos.includes(video.video_id) ? '#155724' : '#333'
                        }}>
                          {video.title.length > 40 ? video.title.substring(0, 40) + '...' : video.title}
                        </span>
                      </div>
                      
                      <div style={{
                        fontSize: '11px',
                        color: '#666',
                        display: 'flex',
                        justifyContent: 'space-between'
                      }}>
                        <span>👁️ {video.view_count} views</span>
                        <span>💬 {video.comment_count} comments</span>
                      </div>
                    </div>
                  ))}
                </div>
                
                <div style={{
                  marginTop: '16px',
                  display: 'flex',
                  gap: '12px',
                  alignItems: 'center'
                }}>
                  <button
                    onClick={() => {
                      setSelectedVideos(userVideos.map(v => v.video_id));
                      userVideos.forEach(video => fetchVideoComments(video.video_id));
                    }}
                    style={{
                      padding: '8px 16px',
                      background: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Select All
                  </button>
                  
                  <button
                    onClick={() => setSelectedVideos([])}
                    style={{
                      padding: '8px 16px',
                      background: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      fontSize: '12px',
                      cursor: 'pointer'
                    }}
                  >
                    Clear All
                  </button>
                  
                  <span style={{
                    fontSize: '13px',
                    color: '#666',
                    fontWeight: '500'
                  }}>
                    {selectedVideos.length} of {userVideos.length} videos selected
                  </span>
                </div>
              </div>
            )}

            {/* Auto-Reply Configuration */}
            <div style={{
              background: '#f8f9fa',
              padding: '20px',
              borderRadius: '12px',
              marginBottom: '30px',
              border: '2px solid #28a745'
            }}>
              <h3 style={{ color: '#28a745', marginBottom: '16px' }}>🤖 Automated Reply Settings</h3>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px',
                marginBottom: '16px'
              }}>
                <div>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '4px', 
                    fontSize: '14px', 
                    fontWeight: '600' 
                  }}>
                    Reply Style
                  </label>
                  <select
                    value={autoReplyConfig.reply_style}
                    onChange={(e) => setAutoReplyConfig(prev => ({
                      ...prev, 
                      reply_style: e.target.value
                    }))}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  >
                    <option value="friendly">Friendly</option>
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="enthusiastic">Enthusiastic</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '4px', 
                    fontSize: '14px', 
                    fontWeight: '600' 
                  }}>
                    Reply Delay (seconds)
                  </label>
                  <select
                    value={autoReplyConfig.reply_delay_seconds || 30}
                    onChange={(e) => setAutoReplyConfig(prev => ({
                      ...prev, 
                      reply_delay_seconds: parseInt(e.target.value)
                    }))}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  >
                    <option value="15">15 seconds</option>
                    <option value="30">30 seconds</option>
                    <option value="60">1 minute</option>
                    <option value="180">3 minutes</option>
                    <option value="240">4 minutes</option>
                  </select>
                </div>
                
                <div>
                  <label style={{ 
                    display: 'block', 
                    marginBottom: '4px', 
                    fontSize: '14px', 
                    fontWeight: '600' 
                  }}>
                    Max Replies/Hour
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={autoReplyConfig.max_replies_per_hour}
                    onChange={(e) => setAutoReplyConfig(prev => ({
                      ...prev, 
                      max_replies_per_hour: parseInt(e.target.value)
                    }))}
                    style={{
                      width: '100%',
                      padding: '8px',
                      borderRadius: '4px',
                      border: '1px solid #ddd',
                      fontSize: '14px'
                    }}
                  />
                </div>
              </div>
              
              <div>
                <label style={{ 
                  display: 'block', 
                  marginBottom: '8px', 
                  fontSize: '14px', 
                  fontWeight: '600' 
                }}>
                  Custom Reply Instructions (Optional)
                </label>
                <textarea
                  value={autoReplyConfig.custom_prompt}
                  onChange={(e) => setAutoReplyConfig(prev => ({
                    ...prev, 
                    custom_prompt: e.target.value
                  }))}
                  placeholder="e.g., Always mention to subscribe, be enthusiastic about cooking videos..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '8px',
                    borderRadius: '4px',
                    border: '1px solid #ddd',
                    fontSize: '14px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{
                marginTop: '12px',
                padding: '12px',
                background: autoReplyEnabled ? '#d4edda' : '#fff3cd',
                borderRadius: '6px',
                fontSize: '13px',
                color: autoReplyEnabled ? '#155724' : '#856404'
              }}>
                <strong>Status:</strong> {autoReplyEnabled 
                  ? `✅ Auto-reply ACTIVE for ${selectedVideos.length} video(s) - IST timezone detected` 
                  : '⏸️ Auto-reply INACTIVE - select videos and click Start'}
              </div>
            </div>

            {/* Comments Display by Video */}
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
            }}>
              <h3 style={{ color: '#333', marginBottom: '20px' }}>
                Recent Comments {selectedVideos.length > 0 && `(${selectedVideos.length} selected videos)`}
              </h3>
              
              {selectedVideos.length > 0 ? (
                <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
                  {selectedVideos.map((videoId, videoIndex) => {
                    const video = userVideos.find(v => v.video_id === videoId);
                    const comments = videoComments[videoId] || [];
                    
                    return (
                      <div key={videoId} style={{
                        marginBottom: '30px',
                        padding: '16px',
                        background: videoIndex % 2 === 0 ? '#f8f9fa' : '#e3f2fd',
                        borderRadius: '8px',
                        border: '2px solid #007bff'
                      }}>
                        <div style={{
                          fontWeight: '700',
                          fontSize: '16px',
                          color: '#007bff',
                          marginBottom: '12px',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px'
                        }}>
                          📹 {video?.title || `Video ${videoIndex + 1}`}
                          <span style={{
                            fontSize: '12px',
                            background: '#007bff',
                            color: 'white',
                            padding: '2px 8px',
                            borderRadius: '12px'
                          }}>
                            {comments.length} comments
                          </span>
                        </div>
                        
                        {comments.length > 0 ? (
                          comments.map((comment, index) => (
                            <div key={comment.comment_id} style={{
                              padding: '12px',
                              background: 'white',
                              borderRadius: '6px',
                              marginBottom: '8px',
                              border: '1px solid #ddd'
                            }}>
                              <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'flex-start'
                              }}>
                                <div style={{ flex: 1 }}>
                                  <div style={{
                                    fontWeight: '600',
                                    fontSize: '13px',
                                    color: '#333',
                                    marginBottom: '4px'
                                  }}>
                                    {comment.author_name}
                                  </div>
                                  <div style={{
                                    fontSize: '14px',
                                    color: '#666',
                                    marginBottom: '8px'
                                  }}>
                                    {comment.text}
                                  </div>
                                  <div style={{
                                    fontSize: '11px',
                                    color: '#999',
                                    display: 'flex',
                                    gap: '12px'
                                  }}>
                                    <span>👍 {comment.like_count}</span>
                                    <span>💬 {comment.reply_count} replies</span>
                                    <span>{new Date(comment.published_at).toLocaleDateString()}</span>
                                  </div>
                                </div>
                                
                                <div style={{
                                  display: 'flex',
                                  gap: '4px',
                                  flexDirection: 'column'
                                }}>
                                  <button
                                    onClick={() => generateAutoReply(comment.text, comment.comment_id)}
                                    style={{
                                      padding: '4px 8px',
                                      background: '#28a745',
                                      color: 'white',
                                      border: 'none',
                                      borderRadius: '4px',
                                      fontSize: '11px',
                                      cursor: 'pointer'
                                    }}
                                  >
                                    🤖 Reply Now
                                  </button>
                                  
                                  <button
                                    onClick={() => deleteComment(comment.comment_id)}
                                    style={{
                                      padding: '4px 8px',
                                      background: '#dc3545',
                                      color: 'white',
                                      border: 'none',
                                      borderRadius: '4px',
                                      fontSize: '11px',
                                      cursor: 'pointer'
                                    }}
                                  >
                                    🗑️ Delete
                                  </button>
                                </div>
                              </div>
                              
                              {/* Manual Reply Section */}
                              <div style={{
                                marginTop: '12px',
                                paddingTop: '12px',
                                borderTop: '1px solid #eee'
                              }}>
                                <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
                                  <div style={{ flex: 1 }}>
                                    <label style={{
                                      display: 'block',
                                      fontSize: '12px',
                                      fontWeight: '600',
                                      marginBottom: '4px',
                                      color: '#555'
                                    }}>
                                      Manual Reply:
                                    </label>
                                    <textarea
                                      value={replyText}
                                      onChange={(e) => setReplyText(e.target.value)}
                                      placeholder="Type your reply..."
                                      rows={2}
                                      style={{
                                        width: '100%',
                                        padding: '8px',
                                        borderRadius: '4px',
                                        border: '1px solid #ddd',
                                        fontSize: '13px',
                                        resize: 'none'
                                      }}
                                    />
                                  </div>
                                  <button
                                    onClick={() => {
                                      if (replyText.trim()) {
                                        replyToComment(comment.comment_id, replyText);
                                      }
                                    }}
                                    disabled={!replyText.trim()}
                                    style={{
                                      padding: '8px 12px',
                                      background: replyText.trim() ? '#007bff' : '#ccc',
                                      color: 'white',
                                      border: 'none',
                                      borderRadius: '4px',
                                      fontSize: '12px',
                                      cursor: replyText.trim() ? 'pointer' : 'not-allowed',
                                      whiteSpace: 'nowrap'
                                    }}
                                  >
                                    📤 Send Reply
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))
                        ) : (
                          <div style={{
                            textAlign: 'center',
                            padding: '20px',
                            color: '#666',
                            fontStyle: 'italic'
                          }}>
                            No comments found for this video
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  padding: '40px', 
                  color: '#666' 
                }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>📹</div>
                  <p>Select videos from above to view and manage their comments</p>
                  <button 
                    onClick={fetchUserVideos}
                    style={{ 
                      padding: '8px 16px', 
                      background: '#007bff', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '6px', 
                      cursor: 'pointer', 
                      fontWeight: '600',
                      marginTop: '12px'
                    }}
                  >
                    Load My Videos
                  </button>
                </div>
              )}
            </div>
          </div>
        )}




{/* Image Slideshow Tab */}
{activeTab === 'slideshow' && status?.youtube_connected && (
  <div style={{ 
    background: 'rgba(255, 255, 255, 0.95)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
  }}>
    <h2 style={{ 
      color: '#FF0000', 
      marginBottom: '30px', 
      fontSize: '28px', 
      fontWeight: '700' 
    }}>
      🎬 Create Image Slideshow
    </h2>

    <div style={{ 
      background: '#fff3cd', 
      padding: '16px', 
      borderRadius: '8px', 
      marginBottom: '30px',
      border: '1px solid #ffc107'
    }}>
      <strong>🚀 Transform Images into Viral Videos!</strong>
      <p style={{ margin: '8px 0 0 0', fontSize: '14px' }}>
        Upload 2-6 images → AI adds transitions & text → Upload to YouTube Shorts
      </p>
    </div>

    {/* Tab Selector */}
    <div style={{ display: 'flex', gap: '12px', marginBottom: '30px' }}>
      <button
        onClick={() => {
          setSlideshowTab('manual');
          setUploadedImages([]);
          setProductUrl('');
          setScrapedProduct(null);
          setSlideshowTitle('');
          setSlideshowDescription('');
          setError('');
        }}
        style={{
          padding: '12px 24px',
          background: slideshowTab === 'manual' ? '#FF0000' : '#f0f0f0',
          color: slideshowTab === 'manual' ? 'white' : '#333',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '16px'
        }}
      >
        📸 Manual Images
      </button>
      <button
        onClick={() => {
          setSlideshowTab('product');
          setUploadedImages([]);
          setSlideshowTitle('');
          setSlideshowDescription('');
          setScrapedProduct(null);
          setProductUrl('');
          setError('');
        }}
        style={{
          padding: '12px 24px',
          background: slideshowTab === 'product' ? '#FF0000' : '#f0f0f0',
          color: slideshowTab === 'product' ? 'white' : '#333',
          border: 'none',
          borderRadius: '8px',
          cursor: 'pointer',
          fontWeight: '600',
          fontSize: '16px'
        }}
      >
        🛒 Product URL
      </button>
    </div>

    {/* MANUAL IMAGES TAB */}
    {slideshowTab === 'manual' && (
      <div>
        {/* Step 1: Upload Images */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
            📸 Step 1: Add Images (2-6)
          </h3>
          
          <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
            <button
              onClick={() => setUploadMethod('file')}
              style={{
                padding: '8px 16px',
                background: uploadMethod === 'file' ? '#FF0000' : '#f0f0f0',
                color: uploadMethod === 'file' ? 'white' : '#333',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              📂 Upload Files
            </button>
            <button
              onClick={() => setUploadMethod('url')}
              style={{
                padding: '8px 16px',
                background: uploadMethod === 'url' ? '#FF0000' : '#f0f0f0',
                color: uploadMethod === 'url' ? 'white' : '#333',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              🔗 Use Image URLs
            </button>
          </div>

          {uploadMethod === 'file' && (
            <input
              type="file"
              accept="image/*"
              multiple
              onChange={async (e) => {
                const files = Array.from(e.target.files).slice(0, 6);
                if (files.length < 2) {
                  alert('Please upload at least 2 images');
                  e.target.value = '';
                  return;
                }
                setLoading(true);
                try {
                  const base64Images = await Promise.all(
                    files.map((file) => new Promise((resolve, reject) => {
                      const reader = new FileReader();
                      reader.onload = () => resolve(reader.result);
                      reader.onerror = () => reject(new Error('Failed to read image'));
                      reader.readAsDataURL(file);
                    }))
                  );
                  setUploadedImages(base64Images);
                } catch (error) {
                  alert('Error: ' + error.message);
                } finally {
                  setLoading(false);
                }
              }}
              style={{
                padding: '12px',
                width: '100%',
                border: '2px dashed #FF0000',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            />
          )}
          {/* ////////////////////////////////////////////////////////////////////////////////////// */}
          

          {/* {uploadMethod === 'url' && (
            <div>
              <textarea
                value={imageUrls}
                onChange={(e) => setImageUrls(e.target.value)}
                placeholder="https://picsum.photos/1080/1920?random=1&#x0A;https://picsum.photos/1080/1920?random=2"
                rows={6}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '2px dashed #FF0000',
                  fontSize: '14px'
                }}
              /> */}

              {/* {uploadMethod === 'url' && (
  <div>
    <textarea
      value={imageUrls}
      onChange={(e) => setImageUrls(e.target.value)}
      placeholder={`https://picsum.photos/1080/1920?random=1
https://picsum.photos/1080/1920?random=2`}
      rows={6}
      style={{
        width: '100%',
        padding: '12px',
        borderRadius: '8px',
        border: '2px dashed #FF0000',
        fontSize: '14px'
      }}
    />

              <button

                onClick={async () => {
                  const urls = imageUrls.split('\n').filter(u => u.trim());
                  if (urls.length < 2 || urls.length > 6) {
                    alert('Enter 2-6 image URLs');
                    return;
                  }
                  setLoading(true);
                  try {
                    const base64Images = await Promise.all(
                      urls.map(async (url) => {
                        const response = await fetch(url);
                        const blob = await response.blob();
                        return new Promise((resolve) => {
                          const reader = new FileReader();
                          reader.onload = () => resolve(reader.result);
                          reader.readAsDataURL(blob);
                        });
                      })
                    );
                    setUploadedImages(base64Images);
                    alert('Images loaded!');
                  } catch (error) {
                    alert('Error: ' + error.message);
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                style={{
                  marginTop: '12px',
                  padding: '10px 20px',
                  background: loading ? '#ccc' : '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? '⏳ Loading...' : '📥 Load Images'}
              </button>
            </div>
          )} */}
          
{uploadMethod === 'url' && (
            <div>
              <textarea
                value={imageUrls}
                onChange={(e) => setImageUrls(e.target.value)}
                placeholder="Paste image URLs here (one per line), or leave empty to use 3 default images"
                rows={6}
                style={{
                  width: '100%',
                  padding: '12px',
                  borderRadius: '8px',
                  border: '2px dashed #FF0000',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={async () => {
                  // ✅ Use default URLs if textarea is empty
                  const finalUrls = imageUrls.trim() === '' ? DEFAULT_IMAGE_URLS : imageUrls;
                  
                  const urls = finalUrls.split('\n').filter(u => u.trim());
                  if (urls.length < 2 || urls.length > 6) {
                    alert('Enter 2-6 image URLs');
                    return;
                  }
                  setLoading(true);
                  try {
                    const base64Images = await Promise.all(
                      urls.map(async (url) => {
                        const response = await fetch(url);
                        const blob = await response.blob();
                        return new Promise((resolve) => {
                          const reader = new FileReader();
                          reader.onload = () => resolve(reader.result);
                          reader.readAsDataURL(blob);
                        });
                      })
                    );
                    setUploadedImages(base64Images);
                    alert('✅ Images loaded successfully!');
                  } catch (error) {
                    alert('❌ Error loading images: ' + error.message);
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading}
                style={{
                  marginTop: '12px',
                  padding: '10px 20px',
                  background: loading ? '#ccc' : '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontWeight: '600'
                }}
              >
                {loading ? '⏳ Loading...' : '📥 Load Images (or use 3 defaults)'}
              </button>
            </div>
          )}



          {/* ######################################################################################### */}
          {uploadedImages.length > 0 && (
            <div style={{marginTop: '20px'}}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                {uploadedImages.map((img, idx) => (
                  <div key={idx} style={{ position: 'relative' }}>
                    <img 
                      src={img} 
                      alt={`Upload ${idx + 1}`} 
                      style={{
                        width: '100%',
                        height: '200px',
                        objectFit: 'cover',
                        borderRadius: '8px'
                      }}
                    />
                    <button
                      onClick={() => setUploadedImages(prev => prev.filter((_, i) => i !== idx))}
                      style={{
                        position: 'absolute',
                        top: '8px',
                        right: '8px',
                        background: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '50%',
                        width: '30px',
                        height: '30px',
                        cursor: 'pointer'
                      }}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
              <div style={{marginTop: '12px', padding: '12px', background: '#d4edda', borderRadius: '6px'}}>
                ✅ {uploadedImages.length} images uploaded
              </div>
            </div>
          )}
        </div>




{/* =========================================== */}


{/* NEW: Music Selection */}
{uploadedImages.length >= 2 && (
  <div style={{ marginBottom: '30px' }}>
    <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
      🎵 Select Background Music
    </h3>
    
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
      gap: '12px',
      marginBottom: '16px'
    }}>
      {[
        { value: 'upbeat', label: 'Upbeat 😄', color: '#FF6B6B', desc: 'Happy & energetic' },
        { value: 'energetic', label: 'Energetic ⚡', color: '#4ECDC4', desc: 'High energy' },
        { value: 'cinematic', label: 'Cinematic 🎬', color: '#95E1D3', desc: 'Premium & dramatic' },
        { value: 'relaxing', label: 'Relaxing 🌿', color: '#38B2AC', desc: 'Calm & peaceful' },
        { value: 'sad', label: 'Emotional 😔', color: '#667eea', desc: 'Sad & touching' },
        { value: 'dark', label: 'Dark 🖤', color: '#2D3748', desc: 'Mysterious' },
        { value: 'lofi', label: 'Lo-Fi 🎧', color: '#FF8C42', desc: 'Chill vibes' },
        { value: 'happy', label: 'Happy 😊', color: '#FFC107', desc: 'Fun & joyful' },
        { value: 'motivational', label: 'Motivational 🔥', color: '#E74C3C', desc: 'Inspiring' }
      ].map((music) => (
        <button
          key={music.value}
          onClick={() => setSlideshowConfig(prev => ({
            ...prev,
            music_style: music.value
          }))}
          style={{
            padding: '16px 12px',
            background: slideshowConfig.music_style === music.value 
              ? `linear-gradient(135deg, ${music.color}, ${music.color}dd)` 
              : '#f8f9fa',
            color: slideshowConfig.music_style === music.value ? 'white' : '#333',
            border: slideshowConfig.music_style === music.value 
              ? `3px solid ${music.color}` 
              : '2px solid #ddd',
            borderRadius: '12px',
            cursor: 'pointer',
            fontWeight: '700',
            fontSize: '13px',
            textAlign: 'center',
            transition: 'all 0.3s',
            boxShadow: slideshowConfig.music_style === music.value 
              ? `0 4px 15px ${music.color}40` 
              : '0 2px 5px rgba(0,0,0,0.1)'
          }}
        >
          <div>{music.label}</div>
          <div style={{
            fontSize: '10px',
            marginTop: '4px',
            opacity: 0.9,
            fontWeight: '500'
          }}>
            {music.desc}
          </div>
        </button>
      ))}
    </div>
    
    <div style={{
      padding: '12px',
      background: '#e7f3ff',
      borderRadius: '8px',
      fontSize: '13px',
      color: '#004085',
      border: '1px solid #bee5eb'
    }}>
      ✅ Selected: <strong>{slideshowConfig.music_style.charAt(0).toUpperCase() + slideshowConfig.music_style.slice(1)}</strong> - Random track will be chosen from 5 options
    </div>
  </div>
)}
{/* ================================== */}













        {/* Step 2: Title & Description - NO AI FOR TITLE */}
        {/* {uploadedImages.length >= 2 && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
              ✍️ Step 2: Add Title & Description
            </h3>




            
            <label style={{display: 'block', marginBottom: '8px', fontWeight: '600'}}>
              Video Title:
            </label>
            <input
              type="text"
              value={slideshowTitle}
              onChange={(e) => setSlideshowTitle(e.target.value)}
              placeholder="Enter an engaging title for your video"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontSize: '15px',
                marginBottom: '20px'
              }}
            />





            

            <label style={{display: 'block', marginBottom: '8px', fontWeight: '600'}}>
              Video Description:
            </label>
            <div style={{display: 'flex', gap: '10px', marginBottom: '10px'}}>
              <textarea
                value={slideshowDescription}
                onChange={(e) => setSlideshowDescription(e.target.value)}
                placeholder="Enter description or click AI Generate for suggestions with hashtags"
                rows={6}
                style={{
                  flex: 1,
                  padding: '12px',
                  borderRadius: '8px',
                  border: '2px solid #ddd',
                  fontSize: '14px'
                }}
              />
              <button
                onClick={async () => {
                  if (!slideshowTitle) {
                    alert('Please enter a title first');
                    return;
                  }
                  setLoading(true);
                  try {
                    const response = await fetch(`${API_BASE}/api/ai/generate-youtube-content`, {
                      method: 'POST',
                      headers: {'Content-Type': 'application/json'},
                      body: JSON.stringify({
                        content_type: 'shorts',
                        topic: slideshowTitle,
                        target_audience: 'general',
                        duration_seconds: 30
                      })
                    });
                    const result = await response.json();
                    if (result.success) {
                      setSlideshowDescription(result.description + '\n\n' + result.tags.map(t => '#' + t).join(' '));
                    }
                  } catch (error) {
                    alert('AI generation failed: ' + error.message);
                  } finally {
                    setLoading(false);
                  }
                }}
                disabled={loading || !slideshowTitle}
                style={{
                  padding: '12px 20px',
                  background: (loading || !slideshowTitle) ? '#ccc' : '#FF0000',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: (loading || !slideshowTitle) ? 'not-allowed' : 'pointer',
                  whiteSpace: 'nowrap',
                  alignSelf: 'flex-start',
                  height: 'fit-content'
                }}
              >
                {loading ? '⏳' : '🤖 AI Enhance'}
              </button>
            </div>
          </div>
        )} */}




{/* ===== STEP 2: AI-POWERED TITLE & DESCRIPTION ===== */}
        {uploadedImages.length >= 2 && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
              ✍️ Step 2: Add Title & Description
            </h3>
            
            {/* ===== AI VIRAL TITLE GENERATOR ===== */}
            <div style={{ 
              marginBottom: '25px',
              padding: '20px',
              background: 'linear-gradient(135deg, #667eea10, #764ba210)',
              borderRadius: '12px',
              border: '2px solid #667eea'
            }}>
              <label style={{
                display: 'block', 
                marginBottom: '12px', 
                fontWeight: '700',
                color: '#667eea',
                fontSize: '16px'
              }}>
                🤖 AI Viral Title Generator
              </label>
              
              {/* Topic Input (3-5 words) */}
              <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
                <input
                  type="text"
                  value={contentData.ai_topic || ''}
                  onChange={(e) => setContentData(prev => ({...prev, ai_topic: e.target.value}))}
                  placeholder="Enter 3-5 keywords (e.g., 'manali hidden waterfall trek')"
                  style={{
                    flex: 1,
                    padding: '14px',
                    borderRadius: '8px',
                    border: '2px solid #ddd',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                  onFocus={(e) => e.target.style.borderColor = '#667eea'}
                  onBlur={(e) => e.target.style.borderColor = '#ddd'}
                />
                <button
                  onClick={async () => {
                    const topic = contentData.ai_topic?.trim();
                    const wordCount = topic ? topic.split(' ').filter(w => w).length : 0;
                    
                    if (!topic || wordCount < 3) {
                      alert('⚠️ Please enter at least 3-5 words about your video\n\nExample: "manali hidden waterfall trek"');
                      return;
                    }
                    
                    setLoading(true);
                    setError('');
                    
                    try {
                      console.log('🎯 Generating titles for:', topic);
                      
                      const response = await fetch(`${API_BASE}/api/youtube/generate-viral-titles`, {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          'Authorization': `Bearer ${token}`
                        },
                        body: JSON.stringify({
                          topic: topic,
                          niche: 'shorts'
                        })
                      });
                      
                      const result = await response.json();
                      console.log('📥 Response:', result);
                      
                      if (result.success && result.titles && result.titles.length > 0) {
                        setContentData(prev => ({
                          ...prev,
                          viral_titles: result.titles,
                          title: result.titles[0].title, // Auto-select highest scoring
                          description: result.description || prev.description,
                          tags: result.tags || []
                        }));
                        
                        // Also update slideshow states
                        setSlideshowTitle(result.titles[0].title);
                        setSlideshowDescription(result.description || '');
                        
                        alert(`✅ Generated 5 viral titles!\n\n🏆 Top pick: "${result.titles[0].title}"\n\nClick any title below to select it.`);
                      } else {
                        alert('❌ Failed: ' + (result.error || 'No titles generated'));
                      }
                    } catch (error) {
                      console.error('❌ Error:', error);
                      alert('❌ Error: ' + error.message);
                    } finally {
                      setLoading(false);
                    }
                  }}
                  disabled={loading}
                  style={{
                    padding: '14px 28px',
                    background: loading 
                      ? '#ccc' 
                      : 'linear-gradient(135deg, #667eea, #764ba2)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '10px',
                    fontWeight: '700',
                    fontSize: '15px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    whiteSpace: 'nowrap',
                    boxShadow: loading ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)',
                    transition: 'all 0.3s'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  {loading ? '⏳ Generating...' : '🚀 Generate 5 Titles'}
                </button>
              </div>
              
              {/* Helper Text */}
              <div style={{
                fontSize: '12px',
                color: '#666',
                marginBottom: '15px'
              }}>
                💡 <strong>Tip:</strong> Use specific keywords like "manali snow trek" instead of just "travel video"
              </div>
              
              {/* Display Generated Title Options */}
              {contentData.viral_titles && contentData.viral_titles.length > 0 && (
                <div style={{
                  background: 'white',
                  padding: '16px',
                  borderRadius: '10px',
                  border: '2px solid #667eea',
                  marginTop: '15px'
                }}>
                  <h4 style={{ 
                    color: '#667eea', 
                    marginBottom: '12px', 
                    fontSize: '15px',
                    fontWeight: '700',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}>
                    <span style={{ fontSize: '20px' }}>🎯</span>
                    Pick Your Viral Title (Click to Select)
                  </h4>
                  
                  {contentData.viral_titles.map((titleObj, idx) => (
                    <div
                      key={idx}
                      onClick={() => {
                        setContentData(prev => ({...prev, title: titleObj.title}));
                        setSlideshowTitle(titleObj.title);
                        console.log('✅ Selected:', titleObj.title);
                      }}
                      style={{
                        padding: '12px 14px',
                        background: slideshowTitle === titleObj.title 
                          ? 'linear-gradient(135deg, #667eea, #764ba2)' 
                          : '#f8f9fa',
                        color: slideshowTitle === titleObj.title ? 'white' : '#333',
                        borderRadius: '8px',
                        marginBottom: '8px',
                        cursor: 'pointer',
                        border: slideshowTitle === titleObj.title 
                          ? '2px solid #764ba2' 
                          : '2px solid transparent',
                        transition: 'all 0.3s',
                        boxShadow: slideshowTitle === titleObj.title 
                          ? '0 4px 12px rgba(102, 126, 234, 0.3)' 
                          : 'none'
                      }}
                      onMouseEnter={(e) => {
                        if (slideshowTitle !== titleObj.title) {
                          e.currentTarget.style.background = '#e9ecef';
                          e.currentTarget.style.borderColor = '#667eea';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (slideshowTitle !== titleObj.title) {
                          e.currentTarget.style.background = '#f8f9fa';
                          e.currentTarget.style.borderColor = 'transparent';
                        }
                      }}
                    >
                      <div style={{ 
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '10px'
                      }}>
                        <span style={{ 
                          fontSize: '18px',
                          minWidth: '24px'
                        }}>
                          {slideshowTitle === titleObj.title ? '✅' : `${idx + 1}.`}
                        </span>
                        <div style={{ flex: 1 }}>
                          <div style={{ 
                            fontWeight: '700', 
                            marginBottom: '4px',
                            fontSize: '14px',
                            lineHeight: '1.4'
                          }}>
                            {titleObj.title}
                          </div>
                          <div style={{ 
                            fontSize: '11px', 
                            opacity: 0.9,
                            fontWeight: '500',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            flexWrap: 'wrap'
                          }}>
                            <span style={{
                              background: slideshowTitle === titleObj.title 
                                ? 'rgba(255,255,255,0.2)' 
                                : '#fff',
                              padding: '2px 8px',
                              borderRadius: '12px',
                              border: slideshowTitle === titleObj.title 
                                ? '1px solid rgba(255,255,255,0.3)' 
                                : '1px solid #ddd'
                            }}>
                              🔥 Score: {titleObj.score}/10
                            </span>
                            <span>• {titleObj.reason}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  <div style={{
                    marginTop: '12px',
                    padding: '10px',
                    background: '#e7f3ff',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#004085'
                  }}>
                    💡 <strong>Selected:</strong> {slideshowTitle || 'None yet - click a title above'}
                  </div>
                </div>
              )}
            </div>
            
            {/* Manual Title Input */}
            <label style={{display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333'}}>
              Video Title:
            </label>
            <input
              type="text"
              value={slideshowTitle}
              onChange={(e) => setSlideshowTitle(e.target.value)}
              placeholder="Selected title appears here, or enter manually"
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontSize: '15px',
                marginBottom: '20px',
                outline: 'none'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />

            {/* Description Section */}
            <label style={{display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333'}}>
              Video Description:
            </label>
            <textarea
              value={slideshowDescription}
              onChange={(e) => setSlideshowDescription(e.target.value)}
              placeholder="AI-generated description will appear here, or write your own"
              rows={6}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '2px solid #ddd',
                fontSize: '14px',
                marginBottom: '10px',
                resize: 'vertical',
                outline: 'none'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#ddd'}
            />
            
            {/* Show Hashtags if Generated */}
            {contentData.tags && contentData.tags.length > 0 && (
              <div style={{
                padding: '14px',
                background: 'linear-gradient(135deg, #d4edda, #c3f0d2)',
                borderRadius: '10px',
                marginBottom: '15px',
                border: '2px solid #28a745'
              }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '8px',
                  marginBottom: '8px'
                }}>
                  <span style={{ fontSize: '18px' }}>📌</span>
                  <strong style={{ color: '#155724', fontSize: '15px' }}>
                    Hashtags (copy to description):
                  </strong>
                </div>
                <div style={{ 
                  fontSize: '14px', 
                  color: '#155724',
                  fontWeight: '500',
                  wordBreak: 'break-word'
                }}>
                  {contentData.tags.map(tag => `#${tag}`).join(' ')}
                </div>
                <button
                  onClick={() => {
                    const hashtags = contentData.tags.map(tag => `#${tag}`).join(' ');
                    navigator.clipboard.writeText(hashtags);
                    alert('✅ Hashtags copied to clipboard!');
                  }}
                  style={{
                    marginTop: '10px',
                    padding: '6px 12px',
                    background: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  📋 Copy Hashtags
                </button>
              </div>
            )}
          </div>
        )}





        {/* Step 3: Generate & Upload */}
        {uploadedImages.length >= 2 && slideshowTitle && slideshowDescription && (
          <div>
            <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
              🚀 Step 3: Generate & Upload
            </h3>
            
            <button
              onClick={async () => {
                setGeneratingSlideshow(true);
                try {
                  const userData = getUserData();
                  const response = await fetch(`${API_BASE}/api/youtube/generate-slideshow`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                      'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                      user_id: userData.user_id,
                      images: uploadedImages,
                      title: slideshowTitle,
                      description: slideshowDescription,
                      duration_per_image: 2.0,
                      music_style: slideshowConfig.music_style
                    })
                  });
                  const result = await response.json();
                  if (result.success) {
                    alert('✅ Video generated and uploaded to YouTube!');
                    setUploadedImages([]);
                    setSlideshowTitle('');
                    setSlideshowDescription('');
                  } else {
                    throw new Error(result.error);
                  }
                } catch (error) {
                  alert('Error: ' + error.message);
                } finally {
                  setGeneratingSlideshow(false);
                }
              }}
              disabled={generatingSlideshow}
              style={{
                width: '100%',
                padding: '16px',
                background: generatingSlideshow ? '#ccc' : '#FF0000',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: '700',
                cursor: generatingSlideshow ? 'not-allowed' : 'pointer'
              }}
            >
              {generatingSlideshow ? '⏳ Generating & Uploading...' : '🚀 Generate & Upload to YouTube'}
            </button>
          </div>
        )}
      </div>
    )}

{/* PRODUCT URL TAB */}
{/* PRODUCT URL TAB */}
{slideshowTab === 'product' && (
  <div>
    {/* Step 1: Scrape Product */}
    <div style={{ marginBottom: '30px' }}>
      <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '22px', fontWeight: '700' }}>
        Step 1: Scrape Product
      </h3>
      
      <input
        type="text"
        placeholder="https://www.flipkart.com/product/..."
        value={productUrl}
        onChange={(e) => setProductUrl(e.target.value)}
        style={{
          width: '100%',
          padding: '15px',
          fontSize: '16px',
          marginBottom: '15px',
          borderRadius: '8px',
          border: '2px solid #ddd'
        }}
      />
      
      <button
        onClick={async () => {
          if (!productUrl.trim()) {
            alert('Enter product URL');
            return;
          }
          
          setLoading(true);
          setError('');
          
          try {
            const userData = getUserData();
            const response = await fetch(`${API_BASE}/api/product-video/generate`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                user_id: userData.user_id,
                product_url: productUrl
              })
            });
            
            const result = await response.json();
            
            if (result.success) {
              setScrapedProduct(result.product_data);
              setSlideshowTitle(result.title);
              setSlideshowDescription(result.description);
              setUploadedImages(result.images);
              setVideoPreview(null);
            } else {
              throw new Error(result.error);
            }
          } catch (error) {
            setError(error.message);
            alert('Error: ' + error.message);
          } finally {
            setLoading(false);
          }
        }}
        disabled={loading}
        style={{
          padding: '14px 28px',
          background: loading ? '#ccc' : '#FF0000',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: loading ? 'not-allowed' : 'pointer',
          fontWeight: '700',
          fontSize: '16px'
        }}
      >
        {loading ? 'Scraping...' : 'Scrape Product'}
      </button>
      
      {error && (
        <div style={{marginTop: '15px', padding: '15px', background: '#f8d7da', borderRadius: '8px', color: '#721c24'}}>
          {error}
        </div>
      )}
    </div>


    {/* ====================================== */}

    {/* NEW: Music Selection for Product Videos */}
{scrapedProduct && (
  <div style={{ marginBottom: '30px' }}>
    <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px', fontWeight: '700' }}>
      🎵 Step 1.5: Select Background Music
    </h3>
    
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
      gap: '12px',
      marginBottom: '16px'
    }}>
      {[
        { value: 'upbeat', label: 'Upbeat 😄', color: '#FF6B6B', desc: 'Best for products' },
        { value: 'energetic', label: 'Energetic ⚡', color: '#4ECDC4', desc: 'High energy ads' },
        { value: 'cinematic', label: 'Cinematic 🎬', color: '#95E1D3', desc: 'Premium products' },
        { value: 'relaxing', label: 'Relaxing 🌿', color: '#38B2AC', desc: 'Wellness items' },
        { value: 'happy', label: 'Happy 😊', color: '#FFC107', desc: 'Fun products' },
        { value: 'motivational', label: 'Motivational 🔥', color: '#E74C3C', desc: 'Fitness gear' }
      ].map((music) => (
        <button
          key={music.value}
          onClick={() => setSlideshowConfig(prev => ({
            ...prev,
            music_style: music.value
          }))}
          style={{
            padding: '16px 12px',
            background: slideshowConfig.music_style === music.value 
              ? `linear-gradient(135deg, ${music.color}, ${music.color}dd)` 
              : '#f8f9fa',
            color: slideshowConfig.music_style === music.value ? 'white' : '#333',
            border: slideshowConfig.music_style === music.value 
              ? `3px solid ${music.color}` 
              : '2px solid #ddd',
            borderRadius: '12px',
            cursor: 'pointer',
            fontWeight: '700',
            fontSize: '13px',
            textAlign: 'center',
            transition: 'all 0.3s',
            boxShadow: slideshowConfig.music_style === music.value 
              ? `0 4px 15px ${music.color}40` 
              : '0 2px 5px rgba(0,0,0,0.1)'
          }}
        >
          <div>{music.label}</div>
          <div style={{
            fontSize: '10px',
            marginTop: '4px',
            opacity: 0.9,
            fontWeight: '500'
          }}>
            {music.desc}
          </div>
        </button>
      ))}
    </div>
    
    <div style={{
      padding: '12px',
      background: '#d4edda',
      borderRadius: '8px',
      fontSize: '13px',
      color: '#155724',
      border: '1px solid #c3e6cb',
      fontWeight: '600'
    }}>
      🎵 Selected: <strong>{slideshowConfig.music_style.charAt(0).toUpperCase() + slideshowConfig.music_style.slice(1)}</strong> music for your product video
    </div>
  </div>
)}

{/* ============================================= */}

    {/* Step 2: Edit (shown after scraping) */}
    {scrapedProduct && (
      <div>
        <div style={{marginBottom: '30px', background: '#f8f9fa', padding: '20px', borderRadius: '12px'}}>
          <h4 style={{fontWeight: '700', marginBottom: '10px'}}>{scrapedProduct.product_name}</h4>
          <p style={{marginBottom: '10px'}}>
            <strong>Brand:</strong> {scrapedProduct.brand} | 
            <strong> Price:</strong> Rs.{scrapedProduct.price} {scrapedProduct.discount}
          </p>
          
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginTop: '15px'}}>
            {uploadedImages.slice(0, 6).map((img, idx) => (
              <img key={idx} src={img} alt="" style={{width: '100%', height: '100px', objectFit: 'cover', borderRadius: '8px'}} />
            ))}
          </div>
        </div>

        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
            Step 2: Review Details
          </h3>
          
          <label style={{display: 'block', marginBottom: '8px', fontWeight: '600'}}>Title:</label>
          <input
            type="text"
            value={slideshowTitle}
            onChange={(e) => setSlideshowTitle(e.target.value)}
            style={{
              width: '100%', 
              padding: '12px', 
              marginBottom: '20px',
              borderRadius: '8px',
              border: '2px solid #ddd',
              fontSize: '15px'
            }}
          />
          
          <label style={{display: 'block', marginBottom: '8px', fontWeight: '600'}}>Description:</label>
          <textarea
            value={slideshowDescription}
            onChange={(e) => setSlideshowDescription(e.target.value)}
            rows={10}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: '8px',
              border: '2px solid #ddd',
              fontSize: '14px'
            }}
          />
        </div>

        {/* Step 3: Generate */}
        {!videoPreview && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
              Step 3: Generate Video
            </h3>
            
            <button




// onClick={async () => {
//   // DEBUG: Check what we have
//   console.log('🔍 DEBUG - uploadedImages:', uploadedImages.length);
//   console.log('🔍 DEBUG - First image preview:', uploadedImages[0]?.substring(0, 50));
  
//   if (!uploadedImages || uploadedImages.length === 0) {
//     alert('No images found! Please scrape the product again.');
//     return;
//   }
  
//   setGeneratingSlideshow(true);
//   try {
//     const userData = getUserData();
    
//     // Convert URLs to base64
//     const base64Images = await Promise.all(
//       uploadedImages.map(async (imgUrl) => {
//         // Already base64
//         if (imgUrl.startsWith('data:')) {
//           console.log('✅ Image already base64');
//           return imgUrl;
//         }
        
//         // Download URL
//         console.log('📥 Downloading:', imgUrl.substring(0, 50));
//         const response = await fetch(imgUrl);
//         const blob = await response.blob();
        
//         return new Promise((resolve) => {
//           const reader = new FileReader();
//           reader.onloadend = () => {
//             console.log('✅ Converted to base64:', reader.result.substring(0, 50));
//             resolve(reader.result);
//           };
//           reader.readAsDataURL(blob);
//         });
//       })
//     );
    
//     console.log('📤 Sending', base64Images.length, 'images to backend');
    



//     // const response = await fetch(`${API_BASE}/api/youtube/generate-slideshow-preview`, {
//     //   method: 'POST',
//     //   headers: {
//     //     'Content-Type': 'application/json',
//     //     'Authorization': `Bearer ${token}`
//     //   },
//     //   body: JSON.stringify({
//     //     user_id: userData.user_id,
//     //     images: base64Images,  // ← MAKE SURE THIS IS HERE
//     //     duration_per_image: 2.0
//     //   })
//     // });

// // ✅ AFTER (with product_data)
// // ✅ CORRECT FORMAT
// const response = await fetch(`${API_BASE}/api/youtube/generate-slideshow-preview`, {
//   method: 'POST',
//   headers: {
//     'Content-Type': 'application/json',
//     'Authorization': `Bearer ${token}`
//   },
//   body: JSON.stringify({
//     user_id: user.user_id,           // ✅ Required
//     images: uploadedImages,           // ✅ Array of base64 strings
//     title: slideshowTitle,            // ✅ String
//     description: slideshowDescription, // ✅ String
//     duration_per_image: 2.0,          // ✅ Number
//     product_data: scrapedProduct      // ✅ Object or null
//   })
// });
    
//     const result = await response.json();
    
//     console.log('📨 Backend response:', result);
    
//     if (result.success) {
//       setVideoPreview(result.video_preview);
//     } else {
//       throw new Error(result.error);
//     }
//   } catch (error) {
//     console.error('❌ Preview error:', error);
//     alert('Error: ' + error.message);
//   } finally {
//     setGeneratingSlideshow(false);
//   }
// }}


onClick={async () => {
  // Validation
  if (!uploadedImages || uploadedImages.length === 0) {
    alert('No images found! Please scrape the product again.');
    return;
  }
  
  setGeneratingSlideshow(true);
  
  try {
    const userData = getUserData();
    
    // ✅ LOG WHAT WE'RE SENDING
    console.log('📤 Sending preview request:');
    console.log('- User ID:', userData.user_id);
    console.log('- Images:', uploadedImages.length);
    console.log('- Title:', slideshowTitle);
    console.log('- Product data:', scrapedProduct ? 'Yes' : 'No');
    
    // ✅ Convert URLs to base64 if needed
    const base64Images = await Promise.all(
      uploadedImages.map(async (imgUrl) => {
        // Already base64
        if (imgUrl.startsWith('data:')) {
          console.log('✅ Image already base64');
          return imgUrl;
        }
        
        // Download URL
        console.log('📥 Downloading:', imgUrl.substring(0, 50));
        const response = await fetch(imgUrl);
        const blob = await response.blob();
        
        return new Promise((resolve) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            console.log('✅ Converted to base64:', reader.result.substring(0, 50));
            resolve(reader.result);
          };
          reader.readAsDataURL(blob);
        });
      })
    );
    
    console.log('📤 Sending', base64Images.length, 'images to backend');
    
    const response = await fetch(`${API_BASE}/api/youtube/generate-slideshow-preview`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userData.user_id,
        images: base64Images,  // ✅ Use converted images
        duration_per_image: 2.0,
        title: slideshowTitle,
        description: slideshowDescription,
        product_data: scrapedProduct,
        music_style: slideshowConfig.music_style
      })
    });
    
    const result = await response.json();
    
    console.log('📨 Backend response:', result);
    
    if (result.success) {
      setVideoPreview(result.preview.video_preview);
    } else {
      throw new Error(result.error);
    }
  } catch (error) {
    console.error('❌ Preview error:', error);
    alert('Error: ' + error.message);
  } finally {
    setGeneratingSlideshow(false);
  }
}}







              disabled={generatingSlideshow || !slideshowTitle || !slideshowDescription}
              style={{
                width: '100%',
                padding: '16px',
                background: (generatingSlideshow || !slideshowTitle || !slideshowDescription) ? '#ccc' : '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: (generatingSlideshow || !slideshowTitle || !slideshowDescription) ? 'not-allowed' : 'pointer',
                fontWeight: '700',
                fontSize: '16px'
              }}
            >
              {generatingSlideshow ? 'Generating...' : 'Generate Video Preview'}
            </button>
          </div>
        )}

        {/* Step 4: Upload */}
        {videoPreview && (
          <div style={{ marginBottom: '30px' }}>
            <h3 style={{ color: '#333', marginBottom: '16px', fontSize: '20px' }}>
              Step 4: Preview & Upload
            </h3>
            
            <video 
              src={videoPreview} 
              controls 
              style={{
                width: '100%', 
                maxHeight: '400px', 
                borderRadius: '12px',
                marginBottom: '20px',
                background: '#000'
              }}
            />
            
            <div style={{display: 'flex', gap: '12px'}}>
              <button
                onClick={() => setVideoPreview(null)}
                style={{
                  flex: 1,
                  padding: '14px',
                  background: '#6c757d',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '700',
                  cursor: 'pointer'
                }}
              >
                Regenerate
              </button>
              
              <button
                onClick={async () => {
                  setGeneratingSlideshow(true);
                  try {
                    const userData = getUserData();
                    
                    const imagePromises = uploadedImages.map(async (imgUrl) => {
                      if (imgUrl.startsWith('data:')) return imgUrl;
                      const response = await fetch(imgUrl);
                      const blob = await response.blob();
                      return new Promise((resolve) => {
                        const reader = new FileReader();
                        reader.onloadend = () => resolve(reader.result);
                        reader.readAsDataURL(blob);
                      });
                    });
                    
                    const base64Images = await Promise.all(imagePromises);
                    
                    const response = await fetch(`${API_BASE}/api/youtube/generate-slideshow`, {
                      method: 'POST',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                      },
                      body: JSON.stringify({
                        user_id: userData.user_id,
                        images: base64Images,
                        title: slideshowTitle,
                        description: slideshowDescription,
                        duration_per_image: 2.0,
                        music_style: slideshowConfig.music_style
                      })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                      alert('Video uploaded to YouTube!');
                      setScrapedProduct(null);
                      setProductUrl('');
                      setSlideshowTitle('');
                      setSlideshowDescription('');
                      setUploadedImages([]);
                      setVideoPreview(null);
                    } else {
                      throw new Error(result.error);
                    }
                  } catch (error) {
                    alert('Upload failed: ' + error.message);
                  } finally {
                    setGeneratingSlideshow(false);
                  }
                }}
                disabled={generatingSlideshow}
                style={{
                  flex: 2,
                  padding: '14px',
                  background: generatingSlideshow ? '#ccc' : '#FF0000',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontWeight: '700',
                  cursor: generatingSlideshow ? 'not-allowed' : 'pointer'
                }}
              >
                {generatingSlideshow ? 'Uploading...' : 'Upload to YouTube'}
              </button>
            </div>
          </div>
        )}
      </div>
    )}
  </div>
)}







    {/* Pro Tips */}
    <div style={{
      marginTop: '30px',
      padding: '20px',
      background: '#e7f3ff',
      borderRadius: '12px',
      border: '1px solid #bee5eb'
    }}>
      <h4 style={{ color: '#004085', marginBottom: '12px' }}>💡 Pro Tips:</h4>
      <ul style={{ fontSize: '14px', color: '#004085', lineHeight: '1.8' }}>
        <li>Use high-quality product images (1080p recommended)</li>
        <li>Edit AI-generated titles and descriptions to match your style</li>
        <li>Add relevant hashtags for better reach (#mensfashion, #electronics, etc.)</li>
        <li>2-second duration per image works best for Shorts</li>
        <li>Review all details before uploading to YouTube</li>
      </ul>
    </div>
  </div>
)}

{/* ============================================ */}
{/* AUTOMATION TAB - PRODUCT SCRAPING + UPLOAD */}
{/* ============================================ */}
{/* End Image Slideshow Tab */}

{/* ============================================ */}
{/* AUTOMATION TAB - COMPLETE A-Z AUTOMATION */}
{/* ============================================ */}
{/* ============================================ */}
{/* AUTOMATION TAB - COMPLETE REPLACEMENT */}
{/* ============================================ */}
{/* ============================================ */}



{/* AUTOMATION TAB - COMPLETE WORKING VERSION */}
{/* Paste this REPLACING your entire automation tab */}


{/* ============================================ */}
{activeTab === 'automation' && status?.youtube_connected && (
  <div style={{ 
    background: 'rgba(255, 255, 255, 0.95)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' 
  }}>
    <h2 style={{ color: '#FF0000', marginBottom: '10px', fontSize: '32px', fontWeight: '700' }}>
      🤖 Smart Product Automation
    </h2>
    <p style={{ color: '#666', marginBottom: '30px', fontSize: '16px' }}>
      Automatically search products → Scrape → Generate videos → Upload to YouTube
    </p>

    {/* STEP 1: CONFIGURATION */}
    <div style={{
      padding: '30px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '15px',
      marginBottom: '30px',
      color: 'white'
    }}>
      <h3 style={{ marginBottom: '20px', fontSize: '22px', fontWeight: '700' }}>
        📍 Step 1: Configure Search
      </h3>
      
      {/* Product Category/Domain */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: '600',
          fontSize: '14px'
        }}>
          Product Category (Required) *
        </label>
        <input
          type="text"
          value={automationConfig.search_query}
          onChange={(e) => setAutomationConfig(prev => ({
            ...prev,
            search_query: e.target.value
          }))}
          placeholder="e.g., wireless earbuds, gaming laptop, running shoes"
          disabled={automationEnabled}
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '10px',
            border: automationConfig.search_query ? '2px solid #4CAF50' : '2px solid rgba(255,255,255,0.3)',
            fontSize: '15px',
            background: automationEnabled ? '#f5f5f5' : 'rgba(255,255,255,0.95)',
            color: '#333'
          }}
        />
        {!automationConfig.search_query && (
          <small style={{ display: 'block', marginTop: '5px', color: '#ffeb3b', fontWeight: '600' }}>
            ⚠️ Required: Enter product type (e.g., "earbuds", "phone", "laptop")
          </small>
        )}
        {automationConfig.search_query && (
          <small style={{ display: 'block', marginTop: '5px', opacity: 0.9 }}>
            ✅ Will search for: "{automationConfig.search_query}"
          </small>
        )}
      </div>

      {/* Website URL */}
      <div style={{ marginBottom: '20px' }}>
        <label style={{
          display: 'block',
          marginBottom: '8px',
          fontWeight: '600',
          fontSize: '14px'
        }}>
          Website URL (Optional - Leave blank for Flipkart):
        </label>
        <input
          type="text"
          value={automationConfig.base_url}
          onChange={(e) => setAutomationConfig(prev => ({
            ...prev,
            base_url: e.target.value || 'https://www.flipkart.com'
          }))}
          placeholder="https://www.flipkart.com (default)"
          disabled={automationEnabled}
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '10px',
            border: '2px solid rgba(255,255,255,0.3)',
            fontSize: '15px',
            background: automationEnabled ? '#f5f5f5' : 'rgba(255,255,255,0.95)',
            color: '#333'
          }}
        />
        <small style={{ display: 'block', marginTop: '5px', opacity: 0.9 }}>
          💡 Supported: Flipkart, Amazon.in, Myntra
        </small>
      </div>

      {/* Preview */}
      {automationConfig.search_query && (
        <div style={{
          marginTop: '15px',
          padding: '12px',
          background: 'rgba(255,255,255,0.2)',
          borderRadius: '8px',
          borderLeft: '4px solid #4CAF50'
        }}>
          <strong>Preview:</strong> Will search "{automationConfig.search_query}" on{' '}
          {automationConfig.base_url || 'https://www.flipkart.com'}
        </div>
      )}
    </div>

    {/* AUTOMATION STATUS */}
    <div style={{
      padding: '25px',
      background: automationEnabled 
        ? 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)' 
        : '#f8f9fa',
      borderRadius: '15px',
      marginBottom: '30px',
      border: `3px solid ${automationEnabled ? '#28a745' : '#ddd'}`
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px'
      }}>
        <div>
          <h3 style={{ 
            color: automationEnabled ? 'white' : '#333', 
            marginBottom: '10px',
            fontSize: '24px',
            fontWeight: '700'
          }}>
            {automationEnabled ? '🟢 AUTOMATION ACTIVE' : '🔴 AUTOMATION INACTIVE'}
          </h3>
          <p style={{ 
            margin: 0, 
            fontSize: '15px',
            color: automationEnabled ? 'rgba(255,255,255,0.95)' : '#666'
          }}>
            {automationEnabled 
              ? `Searching "${automationConfig.search_query}" • ${automationConfig.upload_times.length} scheduled times` 
              : 'Configure settings and click START to begin'}
          </p>
        </div>
        
        <button
          onClick={async () => {
            if (!automationEnabled) {
              // Validate
              if (!automationConfig.search_query || automationConfig.search_query.trim().length < 3) {
                alert('❌ Please enter a product category (at least 3 characters)!');
                return;
              }
              
              if (automationConfig.upload_times.length === 0) {
                alert('❌ Please add at least one upload time!');
                return;
              }
              
              // Start automation
              try {
                const response = await fetch(`${API_BASE}/api/product-automation/start`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                  },
                  body: JSON.stringify({
                    user_id: user.user_id,
                    config: automationConfig
                  })
                });
                
                const result = await response.json();
                
                if (result.success) {
                  setAutomationEnabled(true);
                  alert(`✅ Automation started!\n\nSearching: ${automationConfig.search_query}\nTimes: ${automationConfig.upload_times.join(', ')}`);
                } else {
                  alert('❌ Failed: ' + result.error);
                }
              } catch (error) {
                alert('❌ Error: ' + error.message);
              }
            } else {
              // Stop automation
              if (!confirm('Are you sure you want to stop automation?')) return;
              
              try {
                const response = await fetch(`${API_BASE}/api/product-automation/stop`, {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                  },
                  body: JSON.stringify({
                    user_id: user.user_id
                  })
                });
                
                const result = await response.json();
                
                if (result.success) {
                  setAutomationEnabled(false);
                  alert('⏹️ Automation stopped.');
                } else {
                  alert('❌ Failed: ' + result.error);
                }
              } catch (error) {
                alert('❌ Error: ' + error.message);
              }
            }
          }}
          disabled={!automationEnabled && (!automationConfig.search_query || automationConfig.search_query.length < 3)}
          style={{
            padding: '16px 40px',
            background: automationEnabled ? '#dc3545' : '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontWeight: '700',
            fontSize: '18px',
            cursor: (!automationEnabled && (!automationConfig.search_query || automationConfig.search_query.length < 3)) ? 'not-allowed' : 'pointer',
            opacity: (!automationEnabled && (!automationConfig.search_query || automationConfig.search_query.length < 3)) ? 0.5 : 1,
            boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
            transition: 'all 0.3s'
          }}
        >
          {automationEnabled ? '⏹️ STOP AUTOMATION' : '▶️ START AUTOMATION'}
        </button>
      </div>
    </div>

    {/* CONFIGURATION PANEL */}
    <div style={{
      padding: '30px',
      background: '#fff',
      borderRadius: '15px',
      marginBottom: '30px',
      border: '2px solid #e0e0e0'
    }}>
      <h3 style={{ color: '#333', marginBottom: '25px', fontSize: '20px', fontWeight: '700' }}>
        ⚙️ Configuration
      </h3>
      
      {/* Max Posts Per Day */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '15px'
        }}>
          📊 Maximum Posts Per Day:
        </label>
        <input
          type="number"
          min="1"
          max="100"
          value={automationConfig.max_posts_per_day}
          onChange={(e) => setAutomationConfig(prev => ({
            ...prev,
            max_posts_per_day: parseInt(e.target.value) || 10
          }))}
          disabled={automationEnabled}
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '10px',
            border: '2px solid #ddd',
            fontSize: '15px',
            background: automationEnabled ? '#f5f5f5' : 'white'
          }}
        />
        <small style={{ color: '#666', fontSize: '13px', marginTop: '5px', display: 'block' }}>
          Recommended: 5-10 posts per day
        </small>
      </div>

      {/* Upload Times */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '15px'
        }}>
          🕐 Upload Times (IST - 24-hour format):
        </label>
        
        {/* Display existing times */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '15px' }}>
          {automationConfig.upload_times.filter(t => t && t.trim()).map((time, idx) => (
            <span key={idx} style={{
              padding: '10px 18px',
              background: 'linear-gradient(135deg, #FF0000, #CC0000)',
              color: 'white',
              borderRadius: '25px',
              fontSize: '14px',
              fontWeight: '600',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 2px 8px rgba(255,0,0,0.3)'
            }}>
              🕐 {time}
              {!automationEnabled && (
                <button
                  onClick={() => {
                    setAutomationConfig(prev => ({
                      ...prev,
                      upload_times: prev.upload_times.filter((_, i) => i !== idx)
                    }));
                  }}
                  style={{
                    background: 'rgba(255,255,255,0.3)',
                    border: 'none',
                    color: 'white',
                    cursor: 'pointer',
                    fontSize: '16px',
                    width: '20px',
                    height: '20px',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: 0
                  }}
                >
                  ×
                </button>
              )}
            </span>
          ))}
        </div>
        
        {!automationEnabled && (
          <>
            <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
              <input
                type="time"
                id="newUploadTime"
                style={{
                  padding: '12px',
                  borderRadius: '8px',
                  border: '2px solid #ddd',
                  fontSize: '14px',
                  flex: 1
                }}
              />
              <button
                onClick={() => {
                  const input = document.getElementById('newUploadTime');
                  if (input.value && !automationConfig.upload_times.includes(input.value)) {
                    setAutomationConfig(prev => ({
                      ...prev,
                      upload_times: [...prev.upload_times.filter(t => t && t.trim()), input.value].sort()
                    }));
                    input.value = '';
                  } else if (automationConfig.upload_times.includes(input.value)) {
                    alert('⚠️ This time is already added!');
                  } else {
                    alert('⚠️ Please select a time!');
                  }
                }}
                style={{
                  padding: '12px 24px',
                  background: '#28a745',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontWeight: '600',
                  cursor: 'pointer'
                }}
              >
                ➕ Add Time
              </button>
            </div>

            {/* TEST SCHEDULER */}
            <div style={{
              marginTop: '15px',
              padding: '15px',
              background: '#fff3cd',
              border: '2px solid #ffc107',
              borderRadius: '10px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '10px'
              }}>
                <strong style={{ color: '#856404', fontSize: '15px' }}>
                  🧪 Test Automation (Quick Test)
                </strong>
                <button
                  onClick={() => setShowTestScheduler(!showTestScheduler)}
                  style={{
                    padding: '6px 12px',
                    background: '#ffc107',
                    color: '#000',
                    border: 'none',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: '600',
                    cursor: 'pointer'
                  }}
                >
                  {showTestScheduler ? 'Hide' : 'Show'}
                </button>
              </div>

              {showTestScheduler && (
                <>
                  <p style={{ color: '#856404', fontSize: '13px', marginBottom: '10px' }}>
                    Add a test time (2-3 minutes from now) to verify automation:
                  </p>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                    <input
                      type="time"
                      value={testScheduleTime}
                      onChange={(e) => setTestScheduleTime(e.target.value)}
                      style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '6px',
                        border: '2px solid #ffc107',
                        fontSize: '14px'
                      }}
                    />
                    <button
                      onClick={() => {
                        if (testScheduleTime && !automationConfig.upload_times.includes(testScheduleTime)) {
                          setAutomationConfig(prev => ({
                            ...prev,
                            upload_times: [...prev.upload_times.filter(t => t && t.trim()), testScheduleTime].sort()
                          }));
                          setTestScheduleTime('');
                          alert(`✅ Test time ${testScheduleTime} added!\n\nDon't forget to:\n1. Enter product category\n2. Click START AUTOMATION`);
                        } else {
                          alert('⚠️ Please select a time or time already exists!');
                        }
                      }}
                      style={{
                        padding: '10px 20px',
                        background: '#ffc107',
                        color: '#000',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '13px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        whiteSpace: 'nowrap'
                      }}
                    >
                      Add Test Time
                    </button>
                  </div>
                  <small style={{ color: '#856404', fontSize: '12px', marginTop: '8px', display: 'block' }}>
                    💡 Current time: {new Date().toLocaleTimeString('en-IN', {hour: '2-digit', minute: '2-digit', hour12: true})} IST
                  </small>
                </>
              )}
            </div>
          </>
        )}
        
        <small style={{ color: '#666', fontSize: '13px', marginTop: '10px', display: 'block' }}>
          System checks every minute and posts at scheduled times
        </small>
      </div>
    </div>

    {/* ACTIVITY LOGS */}
    <div style={{
      padding: '25px',
      background: '#fff',
      borderRadius: '15px',
      border: '2px solid #e0e0e0'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3 style={{ color: '#333', fontSize: '20px', fontWeight: '700', margin: 0 }}>
          📋 Activity Logs
        </h3>
        <button
          onClick={async () => {
            setLoadingLogs(true);
            try {
              const response = await fetch(`${API_BASE}/api/automation/logs/${user.user_id}?limit=20`, {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              });
              if (response.ok) {
                const data = await response.json();
                if (data.success) {
                  setAutomationLogs(data.logs || []);
                }
              }
            } catch (error) {
              console.error('Failed to refresh logs:', error);
            }
            setLoadingLogs(false);
          }}
          style={{
            padding: '8px 16px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: '600',
            cursor: 'pointer'
          }}
        >
          {loadingLogs ? '⏳ Refreshing...' : '🔄 Refresh'}
        </button>
      </div>

      {automationLogs.length === 0 ? (
        <div style={{
          padding: '40px',
          textAlign: 'center',
          color: '#999',
          background: '#f8f9fa',
          borderRadius: '10px'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '10px' }}>📭</div>
          <p style={{ margin: 0, fontSize: '16px' }}>
            No activity yet. Start automation to see logs here.
          </p>
        </div>
      ) : (
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          {automationLogs.map((log, idx) => (
            <div key={idx} style={{
              padding: '15px',
              background: log.success ? '#f0f9ff' : '#fff1f0',
              borderLeft: `4px solid ${log.success ? '#0284c7' : '#ef4444'}`,
              borderRadius: '8px',
              marginBottom: '10px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: '600', color: log.success ? '#0284c7' : '#ef4444' }}>
                  {log.success ? '✅ Success' : '❌ Failed'}
                </span>
                <span style={{ fontSize: '13px', color: '#666' }}>
                  {new Date(log.timestamp).toLocaleString('en-IN')}
                </span>
              </div>
              {log.video_id && (
                <div style={{ fontSize: '14px', color: '#333', marginBottom: '4px' }}>
                  🎬 Video ID: <code style={{ background: '#e5e7eb', padding: '2px 6px', borderRadius: '4px' }}>{log.video_id}</code>
                </div>
              )}
              {log.product_url && (
                <div style={{ fontSize: '13px', color: '#666' }}>
                  🔗 Product: {log.product_url.substring(0, 60)}...
                </div>
              )}
              {log.error && (
                <div style={{ fontSize: '13px', color: '#dc2626', marginTop: '8px', background: '#fee2e2', padding: '8px', borderRadius: '4px' }}>
                  Error: {log.error}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>

    {/* HOW IT WORKS */}
    <div style={{
      padding: '25px',
      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      borderRadius: '15px',
      color: 'white',
      marginTop: '30px'
    }}>
      <h3 style={{ marginBottom: '20px', fontSize: '20px', fontWeight: '700' }}>
        📖 How It Works
      </h3>
      <div style={{ display: 'grid', gap: '15px' }}>
        {[
          { icon: '1️⃣', text: `Goes to ${automationConfig.base_url || 'Flipkart'}` },
          { icon: '2️⃣', text: `Searches for "${automationConfig.search_query || 'your product'}"` },
          { icon: '3️⃣', text: 'Scrapes product details from search results (one by one)' },
          { icon: '4️⃣', text: 'Downloads 3 product images for each item' },
          { icon: '5️⃣', text: 'Creates promotional slideshow video with overlays' },
          { icon: '6️⃣', text: 'Uploads to YouTube Shorts at scheduled times' },
          { icon: '7️⃣', text: `Respects daily limit (max ${automationConfig.max_posts_per_day} posts/day)` }
        ].map((step, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '12px',
            alignItems: 'center',
            background: 'rgba(255,255,255,0.15)',
            padding: '12px',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{ fontSize: '24px' }}>{step.icon}</span>
            <span style={{ fontSize: '14px' }}>{step.text}</span>
          </div>
        ))}
      </div>
    </div>

    {/* Activity Logs */}
    <div style={{
      padding: '25px',
      background: 'white',
      borderRadius: '15px',
      maxHeight: '400px',
      overflowY: 'auto',
      border: '2px solid #e0e0e0'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '20px',
        fontWeight: '700'
      }}>
        📋 Activity Logs
      </h3>
      {automationLogs.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '40px 20px',
          color: '#999'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '15px' }}>📭</div>
          <p style={{ fontSize: '16px', fontStyle: 'italic' }}>
            No activity yet. Start automation to see logs here.
          </p>
        </div>
      ) : (
        automationLogs.map((log, idx) => (
          <div key={idx} style={{
            padding: '15px',
            background: '#f8f9fa',
            borderRadius: '8px',
            marginBottom: '10px',
            borderLeft: `4px solid ${log.success ? '#28a745' : '#dc3545'}`
          }}>
            <div style={{ 
              fontSize: '12px', 
              color: '#999', 
              marginBottom: '6px' 
            }}>
              {new Date(log.timestamp).toLocaleString()}
            </div>
            <div style={{ fontSize: '14px', color: '#333', fontWeight: '500' }}>
              {log.message}
            </div>
          </div>
        ))
      )}
    </div>
  </div>
)}

{/* End Automation Tab */}






{/* --------------------------------viral pixel code tab---------------------------------------------------- */}
{/* ============================================ */}
{/* VIRAL PIXEL TAB - FIXED VERSION */}
{/* ============================================ */}
{/* ============================================ */}
{/* ============================================ */}
{/* ============================================ */}
{/* AUTOMATION TAB - FIXED VERSION */}


{/* ============================================ */}
{/* VIRAL PIXEL TAB - FIXED VERSION */}
{/* ============================================ */}
{activeTab === 'viral-pixel' && status?.youtube_connected && (
  <div style={{ 
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    minHeight: '600px'
  }}>
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      marginBottom: '30px' 
    }}>
      <div>
        <h2 style={{ 
          color: 'white', 
          marginBottom: '10px', 
          fontSize: '36px', 
          fontWeight: '800',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          margin: 0
        }}>
          🎬 Viral Pixel Generator
        </h2>
        <p style={{ 
          color: 'rgba(255,255,255,0.95)', 
          fontSize: '18px',
          fontWeight: '500',
          margin: 0
        }}>
          Pixabay HD + Hindi Voice + Creative AI Storytelling
        </p>
      </div>
    </div>

    {/* STEP 1: NICHE SELECTION */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🎯 Step 1: Choose Your Niche
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '15px',
        marginBottom: '20px'
      }}>
        {[
          { id: 'space', emoji: '🌌', name: 'Space & Universe', viral: 'Very High' },
          { id: 'tech_ai', emoji: '🤖', name: 'Technology & AI', viral: 'Very High' },
          { id: 'ocean', emoji: '🌊', name: 'Ocean & Marine', viral: 'High' },
          { id: 'nature', emoji: '🦁', name: 'Nature & Wildlife', viral: 'High' },
          { id: 'success', emoji: '💪', name: 'Success & Motivation', viral: 'Very High' }
        ].map((niche) => (
          <div
            key={niche.id}
            onClick={() => {
              if (!viralPixelGenerating) {
                setViralPixelConfig(prev => ({ ...prev, niche: niche.id }));
              }
            }}
            style={{
              padding: '20px',
              background: viralPixelConfig.niche === niche.id 
                ? 'linear-gradient(135deg, #667eea, #764ba2)' 
                : 'white',
              color: viralPixelConfig.niche === niche.id ? 'white' : '#333',
              border: viralPixelConfig.niche === niche.id 
                ? '3px solid #FFD700' 
                : '2px solid #e0e0e0',
              borderRadius: '12px',
              cursor: viralPixelGenerating ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s',
              textAlign: 'center',
              boxShadow: viralPixelConfig.niche === niche.id 
                ? '0 8px 24px rgba(102,126,234,0.4)' 
                : '0 2px 8px rgba(0,0,0,0.1)',
              opacity: viralPixelGenerating ? 0.6 : 1,
              transform: viralPixelConfig.niche === niche.id ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>
              {niche.emoji}
            </div>
            <div style={{ fontWeight: '700', fontSize: '16px', marginBottom: '8px' }}>
              {niche.name}
            </div>
            <div style={{ 
              fontSize: '12px', 
              opacity: 0.8,
              fontWeight: '500' 
            }}>
              🔥 {niche.viral} Potential
            </div>
          </div>
        ))}
      </div>

      {viralPixelConfig.niche && (
        <div style={{
          padding: '15px',
          background: '#e8f5e9',
          borderLeft: '4px solid #4caf50',
          borderRadius: '8px',
          marginTop: '15px'
        }}>
          <strong style={{ color: '#2e7d32' }}>
            ✅ Selected: {viralPixelConfig.niche.toUpperCase().replace('_', ' & ')}
          </strong>
        </div>
      )}
    </div>

    {/* STEP 2: SETTINGS */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        ⚙️ Step 2: Configure Settings
      </h3>

      {/* Language Selection */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          🎙️ Language:
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {[
            { id: 'hindi', label: 'हिन्दी (Hindi)' },
            { id: 'english_us', label: 'English (US)' },
            { id: 'english_uk', label: 'English (UK)' },
            { id: 'english_in', label: 'English (India)' }
          ].map((lang) => (
            <button
              key={lang.id}
              onClick={() => setViralPixelConfig(prev => ({ ...prev, language: lang.id }))}
              disabled={viralPixelGenerating}
              style={{
                padding: '12px',
                background: viralPixelConfig.language === lang.id 
                  ? 'linear-gradient(135deg, #667eea, #764ba2)' 
                  : 'white',
                color: viralPixelConfig.language === lang.id ? 'white' : '#333',
                border: viralPixelConfig.language === lang.id 
                  ? '2px solid #FFD700' 
                  : '2px solid #ddd',
                borderRadius: '10px',
                cursor: viralPixelGenerating ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                opacity: viralPixelGenerating ? 0.6 : 1,
                transition: 'all 0.3s'
              }}
            >
              {lang.label}
            </button>
          ))}
        </div>
      </div>

      {/* HD Quality Toggle */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '16px',
          background: '#f8f9fa',
          borderRadius: '10px',
          cursor: viralPixelGenerating ? 'not-allowed' : 'pointer',
          border: '2px solid #ddd'
        }}>
          <input
            type="checkbox"
            checked={viralPixelConfig.hd_quality}
            onChange={(e) => setViralPixelConfig(prev => ({ ...prev, hd_quality: e.target.checked }))}
            disabled={viralPixelGenerating}
            style={{
              width: '20px',
              height: '20px',
              cursor: viralPixelGenerating ? 'not-allowed' : 'pointer'
            }}
          />
          <span style={{
            fontWeight: '600',
            fontSize: '15px',
            flex: 1,
            color: '#333'
          }}>
            🎥 HD Quality (720p-1080p)
          </span>
        </label>
      </div>

      {/* Show Captions Toggle */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          padding: '16px',
          background: '#f8f9fa',
          borderRadius: '10px',
          cursor: viralPixelGenerating ? 'not-allowed' : 'pointer',
          border: '2px solid #ddd'
        }}>
          <input
            type="checkbox"
            checked={viralPixelConfig.show_captions}
            onChange={(e) => setViralPixelConfig(prev => ({ ...prev, show_captions: e.target.checked }))}
            disabled={viralPixelGenerating}
            style={{
              width: '20px',
              height: '20px',
              cursor: viralPixelGenerating ? 'not-allowed' : 'pointer'
            }}
          />
          <span style={{
            fontWeight: '600',
            fontSize: '15px',
            flex: 1,
            color: '#333'
          }}>
            💬 Show Golden Captions
          </span>
        </label>
      </div>

      {/* Channel Name */}
      <div>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          📺 Channel Name:
        </label>
        <input
          type="text"
          value={viralPixelConfig.channel_name}
          onChange={(e) => setViralPixelConfig(prev => ({ ...prev, channel_name: e.target.value }))}
          disabled={viralPixelGenerating}
          placeholder="My Awesome Channel"
          style={{
            width: '100%',
            padding: '14px',
            borderRadius: '10px',
            border: '2px solid #ddd',
            fontSize: '15px',
            background: viralPixelGenerating ? '#f5f5f5' : 'white'
          }}
        />
      </div>
    </div>

    {/* STEP 3: GENERATE */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🎬 Step 3: Generate Video
      </h3>

      <button
        onClick={async () => {
          if (!viralPixelConfig.niche) {
            alert('❌ Please select a niche!');
            return;
          }

          setViralPixelGenerating(true);
          setViralPixelProgress(0);

          try {
            console.log('Starting Viral Pixel generation...');
            const response = await fetch(`${API_BASE}/api/viral-pixel/generate`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                user_id: user.user_id,
                niche: viralPixelConfig.niche,
                language: viralPixelConfig.language,
                hd_quality: viralPixelConfig.hd_quality,
                show_captions: viralPixelConfig.show_captions,
                channel_name: viralPixelConfig.channel_name
              })
            });

            const progressInterval = setInterval(() => {
              setViralPixelProgress(prev => {
                if (prev >= 90) {
                  clearInterval(progressInterval);
                  return 90;
                }
                return prev + 10;
              });
            }, 2000);

            const result = await response.json();
            clearInterval(progressInterval);

            if (result.success) {
              setViralPixelProgress(100);
              setViralPixelResult(result);
              console.log('Video generated successfully');
              alert(`✅ Video uploaded!\n\nVideo ID: ${result.video_id}\nURL: ${result.video_url}`);
            } else {
              console.error('Generation failed:', result.error);
              alert('❌ Failed: ' + result.error);
            }
          } catch (error) {
            console.error('Error:', error);
            alert('❌ Error: ' + error.message);
          } finally {
            setViralPixelGenerating(false);
            setViralPixelProgress(0);
          }
        }}
        disabled={viralPixelGenerating || !viralPixelConfig.niche}
        style={{
          width: '100%',
          padding: '20px',
          background: viralPixelGenerating 
            ? 'linear-gradient(135deg, #999, #666)' 
            : 'linear-gradient(135deg, #667eea, #764ba2)',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          fontSize: '20px',
          fontWeight: '800',
          cursor: (viralPixelGenerating || !viralPixelConfig.niche) ? 'not-allowed' : 'pointer',
          boxShadow: '0 6px 20px rgba(102,126,234,0.4)',
          opacity: (viralPixelGenerating || !viralPixelConfig.niche) ? 0.7 : 1,
          transition: 'all 0.3s'
        }}
      >
        {viralPixelGenerating ? '⏳ GENERATING...' : '🎬 GENERATE VIDEO'}
      </button>

      {viralPixelGenerating && (
        <div style={{ marginTop: '20px' }}>
          <div style={{
            width: '100%',
            height: '30px',
            background: '#e0e0e0',
            borderRadius: '15px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${viralPixelProgress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #667eea, #764ba2)',
              transition: 'width 0.5s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{
                color: 'white',
                fontWeight: '700',
                fontSize: '14px'
              }}>
                {viralPixelProgress}%
              </span>
            </div>
          </div>
          <p style={{ 
            textAlign: 'center', 
            marginTop: '10px', 
            color: '#666',
            fontSize: '14px' 
          }}>
            Processing: Script → Videos → Voice → Effects → Upload...
          </p>
        </div>
      )}

      {viralPixelResult && (
        <div style={{
          marginTop: '20px',
          padding: '20px',
          background: '#e8f5e9',
          borderRadius: '12px',
          border: '2px solid #4caf50'
        }}>
          <h4 style={{ color: '#2e7d32', marginBottom: '15px', fontSize: '18px', fontWeight: '700' }}>
            ✅ Video Uploaded Successfully!
          </h4>
          <div style={{ fontSize: '14px', color: '#333', marginBottom: '8px' }}>
            <strong>Video ID:</strong> {viralPixelResult.video_id}
          </div>
          <div style={{ fontSize: '14px', color: '#333', marginBottom: '8px' }}>
            <strong>Title:</strong> {viralPixelResult.title}
          </div>
          <div style={{ fontSize: '14px', color: '#333', marginBottom: '15px' }}>
            <strong>Segments:</strong> {viralPixelResult.segments}
          </div>
          
          <a
            href={viralPixelResult.video_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              padding: '12px 24px',
              background: '#FF0000',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              fontSize: '14px'
            }}
          >
            🎬 View on YouTube
          </a>
        </div>
      )}
    </div>

    {/* HOW IT WORKS */}
    <div style={{
      padding: '25px',
      background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      borderRadius: '15px',
      color: 'white'
    }}>
      <h3 style={{ marginBottom: '20px', fontSize: '20px', fontWeight: '700' }}>
        📖 How It Works
      </h3>
      <div style={{ display: 'grid', gap: '15px' }}>
        {[
          { icon: '1️⃣', text: 'AI generates creative script for your niche' },
          { icon: '2️⃣', text: 'Downloads HD videos from Pixabay' },
          { icon: '3️⃣', text: 'Creates Hindi/English voiceover' },
          { icon: '4️⃣', text: 'Adds animated transitions' },
          { icon: '5️⃣', text: 'Applies golden captions' },
          { icon: '6️⃣', text: 'Adds custom intro/outro' },
          { icon: '7️⃣', text: 'Uploads to YouTube Shorts automatically' }
        ].map((step, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '12px',
            alignItems: 'center',
            background: 'rgba(255,255,255,0.15)',
            padding: '12px',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{ fontSize: '24px' }}>{step.icon}</span>
            <span style={{ fontSize: '14px' }}>{step.text}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
)}

{/* --------------------------------viral pixel code end---------------------------------------------------- */}



{/* ============================================ */}
{/* MRBEAST VIRAL SHORTS GENERATOR TAB */}
{/* ============================================ */}
{activeTab === 'mrbeast-shorts' && status?.youtube_connected && (
  <div style={{ 
    background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    minHeight: '600px'
  }}>
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      marginBottom: '30px' 
    }}>
      <div>
        <h2 style={{ 
          color: 'white', 
          marginBottom: '10px', 
          fontSize: '36px', 
          fontWeight: '800',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          margin: 0
        }}>
          🔥 MrBeast Viral Shorts Generator
        </h2>
        <p style={{ 
          color: 'rgba(255,255,255,0.95)', 
          fontSize: '18px',
          fontWeight: '500',
          margin: 0
        }}>
          Convert ANY YouTube video into viral Hindi Shorts
        </p>
      </div>
    </div>

    {/* STEP 1: YOUTUBE URL */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🎯 Step 1: Paste MrBeast Video URL
      </h3>

      <input
        type="text"
        value={mrBeastConfig.youtube_url}
        onChange={(e) => setMrBeastConfig(prev => ({ ...prev, youtube_url: e.target.value }))}
        disabled={mrBeastGenerating}
        placeholder="https://www.youtube.com/watch?v=..."
        style={{
          width: '100%',
          padding: '16px',
          borderRadius: '10px',
          border: '2px solid #ddd',
          fontSize: '16px',
          background: mrBeastGenerating ? '#f5f5f5' : 'white',
          marginBottom: '15px'
        }}
      />

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '15px',
        marginTop: '20px'
      }}>
        {[
          "https://www.youtube.com/watch?v=0e3GPea1Tyg",
          "https://www.youtube.com/watch?v=fKopy74weus",
          "https://www.youtube.com/watch?v=phz_yvI1-c4"
        ].map((url, idx) => (
          <button
            key={idx}
            onClick={() => {
              if (!mrBeastGenerating) {
                setMrBeastConfig(prev => ({ ...prev, youtube_url: url }));
              }
            }}
            disabled={mrBeastGenerating}
            style={{
              padding: '12px',
              background: mrBeastConfig.youtube_url === url 
                ? 'linear-gradient(135deg, #f093fb, #f5576c)' 
                : 'white',
              color: mrBeastConfig.youtube_url === url ? 'white' : '#333',
              border: mrBeastConfig.youtube_url === url 
                ? 'none' 
                : '2px solid #ddd',
              borderRadius: '10px',
              cursor: mrBeastGenerating ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              opacity: mrBeastGenerating ? 0.6 : 1,
              transition: 'all 0.3s',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
          >
            Example {idx + 1}
          </button>
        ))}
      </div>
    </div>

    {/* STEP 2: SETTINGS */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        ⚙️ Step 2: Configure Settings
      </h3>

      {/* Duration Slider */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          🕐 Shorts Duration: {mrBeastConfig.target_duration} seconds
        </label>
        <input
          type="range"
          min="20"
          max="55"
          step="5"
          value={mrBeastConfig.target_duration}
          onChange={(e) => setMrBeastConfig(prev => ({ ...prev, target_duration: parseInt(e.target.value) }))}
          disabled={mrBeastGenerating}
          style={{
            width: '100%',
            height: '8px',
            borderRadius: '5px',
            outline: 'none',
            opacity: mrBeastGenerating ? 0.6 : 1
          }}
        />
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#666',
          marginTop: '5px'
        }}>
          <span>20s (Quick)</span>
          <span>35s (Balanced)</span>
          <span>55s (Max)</span>
        </div>
      </div>

      {/* Number of Videos */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          🎬 How many viral shorts to generate:
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
          {[1, 2, 3, 4, 5].map((num) => (
            <button
              key={num}
              onClick={() => setMrBeastConfig(prev => ({ ...prev, num_videos: num }))}
              disabled={mrBeastGenerating}
              style={{
                padding: '12px',
                background: mrBeastConfig.num_videos === num 
                  ? 'linear-gradient(135deg, #f093fb, #f5576c)' 
                  : 'white',
                color: mrBeastConfig.num_videos === num ? 'white' : '#333',
                border: mrBeastConfig.num_videos === num 
                  ? 'none' 
                  : '2px solid #ddd',
                borderRadius: '10px',
                cursor: mrBeastGenerating ? 'not-allowed' : 'pointer',
                fontWeight: '700',
                fontSize: '18px',
                opacity: mrBeastGenerating ? 0.6 : 1,
                transition: 'all 0.3s'
              }}
            >
              {num}
            </button>
          ))}
        </div>
      </div>

      {/* Voice Selection */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          🎙️ Hindi Voice Style:
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          {[
            { id: 'male_energetic', label: '👨 Male Energetic', premium: true },
            { id: 'female_warm', label: '👩 Female Warm', premium: true },
            { id: 'male_deep', label: '👨 Male Deep', premium: true },
            { id: 'female_cheerful', label: '👩 Female Cheerful', premium: true },
            { id: 'edge_free', label: '🆓 Free Hindi Voice', premium: false }
          ].map((voice) => (
            <button
              key={voice.id}
              onClick={() => setMrBeastConfig(prev => ({ ...prev, voice_type: voice.id }))}
              disabled={mrBeastGenerating}
              style={{
                padding: '14px',
                background: mrBeastConfig.voice_type === voice.id 
                  ? 'linear-gradient(135deg, #f093fb, #f5576c)' 
                  : 'white',
                color: mrBeastConfig.voice_type === voice.id ? 'white' : '#333',
                border: mrBeastConfig.voice_type === voice.id 
                  ? 'none' 
                  : '2px solid #ddd',
                borderRadius: '10px',
                cursor: mrBeastGenerating ? 'not-allowed' : 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                opacity: mrBeastGenerating ? 0.6 : 1,
                transition: 'all 0.3s',
                position: 'relative'
              }}
            >
              {voice.label}
              {voice.premium && (
                <span style={{
                  position: 'absolute',
                  top: '5px',
                  right: '5px',
                  background: '#FFD700',
                  color: '#333',
                  fontSize: '10px',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  fontWeight: '700'
                }}>
                  PRO
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>

    {/* STEP 3: GENERATE */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🚀 Step 3: Generate Viral Shorts
      </h3>

      <button
        onClick={async () => {
          if (!mrBeastConfig.youtube_url) {
            alert('❌ Please paste a YouTube URL!');
            return;
          }

          if (!mrBeastConfig.youtube_url.includes('youtube.com') && !mrBeastConfig.youtube_url.includes('youtu.be')) {
            alert('❌ Invalid YouTube URL!');
            return;
          }

          setMrBeastGenerating(true);
          setMrBeastProgress(0);

          try {
            console.log('Starting MrBeast generation...');
            const response = await fetch(`${API_BASE}/api/mrbeast/generate`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                user_id: user.user_id,
                youtube_url: mrBeastConfig.youtube_url,
                target_duration: mrBeastConfig.target_duration,
                voice_type: mrBeastConfig.voice_type,
                num_videos: mrBeastConfig.num_videos
              })
            });

            const progressInterval = setInterval(() => {
              setMrBeastProgress(prev => {
                if (prev >= 90) {
                  clearInterval(progressInterval);
                  return 90;
                }
                return prev + 5;
              });
            }, 3000);

            const result = await response.json();
            clearInterval(progressInterval);

            if (result.success) {
              setMrBeastProgress(100);
              setMrBeastResult(result);
              console.log('Videos generated successfully');
              alert(`✅ Generated ${result.count} viral shorts successfully!`);
            } else {
              console.error('Generation failed:', result.error);
              alert('❌ Failed: ' + result.error);
            }
          } catch (error) {
            console.error('Error:', error);
            alert('❌ Error: ' + error.message);
          } finally {
            setMrBeastGenerating(false);
            setMrBeastProgress(0);
          }
        }}
        disabled={mrBeastGenerating || !mrBeastConfig.youtube_url}
        style={{
          width: '100%',
          padding: '20px',
          background: mrBeastGenerating 
            ? 'linear-gradient(135deg, #999, #666)' 
            : 'linear-gradient(135deg, #f093fb, #f5576c)',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          fontSize: '20px',
          fontWeight: '800',
          cursor: (mrBeastGenerating || !mrBeastConfig.youtube_url) ? 'not-allowed' : 'pointer',
          boxShadow: '0 6px 20px rgba(240,147,251,0.4)',
          opacity: (mrBeastGenerating || !mrBeastConfig.youtube_url) ? 0.7 : 1,
          transition: 'all 0.3s'
        }}
      >
        {mrBeastGenerating ? '⏳ GENERATING VIRAL SHORTS...' : '🔥 GENERATE VIRAL SHORTS'}
      </button>

      {mrBeastGenerating && (
        <div style={{ marginTop: '20px' }}>
          <div style={{
            width: '100%',
            height: '30px',
            background: '#e0e0e0',
            borderRadius: '15px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${mrBeastProgress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #f093fb, #f5576c)',
              transition: 'width 0.5s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{
                color: 'white',
                fontWeight: '700',
                fontSize: '14px'
              }}>
                {mrBeastProgress}%
              </span>
            </div>
          </div>
          <p style={{ 
            textAlign: 'center', 
            marginTop: '10px', 
            color: '#666',
            fontSize: '14px' 
          }}>
            Processing: Download → Transcribe → Translate → Voice → Cut → Upload...
          </p>
        </div>
      )}

      {mrBeastResult && (
        <div style={{
          marginTop: '20px',
          padding: '20px',
          background: '#e8f5e9',
          borderRadius: '12px',
          border: '2px solid #4caf50'
        }}>
          <h4 style={{ color: '#2e7d32', marginBottom: '15px', fontSize: '18px', fontWeight: '700' }}>
            ✅ {mrBeastResult.count} Viral Shorts Generated!
          </h4>
          
          <div style={{ display: 'grid', gap: '15px' }}>
            {mrBeastResult.videos?.map((video, idx) => (
              <div key={idx} style={{
                padding: '15px',
                background: 'white',
                borderRadius: '8px',
                border: '1px solid #ddd'
              }}>
                <div style={{ fontSize: '14px', color: '#333', marginBottom: '8px' }}>
                  <strong>Video {idx + 1}:</strong> {video.duration.toFixed(1)}s | Score: {video.viral_score}/10
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                  <strong>Hindi:</strong> {video.hindi_text.substring(0, 100)}...
                </div>
                <div style={{ fontSize: '11px', color: '#999' }}>
                  <strong>English:</strong> {video.english_text.substring(0, 80)}...
                </div>
              </div>
            ))}
          </div>
          
          <div style={{ marginTop: '15px', textAlign: 'center' }}>
            <p style={{ fontSize: '13px', color: '#666' }}>
              Videos will be uploaded to your connected YouTube channel
            </p>
          </div>
        </div>
      )}
    </div>

    {/* HOW IT WORKS */}
    <div style={{
      padding: '25px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '15px',
      color: 'white'
    }}>
      <h3 style={{ marginBottom: '20px', fontSize: '20px', fontWeight: '700' }}>
        📖 How It Works
      </h3>
      <div style={{ display: 'grid', gap: '15px' }}>
        {[
          { icon: '1️⃣', text: 'Downloads original MrBeast video' },
          { icon: '2️⃣', text: 'Extracts transcript using AI (Whisper)' },
          { icon: '3️⃣', text: 'Identifies 3-5 most viral moments' },
          { icon: '4️⃣', text: 'Translates to creative Hindi script' },
          { icon: '5️⃣', text: 'Generates energetic Hindi voice-over' },
          { icon: '6️⃣', text: 'Cuts video into perfect 20-55s segments' },
          { icon: '7️⃣', text: 'Adds captions and combines audio' },
          { icon: '8️⃣', text: 'Uploads to YouTube Shorts automatically' }
        ].map((step, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '12px',
            alignItems: 'center',
            background: 'rgba(255,255,255,0.15)',
            padding: '12px',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{ fontSize: '24px' }}>{step.icon}</span>
            <span style={{ fontSize: '14px' }}>{step.text}</span>
          </div>
        ))}
      </div>
    </div>
  </div>
)}

{/* -------------------------------- MrBeast code end ---------------------------------------------------- */}



// ============================================================================
// PART 4: ADD THIS FULL TAB CONTENT IN YOUR MAIN CONTENT AREA
// ============================================================================

{/* ============================================ */}
{/* CHINA MULTI-NICHE AUTOMATION TAB */}
{/* ============================================ */}
{activeTab === 'china-automation' && status?.youtube_connected && (
  <div style={{ 
    background: 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)', 
    borderRadius: '20px', 
    padding: '40px', 
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    minHeight: '600px'
  }}>
    <div style={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center', 
      marginBottom: '30px' 
    }}>
      <div>
        <h2 style={{ 
          color: 'white', 
          marginBottom: '10px', 
          fontSize: '36px', 
          fontWeight: '800',
          textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
          margin: 0
        }}>
          🇨🇳 China Video Automation
        </h2>
        <p style={{ 
          color: 'rgba(255,255,255,0.95)', 
          fontSize: '18px',
          fontWeight: '500',
          margin: 0
        }}>
          Auto-find viral Chinese videos, translate to Hindi, and upload to YouTube
        </p>
      </div>
    </div>

    {/* STEP 1: NICHE SELECTION */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🎯 Step 1: Choose Your Niche
      </h3>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '15px'
      }}>
        {Object.entries(chinaNiches).map(([nicheKey, nicheData]) => (
          <button
            key={nicheKey}
            onClick={() => {
              if (!chinaGenerating) {
                setChinaConfig(prev => ({ ...prev, niche: nicheKey }));
              }
            }}
            disabled={chinaGenerating}
            style={{
              padding: '20px',
              background: chinaConfig.niche === nicheKey 
                ? 'linear-gradient(135deg, #FF6B6B, #FF8E53)' 
                : 'white',
              color: chinaConfig.niche === nicheKey ? 'white' : '#333',
              border: chinaConfig.niche === nicheKey 
                ? 'none' 
                : '2px solid #ddd',
              borderRadius: '12px',
              cursor: chinaGenerating ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              fontSize: '14px',
              opacity: chinaGenerating ? 0.6 : 1,
              transition: 'all 0.3s',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '8px',
              boxShadow: chinaConfig.niche === nicheKey 
                ? '0 4px 15px rgba(255,107,107,0.3)' 
                : '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <span style={{ fontSize: '32px' }}>{nicheData.icon}</span>
            <span style={{ textAlign: 'center', lineHeight: '1.3' }}>
              {nicheData.name}
            </span>
          </button>
        ))}
      </div>

      {/* Show selected niche keywords */}
      {chinaNiches[chinaConfig.niche] && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: '#f5f5f5',
          borderRadius: '10px'
        }}>
          <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>
            <strong>Search Keywords:</strong>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {chinaNiches[chinaConfig.niche].english_keywords?.map((keyword, idx) => (
              <span
                key={idx}
                style={{
                  padding: '4px 10px',
                  background: 'white',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#666',
                  border: '1px solid #ddd'
                }}
              >
                {keyword}
              </span>
            ))}
          </div>
          <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {chinaNiches[chinaConfig.niche].chinese_keywords?.map((keyword, idx) => (
              <span
                key={idx}
                style={{
                  padding: '4px 10px',
                  background: 'white',
                  borderRadius: '6px',
                  fontSize: '12px',
                  color: '#666',
                  border: '1px solid #ddd'
                }}
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>

    {/* STEP 2: SETTINGS */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        ⚙️ Step 2: Configure Settings
      </h3>

      {/* Number of Videos */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'block', 
          marginBottom: '10px', 
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          🎬 How many videos to generate:
        </label>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
          {[1, 2, 3, 4, 5].map((num) => (
            <button
              key={num}
              onClick={() => setChinaConfig(prev => ({ ...prev, num_videos: num }))}
              disabled={chinaGenerating}
              style={{
                padding: '12px',
                background: chinaConfig.num_videos === num 
                  ? 'linear-gradient(135deg, #FF6B6B, #FF8E53)' 
                  : 'white',
                color: chinaConfig.num_videos === num ? 'white' : '#333',
                border: chinaConfig.num_videos === num 
                  ? 'none' 
                  : '2px solid #ddd',
                borderRadius: '10px',
                cursor: chinaGenerating ? 'not-allowed' : 'pointer',
                fontWeight: '700',
                fontSize: '18px',
                opacity: chinaGenerating ? 0.6 : 1,
                transition: 'all 0.3s'
              }}
            >
              {num}
            </button>
          ))}
        </div>
      </div>

      {/* Show Captions Toggle */}
      <div style={{ marginBottom: '25px' }}>
        <label style={{ 
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          cursor: chinaGenerating ? 'not-allowed' : 'pointer',
          fontWeight: '600',
          color: '#333',
          fontSize: '16px'
        }}>
          <input
            type="checkbox"
            checked={chinaConfig.show_captions}
            onChange={(e) => setChinaConfig(prev => ({ ...prev, show_captions: e.target.checked }))}
            disabled={chinaGenerating}
            style={{
              width: '20px',
              height: '20px',
              cursor: chinaGenerating ? 'not-allowed' : 'pointer'
            }}
          />
          <span>📝 Add text overlays / captions</span>
        </label>
      </div>
    </div>

    {/* STEP 3: GENERATE */}
    <div style={{
      background: 'rgba(255,255,255,0.95)',
      borderRadius: '15px',
      padding: '30px',
      marginBottom: '25px'
    }}>
      <h3 style={{ 
        color: '#333', 
        marginBottom: '20px', 
        fontSize: '24px', 
        fontWeight: '700' 
      }}>
        🚀 Step 3: Generate Videos
      </h3>

      <button
        onClick={async () => {
          setChinaGenerating(true);
          setChinaProgress(0);
          setChinaResult(null);

          try {
            console.log('Starting China generation...', chinaConfig);
            
            const progressInterval = setInterval(() => {
              setChinaProgress(prev => {
                if (prev >= 90) {
                  clearInterval(progressInterval);
                  return 90;
                }
                return prev + 5;
              });
            }, 4000);

            const promises = [];
            
            for (let i = 0; i < chinaConfig.num_videos; i++) {
              const promise = fetch(`${API_BASE}/api/china/generate`, {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                  user_id: user.user_id,
                  niche: chinaConfig.niche,
                  show_captions: chinaConfig.show_captions
                })
              }).then(res => res.json());
              
              promises.push(promise);
            }

            const results = await Promise.all(promises);
            clearInterval(progressInterval);

            const successful = results.filter(r => r.success);
            const failed = results.filter(r => !r.success);

            setChinaProgress(100);
            setChinaResult({
              success: successful.length > 0,
              count: successful.length,
              videos: successful,
              failed_count: failed.length,
              failed: failed
            });

            if (successful.length > 0) {
              console.log(`✅ Generated ${successful.length} videos`);
              alert(`✅ Generated ${successful.length} videos successfully!${failed.length > 0 ? ` (${failed.length} failed)` : ''}`);
            } else {
              console.error('All generations failed');
              alert('❌ All video generations failed. Check console for details.');
            }
          } catch (error) {
            console.error('Error:', error);
            alert('❌ Error: ' + error.message);
          } finally {
            setChinaGenerating(false);
            setChinaProgress(0);
          }
        }}
        disabled={chinaGenerating}
        style={{
          width: '100%',
          padding: '20px',
          background: chinaGenerating 
            ? 'linear-gradient(135deg, #999, #666)' 
            : 'linear-gradient(135deg, #FF6B6B, #FF8E53)',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          fontSize: '20px',
          fontWeight: '800',
          cursor: chinaGenerating ? 'not-allowed' : 'pointer',
          boxShadow: '0 6px 20px rgba(255,107,107,0.4)',
          opacity: chinaGenerating ? 0.7 : 1,
          transition: 'all 0.3s'
        }}
      >
        {chinaGenerating ? '⏳ GENERATING VIDEOS...' : `🔥 GENERATE ${chinaConfig.num_videos} VIDEO${chinaConfig.num_videos > 1 ? 'S' : ''}`}
      </button>

      {chinaGenerating && (
        <div style={{ marginTop: '20px' }}>
          <div style={{
            width: '100%',
            height: '30px',
            background: '#e0e0e0',
            borderRadius: '15px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${chinaProgress}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #FF6B6B, #FF8E53)',
              transition: 'width 0.5s',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{
                color: 'white',
                fontWeight: '700',
                fontSize: '14px'
              }}>
                {chinaProgress}%
              </span>
            </div>
          </div>
          <p style={{ 
            textAlign: 'center', 
            marginTop: '10px', 
            color: '#666',
            fontSize: '14px' 
          }}>
            Processing: Search → Download → Transcribe → Translate → Script → Voice → Edit → Upload...
          </p>
        </div>
      )}

      {chinaResult && chinaResult.success && (
        <div style={{
          marginTop: '20px',
          padding: '20px',
          background: '#e8f5e9',
          borderRadius: '12px',
          border: '2px solid #4caf50'
        }}>
          <h4 style={{ color: '#2e7d32', marginBottom: '15px', fontSize: '18px', fontWeight: '700' }}>
            ✅ {chinaResult.count} Video{chinaResult.count > 1 ? 's' : ''} Generated Successfully!
            {chinaResult.failed_count > 0 && (
              <span style={{ color: '#f57c00', fontSize: '14px', marginLeft: '10px' }}>
                ({chinaResult.failed_count} failed)
              </span>
            )}
          </h4>
          
          <div style={{ display: 'grid', gap: '15px' }}>
            {chinaResult.videos?.map((video, idx) => (
              <div key={idx} style={{
                padding: '15px',
                background: 'white',
                borderRadius: '8px',
                border: '1px solid #ddd'
              }}>
                <div style={{ fontSize: '14px', color: '#333', marginBottom: '8px', fontWeight: '600' }}>
                  Video {idx + 1}: {video.title?.substring(0, 60)}...
                </div>
                <div style={{ fontSize: '12px', color: '#666', marginBottom: '8px' }}>
                  <strong>Original:</strong> {video.original_title?.substring(0, 50)}...
                </div>
                <div style={{ fontSize: '12px', color: '#4caf50', marginBottom: '8px' }}>
                  <strong>YouTube:</strong>{' '}
                  <a 
                    href={video.video_url} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style={{ color: '#4caf50', textDecoration: 'underline' }}
                  >
                    {video.video_url}
                  </a>
                </div>
                <div style={{ fontSize: '11px', color: '#999' }}>
                  Niche: {video.niche} | Voice segments: {video.voice_segments}
                </div>
              </div>
            ))}
          </div>
          
          {chinaResult.failed_count > 0 && (
            <div style={{ marginTop: '15px', padding: '15px', background: '#fff3cd', borderRadius: '8px' }}>
              <h5 style={{ color: '#856404', marginBottom: '10px', fontSize: '14px' }}>
                ⚠️ Failed Generations ({chinaResult.failed_count}):
              </h5>
              {chinaResult.failed?.map((fail, idx) => (
                <div key={idx} style={{ fontSize: '12px', color: '#856404', marginBottom: '5px' }}>
                  • {fail.error}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>

    {/* HOW IT WORKS */}
    <div style={{
      padding: '25px',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '15px',
      color: 'white'
    }}>
      <h3 style={{ marginBottom: '20px', fontSize: '20px', fontWeight: '700' }}>
        📖 How It Works
      </h3>
      <div style={{ display: 'grid', gap: '15px' }}>
        {[
          { icon: '1️⃣', text: 'Searches Chinese platforms for trending videos in your niche' },
          { icon: '2️⃣', text: 'Downloads video automatically using smart keyword matching' },
          { icon: '3️⃣', text: 'Extracts and transcribes original audio (Chinese)' },
          { icon: '4️⃣', text: 'Translates Chinese → Hindi using AI' },
          { icon: '5️⃣', text: 'Generates creative viral script with Mistral AI' },
          { icon: '6️⃣', text: 'Creates Hindi voiceover with ElevenLabs' },
          { icon: '7️⃣', text: 'Processes video for Shorts (720x1280)' },
          { icon: '8️⃣', text: 'Adds text overlays and background music' },
          { icon: '9️⃣', text: 'Uploads to YouTube Shorts automatically' }
        ].map((step, idx) => (
          <div key={idx} style={{
            display: 'flex',
            gap: '12px',
            alignItems: 'center',
            background: 'rgba(255,255,255,0.15)',
            padding: '12px',
            borderRadius: '8px',
            backdropFilter: 'blur(10px)'
          }}>
            <span style={{ fontSize: '24px' }}>{step.icon}</span>
            <span style={{ fontSize: '14px' }}>{step.text}</span>
          </div>
        ))}
      </div>
      
      <div style={{
        marginTop: '20px',
        padding: '15px',
        background: 'rgba(255,255,255,0.15)',
        borderRadius: '10px',
        backdropFilter: 'blur(10px)'
      }}>
        <h4 style={{ fontSize: '16px', marginBottom: '10px', fontWeight: '700' }}>
          🎯 Available Niches:
        </h4>
        <div style={{ fontSize: '13px', lineHeight: '1.8' }}>
          {Object.entries(chinaNiches).map(([key, data], idx) => (
            <div key={key}>
              <strong>{data.icon} {data.name}</strong>
              {idx < Object.keys(chinaNiches).length - 1 && ' • '}
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
)}

{/* -------------------------------- China Automation code end ---------------------------------------------------- */}





        {/* Not Connected Message */}
        {activeTab !== 'connect' && !status?.youtube_connected && (
          <div style={{ 
            background: 'rgba(255, 255, 255, 0.95)', 
            borderRadius: '20px', 
            padding: '40px', 
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', 
            textAlign: 'center' 
          }}>
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔗</div>
            <h3 style={{ color: '#FF0000', marginBottom: '20px' }}>
              YouTube Not Connected
            </h3>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              Please connect your YouTube channel first.
            </p>
            <button 
              onClick={() => setActiveTab('connect')} 
              style={{ 
                padding: '12px 24px', 
                background: '#FF0000', 
                color: 'white', 
                border: 'none', 
                borderRadius: '8px', 
                cursor: 'pointer', 
                fontWeight: '600'
              }}
            >
              Connect YouTube
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default YouTubeAutomation;