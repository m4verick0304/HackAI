# PrepGenie - Production Deployment Guide

## 📋 Table of Contents
1. [Local Deployment with Docker](#local-deployment-with-docker)
2. [Render.com Deployment](#rendercom-deployment)
3. [Railway.app Deployment](#railwayapp-deployment)
4. [Heroku Deployment](#heroku-deployment)
5. [AWS Deployment](#aws-deployment)
6. [Production Checklist](#production-checklist)

---

## Local Deployment with Docker

### Prerequisites
- Docker & Docker Compose installed
- Environment variables configured (.env file)

### Quick Start

1. **Clone and Setup**
   ```bash
   cd PrepGenie
   cp .env.example .env
   # Edit .env with your actual Supabase and Gemini credentials
   ```

2. **Build Containers**
   ```bash
   docker-compose build
   ```

3. **Start Services**
   ```bash
   docker-compose up -d
   ```

4. **Verify Deployment**
   ```bash
   # Check backend health
   curl http://localhost:8000/health
   
   # Check frontend
   open http://localhost
   ```

5. **Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

6. **Stop Services**
   ```bash
   docker-compose down
   ```

---

## Render.com Deployment

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 2: Deploy Backend

1. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Select your repository
   - Set build command: `pip install -r backend/requirements.txt`
   - Set start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`

2. **Configure Environment**
   - Go to "Environment" tab
   - Add environment variables:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
     GEMINI_API_KEY=your_gemini_api_key
     ```

3. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Note the backend URL (e.g., `https://prepgenie-backend.onrender.com`)

### Step 3: Deploy Frontend

1. **Update Frontend Configuration**
   - Edit `frontend/.env`:
     ```
     REACT_APP_SUPABASE_URL=your_supabase_url
     REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
     REACT_APP_API_URL=https://prepgenie-backend.onrender.com
     ```

2. **Create Static Site**
   - Click "New +" → "Static Site"
   - Select your repository
   - Set build command: `cd frontend && npm install && npm run build`
   - Set publish directory: `frontend/build`

3. **Configure Backend URL in API**
   - Edit `frontend/src/api.js`
   - Update BASE_URL to your Render backend URL

### Step 4: Deploy
- Render automatically deploys on GitHub push
- Frontend URL will be provided (e.g., `https://prepgenie.onrender.com`)

---

## Railway.app Deployment

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create new project

### Step 2: Add Services

**Option A: Using Docker Compose (Recommended)**
1. Click "Deploy from Repo"
2. Select your GitHub repository
3. Railway auto-detects `docker-compose.yml`
4. Configure environment variables in Railway dashboard

**Option B: Manual Setup**

1. **Add Backend Service**
   - Click "Add Service" → "GitHub Repo"
   - Select your repo
   - Set root directory: `backend`
   - Environment variables:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
     GEMINI_API_KEY=your_gemini_api_key
     ```
   - Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`

2. **Add Frontend Service**
   - Click "Add Service" → "GitHub Repo"
   - Root directory: `frontend`
   - Environment variables:
     ```
     REACT_APP_SUPABASE_URL=your_supabase_url
     REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
     ```
   - Build command: `npm install && npm run build`
   - Start command: `npm start` or use Static Site option

### Step 3: Connect Services
- Link backend URL to frontend in API configuration
- Test endpoints

---

## Heroku Deployment

### Step 1: Heroku Setup
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create apps
heroku create prepgenie-backend
heroku create prepgenie-frontend
```

### Step 2: Deploy Backend
```bash
# Add Heroku remote
heroku git:remote -a prepgenie-backend

# Add buildpack for Python
heroku buildpacks:add heroku/python -a prepgenie-backend

# Set environment variables
heroku config:set SUPABASE_URL=your_supabase_url -a prepgenie-backend
heroku config:set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key -a prepgenie-backend
heroku config:set GEMINI_API_KEY=your_gemini_api_key -a prepgenie-backend

# Create Procfile in backend directory:
# web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Push and deploy
git push heroku main:main
```

### Step 3: Deploy Frontend
```bash
# Create Procfile in frontend directory:
# web: npm run build && npm start

heroku create prepgenie-frontend
heroku config:set REACT_APP_SUPABASE_URL=your_supabase_url -a prepgenie-frontend
heroku config:set REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key -a prepgenie-frontend

git push heroku main:main
```

### Step 4: Link Services
- Update frontend API URL to point to Heroku backend

---

## AWS Deployment

### Step 1: Setup AWS Account
- Create AWS account
- Set up IAM user with appropriate permissions
- Install AWS CLI: `pip install awscli`

### Step 2: ECR (Elastic Container Registry)

```bash
# Create ECR repositories
aws ecr create-repository --repository-name prepgenie-backend --region us-east-1
aws ecr create-repository --repository-name prepgenie-frontend --region us-east-1

# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin [your-account-id].dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
docker build -f Dockerfile.backend -t prepgenie-backend .
docker tag prepgenie-backend:latest [your-account-id].dkr.ecr.us-east-1.amazonaws.com/prepgenie-backend:latest
docker push [your-account-id].dkr.ecr.us-east-1.amazonaws.com/prepgenie-backend:latest

# Build and push frontend
docker build -f Dockerfile.frontend -t prepgenie-frontend .
docker tag prepgenie-frontend:latest [your-account-id].dkr.ecr.us-east-1.amazonaws.com/prepgenie-frontend:latest
docker push [your-account-id].dkr.ecr.us-east-1.amazonaws.com/prepgenie-frontend:latest
```

### Step 3: ECS (Elastic Container Service)

1. **Create Cluster**
   - Go to ECS → Clusters
   - Create new cluster (Fargate)

2. **Create Task Definitions**
   - Create task for backend with ECR image
   - Create task for frontend with ECR image

3. **Create Services**
   - Create service in cluster for each task
   - Configure load balancer
   - Set auto-scaling

### Step 4: RDS (Optional - if using managed database)
- Create RDS instance if not using Supabase
- Update connection strings in environment variables

---

## Production Checklist

### Security
- [ ] Never commit `.env` file
- [ ] Use secrets manager for API keys
- [ ] Enable HTTPS/SSL certificate
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring and alerting

### Performance
- [ ] Enable caching (Redis for backend, CDN for frontend)
- [ ] Optimize database queries
- [ ] Set up database indexes
- [ ] Enable compression (gzip)
- [ ] Minify and bundle frontend assets
- [ ] Use lazy loading for React components

### Reliability
- [ ] Set up health checks
- [ ] Configure auto-scaling
- [ ] Implement proper error handling
- [ ] Set up logging and monitoring (Sentry, DataDog)
- [ ] Create database backups
- [ ] Test failover scenarios

### Monitoring
- [ ] Application performance monitoring (APM)
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring
- [ ] Log aggregation (CloudWatch, ELK)
- [ ] Performance metrics dashboard
- [ ] Alert rules for critical issues

### CI/CD
- [ ] Set up GitHub Actions or similar
- [ ] Automated testing on pull requests
- [ ] Automated deployment on merge to main
- [ ] Database migration automation
- [ ] Blue-green deployment strategy

---

## Environment Variables Reference

### Backend (.env)
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Gemini AI
GEMINI_API_KEY=AIza...

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production
```

### Frontend (.env or .env.production)
```bash
# Supabase
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJ...

# API
REACT_APP_API_URL=https://your-backend-url.com
```

---

## Troubleshooting

### Backend Won't Start
```bash
# Check logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env

# Rebuild
docker-compose build --no-cache backend
```

### Frontend Won't Load
```bash
# Check nginx logs
docker-compose logs frontend

# Verify API connectivity
docker-compose exec frontend curl http://backend:8000/health
```

### Database Connection Issues
```bash
# Test Supabase connection
docker-compose exec backend python -c "from utils.storage import get_supabase_client; print(get_supabase_client())"
```

---

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec backend bash

# Restart services
docker-compose restart

# Remove all containers and volumes
docker-compose down -v

# Scale services
docker-compose up -d --scale backend=3

# Update containers
docker-compose pull && docker-compose up -d
```

---

## Cost Estimates (Monthly)

| Platform | Backend | Frontend | Database | Estimated Total |
|----------|---------|----------|----------|-----------------|
| Render.com | $10-25 | Free+ | Supabase $25+ | $35-50 |
| Railway | $10+ | Free+ | Supabase $25+ | $35+ |
| Heroku | $10-100+ | $10-100+ | Supabase $25+ | $45-225+ |
| AWS | $20-100+ | $20-100+ | Free tier or $25+ | $40-225+ |

---

## Support & Monitoring Links

- Supabase Dashboard: https://app.supabase.com
- Render Dashboard: https://dashboard.render.com
- Railway Dashboard: https://railway.app/dashboard
- Heroku Dashboard: https://dashboard.heroku.com
- AWS Console: https://console.aws.amazon.com
