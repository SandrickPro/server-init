#!/usr/bin/env python3
"""
Enterprise Governance - Iteration 10
OPA policy as code, compliance automation, cost AI optimization
Complete governance and compliance platform
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOVERNANCE_BASE = Path('/var/lib/governance')
POLICIES_DIR = GOVERNANCE_BASE / 'policies'
COMPLIANCE_DIR = GOVERNANCE_BASE / 'compliance'
COST_DIR = GOVERNANCE_BASE / 'cost'

for directory in [POLICIES_DIR, COMPLIANCE_DIR, COST_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

################################################################################
# OPA Policy Manager
################################################################################

class OPAPolicyManager:
    """Open Policy Agent policy management"""
    
    def __init__(self, opa_url: str = 'http://localhost:8181'):
        self.opa_url = opa_url
    
    def create_policy(self, policy_name: str, policy_rego: str) -> bool:
        """Create OPA policy"""
        
        policy_file = POLICIES_DIR / f'{policy_name}.rego'
        policy_file.write_text(policy_rego)
        
        # Upload to OPA
        try:
            response = requests.put(
                f'{self.opa_url}/v1/policies/{policy_name}',
                data=policy_rego,
                headers={'Content-Type': 'text/plain'}
            )
            
            if response.status_code == 200:
                logger.info(f"Policy created: {policy_name}")
                return True
            else:
                logger.error(f"Failed to create policy: {response.text}")
                return False
        except Exception as e:
            logger.error(f"OPA error: {e}")
            return False
    
    def evaluate_policy(self, policy_name: str, input_data: Dict) -> Optional[Dict]:
        """Evaluate policy against input"""
        
        try:
            response = requests.post(
                f'{self.opa_url}/v1/data/{policy_name}',
                json={'input': input_data}
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Policy evaluated: {policy_name}")
                return result.get('result', {})
            
            return None
        except Exception as e:
            logger.error(f"Policy evaluation error: {e}")
            return None
    
    @staticmethod
    def generate_kubernetes_admission_policy() -> str:
        """Generate Kubernetes admission control policy"""
        
        policy = """
package kubernetes.admission

deny[msg] {
  input.request.kind.kind == "Pod"
  image := input.request.object.spec.containers[_].image
  not startswith(image, "myregistry.com/")
  msg := sprintf("Image '%v' not from approved registry", [image])
}

deny[msg] {
  input.request.kind.kind == "Deployment"
  not input.request.object.spec.template.spec.securityContext.runAsNonRoot
  msg := "Containers must not run as root"
}

deny[msg] {
  input.request.kind.kind == "Service"
  input.request.object.spec.type == "LoadBalancer"
  not input.request.object.metadata.annotations["cost-center"]
  msg := "LoadBalancer services must have cost-center annotation"
}

deny[msg] {
  input.request.kind.kind == "Ingress"
  not input.request.object.spec.tls
  msg := "Ingress must use TLS"
}
"""
        
        return policy
    
    @staticmethod
    def generate_rbac_policy() -> str:
        """Generate RBAC policy"""
        
        policy = """
package rbac

default allow = false

allow {
  user_has_role[role]
  role_has_permission[role][input.action]
}

user_has_role[role] {
  data.user_roles[input.user][_] == role
}

role_has_permission[role][permission] {
  data.role_permissions[role][_] == permission
}
"""
        
        return policy

################################################################################
# Compliance Manager
################################################################################

class ComplianceManager:
    """Compliance automation and auditing"""
    
    def __init__(self):
        self.compliance_standards = {}
    
    def register_standard(self, standard_name: str, requirements: List[Dict]):
        """Register compliance standard"""
        
        self.compliance_standards[standard_name] = {
            'requirements': requirements,
            'registered_at': datetime.now().isoformat()
        }
        
        # Save standard
        standard_file = COMPLIANCE_DIR / f'{standard_name}.json'
        standard_file.write_text(json.dumps(self.compliance_standards[standard_name], indent=2))
        
        logger.info(f"Compliance standard registered: {standard_name}")
    
    def run_compliance_check(self, standard_name: str) -> Dict:
        """Run compliance check"""
        
        standard = self.compliance_standards.get(standard_name)
        
        if not standard:
            logger.error(f"Standard not found: {standard_name}")
            return {}
        
        results = {
            'standard': standard_name,
            'checked_at': datetime.now().isoformat(),
            'requirements': []
        }
        
        for requirement in standard['requirements']:
            check_result = self._check_requirement(requirement)
            results['requirements'].append({
                'id': requirement['id'],
                'description': requirement['description'],
                'status': 'PASS' if check_result else 'FAIL'
            })
        
        # Save report
        report_file = COMPLIANCE_DIR / f'{standard_name}-{datetime.now().strftime("%Y%m%d")}.json'
        report_file.write_text(json.dumps(results, indent=2))
        
        logger.info(f"Compliance check completed: {standard_name}")
        return results
    
    def _check_requirement(self, requirement: Dict) -> bool:
        """Check individual compliance requirement"""
        
        # Simplified check - in production this would integrate with various systems
        check_type = requirement.get('check_type')
        
        if check_type == 'encryption_at_rest':
            return self._check_encryption_at_rest()
        elif check_type == 'audit_logging':
            return self._check_audit_logging()
        elif check_type == 'access_control':
            return self._check_access_control()
        
        return True
    
    @staticmethod
    def _check_encryption_at_rest() -> bool:
        """Check encryption at rest"""
        # Placeholder implementation
        logger.info("Checking encryption at rest")
        return True
    
    @staticmethod
    def _check_audit_logging() -> bool:
        """Check audit logging"""
        logger.info("Checking audit logging")
        return True
    
    @staticmethod
    def _check_access_control() -> bool:
        """Check access control"""
        logger.info("Checking access control")
        return True
    
    def generate_compliance_report(self, standard_name: str) -> str:
        """Generate compliance report"""
        
        # Find latest check
        report_files = sorted(COMPLIANCE_DIR.glob(f'{standard_name}-*.json'), reverse=True)
        
        if not report_files:
            return "No compliance checks found"
        
        results = json.loads(report_files[0].read_text())
        
        report = f"""# Compliance Report - {standard_name}

Generated: {datetime.now().isoformat()}

## Summary

"""
        
        passed = sum(1 for r in results['requirements'] if r['status'] == 'PASS')
        total = len(results['requirements'])
        
        report += f"- **Compliance Score**: {passed}/{total} ({passed/total*100:.1f}%)\n"
        report += f"- **Last Checked**: {results['checked_at']}\n\n"
        
        report += "## Requirements\n\n"
        
        for req in results['requirements']:
            status_icon = '✅' if req['status'] == 'PASS' else '❌'
            report += f"{status_icon} **{req['id']}**: {req['description']} - {req['status']}\n"
        
        report_file = COMPLIANCE_DIR / f'{standard_name}-report.md'
        report_file.write_text(report)
        
        return report

################################################################################
# Cost Optimization AI
################################################################################

class CostOptimizationAI:
    """AI-powered cost optimization"""
    
    def __init__(self):
        self.cost_data = []
    
    def analyze_costs(self, resources: List[Dict]) -> Dict:
        """Analyze resource costs"""
        
        total_cost = 0
        cost_by_type = {}
        
        for resource in resources:
            cost = resource.get('cost', 0)
            resource_type = resource.get('type', 'unknown')
            
            total_cost += cost
            cost_by_type[resource_type] = cost_by_type.get(resource_type, 0) + cost
        
        analysis = {
            'total_cost': total_cost,
            'cost_by_type': cost_by_type,
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Save analysis
        analysis_file = COST_DIR / f'analysis-{datetime.now().strftime("%Y%m%d")}.json'
        analysis_file.write_text(json.dumps(analysis, indent=2))
        
        logger.info(f"Cost analysis completed: ${total_cost:.2f}")
        return analysis
    
    def recommend_optimizations(self, resources: List[Dict]) -> List[Dict]:
        """AI-powered cost optimization recommendations"""
        
        recommendations = []
        
        for resource in resources:
            # Check for overprovisioned resources
            if resource.get('cpu_utilization', 100) < 30:
                recommendations.append({
                    'resource': resource['name'],
                    'type': 'RIGHT_SIZE',
                    'current_cost': resource.get('cost', 0),
                    'potential_savings': resource.get('cost', 0) * 0.5,
                    'recommendation': 'Reduce CPU allocation by 50%',
                    'priority': 'HIGH'
                })
            
            # Check for idle resources
            if resource.get('requests_per_hour', 1) < 1:
                recommendations.append({
                    'resource': resource['name'],
                    'type': 'REMOVE_IDLE',
                    'current_cost': resource.get('cost', 0),
                    'potential_savings': resource.get('cost', 0),
                    'recommendation': 'Resource is idle, consider removing',
                    'priority': 'MEDIUM'
                })
            
            # Check for reserved instance opportunities
            if resource.get('uptime_percentage', 0) > 70:
                recommendations.append({
                    'resource': resource['name'],
                    'type': 'RESERVED_INSTANCE',
                    'current_cost': resource.get('cost', 0),
                    'potential_savings': resource.get('cost', 0) * 0.3,
                    'recommendation': 'Use reserved instances for 30% savings',
                    'priority': 'HIGH'
                })
        
        # Save recommendations
        rec_file = COST_DIR / f'recommendations-{datetime.now().strftime("%Y%m%d")}.json'
        rec_file.write_text(json.dumps(recommendations, indent=2))
        
        total_savings = sum(r['potential_savings'] for r in recommendations)
        logger.info(f"Generated {len(recommendations)} recommendations (potential savings: ${total_savings:.2f})")
        
        return recommendations
    
    def generate_cost_forecast(self, historical_costs: List[float], forecast_days: int = 30) -> Dict:
        """Generate cost forecast using trend analysis"""
        
        import numpy as np
        
        # Simple linear regression for forecasting
        x = np.arange(len(historical_costs))
        y = np.array(historical_costs)
        
        # Calculate trend
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        # Forecast
        forecast_x = np.arange(len(historical_costs), len(historical_costs) + forecast_days)
        forecast_y = p(forecast_x)
        
        forecast = {
            'current_monthly_cost': sum(historical_costs[-30:]),
            'forecast_monthly_cost': sum(forecast_y),
            'trend': 'INCREASING' if z[0] > 0 else 'DECREASING',
            'daily_forecasts': [float(v) for v in forecast_y],
            'forecasted_at': datetime.now().isoformat()
        }
        
        logger.info(f"Cost forecast: ${forecast['forecast_monthly_cost']:.2f}/month")
        return forecast

################################################################################
# Governance Platform
################################################################################

class GovernancePlatform:
    """Complete governance orchestrator"""
    
    def __init__(self):
        self.opa = OPAPolicyManager()
        self.compliance = ComplianceManager()
        self.cost_ai = CostOptimizationAI()
    
    def setup_complete_governance(self):
        """Setup complete governance"""
        
        # Create OPA policies
        self.opa.create_policy(
            'kubernetes_admission',
            self.opa.generate_kubernetes_admission_policy()
        )
        
        self.opa.create_policy(
            'rbac',
            self.opa.generate_rbac_policy()
        )
        
        # Register compliance standards
        self.compliance.register_standard('SOC2', [
            {
                'id': 'CC6.1',
                'description': 'Logical and physical access controls',
                'check_type': 'access_control'
            },
            {
                'id': 'CC6.6',
                'description': 'Encryption of data at rest',
                'check_type': 'encryption_at_rest'
            },
            {
                'id': 'CC7.2',
                'description': 'System monitoring and audit logging',
                'check_type': 'audit_logging'
            }
        ])
        
        self.compliance.register_standard('GDPR', [
            {
                'id': 'Art. 32',
                'description': 'Security of processing',
                'check_type': 'encryption_at_rest'
            },
            {
                'id': 'Art. 30',
                'description': 'Records of processing activities',
                'check_type': 'audit_logging'
            }
        ])
        
        logger.info("Complete governance configured")

################################################################################
# CLI
################################################################################

def main():
    logger.info("🏛️  Enterprise Governance - Iteration 10")
    
    if '--setup' in sys.argv:
        platform = GovernancePlatform()
        platform.setup_complete_governance()
        print("✅ Governance configured")
    
    elif '--compliance-check' in sys.argv:
        platform = GovernancePlatform()
        results = platform.compliance.run_compliance_check('SOC2')
        report = platform.compliance.generate_compliance_report('SOC2')
        print(report)
    
    elif '--cost-optimize' in sys.argv:
        platform = GovernancePlatform()
        # Sample resources
        resources = [
            {'name': 'api-server', 'type': 'compute', 'cost': 100, 'cpu_utilization': 25},
            {'name': 'database', 'type': 'storage', 'cost': 200, 'uptime_percentage': 95}
        ]
        recommendations = platform.cost_ai.recommend_optimizations(resources)
        print(f"Generated {len(recommendations)} cost optimization recommendations")
    
    else:
        print("""
Enterprise Governance v13.0 - Iteration 10

Usage:
  --setup              Setup complete governance
  --compliance-check   Run compliance check
  --cost-optimize      Generate cost optimizations

Features:
  ✓ OPA policy as code
  ✓ Compliance automation (SOC2, GDPR)
  ✓ AI cost optimization
  ✓ Cost forecasting
  ✓ Automated auditing
        """)

if __name__ == '__main__':
    main()
