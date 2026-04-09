# PrepGenie Production Deployment Checklist

## Pre-Deployment (Before Going Live)

### Security ✓
- [ ] Remove all hardcoded credentials
- [ ] Enable HTTPS/SSL certificates
- [ ] Set secure CORS origins (only your domains)
- [ ] Configure firewall rules
- [ ] Enable WAF (Web Application Firewall)
- [ ] Rotate API keys
- [ ] Set strong database passwords
- [ ] Enable database backups
- [ ] Test vulnerability scanning
- [ ] Review security headers

### Environment Setup ✓
- [ ] Production Supabase project created
- [ ] Database schema deployed (`supabase_setup.sql`)
- [ ] Environment variables configured
- [ ] Secrets manager initialized (e.g., AWS Secrets Manager)
- [ ] .env file NOT committed to repository
- [ ] API keys rotated
- [ ] OAuth providers configured (Google)

### Backend Configuration ✓
- [ ] FastAPI configured for production
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Request timeout configured
- [ ] Error handling tested
- [ ] Database connection pooling enabled
- [ ] Logging configured
- [ ] Monitoring configured

### Frontend Configuration ✓
- [ ] Build optimized (npm run build)
- [ ] Environment variables set correctly
- [ ] API URL points to production backend
- [ ] Service worker configured (if PWA)
- [ ] CDN configured (optional)
- [ ] Analytics enabled
- [ ] Error tracking enabled (Sentry)

### Database ✓
- [ ] All tables created
- [ ] RLS policies enabled
- [ ] Indexes created for performance
- [ ] Backup strategy defined
- [ ] Point-in-time recovery enabled
- [ ] Read replicas configured (if needed)
- [ ] Connection limits set

### Monitoring & Logging ✓
- [ ] APM configured (Datadog, New Relic)
- [ ] Error tracking setup (Sentry)
- [ ] Log aggregation configured (CloudWatch, ELK)
- [ ] Health check endpoints verified
- [ ] Alert rules created
- [ ] Dashboard created
- [ ] Uptime monitoring enabled

---

## Deployment Day Checklist

### Pre-Deployment Verification ✓
- [ ] Database backed up
- [ ] Monitoring systems online
- [ ] Incident response team on standby
- [ ] Communication channels open
- [ ] Rollback plan documented
- [ ] Pre-deployment testing completed

### Deployment Steps ✓
- [ ] Deploy database migrations
- [ ] Deploy backend services
- [ ] Verify backend health checks
- [ ] Deploy frontend static assets
- [ ] Verify frontend loads
- [ ] Run smoke tests
- [ ] Monitor error rates
- [ ] Check performance metrics

### Post-Deployment Verification ✓
- [ ] All endpoints responding
- [ ] No error spike in logs
- [ ] Database performing well
- [ ] Frontend loads < 2s
- [ ] API responses < 500ms
- [ ] Authentication working
- [ ] Admin dashboard accessible
- [ ] Student dashboard functional

### Post-Deployment Monitoring ✓
- [ ] Monitor for 1 hour continuously
- [ ] Check error rates every 5 minutes
- [ ] Verify database performance
- [ ] Monitor server resources (CPU, Memory)
- [ ] Check user feedback
- [ ] Review analytics

---

## Post-Deployment Maintenance

### Daily (First Week)
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Review user feedback
- [ ] Verify backups completed
- [ ] Check uptime monitoring

### Weekly
- [ ] Review security logs
- [ ] Check for updates
- [ ] Analyze performance trends
- [ ] Update documentation
- [ ] Review cost metrics

### Monthly
- [ ] Security audit
- [ ] Performance audit
- [ ] Capacity planning
- [ ] Cost optimization
- [ ] Backup testing
- [ ] Disaster recovery drill

---

## Rollback Procedure

If deployment fails:

1. **Immediate Actions**
   - Alert the team
   - Stop deployments
   - Activate incident response

2. **Database Rollback**
   - Restore from backup
   - Verify data integrity
   - Test connections

3. **Application Rollback**
   - Docker: `docker-compose down && docker-compose up -d [old-version]`
   - Kubernetes: `kubectl rollout undo deployment/prepgenie`
   - Platform-specific: Use platform's rollback feature

4. **Verification**
   - Run smoke tests
   - Verify all endpoints
   - Check database integrity
   - Monitor error rates

5. **Post-Incident**
   - Document what went wrong
   - Create action items
   - Schedule post-mortem
   - Update runbooks

---

## Performance Targets

| Metric | Target | Action If Failed |
|--------|--------|------------------|
| Frontend Load | < 2s | Check CDN, optimize assets |
| API Response | < 500ms | Check database, scale backend |
| Error Rate | < 0.1% | Review logs, fix bugs |
| Uptime | > 99.9% | Check infrastructure, failover |
| Database CPU | < 70% | Scale database, optimize queries |
| Memory Usage | < 80% | Scale servers, optimize code |

---

## Incident Response Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| On-Call Engineer | TBD | - | - |
| Backend Lead | TBD | - | - |
| DevOps Lead | TBD | - | - |
| Product Lead | TBD | - | - |

---

## Important URLs

- **Supabase Dashboard:** https://app.supabase.com
- **Production Backend:** (Add your URL)
- **Production Frontend:** (Add your URL)
- **Monitoring Dashboard:** (Add your URL)
- **Error Tracking:** (Add your URL)
- **Log Aggregation:** (Add your URL)

---

## Secrets Management

### AWS Secrets Manager Example
```bash
# Store secrets
aws secretsmanager create-secret \
  --name prepgenie/prod \
  --secret-string '{"SUPABASE_URL":"...","GEMINI_API_KEY":"..."}'

# Retrieve secrets
aws secretsmanager get-secret-value --secret-id prepgenie/prod
```

### Environment Variables
- Never commit .env files
- Use platform's secrets manager
- Rotate keys quarterly
- Use service accounts with limited permissions

---

## Scaling Guidelines

### When to Scale Backend
- CPU > 70%
- Memory > 80%
- Response time > 1s
- Error rate > 0.5%

### When to Scale Database
- Query time > 500ms
- CPU > 75%
- Connections > 80% of max
- Disk usage > 80%

### When to Scale Frontend
- CDN bandwidth > limits
- Cache hit rate < 60%
- First contentful paint > 3s

---

## Cost Optimization

- [ ] Enable spot instances (AWS)
- [ ] Use CDN for static assets
- [ ] Optimize database queries
- [ ] Right-size server instances
- [ ] Set up auto-scaling policies
- [ ] Use caching (Redis)
- [ ] Archive old data
- [ ] Review cloud spending monthly

---

## Compliance & Security

- [ ] GDPR compliant (data retention)
- [ ] SOC2 requirements met
- [ ] HIPAA compliant if needed
- [ ] Encrypted at rest
- [ ] Encrypted in transit
- [ ] Regular penetration testing
- [ ] Security patches applied
- [ ] Audit logs enabled

---

## Disaster Recovery Plan

### RTO/RPO Targets
- **RTO:** 4 hours
- **RPO:** 1 hour

### Recovery Steps
1. Restore database from backup
2. Redeploy application
3. Verify all Services
4. Notify stakeholders
5. Document incident

### Test Schedule
- [ ] Test quarterly (minimal)
- [ ] Full test bi-annually
- [ ] Post-incident testing

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Deployment Lead | | | |
| Backend Lead | | | |
| DevOps Lead | | | |
| Product Lead | | | |
| CTO/Tech Lead | | | |

---

**Prepared By:** ________________________  
**Date:** ________________________  
**For Deployment:** ________________________  
**Review Date:** ________________________
