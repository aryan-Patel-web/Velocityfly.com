import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();
const API_BASE_URL = import.meta.env?.VITE_API_URL || 'https://velocitypost-984x.onrender.com';

console.log('🔗 API Base URL:', API_BASE_URL);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  const clearUserRedditData = useCallback((email) => {
    if (email) {
      localStorage.removeItem(`reddit_connected_${email}`);
      localStorage.removeItem(`reddit_username_${email}`);
      localStorage.removeItem(`redditUserProfile_${email}`);
    }
  }, []);

  const clearAllTokens = useCallback((userEmail) => {
    ['auth_token', 'token', 'authToken', 'cached_user', 'user'].forEach(key => 
      localStorage.removeItem(key)
    );
    
    if (userEmail) {
      clearUserRedditData(userEmail);
    }
    
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  }, [clearUserRedditData]);

  useEffect(() => {
    const initAuth = () => {
      try {
        const savedToken = localStorage.getItem('authToken');
        const cachedUser = localStorage.getItem('cached_user');
        
        if (savedToken && cachedUser) {
          const userData = JSON.parse(cachedUser);
          setUser(userData);
          setToken(savedToken);
          setIsAuthenticated(true);
        } else {
          clearAllTokens(null);
        }
      } catch (error) {
        clearAllTokens(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [clearAllTokens]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      if (user?.email && user.email !== email) {
        clearUserRedditData(user.email);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ email, password })
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Network error' }));
        return { 
          success: false, 
          error: errorData.detail || errorData.error || errorData.message || 'Login failed' 
        };
      }

      const data = await response.json();
      
      if (data.success === true) {
        const userData = {
          user_id: data.user?.user_id || data.user?.id || data.user_id,
          id: data.user?.user_id || data.user?.id || data.user_id,
          email: data.user?.email || data.email || email,
          name: data.user?.name || data.name || email.split('@')[0],
          platforms_connected: data.user?.platforms_connected || data.platforms_connected || []
        };
        
        const authToken = data.token || data.access_token || `session_${Date.now()}`;
        
        const allKeys = Object.keys(localStorage);
        allKeys.forEach(key => {
          if (key.startsWith('reddit_') && !key.includes(email)) {
            localStorage.removeItem(key);
          }
        });
        
        setUser(userData);
        setIsAuthenticated(true);
        setToken(authToken);
        
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('cached_user', JSON.stringify(userData));
        
        return { success: true, user: userData, token: authToken };
      } else {
        return { 
          success: false, 
          error: data.detail || data.error || data.message || 'Invalid credentials' 
        };
      }
      
    } catch (error) {
      return { 
        success: false, 
        error: 'Network error: ' + error.message 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      if (user?.email && user.email !== email) {
        clearUserRedditData(user.email);
      }
      
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      
      if (response.ok && data.success) {
        if (data.token || data.user_id) {
          const userData = { 
            user_id: data.user_id || data.user?.user_id || data.user?.id,
            id: data.user_id || data.user?.user_id || data.user?.id,
            email: data.email || data.user?.email || email,
            name: data.name || data.user?.name || name,
            platforms_connected: data.platforms_connected || []
          };
          
          const authToken = data.token || data.access_token || `session_${Date.now()}`;
          
          const allKeys = Object.keys(localStorage);
          allKeys.forEach(key => {
            if (key.startsWith('reddit_') && !key.includes(email)) {
              localStorage.removeItem(key);
            }
          });
          
          setUser(userData);
          setIsAuthenticated(true);
          setToken(authToken);
          
          localStorage.setItem('authToken', authToken);
          localStorage.setItem('cached_user', JSON.stringify(userData));
          
          return { success: true, user: userData, message: data.message, token: authToken };
        }
        return { success: true, message: data.message };
      } else {
        return { 
          success: false, 
          error: data.detail || data.error || data.message || 'Registration failed' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: 'Registration failed: ' + error.message 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = useCallback(() => {
    const userEmail = user?.email;
    if (userEmail) {
      clearUserRedditData(userEmail);
    }
    clearAllTokens(userEmail);
  }, [user?.email, clearAllTokens, clearUserRedditData]);

  const updateUser = useCallback((userData) => {
    setUser(prevUser => {
      const updatedUser = { ...prevUser, ...userData };
      localStorage.setItem('cached_user', JSON.stringify(updatedUser));
      return updatedUser;
    });
  }, []);

  const makeAuthenticatedRequest = useCallback(async (endpoint, options = {}) => {
    const authToken = token || localStorage.getItem('authToken');
    
    if (!authToken) {
      const userEmail = user?.email;
      clearAllTokens(userEmail);
      throw new Error('No authentication token found');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
      ...(options.headers || {})
    };

    const requestOptions = {
      ...options,
      headers
    };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      
      if (response.status === 401) {
        const userEmail = user?.email;
        clearAllTokens(userEmail);
        throw new Error('Authentication failed - please log in again');
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText || 'Request failed'}`);
      }
      
      return response;
    } catch (error) {
      if (error.message.includes('Authentication failed')) {
        throw error;
      }
      throw new Error('Network request failed: ' + error.message);
    }
  }, [token, user?.email, clearAllTokens]);

  const isReallyAuthenticated = useCallback(() => {
    return isAuthenticated && user && user.user_id && token;
  }, [isAuthenticated, user, token]);

  const getCurrentUserRedditData = useCallback(() => {
    if (!user?.email) return null;
    
    const connected = localStorage.getItem(`reddit_connected_${user.email}`);
    const username = localStorage.getItem(`reddit_username_${user.email}`);
    
    return {
      connected: connected === 'true',
      username: username || null
    };
  }, [user?.email]);

  const value = {
    isAuthenticated,
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    makeAuthenticatedRequest,
    isReallyAuthenticated,
    clearUserRedditData,
    getCurrentUserRedditData
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthProvider;