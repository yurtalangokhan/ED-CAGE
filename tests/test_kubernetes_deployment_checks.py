from pathlib import Path

from ed_cage.checks.deployment.kubernetes_image_policy_check import (
    KubernetesImagePolicyCheck,
)
from ed_cage.checks.deployment.kubernetes_manifests_exist_check import (
    KubernetesManifestsExistCheck,
)
from ed_cage.checks.deployment.kubernetes_probe_check import KubernetesProbeCheck
from ed_cage.checks.deployment.kubernetes_resource_policy_check import (
    KubernetesResourcePolicyCheck,
)
from ed_cage.checks.deployment.kubernetes_security_context_check import (
    KubernetesSecurityContextCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_kubernetes_manifests_exist_check_passes_when_manifest_exists(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _valid_deployment_manifest())

    finding = KubernetesManifestsExistCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-001",
            check_type="kubernetes_manifests_exist",
            params=_base_params(),
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["manifest_count"] == 1


def test_kubernetes_image_policy_check_fails_for_latest_tag(
    tmp_path: Path,
) -> None:
    _write_manifest(
        tmp_path,
        _valid_deployment_manifest().replace(
            "image: app:1.0.0",
            "image: app:latest",
        ),
    )

    finding = KubernetesImagePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-002",
            check_type="kubernetes_image_policy",
            params={
                **_base_params(),
                "disallow_latest_tag": True,
                "require_explicit_tag": True,
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "latest_tag_is_not_allowed"


def test_kubernetes_resource_policy_check_fails_when_requests_missing(
    tmp_path: Path,
) -> None:
    manifest = _valid_deployment_manifest().replace(
        """
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
""",
        """
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
""",
    )
    _write_manifest(tmp_path, manifest)

    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-003",
            check_type="kubernetes_resource_policy",
            params={
                **_base_params(),
                "policy": "require_requests",
                "required_resources": ["cpu", "memory"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    evidence_data = finding.evidence[0].data
    assert evidence_data["policy"] == "require_requests"
    assert evidence_data["resource_section"] == "requests"
    violations = evidence_data["violations"]
    assert violations[0]["reason"] == "requests_section_missing"
    assert violations[0]["missing_resources"] == ["cpu", "memory"]


def test_kubernetes_resource_policy_check_fails_when_limits_missing(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest_without_limits())

    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-004",
            check_type="kubernetes_resource_policy",
            params={
                **_base_params(),
                "policy": "require_limits",
                "required_resources": ["cpu", "memory"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    evidence_data = finding.evidence[0].data
    assert evidence_data["policy"] == "require_limits"
    assert evidence_data["resource_section"] == "limits"
    violations = evidence_data["violations"]
    assert violations[0]["reason"] == "limits_section_missing"
    assert violations[0]["missing_resources"] == ["cpu", "memory"]


def test_dep004_passes_when_limits_exist_even_if_requests_are_missing(
    tmp_path: Path,
) -> None:
    manifest = _valid_deployment_manifest().replace(
        """
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
""",
        """
          resources:
            limits:
              cpu: 500m
              memory: 512Mi
""",
    )
    _write_manifest(tmp_path, manifest)

    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-004",
            check_type="kubernetes_resource_policy",
            params={
                **_base_params(),
                "policy": "require_limits",
                "required_resources": ["cpu", "memory"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    evidence_data = finding.evidence[0].data
    assert evidence_data["policy"] == "require_limits"
    assert evidence_data["resource_section"] == "limits"
    assert evidence_data["violations"] == []


def test_legacy_required_resource_section_limits_is_supported(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest_without_limits())

    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-004",
            check_type="kubernetes_resource_policy",
            params={
                **_base_params(),
                "required_resource_section": "limits",
                "required_resources": ["cpu", "memory"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    evidence_data = finding.evidence[0].data
    assert evidence_data["manifest_count"] == 1
    assert evidence_data["evaluated_containers"] == 1
    assert evidence_data["policy"] == "require_limits"
    assert evidence_data["resource_section"] == "limits"
    assert evidence_data["violations"][0]["reason"] == "limits_section_missing"


def test_conflicting_resource_policy_parameters_return_error(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _valid_deployment_manifest())

    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-004",
            check_type="kubernetes_resource_policy",
            params={
                **_base_params(),
                "policy": "require_limits",
                "required_resource_section": "requests",
                "required_resources": ["cpu", "memory"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.ERROR
    evidence_data = finding.evidence[0].data
    assert evidence_data["reason"] == "conflicting_resource_policy_parameters"


def test_kubernetes_probe_check_fails_when_readiness_probe_missing(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest_without_readiness_probe())

    finding = KubernetesProbeCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-005",
            check_type="kubernetes_probe",
            params={
                **_base_params(),
                "probe_type": "readinessProbe",
                "required_for_kinds": ["Deployment"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    violations = finding.evidence[0].data["violations"]
    assert len(violations) == 1
    assert violations[0]["missing_probe"] == "readinessProbe"


def test_kubernetes_security_context_check_fails_for_privileged_container(
    tmp_path: Path,
) -> None:
    manifest = _valid_deployment_manifest().replace(
        "privileged: false",
        "privileged: true",
    )
    _write_manifest(tmp_path, manifest)

    finding = KubernetesSecurityContextCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-007",
            check_type="kubernetes_security_context",
            severity=Severity.CRITICAL,
            params={
                **_base_params(),
                "policy": "disallow_privileged",
                "required_for_kinds": ["Deployment"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "privileged_container_is_not_allowed"


def test_kubernetes_security_context_check_passes_for_non_root_container(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _valid_deployment_manifest())

    finding = KubernetesSecurityContextCheck().evaluate(
        rule=_build_rule(
            rule_id="DEP-008",
            check_type="kubernetes_security_context",
            severity=Severity.HIGH,
            params={
                **_base_params(),
                "policy": "require_run_as_non_root",
                "required_for_kinds": ["Deployment"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )


def _build_rule(
    rule_id: str,
    check_type: str,
    params: dict[str, object],
    severity: Severity = Severity.HIGH,
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        category="deployment",
        severity=severity,
        target="kubernetes",
        check_type=check_type,
        params=params,
    )


def _base_params() -> dict[str, object]:
    return {
        "manifest_paths": ["k8s"],
        "file_patterns": ["*.yaml"],
    }


def _write_manifest(tmp_path: Path, content: str) -> None:
    manifest_dir = tmp_path / "k8s"
    manifest_dir.mkdir(exist_ok=True)
    manifest_file = manifest_dir / "deployment.yaml"
    manifest_file.write_text(content, encoding="utf-8")


def _valid_deployment_manifest() -> str:
    return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: app
          image: app:1.0.0
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          securityContext:
            privileged: false
            runAsNonRoot: true
            runAsUser: 10001
"""


def _deployment_manifest_without_limits() -> str:
    return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: app
          image: app:1.0.0
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
          readinessProbe:
            httpGet:
              path: /ready
              port: 8080
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          securityContext:
            privileged: false
            runAsNonRoot: true
            runAsUser: 10001
"""


def _deployment_manifest_without_readiness_probe() -> str:
    return """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 10001
      containers:
        - name: app
          image: app:1.0.0
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
          securityContext:
            privileged: false
            runAsNonRoot: true
            runAsUser: 10001
"""
