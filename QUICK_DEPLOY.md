# 🚀 PrepGenie Quick Deployment Guide

## Choose Your Deployment Method

### 🐳 Option 1: Docker (Local/Any Server)

**Prerequisites:**
- Docker installed
- Docker Compose installed
- Environment variables configured

**Windows Users:**
```powershell
# Run the deployment script
powershell -ExecutionPolicy Bypass -File deploy.ps1
# Select option 1 to build and start
```

**Mac/Linux Users:**
```bash
# Make script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

**Manual Docker Setup:**
```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env with your credentials

# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# Access:
# - Frontend: http://localhost
# - Backend: http://localhost:8000
```

---

### ◀️ Option 2: Render.com (Easiest - Recommended for Beginners)

1. **Create Account:** https://render.com (connect GitHub)

2. **Deploy Backend:**
   - New → Web Service
   - Select repo
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`
   - Add environment variables
   - Deploy
   - Copy backend URL (e.g., `https://prepgenie-backend.onrender.com`)

3. **Deploy Frontend:**
   - New → Static Site
   - Select repo
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/build`
   - Add environment variables
   - Deploy
   - Copy frontend URL

4. **Update API URL:**
   - Edit `frontend/src/api.js`
   - Change BASE_URL to your Render backend URL

---

### 🚂 Option 3: Railway.app (Very Easy)

1. **Create Account:** https://railway.app (connect GitHub)

2. **Deploy:**
   - New Project → Deploy from GitHub
   - Select your repo
   - Railway auto-detects `docker-compose.yml`
   - Add environment variables
   - Deploy automatically

3. **Get URLs:**
   - Railway generates URLs for frontend and backend
   - Update API configuration

---

### 🟣 Option 4: Heroku

1. **Setup:**
   ```bash
   npm install -g heroku
   heroku login
   ```

2. **Deploy Backend:**
   ```bash
   heroku create prepgenie-backend
   heroku config:set SUPABASE_URL=your_url -a prepgenie-backend
   heroku config:set SUPABASE_SERVICE_ROLE_KEY=your_key -a prepgenie-backend
   heroku config:set GEMINI_API_KEY=your_key -a prepgenie-backend
   git push heroku main:main
   ```

3. **Deploy Frontend:**
   ```bash
   heroku create prepgenie-frontend
   heroku config:set REACT_APP_SUPABASE_URL=your_url -a prepgenie-frontend
   git push heroku main:main
   ```

---

## Environment Variables Needed

### Backend
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_xxxxx
GEMINI_API_KEY=AIza_xxxxx
```

### Frontend
```
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=sb_publishable_xxxxx
```

---

## Post-Deployment Checklist

- [ ] Set up Supabase database (run `supabase_setup.sql`)
- [ ] Test login with Supabase auth
- [ ] Generate a roadmap
- [ ] Mark tasks as complete
- [ ] Check admin dashboard
- [ ] Monitor backend health endpoint
- [ ] Set up error tracking (Sentry)
- [ ] Configure domain/SSL
- [ ] Enable monitoring/alerting

---

## Service Comparison

| Platform | Setup Time | Cost | Best For |
|----------|-----------|------|----------|
| Docker | 10 mins | Server cost | Development, self-hosted |
| Render | 15 mins | $10/mo+ | Small to medium projects |
| Railway | 15 mins | $10/mo+ | Startups |
| Heroku | 20 mins | $10-100+/mo | Quick deployment |
| AWS | 30+ mins | $20-200+/mo | Scalable enterprise |

---

## Help & Support

**Troubleshooting:**
- Backend won't start? Check `docker-compose logs backend`
- Frontend can't reach API? Verify BASE_URL in `api.js`
- Database error? Run Supabase setup SQL
- Auth failing? Check Supabase anon key

**Documentation:**
- [Full Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Audit Summary](./AUDIT_FIXES_SUMMARY.md)
- [Supabase Docs](https://supabase.com/docs)

---

## Next Steps

1. **Choose deployment method** (recommended: Render for simplicity)
2. **Set up environment variables**
3. **Deploy services**
4. **Run database setup**
5. **Test the application**
6. **Configure monitoring**
7. **Scale as needed**

---

Good luck! 🎉
