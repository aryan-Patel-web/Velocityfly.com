import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
// import './index.css'
import App from './App'
import "./styles/globals.css";


window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
  event.preventDefault();
});

window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

const initializeApp = () => {
  try {
    const rootElement = document.getElementById('root');
    
    if (!rootElement) {
      throw new Error('Root element not found');
    }

    const root = createRoot(rootElement);
    
    root.render(
      <StrictMode>
        <App />
      </StrictMode>
    );
    
    console.log('🚀 Application initialized');
    
  } catch (error) {
    console.error('Failed to initialize app:', error);
    
    const rootElement = document.getElementById('root');
    if (rootElement) {
      rootElement.innerHTML = `
        <div style="
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 100vh;
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
          ">
            <h1>Application Error</h1>
            <p>${error.message}</p>
            <button onclick="window.location.reload()" style="
              background: white;
              color: #333;
              border: none;
              padding: 12px 24px;
              border-radius: 8px;
              cursor: pointer;
            ">
              Reload Page
            </button>
          </div>
        </div>
      `;
    }
  }
};

initializeApp();