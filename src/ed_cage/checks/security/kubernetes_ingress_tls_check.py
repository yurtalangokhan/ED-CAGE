from typing import Any

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import KubernetesManifestLoader
from ed_cage.checks.common.kubernetes_utils import get_file_patterns, get_manifest_paths
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class KubernetesIngressTlsCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_ingress_tls"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        manifest_paths = get_manifest_paths(rule.params)
        file_patterns = get_file_patterns(rule.params)
        require_host_coverage = bool(
            rule.params.get("require_tls_hosts_cover_rules", True)
        )

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        ingresses = [
            manifest for manifest in load_result.manifests if manifest.kind == "Ingress"
        ]

        if not ingresses:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message="No Kubernetes Ingress resources were found.",
                evidence=[
                    Evidence(
                        source="kubernetes-ingress-tls-policy",
                        message="No Ingress resources were available for TLS evaluation.",
                        data={
                            "manifest_paths": manifest_paths,
                            "file_patterns": file_patterns,
                            "manifest_count": len(load_result.manifests),
                            "ingress_count": 0,
                            "load_errors": [
                                {
                                    "path": str(error.path),
                                    "message": error.message,
                                }
                                for error in load_result.errors
                            ],
                        },
                    )
                ],
            )

        violations: list[dict[str, object]] = []

        for ingress in ingresses:
            spec = self._get_dict(ingress.raw.get("spec"))
            tls_entries = spec.get("tls", [])

            if not isinstance(tls_entries, list) or not tls_entries:
                violations.append(
                    {
                        "resource_id": ingress.resource_id,
                        "reason": "missing_tls",
                    }
                )
                continue

            if require_host_coverage:
                rule_hosts = self._extract_rule_hosts(spec)
                tls_hosts = self._extract_tls_hosts(tls_entries)
                missing_tls_hosts = sorted(rule_hosts - tls_hosts)

                if missing_tls_hosts:
                    violations.append(
                        {
                            "resource_id": ingress.resource_id,
                            "reason": "tls_hosts_do_not_cover_ingress_rules",
                            "missing_tls_hosts": missing_tls_hosts,
                        }
                    )

        evidence = [
            Evidence(
                source="kubernetes-ingress-tls-policy",
                message="Kubernetes Ingress TLS policy evaluation completed.",
                data={
                    "manifest_paths": manifest_paths,
                    "file_patterns": file_patterns,
                    "manifest_count": len(load_result.manifests),
                    "ingress_count": len(ingresses),
                    "require_tls_hosts_cover_rules": require_host_coverage,
                    "violations": violations,
                    "load_errors": [
                        {
                            "path": str(error.path),
                            "message": error.message,
                        }
                        for error in load_result.errors
                    ],
                },
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes Ingress TLS violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Kubernetes Ingress TLS policy passed.",
            evidence=evidence,
        )

    def _extract_rule_hosts(self, spec: dict[str, Any]) -> set[str]:
        rules = spec.get("rules", [])

        if not isinstance(rules, list):
            return set()

        hosts: set[str] = set()

        for rule in rules:
            if not isinstance(rule, dict):
                continue

            host = rule.get("host")

            if isinstance(host, str) and host.strip():
                hosts.add(host.strip())

        return hosts

    def _extract_tls_hosts(self, tls_entries: list[object]) -> set[str]:
        hosts: set[str] = set()

        for tls_entry in tls_entries:
            if not isinstance(tls_entry, dict):
                continue

            tls_hosts = tls_entry.get("hosts", [])

            if not isinstance(tls_hosts, list):
                continue

            for host in tls_hosts:
                if isinstance(host, str) and host.strip():
                    hosts.add(host.strip())

        return hosts

    def _get_dict(self, value: object) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}

        return value