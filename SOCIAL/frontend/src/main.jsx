import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './app'
import App from './src/App.jsx'

// Global error handler for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  // Prevent the default browser behavior (logging to console)
  event.preventDefault();
});

// Global error handler for JavaScript errors
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

// Application initialization
const initializeApp = () => {
  try {
    const rootElement = document.getElementById('root');
    
    if (!rootElement) {
      throw new Error('Root element not found. Make sure you have a div with id="root" in your HTML.');
    }

    const root = createRoot(rootElement);
    
    root.render(
      <StrictMode>
        <App />
      </StrictMode>
    );
    
    console.log('🚀 Multi-User Reddit Automation Platform initialized successfully');
    
  } catch (error) {
    console.error('Failed to initialize app:', error);
    
    // Fallback error display
    const rootElement = document.getElementById('root');
    if (rootElement) {
      rootElement.innerHTML = `
        <div style="
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
          font-family: system-ui, -apple-system, sans-serif;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          text-align: center;
          padding: 20px;
        ">
          <div style="
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
          ">
            <h1 style="margin-bottom: 20px;">Application Error</h1>
            <p style="margin-bottom: 20px;">
              Sorry, there was an error loading the Reddit Automation Platform.
            </p>
            <p style="font-size: 14px; opacity: 0.8; margin-bottom: 20px;">
              ${error.message}
            </p>
            <button 
              onclick="window.location.reload()"
              style="
                background: white;
                color: #333;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
              "
            >
              Reload Page
            </button>
            <div style="margin-top: 20px; font-size: 12px; opacity: 0.7;">
              If the problem persists, please contact support.
            </div>
          </div>
        </div>
      `;
    }
  }
};

// Initialize the app
initializeApp();