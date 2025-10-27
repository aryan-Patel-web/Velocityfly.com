# Render.com Deployment Configuration

## Build Settings

```yaml
Build Command: pip install -r requirements.txt
Start Command: python main.py
Environment: Python 3.11.6
```

## Environment Variables to Add in Render Dashboard

### Required Variables (Add these in Render Environment section):

```bash
# Database
MONGODB_URI=mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# Reddit API (Get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_REDIRECT_URI=https://agentic-u5lx.onrender.com/api/oauth/reddit/callback

# AI Services (Get from respective providers)
MISTRAL_API_KEY=your_mistral_api_key
GROQ_API_KEY=your_groq_api_key

# Authentication & Security (Generate secure random strings)
JWT_SECRET_KEY=your_jwt_secret_minimum_32_characters_long
TOKEN_ENCRYPTION_KEY=another_32_character_encryption_key

# Server
PORT=8000
ENVIRONMENT=production

# Optional
FRONTEND_URL=https://velocitypost-ai.onrender.com
```

## Deployment Steps

1. **Connect GitHub Repository** to Render
2. **Set Service Type**: Web Service
3. **Configure Build Settings** (above)
4. **Add Environment Variables** (above)
5. **Deploy Service**

## API Keys Setup Guide

### 1. Reddit API Setup
- Go to https://www.reddit.com/prefs/apps
- Click "Create App" or "Create Another App"
- Choose "web app"
- Set redirect URI: `https://agentic-u5lx.onrender.com/api/oauth/reddit/callback`
- Copy Client ID and Client Secret

### 2. Mistral AI Setup
- Visit https://console.mistral.ai/
- Create account and get API key
- Copy the API key

### 3. Groq AI Setup  
- Visit https://console.groq.com/
- Create account and get API key
- Copy the API key

### 4. Generate Secure Keys
Use Python to generate secure keys:
```python
import secrets
jwt_secret = secrets.token_urlsafe(32)
encryption_key = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={jwt_secret}")
print(f"TOKEN_ENCRYPTION_KEY={encryption_key}")
```

## Health Check URLs

After deployment, test these endpoints:

- **Health Check**: `https://agentic-u5lx.onrender.com/health`
- **API Docs**: `https://agentic-u5lx.onrender.com/docs`
- **Root**: `https://agentic-u5lx.onrender.com/`

## Frontend Integration

Update your frontend environment variables:

```bash
REACT_APP_API_URL=https://agentic-u5lx.onrender.com
```

## Domain Configuration

If using custom domain:
1. Update `REDDIT_REDIRECT_URI` to use your domain
2. Update `FRONTEND_URL` to your frontend domain
3. Update Reddit app settings with new redirect URI



# MongoDB Atlas Database Connection
MONGODB_URI=mongodb+srv://aryan:aryan@cluster0.7iquw6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0

# Reddit API Credentials (Create at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_REDIRECT_URI=https://agentic-u5lx.onrender.com/api/oauth/reddit/callback

# AI Service API Keys
MISTRAL_API_KEY=your_mistral_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# Authentication & Security
JWT_SECRET_KEY=your_jwt_secret_key_minimum_32_characters_long_secure_random_string
TOKEN_ENCRYPTION_KEY=another_32_character_encryption_key_for_reddit_tokens

# Server Configuration
PORT=8000
ENVIRONMENT=production

# Optional: Rate Limiting & Monitoring
RATE_LIMIT_ENABLED=true
MAX_REQUESTS_PER_MINUTE=60

# Optional: Frontend URL (for CORS)
FRONTEND_URL=https://velocitypost-ai.onrender.com