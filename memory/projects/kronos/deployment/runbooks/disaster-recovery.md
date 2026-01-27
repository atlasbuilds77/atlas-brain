# =====================================================
# KRONOS DISASTER RECOVERY PLAN
# =====================================================
# Recovery procedures for major incidents
# =====================================================

## Recovery Objectives

| Metric | Target | Description |
|--------|--------|-------------|
| **RTO** (Recovery Time Objective) | 4 hours | Maximum acceptable downtime |
| **RPO** (Recovery Point Objective) | 1 hour | Maximum acceptable data loss |

---

## Backup Strategy

### Database Backups
| Type | Frequency | Retention | Location |
|------|-----------|-----------|----------|
| Automated RDS Snapshots | Daily | 7 days | Same region |
| Manual Pre-deployment | Before each deployment | 30 days | Same region |
| Cross-region Copy | Daily | 30 days | us-east-1 (DR region) |
| Point-in-time Recovery | Continuous | 7 days | RDS built-in |

### File Storage (S3)
- **Versioning**: Enabled on all buckets
- **Cross-region Replication**: kronos-files → kronos-files-dr (us-east-1)
- **Lifecycle**: Archive to Glacier after 365 days (WISP compliance)

### Configuration Backups
- Terraform state in S3 with versioning
- Secrets Manager with multi-region replication
- Infrastructure documented in code

---

## Disaster Scenarios

### Scenario 1: Single Service Failure
**Impact**: One service (backend/frontend/worker) down
**Detection**: CloudWatch alarm, health check failure
**Recovery Time**: 5-15 minutes

**Procedure**:
1. ECS will automatically replace unhealthy tasks
2. If persistent, force new deployment:
   ```bash
   aws ecs update-service --cluster kronos-production \
     --service kronos-backend --force-new-deployment
   ```
3. If still failing, rollback to previous version

---

### Scenario 2: Database Failure
**Impact**: All services affected, data access lost
**Detection**: RDS alarm, connection errors in Sentry
**Recovery Time**: 15-60 minutes

**Procedure**:

**Option A: Failover to Read Replica (if configured)**
```bash
aws rds promote-read-replica \
  --db-instance-identifier kronos-production-replica
```

**Option B: Restore from Snapshot**
```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier kronos-production

# Restore
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier kronos-production-restored \
  --db-snapshot-identifier kronos-production-2024-01-15
```

**Option C: Point-in-Time Recovery**
```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier kronos-production \
  --target-db-instance-identifier kronos-production-pit \
  --restore-time 2024-01-15T10:00:00Z
```

After restore:
1. Update application connection strings
2. Verify data integrity
3. Run application health checks
4. Update DNS/load balancer if needed

---

### Scenario 3: Region-Wide Outage
**Impact**: Complete service unavailability
**Detection**: Multiple AWS service alarms, CloudFlare alerts
**Recovery Time**: 1-4 hours

**Procedure**:

1. **Assess** (10 min)
   - Check AWS Health Dashboard
   - Confirm region-wide issue
   - Notify stakeholders

2. **Activate DR Region** (30 min)
   ```bash
   # Switch Terraform to DR region
   cd terraform/
   terraform workspace select dr
   
   # Apply DR infrastructure
   terraform apply -var="environment=dr"
   ```

3. **Restore Database** (30 min)
   ```bash
   # Copy latest snapshot to DR region
   aws rds copy-db-snapshot \
     --source-db-snapshot-identifier arn:aws:rds:us-west-2:ACCOUNT:snapshot:kronos-daily \
     --target-db-snapshot-identifier kronos-dr-restore \
     --source-region us-west-2 \
     --region us-east-1
   
   # Restore in DR region
   aws rds restore-db-instance-from-db-snapshot \
     --db-instance-identifier kronos-dr \
     --db-snapshot-identifier kronos-dr-restore \
     --region us-east-1
   ```

4. **Deploy Services** (30 min)
   ```bash
   # Deploy to DR ECS cluster
   ./scripts/deploy.sh dr latest
   ```

5. **Update DNS** (10 min)
   - Route 53 health check should auto-failover
   - If manual: update CNAME to DR load balancer
   - CloudFlare: update origin servers

6. **Verify & Communicate**
   - Run smoke tests
   - Update status page
   - Notify users

---

### Scenario 4: Data Corruption
**Impact**: Incorrect or corrupted data in database
**Detection**: User reports, data integrity checks
**Recovery Time**: 1-2 hours

**Procedure**:

1. **Stop the Bleeding**
   - Identify source of corruption
   - If application bug: rollback deployment
   - If external: block access

2. **Assess Damage**
   ```sql
   -- Check recent changes
   SELECT * FROM audit_log 
   WHERE timestamp > NOW() - INTERVAL '24 hours'
   ORDER BY timestamp DESC;
   ```

3. **Choose Recovery Method**

   **Option A: Targeted Restore (preferred)**
   - Restore corrupted tables only from backup
   - Use pg_dump/pg_restore for specific tables

   **Option B: Point-in-Time Recovery**
   - Restore entire database to before corruption
   - May lose some valid data

4. **Verify Data Integrity**
   ```bash
   # Run data integrity checks
   python manage.py check_data_integrity
   ```

---

### Scenario 5: Security Breach
**Impact**: Potential data exposure, system compromise
**Detection**: Sentry alerts, unusual activity, user reports
**Recovery Time**: Variable (prioritize containment)

**Procedure**:

1. **Contain** (Immediate)
   ```bash
   # Revoke all user sessions
   redis-cli FLUSHALL
   
   # Rotate secrets
   aws secretsmanager rotate-secret --secret-id kronos/production/app-secrets
   
   # If severe: take service offline
   aws ecs update-service --cluster kronos-production \
     --service kronos-backend --desired-count 0
   ```

2. **Investigate**
   - Review CloudTrail logs
   - Check Sentry for suspicious errors
   - Analyze access patterns

3. **Remediate**
   - Patch vulnerability
   - Rotate all credentials
   - Review and revoke compromised tokens

4. **Communicate**
   - Legal team notification
   - User notification (if data exposed)
   - Regulatory reporting (if required)

5. **Post-Incident**
   - Full security audit
   - Penetration testing
   - Updated security procedures

---

## DR Testing Schedule

| Test Type | Frequency | Description |
|-----------|-----------|-------------|
| Backup Restore | Monthly | Restore from snapshot to test instance |
| Failover Drill | Quarterly | Simulate service failure and recovery |
| Full DR Exercise | Annually | Complete region failover simulation |

### Monthly Backup Test Procedure
```bash
# Restore test
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier kronos-backup-test \
  --db-snapshot-identifier $(aws rds describe-db-snapshots \
    --db-instance-identifier kronos-production \
    --query 'DBSnapshots[-1].DBSnapshotIdentifier' \
    --output text)

# Verify
psql -h kronos-backup-test.xxx.us-west-2.rds.amazonaws.com -U kronos_admin -c "SELECT COUNT(*) FROM users;"

# Cleanup
aws rds delete-db-instance --db-instance-identifier kronos-backup-test --skip-final-snapshot
```

---

## Emergency Contacts

| Role | Contact | Escalation |
|------|---------|------------|
| On-Call Engineer | PagerDuty | 24/7 |
| Platform Lead | TBD | Business hours |
| AWS TAM | AWS Console | P1 issues |
| Security Lead | TBD | Security incidents |

---

*Last Updated: 2024-01-26*
*Next DR Test: 2024-02-15*
*Annual Review: 2025-01-01*
