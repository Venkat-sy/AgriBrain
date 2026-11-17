# AgriBrain Operations Runbook

**Version:** 3.0.0  
**Last Updated:** 2025-11-17  
**Platform:** Vercel (Frontend) + Render (Backend) + PostgreSQL

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Backup & Restore](#database-backup--restore)
3. [Secret Key Rotation](#secret-key-rotation)
4. [Deployment Procedures](#deployment-procedures)
5. [Cold Start & Troubleshooting](#cold-start--troubleshooting)
6. [Monitoring & Alerting](#monitoring--alerting)
7. [Rollback Procedures](#rollback-procedures)

---

## Architecture Overview

```
+-----------------+     HTTPS      +-----------------+
|   Vercel        | <------------> |   Render        |
|   (Frontend)    |   API Calls    |   (Backend)     |
|   Next.js 16    |                |   FastAPI       |
+-----------------+                +--------+--------+
                                    |
                                    v
                             +-----------------+
                             |   PostgreSQL    |
                             |   (Render DB)   |
                             +-----------------+
```

**Services:**
- **Frontend:** Vercel (Next.js 16, App Router, standalone output)
- **Backend:** Render Web Service (FastAPI, uvicorn, Python 3.11)
- **Database:** Render PostgreSQL (managed, auto-backed up)
- **Redis:** Upstash (optional, for distributed rate limiting)
- **External APIs:** Open-Meteo (weather), Nominatim (geocoding), Groq (LLM)

---

## Database Backup & Restore

### Automated Backups (Render Managed)

Render PostgreSQL provides automatic daily backups with 7-day retention.
- **Location:** Render Dashboard > Database > Backups
- **Retention:** 7 days (Starter plan), 30 days (Pro+)
- **Format:** pg_dump custom format

### Manual Backup (On-Demand)

```bash
# 1. Get connection string from Render Dashboard
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# 2. Create backup
pg_dump -Fc --no-acl --no-owner $DATABASE_URL > agribrain_backup_$(date +%Y%m%d_%H%M%S).dump

# 3. Verify backup
pg_restore --list agribrain_backup_$(date +%Y%m%d).dump | head -20
```

### Restore Procedure

```bash
# 1. Download backup from Render Dashboard or use local .dump file
# 2. Get target database URL
export TARGET_DB_URL="postgresql://user:pass@host:5432/dbname"

# 3. Terminate existing connections
psql $TARGET_DB_URL -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'agribrain' AND pid <> pg_backend_pid();
"

# 4. Drop and recreate database (if needed)
# WARNING: This destroys all data!
# psql $TARGET_DB_URL -c "DROP DATABASE agribrain; CREATE DATABASE agribrain;"

# 5. Restore
pg_restore --verbose --clean --no-acl --no-owner -d $TARGET_DB_URL agribrain_backup_20251117.dump

# 6. Verify
psql $TARGET_DB_URL -c "SELECT COUNT(*) FROM districts; SELECT COUNT(*) FROM crop_profiles;"
```

### Schema Migrations

```bash
# Run migrations after restore
cd backend
alembic upgrade head

# Verify migration
alembic current
```

---

## Secret Key Rotation

### Groq API Key (LLM)

**When to rotate:** Monthly, or immediately if exposed.

**Procedure:**
1. Go to https://console.groq.com/keys
2. Create new API key
3. Update in both platforms:

**Render (Backend):**
```
Render Dashboard > agribrain-backend > Environment > GROQ_API_KEY > Edit > Paste new key > Save
```

**Vercel (Frontend - if used client-side):**
```
Vercel Dashboard > agribrain-frontend > Settings > Environment Variables > GROQ_API_KEY > Edit > Save > Redeploy
```

4. Verify: Test chat endpoint
```bash
curl -X POST https://agribrain-backend.onrender.com/api/v1/chat/troubleshoot   -H "Authorization: Bearer <token>"   -H "Content-Type: application/json"   -d '{"session_id": "test", "user_question": "Hello", "is_context_aware": false}'
```

### JWT RS256 Keys (Critical - affects ALL active sessions)

**When to rotate:** Quarterly, or immediately if private key compromised.

**WARNING:** Rotating JWT keys invalidates ALL existing access/refresh tokens. Users will be logged out.

**Procedure:**
```bash
# 1. Generate new keys (run on backend server)
cd backend
python scripts/generate_keys.py

# 2. This creates:
#    - keys/private_key.pem (NEW)
#    - keys/public_key.pem (NEW)
#    - keys/jwks.json (NEW - for public key distribution)

# 3. Update Render environment variables
#    Render Dashboard > agribrain-backend > Environment
#    No env vars needed for keys (files are in repo), but ensure keys/ directory is deployed

# 4. Deploy backend (triggers restart)
#    Render Dashboard > Manual Deploy > Deploy latest commit

# 5. Frontend users will need to re-login (tokens invalidated)
```

### Database Password

Render manages this. To rotate:
```
Render Dashboard > Database > Settings > Rotate Password
```
Then update `DATABASE_URL` in backend service env vars.

### Redis (Upstash) Token

```
Upstash Console > Database > Settings > Regenerate Token
Update UPSTASH_REDIS_REST_TOKEN in Render backend env vars
```

---

## Deployment Procedures

### Prerequisites

- GitHub repo connected to both Vercel and Render
- Render PostgreSQL database created and linked
- All environment variables configured (see `.env.example`)

### Backend Deployment (Render)

**Automatic (on push to main):**
1. Push to `main` branch
2. Render detects changes > builds > deploys automatically
3. Monitor: Render Dashboard > Events

**Manual Deploy:**
```bash
# Option 1: Render Dashboard
# Render Dashboard > agribrain-backend > Manual Deploy > Deploy latest commit

# Option 2: Render CLI
render deploy agribrain-backend
```

**Build Process:**
```bash
# 1. pip install -r requirements.txt
# 2. python -m py_compile (syntax check)
# 3. alembic upgrade head (migrations)
# 4. uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Health Check:**
- Path: `/health`
- Expected: `{"status": "healthy", "database": "connected"}`

### Frontend Deployment (Vercel)

**Automatic (on push to main):**
1. Push to `main` branch
2. Vercel detects changes > builds > deploys
3. Monitor: Vercel Dashboard > Deployments

**Manual Deploy:**
```bash
# Option 1: Vercel Dashboard
# Vercel Dashboard > agribrain-frontend > Deployments > Redeploy

# Option 2: Vercel CLI
cd frontend_web
vercel --prod
```

**Build Process:**
```bash
# 1. npm install
# 2. npm run build (Next.js standalone output)
# 3. Output: .next/standalone/
```

**Environment Variables (Vercel):**
```
NEXT_PUBLIC_BACKEND_URL=https://agribrain-backend.onrender.com
```

### Full Stack Deploy Order

1. **Database migrations first** (if schema changes)
   ```bash
   # Render runs alembic upgrade head during build
   ```

2. **Backend deploy** (with new API)
   ```bash
   # Wait for health check to pass
   ```

3. **Frontend deploy** (with new UI)
   ```bash
   # Uses new backend API
   ```

---

## Cold Start & Troubleshooting

### Backend Cold Start (Render Starter Plan)

**Symptom:** First request after 15min inactivity takes 30-60s.

**Cause:** Render spins down free/Starter services.

**Solutions:**
1. **Upgrade to Standard plan** (always on)
2. **External ping** (cron job every 10min):
   ```bash
   # GitHub Actions / cron-job.org / UptimeRobot
   curl -s https://agribrain-backend.onrender.com/health > /dev/null
   ```
3. **Acceptable for dev** - users see loading spinner

### Frontend Cold Start (Vercel)

**Symptom:** First page load slower.

**Cause:** Edge function cold start.

**Solution:** Vercel Pro enables "Always On" for functions.

### Common Issues

| Issue | Diagnosis | Fix |
|-------|-----------|-----|
| 502 Bad Gateway | Backend not started | Check Render logs, wait for deploy |
| CORS error | Wrong ALLOWED_ORIGINS | Update Render env var, redeploy |
| JWT expired | Token > 15min old | Frontend should auto-refresh |
| Rate limited | Too many requests | Check tier, implement backoff |
| DB connection failed | DB down or wrong URL | Check Render DB status, verify DATABASE_URL |
| Groq API error | Invalid/expired key | Rotate GROQ_API_KEY |
| Weather not loading | Open-Meteo down | Check fallback in logs |

### Debugging Commands

```bash
# Backend logs
render logs agribrain-backend --tail 100

# Test health endpoint
curl https://agribrain-backend.onrender.com/health

# Test API with auth
curl -X POST https://agribrain-backend.onrender.com/api/v1/auth/login   -H "Content-Type: application/x-www-form-urlencoded"   -d "username=test@example.com&password=test123"

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM districts;"

# Frontend logs (Vercel)
vercel logs agribrain-frontend --since 1h
```

---

## Monitoring & Alerting

### Health Checks

| Service | Endpoint | Expected | Frequency |
|---------|----------|----------|-----------|
| Backend | /health | status: healthy | Every 30s |
| Frontend | / | 200 OK | Every 60s |
| Database | SELECT 1 | 1 row | Every 60s |
| Weather API | /api/v1/spatial/weather | 200 OK | Every 5min |

### Recommended Alerts

1. **Backend Down** - /health returns non-200 for 2 consecutive checks
2. **High Error Rate** - >5% 5xx errors in 5min
3. **Rate Limit Exhausted** - >80% of tier limit used
4. **Database Connections** - >80% of pool used
5. **Slow Response** - p95 > 5s for /api/v1/simulation/run

### Key Metrics to Watch

- Request latency (p50, p95, p99)
- Error rate by endpoint
- Active users / sessions
- Rate limit utilization by tier
- Database query performance
- ML inference time (SHAP + XGBoost)

---

## Rollback Procedures

### Backend Rollback

```bash
# Option 1: Render Dashboard > Deployments > Rollback to previous
# Option 2: Git revert + push
git revert HEAD
git push origin main

# Option 3: Manual deploy specific commit
render deploy agribrain-backend --commit <commit-sha>
```

### Frontend Rollback

```bash
# Option 1: Vercel Dashboard > Deployments > Promote previous
# Option 2: Git revert + push
git revert HEAD
git push origin main

# Option 3: Vercel CLI
vercel rollback agribrain-frontend
```

### Database Rollback (Schema)

```bash
# 1. Identify migration to rollback
alembic history

# 2. Downgrade
alembic downgrade -1  # or specific revision

# 3. Verify
alembic current
```

### Database Rollback (Data)

```bash
# Use pg_restore from backup (see Database Backup & Restore)
pg_restore --clean --no-acl --no-owner -d $TARGET_DB_URL backup.dump
```

---

## Appendix: Key File Locations

| File | Purpose |
|------|---------|
| backend/requirements.txt | Python dependencies |
| backend/render.yaml | Render service definition |
| frontend_web/vercel.json | Vercel deployment config |
| backend/.env.example | All environment variables |
| backend/scripts/generate_keys.py | JWT key generation |
| backend/alembic/ | Database migrations |
| backend/models/ | ML model artifacts |

---

*End of Runbook*
