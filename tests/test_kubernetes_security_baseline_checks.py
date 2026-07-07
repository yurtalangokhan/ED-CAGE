from pathlib import Path

from ed_cage.checks.security.kubernetes_ingress_tls_check import KubernetesIngressTlsCheck
from ed_cage.checks.security.kubernetes_service_exposure_policy_check import (
    KubernetesServiceExposurePolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_kubernetes_ingress_tls_check_passes_when_tls_covers_rule_host(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _ingress_with_tls())

    finding = KubernetesIngressTlsCheck().evaluate(
        rule=_build_rule(
            rule_id="SEC-002",
            check_type="kubernetes_ingress_tls",
            params={
                **_base_params(),
                "require_tls_hosts_cover_rules": True,
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_kubernetes_ingress_tls_check_fails_when_tls_missing(tmp_path: Path) -> None:
    _write_manifest(tmp_path, _ingress_without_tls())

    finding = KubernetesIngressTlsCheck().evaluate(
        rule=_build_rule(
            rule_id="SEC-002",
            check_type="kubernetes_ingress_tls",
            params={
                **_base_params(),
                "require_tls_hosts_cover_rules": True,
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "missing_tls"


def test_kubernetes_service_exposure_policy_passes_for_cluster_ip(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _cluster_ip_service())

    finding = KubernetesServiceExposurePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="SEC-003",
            check_type="kubernetes_service_exposure_policy",
            params={
                **_base_params(),
                "disallowed_service_types": ["NodePort", "LoadBalancer"],
                "allowed_external_service_names": [],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_kubernetes_service_exposure_policy_fails_for_load_balancer(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _load_balancer_service())

    finding = KubernetesServiceExposurePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="SEC-003",
            check_type="kubernetes_service_exposure_policy",
            params={
                **_base_params(),
                "disallowed_service_types": ["NodePort", "LoadBalancer"],
                "allowed_external_service_names": [],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["service_type"] == "LoadBalancer"


def test_kubernetes_service_exposure_policy_allows_explicit_exception(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _load_balancer_service())

    finding = KubernetesServiceExposurePolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="SEC-003",
            check_type="kubernetes_service_exposure_policy",
            params={
                **_base_params(),
                "disallowed_service_types": ["NodePort", "LoadBalancer"],
                "allowed_external_service_names": ["public-gateway"],
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
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        category="security",
        severity=Severity.HIGH,
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
    manifest_file = manifest_dir / "security.yaml"
    manifest_file.write_text(content, encoding="utf-8")


def _ingress_with_tls() -> str:
    return """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
spec:
  tls:
    - hosts:
        - app.local
      secretName: app-tls
  rules:
    - host: app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app
                port:
                  number: 80
"""


def _ingress_without_tls() -> str:
    return """
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app
spec:
  rules:
    - host: app.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: app
                port:
                  number: 80
"""


def _cluster_ip_service() -> str:
    return """
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  type: ClusterIP
  selector:
    app: app
  ports:
    - port: 80
      targetPort: 8080
"""


def _load_balancer_service() -> str:
    return """
apiVersion: v1
kind: Service
metadata:
  name: public-gateway
spec:
  type: LoadBalancer
  selector:
    app: public-gateway
  ports:
    - port: 80
      targetPort: 8080
"""