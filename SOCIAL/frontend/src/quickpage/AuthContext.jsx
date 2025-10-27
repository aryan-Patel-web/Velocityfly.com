import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

const AuthContext = createContext();
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://velocitypost-984x.onrender.com';

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

  // Debug helper for auth state
  const debugAuth = useCallback(() => {
    console.log('Auth Debug State:', {
      isAuthenticated,
      user,
      token: token ? token.substring(0, 20) + '...' : null,
      localStorage: {
        authToken: localStorage.getItem('authToken') ? 'present' : 'missing',
        cached_user: localStorage.getItem('cached_user') ? 'present' : 'missing'
      }
    });
  }, [isAuthenticated, user, token]);

  // Clear all tokens helper
  const clearAllTokens = useCallback(() => {
    ['auth_token', 'token', 'authToken', 'cached_user', 'user'].forEach(key => 
      localStorage.removeItem(key)
    );
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    console.log('All tokens cleared');
  }, []);

  // Initialize authentication on app load
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check for any existing token
        const savedToken = localStorage.getItem('authToken') || 
                          localStorage.getItem('auth_token') || 
                          localStorage.getItem('token');
        
        const cachedUser = localStorage.getItem('cached_user') || 
                          localStorage.getItem('user');
        
        if (savedToken && cachedUser) {
          try {
            const userData = JSON.parse(cachedUser);
            console.log('Attempting to restore user session...');
            
            // Validate token format
            if (savedToken.length > 10) {
              // Test token with backend
              const testResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
                headers: {
                  'Authorization': `Bearer ${savedToken}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (testResponse.ok) {
                const validatedUser = await testResponse.json();
                if (validatedUser.success) {
                  setUser(userData);
                  setToken(savedToken);
                  setIsAuthenticated(true);
                  
                  // Ensure token is stored with correct key
                  localStorage.setItem('authToken', savedToken);
                  console.log('User session restored:', userData.email);
                  setLoading(false);
                  return;
                }
              } else if (testResponse.status === 404) {
                // /me endpoint doesn't exist, but token might still be valid
                // Skip validation and trust the cached session
                setUser(userData);
                setToken(savedToken);
                setIsAuthenticated(true);
                localStorage.setItem('authToken', savedToken);
                console.log('User session restored (no validation):', userData.email);
                setLoading(false);
                return;
              }
            }
            
            // If we reach here, token is invalid
            throw new Error('Invalid token');
          } catch (parseError) {
            console.error('Token validation failed:', parseError);
            clearAllTokens();
          }
        } else {
          console.log('No saved session found');
          clearAllTokens();
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        clearAllTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [clearAllTokens]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      console.log('Login attempt:', { email, apiUrl: API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ email, password })
      });

      console.log('Login response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Network error' }));
        console.error('Login HTTP error:', response.status, errorData);
        return { 
          success: false, 
          error: errorData.error || errorData.message || `HTTP ${response.status}: Login failed` 
        };
      }

      const data = await response.json();
      console.log('Login response data:', data);
      
      // FIXED: Check for success regardless of token presence
      if (data.success === true) {
        console.log('Login successful - processing user data');
        
        // Extract user data with multiple fallback paths
        let userData;
        if (data.user && typeof data.user === 'object') {
          // Backend returns user object
          userData = {
            user_id: data.user.user_id || data.user.id || data.user_id,
            id: data.user.user_id || data.user.id || data.user_id,
            email: data.user.email || data.email || email,
            name: data.user.name || data.name || email.split('@')[0],
            platforms_connected: data.user.platforms_connected || data.platforms_connected || []
          };
        } else {
          // Backend returns flat structure
          userData = {
            user_id: data.user_id || data.id,
            id: data.user_id || data.id,
            email: data.email || email,
            name: data.name || email.split('@')[0],
            platforms_connected: data.platforms_connected || []
          };
        }
        
        // Generate a token if backend doesn't provide one
        const authToken = data.token || 
                         data.access_token || 
                         data.authToken ||
                         `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Set state
        setUser(userData);
        setIsAuthenticated(true);
        setToken(authToken);
        
        // Store with correct key
        localStorage.setItem('authToken', authToken);
        localStorage.setItem('cached_user', JSON.stringify(userData));
        
        // Clean up old keys
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        console.log('Login successful - user authenticated:', userData.email);
        console.log('Token stored:', authToken.substring(0, 20) + '...');
        
        return { success: true, user: userData, token: authToken };
        
      } else {
        // Explicit failure case
        console.error('Login failed - backend returned error:', data);
        return { 
          success: false, 
          error: data.error || data.message || 'Login failed - invalid credentials' 
        };
      }
      
    } catch (error) {
      console.error('Login network error:', error);
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
      console.log('Registration attempt:', { email, name });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      console.log('Registration response:', data);
      
      if (response.ok && data.success) {
        // Auto-login after successful registration
        if (data.token || data.user_id) {
          const userData = { 
            user_id: data.user_id || data.user?.user_id || data.user?.id,
            id: data.user_id || data.user?.user_id || data.user?.id,
            email: data.email || data.user?.email || email,
            name: data.name || data.user?.name || name,
            platforms_connected: data.platforms_connected || []
          };
          
          const authToken = data.token || 
                           data.access_token ||
                           `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
          
          setUser(userData);
          setIsAuthenticated(true);
          setToken(authToken);
          
          localStorage.setItem('authToken', authToken);
          localStorage.setItem('cached_user', JSON.stringify(userData));
          
          console.log('Registration and auto-login successful');
          return { success: true, user: userData, message: data.message, token: authToken };
        }
        return { success: true, message: data.message };
      } else {
        return { 
          success: false, 
          error: data.error || data.message || 'Registration failed' 
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: 'Registration failed: ' + error.message 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = useCallback(() => {
    clearAllTokens();
    console.log('User logged out');
  }, [clearAllTokens]);

  const updateUser = useCallback((userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('cached_user', JSON.stringify(updatedUser));
  }, [user]);

  // Enhanced makeAuthenticatedRequest function
  const makeAuthenticatedRequest = useCallback(async (endpoint, options = {}) => {
    // Use state token first, fallback to localStorage
    const authToken = token || localStorage.getItem('authToken');
    
    if (!authToken) {
      console.error('No authentication token available');
      logout();
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
      console.log(`Making request to: ${API_BASE_URL}${endpoint}`);
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      
      if (response.status === 401) {
        console.error('401 Unauthorized - token expired or invalid');
        logout();
        throw new Error('Authentication failed - please log in again');
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error(`HTTP ${response.status}:`, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText || 'Request failed'}`);
      }
      
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      if (error.message.includes('Authentication failed')) {
        throw error; // Re-throw auth errors
      }
      throw new Error('Network request failed: ' + error.message);
    }
  }, [token, logout]);

  // Helper function to check if user is really authenticated
  const isReallyAuthenticated = useCallback(() => {
    return isAuthenticated && user && user.user_id && token;
  }, [isAuthenticated, user, token]);

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
    debugAuth,
    isReallyAuthenticated
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};