# Platform v14.0 - Quick Start Guide

## 🚀 Quick Start (5 minutes)

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Kubernetes cluster (local or cloud)
kubectl version

# Docker
docker version
```

### 1. Deploy Complete Platform
```bash
# Deploy all 10 iterations
python code/bots/master_integration.py --deploy

# Expected output:
# 📦 Deploying CI/CD Pipeline...
# ✅ CI/CD Pipeline deployed successfully
# 📦 Deploying Service Mesh...
# ✅ Service Mesh deployed successfully
# ... (8 more iterations)
# ✅ Complete platform deployment finished!
```

### 2. Verify Deployment
```bash
# Check health of all iterations
python code/bots/master_integration.py --health

# Run integration tests
python code/bots/automated_testing.py

# Generate status report
python code/bots/master_integration.py --report
```

### 3. Start Monitoring Dashboard
```bash
# Launch web dashboard
python code/bots/monitoring_dashboard.py

# Open in browser: http://localhost:8080
```

---

## 📚 Module Usage

### Iteration 1: CI/CD Pipeline
```bash
# Create pipeline
python code/bots/iteration1_cicd_pipeline.py --create-pipeline

# Execute deployment
python code/bots/iteration1_cicd_pipeline.py --deploy
```

### Iteration 2: Service Mesh
```bash
# Setup service mesh
python code/bots/iteration2_service_mesh.py --setup-mesh
```

### Iteration 3: Observability
```bash
# Configure monitoring stack
python code/bots/iteration3_observability.py --setup
```

### Iteration 4: Chaos Engineering
```bash
# Run resilience suite
python code/bots/iteration4_chaos_engineering.py --run-suite
```

### Iteration 5: Secret Management
```bash
# Setup Vault
python code/bots/iteration5_secret_management.py --setup

# Provision secrets
python code/bots/iteration5_secret_management.py --provision
```

### Iteration 6: MLOps Platform
```bash
# Deploy ML pipeline
python code/bots/iteration6_mlops.py --deploy-model
```

### Iteration 7: Advanced Networking
```bash
# Configure networking
python code/bots/iteration7_networking.py --setup
```

### Iteration 8: Disaster Recovery
```bash
# Setup DR
python code/bots/iteration8_disaster_recovery.py --setup

# Test DR plan
python code/bots/iteration8_disaster_recovery.py --test-dr
```

### Iteration 9: Developer Portal
```bash
# Bootstrap portal
python code/bots/iteration9_developer_portal.py --bootstrap

# Start portal server
python code/bots/iteration9_developer_portal.py --serve
```

### Iteration 10: Enterprise Governance
```bash
# Configure governance
python code/bots/iteration10_governance.py --setup

# Run compliance check
python code/bots/iteration10_governance.py --compliance-check

# Cost optimization
python code/bots/iteration10_governance.py --cost-optimize
```

---

## 🎯 Common Workflows

### Deploy New Application
```bash
# 1. Create project from template
curl -X POST http://localhost:5000/api/templates/python-microservice

# 2. Provision namespace
curl -X POST http://localhost:5000/api/namespaces \
  -H "Content-Type: application/json" \
  -d '{"namespace":"my-app","team":"platform","quotas":{"requests.cpu":"10"}}'

# 3. Deploy via CI/CD
python code/bots/iteration1_cicd_pipeline.py --deploy
```

### Monitor Application
```bash
# 1. Check dashboard
open http://localhost:8080

# 2. View Grafana
open http://localhost:3000

# 3. Query Prometheus
curl http://localhost:9090/api/v1/query?query=up
```

### Chaos Testing
```bash
# Run full resilience suite
python code/bots/iteration4_chaos_engineering.py --run-suite

# View report
cat /var/lib/chaos/reports/*.md
```

### Disaster Recovery
```bash
# Trigger backup
python code/bots/iteration8_disaster_recovery.py --setup

# Execute failover
python code/bots/iteration8_disaster_recovery.py --test-dr
```

---

## 📊 Monitoring & Observability

### Dashboards
- **Platform Dashboard**: http://localhost:8080
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Developer Portal**: http://localhost:5000

### Logs
```bash
# Platform logs
tail -f /var/lib/master-platform/logs/*.log

# Kubernetes logs
kubectl logs -f -l app=my-service

# Loki logs
curl http://localhost:3100/loki/api/v1/query_range
```

---

## 🔧 Troubleshooting

### Check Platform Status
```bash
python code/bots/master_integration.py --health
```

### View Integration Tests
```bash
python code/bots/automated_testing.py
```

### Reset Platform
```bash
# Delete all resources
kubectl delete namespace default --all

# Redeploy
python code/bots/master_integration.py --deploy
```

---

## 📦 Platform Components

| Iteration | Module | Port | Dashboard |
|-----------|--------|------|-----------|
| 1 | CI/CD | - | Jenkins: 8080 |
| 2 | Service Mesh | - | Kiali: 20001 |
| 3 | Observability | 9090 | Grafana: 3000 |
| 4 | Chaos | - | - |
| 5 | Secrets | 8200 | Vault UI: 8200 |
| 6 | MLOps | 5000 | MLflow: 5000 |
| 7 | Networking | - | - |
| 8 | DR | - | - |
| 9 | Dev Portal | 5000 | Portal: 5000 |
| 10 | Governance | 8181 | OPA: 8181 |

---

## 🎓 Next Steps

1. **Customize Configuration**: Edit configs in `/var/lib/*/`
2. **Add Services**: Use Developer Portal templates
3. **Set Up Monitoring**: Configure Prometheus scrape targets
4. **Enable DR**: Configure backup schedules
5. **Implement Policies**: Add OPA policies for governance

---

## 💡 Best Practices

- ✅ Run integration tests before production
- ✅ Enable all observability features
- ✅ Schedule regular DR tests
- ✅ Use chaos engineering weekly
- ✅ Review cost optimization recommendations
- ✅ Keep secrets rotated (30/90 days)
- ✅ Monitor SLO/SLI dashboards
- ✅ Use self-service templates

---

## 📞 Support

- **Documentation**: See `V14_MEGA_EXPANSION_REPORT.md`
- **Integration Guide**: See `master_integration.py --help`
- **Test Results**: See `/var/lib/master-platform/logs/`

---

**Platform v14.0 is ready for production! 🚀**
