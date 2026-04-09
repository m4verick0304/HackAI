# 🎯 PrepGenie Complete Deployment Guide with APIs

## 📚 Quick Navigation

1. **[First Time? Start Here](#getting-started)** ← Begin here
2. **[Docker Quick Start](#docker-quick-start)** ← Recommended
3. **[Cloud Deployment](#cloud-deployment)** ← Render, Railway, Heroku
4. **[API Reference](#api-reference)** ← All endpoints
5. **[Production Setup](#production-setup)** ← Before going live

---

## 🚀 Getting Started

### What You'll Need

| Item | Why | Where to Get |
|------|-----|-------------|
| Supabase Account | Database | [supabase.com](https://supabase.com) - Free tier |
| Gemini API Key | AI Power | [makersuite.google.com](https://makersuite.google.com) - Free tier |
| GitHub Account | Code hosting | [github.com](https://github.com) - Free |
| Docker (Optional) | Easy deployment | [docker.com](https://docker.com) - Free |

### Time Required

| Method | Setup Time | Running Time |
|--------|-----------|--------------|
| Docker | 10 minutes | Ongoing |
| Render | 15 minutes | Ongoing |
| Railway | 15 minutes | Ongoing |
| Local Setup | 20 minutes | Running on your machine |

---

## 🐳 Docker Quick Start

### Step 1: Prepare Files

```bash
# Navigate to project
cd PrepGenie

# Copy environment template
cp .env.example .env

# Edit .env with YOUR credentials
# (Windows: notepad .env)
# (Mac: nano .env)
# (Linux: vim .env)
```

### Step 2: Run Using Script

**Windows Users:**
```powershell
# Run the deployment script (PowerShell)
powershell -ExecutionPolicy Bypass -File deploy.ps1

# Select option 1 to build and start
```

**Mac/Linux Users:**
```bash
# Make script executable
chmod +x deploy.sh

# Run script
./deploy.sh
```

### Step 3: Verify It's Running

```bash
# Check services are healthy
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 4: Access the Application

```
🌐 Frontend:  http://localhost
📡 Backend:   http://localhost:8000
📚 API Docs:  http://localhost:8000/docs
📊 Health:    http://localhost:8000/health
```

---

## 🌩️ Cloud Deployment

### Option A: Render.com (EASIEST ⭐)

**Why Render?** Free tier, automatic CI/CD, no credit card needed

**Step 1: Connect GitHub**
1. Go to [render.com](https://render.com)
2. Click "New +"
3. Sign up with GitHub

**Step 2: Deploy Backend**
1. Click "New +" → "Web Service"
2. Select your PrepGenie repository
3. Configure:
   ```
   Build command:  pip install -r backend/requirements.txt
   Start command:  cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
   ```
4. Add environment variables:
   ```
   SUPABASE_URL = your_supabase_url
   SUPABASE_SERVICE_ROLE_KEY = your_service_role_key
   GEMINI_API_KEY = your_gemini_api_key
   ```
5. Click "Create Web Service"
6. Wait ~3 minutes for deployment
7. Copy the backend URL (e.g., `https://prepgenie-backend.onrender.com`)

**Step 3: Deploy Frontend**
1. Click "New +" → "Static Site"
2. Select same repository
3. Configure:
   ```
   Build command:        cd frontend && npm install && npm run build
   Publish directory:    frontend/build
   ```
4. Add environment variables:
   ```
   REACT_APP_SUPABASE_URL = your_supabase_url
   REACT_APP_SUPABASE_ANON_KEY = your_supabase_anon_key
   ```
5. Click "Create Static Site"
6. Get your frontend URL

**Step 4: Update API URL**
```javascript
// frontend/src/api.js - Change line 1:
// OLD: const BASE_URL = 'http://localhost:8000';
// NEW: const BASE_URL = 'https://prepgenie-backend.onrender.com';
```

Done! ✅ Both services deployed and running.

---

### Option B: Railway.app

1. Go to [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub"
3. Select PrepGenie repo
4. Railway auto-detects `docker-compose.yml`
5. Add environment variables
6. Auto-deploys on GitHub push

---

### Option C: Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Deploy backend
heroku create prepgenie-backend -b heroku/python
heroku config:set SUPABASE_URL=... SUPABASE_SERVICE_ROLE_KEY=... GEMINI_API_KEY=...
git push heroku main:main

# Deploy frontend
heroku create prepgenie-frontend -b heroku/static
```

---

## 🔌 API Reference

All endpoints are BASE_URL based:
- Local: `http://localhost:8000`
- Production: `https://your-backend.deployed.com`

### Authentication

```bash
# All protected endpoints require:
Authorization: Bearer <supabase_jwt_token>
```

### Core Endpoints

#### 1️⃣ Health Check
```bash
GET /health
# No auth required
# Response: { "status": "ok", "service": "PrepGenie FastAPI Backend", "version": "2.0.0" }
```

#### 2️⃣ Generate Roadmap
```bash
POST /generate-roadmap
Content-Type: application/json

{
  "resume_text": "John Doe\nSkills: Python, React, SQL...",
  "goal": "SDE",
  "name": "John Doe"
}

# Response:
{
  "success": true,
  "student_id": "uuid",
  "name": "John Doe",
  "skills": ["python", "react", "sql"],
  "goal": "SDE",
  "roadmap": [
    {
      "day": 1,
      "task": "Revise Arrays & Strings...",
      "topic": "DSA",
      "completed": false,
      "missed": false
    }
  ],
  "probability": 62,
  "status": "Learning"
}
```

#### 3️⃣ Update Tasks
```bash
POST /update-tasks
Content-Type: application/json

{
  "student_id": "uuid",
  "roadmap": [
    {
      "day": 1,
      "task": "...",
      "topic": "DSA",
      "completed": true,
      "missed": false
    }
  ]
}

# Response: Updated student with new probability
```

#### 4️⃣ Simulate Improvement
```bash
POST /simulate
Content-Type: application/json

{
  "skills": ["python", "react"],
  "goal": "SDE",
  "tasks_completed": 5,
  "tasks_missed": 1
}

# Response:
{
  "current_probability": 62,
  "improved_probability": 85,
  "probability_gain": 23,
  "skills_to_add": ["system design", "dsa"],
  "simulation_narrative": "..."
}
```

#### 5️⃣ Get Admin Data
```bash
GET /admin-data
Authorization: Bearer <admin_jwt>

# Response:
{
  "success": true,
  "students": [
    {
      "id": "uuid",
      "name": "John",
      "status": "Learning",
      "probability": 62
    }
  ],
  "total": 1,
  "by_status": {
    "Ready": 0,
    "Learning": 1,
    "At Risk": 0
  }
}
```

### Testing Endpoints

**Using cURL:**
```bash
# Health check
curl http://localhost:8000/health

# Generate roadmap
curl -X POST http://localhost:8000/generate-roadmap \
  -H "Content-Type: application/json" \
  -d '{"resume_text":"Python, SQL, Git","goal":"SDE","name":"Test"}'

# API Documentation (interactive)
open http://localhost:8000/docs
```

**Using Python:**
```python
import requests

# Generate roadmap
response = requests.post(
    'http://localhost:8000/generate-roadmap',
    json={
        'resume_text': 'Python, SQL, reactjs',
        'goal': 'SDE',
        'name': 'Test User'
    }
)
print(response.json())
```

**Using JavaScript:**
```javascript
// Generate roadmap
const response = await fetch('http://localhost:8000/generate-roadmap', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    resume_text: 'Python, SQL, React',
    goal: 'SDE',
    name: 'Test User'
  })
});
const data = await response.json();
console.log(data);
```

---

## 🗄️ Database Setup

### Initial Setup (One Time)

1. **Create Supabase Project**
   - Go to supabase.com → New Project
   - Set password securely
   - Save credentials

2. **Run SQL Setup**
   - Open Supabase Dashboard
   - SQL Editor → New Query
   - Copy from `backend/supabase_setup.sql`
   - Execute
   - Tables created with RLS policies ✅

3. **Verify Tables**
   ```sql
   SELECT * FROM profiles;
   SELECT * FROM students;
   SELECT * FROM job_descriptions;
   ```

### Sample Data

```sql
-- Check sample jobs added
SELECT * FROM job_descriptions LIMIT 5;

-- Create test user (optional)
INSERT INTO profiles (id, email, full_name, role)
VALUES (
  gen_random_uuid(),
  'test@example.com',
  'Test User',
  'student'
);
```

---

## 🔐 Production Setup

### Before Going Live

See [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md) for complete checklist.

**Key Points:**
- [ ] SSL Certificate configured
- [ ] Database backups enabled
- [ ] Monitoring/alerts set up
- [ ] Error tracking enabled (Sentry)
- [ ] Rate limiting configured
- [ ] CORS properly set
- [ ] Environment variables in secrets manager
- [ ] Team on-call schedule

### Environment Variables (Secrets Manager)

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name prepgenie/production \
  --secret-string '{
    "SUPABASE_URL": "...",
    "SUPABASE_SERVICE_ROLE_KEY": "...",
    "GEMINI_API_KEY": "..."
  }'
```

---

## 📊 Monitoring & Logging

### Health Checks
```bash
# Backend health
curl https://your-backend.com/health

# Expected response
{"status": "ok", ...}
```

### Docker Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Production Monitoring
- Uptime: https://uptimerobot.com
- Error Tracking: https://sentry.io
- Analytics: https://analytics.google.com
- Performance: https://newrelic.com

---

## 🆘 Troubleshooting

### "Cannot connect to backend"
```
Fix: 
1. Check backend is running: docker-compose ps
2. Verify BASE_URL in frontend/src/api.js
3. Check firewall rules
4. Restart services: docker-compose restart
```

### "Database connection failed"
```
Fix:
1. Verify SUPABASE_URL in .env
2. Check SUPABASE_SERVICE_ROLE_KEY is correct
3. Verify network access in Supabase dashboard
4. Test from backend: python -c "from utils.storage import get_supabase_client; print(get_supabase_client())"
```

### "Authentication error"
```
Fix:
1. Verify REACT_APP_SUPABASE_ANON_KEY
2. Check Supabase OAuth settings
3. Clear browser cookies
4. Verify JWT token expiration
```

---

## 📈 Scaling Guide

| Load | Recommendation |
|------|----------------|
| 1-100 users | Single container + Supabase free |
| 100-1K users | 2-3 backend containers + basic DB scaling |
| 1K-10K users | Load balancer + DB read replicas + CDN |
| 10K+ users | Auto-scaling + Database sharding + Redis cache |

---

## 🎓 Useful Resources

| Resource | Purpose |
|----------|---------|
| [FastAPI Docs](https://fastapi.tiangolo.com) | Backend framework |
| [React Docs](https://react.dev) | Frontend framework |
| [Supabase Docs](https://supabase.com/docs) | Database |
| [Docker Docs](https://docs.docker.com) | Containerization |
| [GitHub Actions](https://docs.github.com/actions) | CI/CD |

---

## 🚀 Next Steps

1. ✅ Set up Supabase account
2. ✅ Get Gemini API key
3. ✅ Choose deployment method
4. ✅ Deploy services
5. ✅ Test endpoints
6. ✅ Set up monitoring
7. ✅ Go live! 🎉

---

## 📞 Support

- **Documentation:** See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Troubleshooting:** See [QUICK_DEPLOY.md](./QUICK_DEPLOY.md)
- **Production:** See [PRODUCTION_CHECKLIST.md](./PRODUCTION_CHECKLIST.md)
- **Issues:** Create GitHub issue

---

**Happy Deploying! 🎉**
