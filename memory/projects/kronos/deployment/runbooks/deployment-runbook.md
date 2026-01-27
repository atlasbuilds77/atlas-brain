# =====================================================
# KRONOS DEPLOYMENT RUNBOOK
# =====================================================
# Operations guide for managing Kronos deployments
# =====================================================

## Table of Contents
1. [Daily Operations](#daily-operations)
2. [Deployment Procedures](#deployment-procedures)
3. [Incident Response](#incident-response)
4. [Monitoring & Alerts](#monitoring--alerts)
5. [Database Operations](#database-operations)
6. [Scaling](#scaling)

---

## Daily Operations

### Morning Checklist
- [ ] Check Sentry for overnight errors
- [ ] Review CloudWatch dashboards
- [ ] Verify daily digest emails were sent (6 AM)
- [ ] Check database backup status
- [ ] Review any pending deployments

### Health Check Commands
```bash
# Quick health check
curl https://app.kronos.app/health

# Detailed system status
curl https://app.kronos.app/api/v1/system/status

# Check all services
aws ecs describe-services \
  --cluster kronos-production \
  --services kronos-backend kronos-frontend kronos-worker \
  --query 'services[*].[serviceName,runningCount,desiredCount]' \
  --output table
```

---

## Deployment Procedures

### Standard Deployment (via CI/CD)
1. Merge PR to `main` branch
2. CI/CD automatically triggers
3. Monitor deployment in GitHub Actions
4. Verify in Sentry release tracking
5. Check smoke tests pass

### Manual Deployment (Emergency Only)
```bash
# From deployment directory
./scripts/deploy.sh production v1.2.3
```

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Security scan clean
- [ ] Database migrations tested on staging
- [ ] Feature flags configured
- [ ] Stakeholders notified
- [ ] Rollback plan ready

### Rollback Procedure
```bash
# Rollback to previous version
./scripts/rollback.sh production 1

# Rollback to specific deployment
aws s3 ls s3://kronos-deployments/production/  # List deployments
# Then manually apply specific deployment JSON
```

---

## Incident Response

### Severity Levels
- **P1 (Critical)**: Service down, data loss risk, security breach
- **P2 (High)**: Major feature broken, significant performance degradation
- **P3 (Medium)**: Minor feature issue, workaround available
- **P4 (Low)**: Cosmetic issues, documentation

### P1 Incident Playbook
1. **Assess** (2 min)
   - Check Sentry for errors
   - Review CloudWatch alarms
   - Identify affected services

2. **Communicate** (5 min)
   - Post in #kronos-incidents Slack channel
   - Notify on-call engineer
   - Update status page

3. **Mitigate** (immediate)
   - If deployment-related: ROLLBACK IMMEDIATELY
   - If traffic-related: Enable rate limiting
   - If database-related: Failover to replica

4. **Resolve**
   - Apply fix or confirm rollback successful
   - Verify services healthy
   - Monitor for 15 minutes

5. **Post-Mortem** (within 48 hours)
   - Document timeline
   - Root cause analysis
   - Action items

### Common Issues & Fixes

#### API 502 Errors
```bash
# Check ECS task health
aws ecs describe-tasks --cluster kronos-production --tasks $(aws ecs list-tasks --cluster kronos-production --service-name kronos-backend --query 'taskArns[0]' --output text)

# Force new deployment
aws ecs update-service --cluster kronos-production --service kronos-backend --force-new-deployment
```

#### Database Connection Issues
```bash
# Check RDS status
aws rds describe-db-instances --db-instance-identifier kronos-production --query 'DBInstances[0].DBInstanceStatus'

# Check connection count
psql -h $DB_HOST -U kronos_admin -c "SELECT count(*) FROM pg_stat_activity;"
```

#### Redis Connection Issues
```bash
# Check ElastiCache status
aws elasticache describe-cache-clusters --cache-cluster-id kronos-production

# Flush cache if corrupted (CAUTION)
redis-cli -h $REDIS_HOST FLUSHALL
```

---

## Monitoring & Alerts

### Key Metrics
| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API Response Time | >500ms | >2s | Scale up / investigate |
| Error Rate | >1% | >5% | Investigate / rollback |
| CPU Utilization | >70% | >90% | Scale up |
| Memory Usage | >80% | >95% | Scale up / restart |
| Database Connections | >80% | >95% | Increase pool size |
| Queue Depth | >100 | >500 | Scale workers |

### CloudWatch Dashboards
- **Production Overview**: Main service health
- **API Performance**: Latency percentiles, error rates
- **Database**: Connections, CPU, storage
- **Workers**: Queue depth, processing time

### Setting Up Alerts
```bash
# Create CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name "kronos-backend-cpu-high" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ClusterName,Value=kronos-production Name=ServiceName,Value=kronos-backend \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-west-2:ACCOUNT:kronos-alerts
```

---

## Database Operations

### Backup Verification
```bash
# List recent snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier kronos-production \
  --query 'DBSnapshots[-5:].[DBSnapshotIdentifier,SnapshotCreateTime,Status]' \
  --output table

# Create manual snapshot before major changes
aws rds create-db-snapshot \
  --db-snapshot-identifier kronos-pre-migration-$(date +%Y%m%d) \
  --db-instance-identifier kronos-production
```

### Running Migrations
```bash
# Via ECS task
aws ecs run-task \
  --cluster kronos-production \
  --task-definition kronos-migrations \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={...}"

# Monitor migration
aws logs tail /ecs/kronos/production/migrations --follow
```

### Emergency Database Restore
```bash
# Restore to point in time
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier kronos-production \
  --target-db-instance-identifier kronos-production-restored \
  --restore-time 2024-01-15T10:00:00Z
```

---

## Scaling

### Manual Scaling
```bash
# Scale backend service
aws ecs update-service \
  --cluster kronos-production \
  --service kronos-backend \
  --desired-count 4

# Scale worker service
aws ecs update-service \
  --cluster kronos-production \
  --service kronos-worker \
  --desired-count 3
```

### Autoscaling Configuration
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/kronos-production/kronos-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
  --policy-name kronos-cpu-scaling \
  --service-namespace ecs \
  --resource-id service/kronos-production/kronos-backend \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    }
  }'
```

### Tax Season Scaling (January-April)
During tax season, increase baseline capacity:
- Backend: 4 → 8 instances
- Workers: 2 → 4 instances
- Database: db.t3.medium → db.r6g.large
- Redis: cache.t3.micro → cache.r6g.large

---

## Contacts

| Role | Name | Contact |
|------|------|---------|
| Primary On-Call | TBD | Slack: #kronos-oncall |
| Platform Lead | TBD | |
| Database Admin | TBD | |
| AWS Support | - | AWS Console |

---

*Last Updated: 2024-01-26*
*Review Schedule: Monthly*
