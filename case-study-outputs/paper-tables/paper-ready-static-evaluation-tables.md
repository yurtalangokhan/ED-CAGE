# ED-CAGE Paper-Ready Static Evaluation Tables

## Table 1. Case Study Systems

| System | Architecture Style | Deployment Artifact Profile | Evaluated Mode | Applicable Governance Categories | Applicable Rules | Not Applicable Rules |
| --- | --- | --- | --- | --- | --- | --- |
| Spring PetClinic Microservices | Microservices | Docker Compose | Static | architecture, dependency, deployment, reliability, repository, security | 16 | 14 |
| Online Boutique | Microservices | Kubernetes manifests | Static | architecture, dependency, deployment, reliability, repository, security | 25 | 5 |
| Train Ticket | Microservices | Docker Compose + Kubernetes manifests | Static | architecture, dependency, deployment, reliability, repository, security | 28 | 2 |

## Table 2. Category-Weighted Governance Score Results

| System | Overall Score | Maturity Band | Applicable Rules | Not Applicable Rules | Passed Findings | Failed Findings | Skipped Findings | Error Findings |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Spring PetClinic Microservices | 73.58 | Managed Governance | 16 | 14 | 11 | 5 | 0 | 0 |
| Online Boutique | 53.69 | Emerging Governance | 25 | 5 | 11 | 13 | 1 | 1 |
| Train Ticket | 42.91 | Emerging Governance | 28 | 2 | 10 | 17 | 1 | 1 |

## Table 3. Category-Level Governance Scores

| System | Category | Category Score | Category Weight |
| --- | --- | --- | --- |
| Spring PetClinic Microservices | architecture | 50.00 | 1.20 |
| Spring PetClinic Microservices | dependency | 100.00 | 1.10 |
| Spring PetClinic Microservices | deployment | 100.00 | 1.10 |
| Spring PetClinic Microservices | reliability | 60.00 | 1.30 |
| Spring PetClinic Microservices | repository | 100.00 | 0.70 |
| Spring PetClinic Microservices | security | 50.00 | 1.30 |
| Online Boutique | architecture | 50.00 | 1.20 |
| Online Boutique | dependency | 100.00 | 1.10 |
| Online Boutique | deployment | 14.29 | 1.10 |
| Online Boutique | reliability | 40.00 | 1.30 |
| Online Boutique | repository | 100.00 | 0.70 |
| Online Boutique | security | 40.00 | 1.30 |
| Train Ticket | architecture | 25.00 | 1.20 |
| Train Ticket | dependency | 66.67 | 1.10 |
| Train Ticket | deployment | 25.00 | 1.10 |
| Train Ticket | reliability | 33.33 | 1.30 |
| Train Ticket | repository | 100.00 | 0.70 |
| Train Ticket | security | 33.33 | 1.30 |

## Table 4. Top Governance Gaps

| System | Rule ID | Category | Severity | Finding Title | Finding Message |
| --- | --- | --- | --- | --- | --- |
| Spring PetClinic Microservices | SEC-001 | security | critical | Repository must not contain obvious secrets | Potential committed secrets detected: 1. |
| Spring PetClinic Microservices | ARCH-002 | architecture | high | Quality attribute scenarios must be documented | Required repository path violations detected: 1. |
| Spring PetClinic Microservices | CMP-002 | reliability | high | Docker Compose services should define healthchecks | Docker Compose service healthcheck violations detected: 7. |
| Spring PetClinic Microservices | REL-005 | reliability | high | Retry policy must be bounded | Required repository configuration pattern group(s) missing: retry_attempt_bound. |
| Spring PetClinic Microservices | ARCH-001 | architecture | medium | ADR directory must exist | Required repository path violations detected: 1. |
| Online Boutique | SEC-001 | security | critical | Repository must not contain obvious secrets | Potential committed secrets detected: 1. |
| Online Boutique | TOOL-TRIVY-001 | security | critical | Repository should pass Trivy filesystem security baseline | External tool produced governance finding(s): 80. |
| Online Boutique | ARCH-002 | architecture | high | Quality attribute scenarios must be documented | Required repository path violations detected: 1. |
| Online Boutique | DEP-002 | deployment | high | Container image must not use latest tag | Kubernetes image policy violations detected: 1. |
| Online Boutique | DEP-003 | deployment | high | Container must define resource requests | Kubernetes resource requests policy violations detected: 1. |
| Online Boutique | DEP-004 | deployment | high | Container must define resource limits | Kubernetes resource requests policy violations detected: 1. |
| Online Boutique | DEP-005 | deployment | high | Deployment must define readinessProbe | Kubernetes readinessProbe policy violations detected: 2. |
| Online Boutique | DEP-006 | deployment | high | Deployment must define livenessProbe | Kubernetes livenessProbe policy violations detected: 2. |
| Train Ticket | DEPEN-002 | dependency | critical | Circular service dependencies must not exist | Architecture catalog policy failed: disallow_circular_dependencies. |
| Train Ticket | SEC-001 | security | critical | Repository must not contain obvious secrets | Potential committed secrets detected: 10. |
| Train Ticket | TOOL-TRIVY-001 | security | critical | Repository should pass Trivy filesystem security baseline | External tool produced governance finding(s): 3154. |
| Train Ticket | ARCH-002 | architecture | high | Quality attribute scenarios must be documented | Required repository path violations detected: 1. |
| Train Ticket | CMP-002 | reliability | high | Docker Compose services should define healthchecks | Docker Compose service healthcheck violations detected: 68. |
| Train Ticket | DEP-002 | deployment | high | Container image must not use latest tag | Kubernetes image policy violations detected: 67. |
| Train Ticket | DEP-003 | deployment | high | Container must define resource requests | Kubernetes resource requests policy violations detected: 7. |
| Train Ticket | DEP-004 | deployment | high | Container must define resource limits | Kubernetes resource requests policy violations detected: 7. |

## Table 5. Excluded / Not Applicable Rules

| System | Excluded Rule ID | Reason |
| --- | --- | --- |
| Spring PetClinic Microservices | DEP-001 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-002 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-003 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-004 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-005 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-006 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-007 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | DEP-008 | Kubernetes governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | REL-001 | Kubernetes-specific runtime/deployment evidence not available for this case. |
| Spring PetClinic Microservices | SEC-002 | Kubernetes-specific runtime/deployment evidence not available for this case. |
| Spring PetClinic Microservices | SEC-003 | Kubernetes-specific runtime/deployment evidence not available for this case. |
| Spring PetClinic Microservices | TOOL-K8S-001 | Kubernetes/IaC tool governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | TOOL-TRIVY-001 | Kubernetes/IaC tool governance not applicable to this case artifact profile. |
| Spring PetClinic Microservices | REPO-002 | Python-specific project metadata rule not applicable to this case technology stack. |
| Online Boutique | CMP-001 | Docker Compose governance not applicable to this case artifact profile. |
| Online Boutique | CMP-002 | Docker Compose governance not applicable to this case artifact profile. |
| Online Boutique | CMP-003 | Docker Compose governance not applicable to this case artifact profile. |
| Online Boutique | REPO-002 | Python-specific project metadata rule not applicable to this case technology stack. |
| Train Ticket | REPO-002 | Python-specific project metadata rule not applicable to this case technology stack. |
