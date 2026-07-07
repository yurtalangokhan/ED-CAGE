from typing import Any

from ed_cage.adapters.filesystem.architecture_catalog_loader import (
    ArchitectureCatalogLoader,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)


class ArchitectureCatalogPolicyCheck:
    @property
    def check_type(self) -> str:
        return "architecture_catalog_policy"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        policy = str(rule.params.get("policy", "")).strip()
        catalog_path = self._get_catalog_path(rule, context)

        load_result = ArchitectureCatalogLoader(context.repository_path).load(
            catalog_path
        )

        base_evidence_data: dict[str, object] = {
            "policy": policy,
            "architecture_catalog_path": catalog_path,
            "resolved_path": str(load_result.path),
            "catalog_exists": load_result.exists,
            "load_errors": load_result.errors,
        }

        if not load_result.exists:
            evidence = [
                Evidence(
                    source="architecture-catalog-policy",
                    message="Architecture catalog does not exist.",
                    data=base_evidence_data,
                )
            ]

            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message="Required architecture catalog does not exist.",
                evidence=evidence,
            )

        if load_result.errors:
            evidence = [
                Evidence(
                    source="architecture-catalog-policy",
                    message="Architecture catalog could not be loaded.",
                    data=base_evidence_data,
                )
            ]

            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message="Architecture catalog policy could not be evaluated.",
                evidence=evidence,
            )

        policy_result = self._evaluate_policy(
            policy=policy,
            catalog=load_result.catalog,
            rule=rule,
        )

        evidence = [
            Evidence(
                source="architecture-catalog-policy",
                message=f"Architecture catalog policy evaluation completed: {policy}.",
                data={
                    **base_evidence_data,
                    **policy_result,
                },
            )
        ]

        if not policy_result["success"]:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Architecture catalog policy failed: {policy}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"Architecture catalog policy passed: {policy}.",
            evidence=evidence,
        )

    def _evaluate_policy(
        self,
        policy: str,
        catalog: dict[str, Any],
        rule: GovernanceRule,
    ) -> dict[str, object]:
        if policy == "require_critical_services":
            return self._require_critical_services(catalog)

        if policy == "require_declared_dependencies":
            return self._require_declared_dependencies(catalog)

        if policy == "disallow_circular_dependencies":
            return self._disallow_circular_dependencies(catalog)

        if policy == "require_external_dependency_metadata":
            return self._require_external_dependency_metadata(catalog, rule)

        return {
            "success": False,
            "failure_reason": "unsupported_architecture_catalog_policy",
            "service_count": len(self._get_services(catalog)),
        }

    def _require_critical_services(self, catalog: dict[str, Any]) -> dict[str, object]:
        critical_services = self._get_critical_services(catalog)

        return {
            "success": bool(critical_services),
            "failure_reason": (
                None if critical_services else "critical_services_not_declared"
            ),
            "critical_services": sorted(critical_services),
            "service_count": len(self._get_services(catalog)),
        }

    def _require_declared_dependencies(
        self,
        catalog: dict[str, Any],
    ) -> dict[str, object]:
        services = self._get_services(catalog)
        violations: list[dict[str, object]] = []

        for service in services:
            service_name = self._get_service_name(service)

            if "dependencies" not in service:
                violations.append(
                    {
                        "service_name": service_name,
                        "reason": "dependencies_field_missing",
                    }
                )
                continue

            dependencies = service.get("dependencies")

            if not isinstance(dependencies, list):
                violations.append(
                    {
                        "service_name": service_name,
                        "reason": "dependencies_is_not_list",
                    }
                )

        return {
            "success": not violations,
            "failure_reason": (
                None if not violations else "service_dependencies_not_declared"
            ),
            "service_count": len(services),
            "violations": violations,
        }

    def _disallow_circular_dependencies(
        self,
        catalog: dict[str, Any],
    ) -> dict[str, object]:
        graph = self._build_internal_service_graph(catalog)
        cycles = self._find_cycles(graph)

        return {
            "success": not cycles,
            "failure_reason": None if not cycles else "circular_dependencies_detected",
            "service_count": len(self._get_services(catalog)),
            "graph": graph,
            "cycles": cycles,
        }

    def _require_external_dependency_metadata(
        self,
        catalog: dict[str, Any],
        rule: GovernanceRule,
    ) -> dict[str, object]:
        required_metadata = self._get_required_metadata(rule)
        services = self._get_services(catalog)

        violations: list[dict[str, object]] = []
        evaluated_external_dependencies = 0

        for service in services:
            service_name = self._get_service_name(service)
            dependencies = service.get("dependencies", [])

            if not isinstance(dependencies, list):
                continue

            for dependency in dependencies:
                if not isinstance(dependency, dict):
                    continue

                if not bool(dependency.get("external", False)):
                    continue

                evaluated_external_dependencies += 1
                missing_metadata = [
                    metadata_key
                    for metadata_key in required_metadata
                    if not self._has_non_empty_value(dependency.get(metadata_key))
                ]

                if missing_metadata:
                    violations.append(
                        {
                            "service_name": service_name,
                            "dependency_name": str(dependency.get("name", "unknown")),
                            "missing_metadata": missing_metadata,
                        }
                    )

        return {
            "success": not violations,
            "failure_reason": (
                None if not violations else "external_dependency_metadata_missing"
            ),
            "service_count": len(services),
            "evaluated_external_dependencies": evaluated_external_dependencies,
            "required_metadata": required_metadata,
            "violations": violations,
        }

    def _get_services(self, catalog: dict[str, Any]) -> list[dict[str, Any]]:
        services = catalog.get("services", [])

        if not isinstance(services, list):
            return []

        return [service for service in services if isinstance(service, dict)]

    def _get_service_name(self, service: dict[str, Any]) -> str:
        return str(service.get("name", "unknown-service"))

    def _get_critical_services(self, catalog: dict[str, Any]) -> set[str]:
        critical_services: set[str] = set()

        raw_critical_services = catalog.get("critical_services", [])

        if isinstance(raw_critical_services, list):
            for service_name in raw_critical_services:
                if isinstance(service_name, str) and service_name.strip():
                    critical_services.add(service_name.strip())

        for service in self._get_services(catalog):
            criticality = str(service.get("criticality", "")).strip().lower()

            if criticality in {"high", "critical"}:
                critical_services.add(self._get_service_name(service))

        return critical_services

    def _build_internal_service_graph(
        self,
        catalog: dict[str, Any],
    ) -> dict[str, list[str]]:
        services = self._get_services(catalog)
        service_names = {self._get_service_name(service) for service in services}
        graph: dict[str, list[str]] = {
            service_name: [] for service_name in service_names
        }

        for service in services:
            service_name = self._get_service_name(service)
            dependencies = service.get("dependencies", [])

            if not isinstance(dependencies, list):
                continue

            for dependency in dependencies:
                if not isinstance(dependency, dict):
                    continue

                dependency_name = str(dependency.get("name", "")).strip()
                is_external = bool(dependency.get("external", False))
                dependency_type = (
                    str(dependency.get("dependency_type", "")).strip().lower()
                )

                if is_external:
                    continue

                if dependency_name not in service_names:
                    continue

                if dependency_type not in {"", "service", "microservice"}:
                    continue

                graph[service_name].append(dependency_name)

        return {
            service_name: sorted(set(dependencies))
            for service_name, dependencies in graph.items()
        }

    def _find_cycles(self, graph: dict[str, list[str]]) -> list[list[str]]:
        visited: set[str] = set()
        stack: list[str] = []
        on_stack: set[str] = set()
        cycles: list[list[str]] = []

        def visit(node: str) -> None:
            visited.add(node)
            stack.append(node)
            on_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visit(neighbor)
                    continue

                if neighbor in on_stack:
                    cycle_start_index = stack.index(neighbor)
                    cycle = [*stack[cycle_start_index:], neighbor]

                    if not self._cycle_already_recorded(cycles, cycle):
                        cycles.append(cycle)

            stack.pop()
            on_stack.remove(node)

        for node in graph:
            if node not in visited:
                visit(node)

        return cycles

    def _cycle_already_recorded(
        self,
        cycles: list[list[str]],
        candidate_cycle: list[str],
    ) -> bool:
        candidate_nodes = set(candidate_cycle)

        return any(set(cycle) == candidate_nodes for cycle in cycles)

    def _get_required_metadata(self, rule: GovernanceRule) -> list[str]:
        raw_metadata = rule.params.get("required_metadata", ["owner", "sla"])

        if not isinstance(raw_metadata, list) or not raw_metadata:
            return ["owner", "sla"]

        return [str(item) for item in raw_metadata]

    def _has_non_empty_value(self, value: object) -> bool:
        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True

    def _get_catalog_path(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> str:
        if context.architecture_catalog_path is not None:
            return str(context.architecture_catalog_path)

        return str(
            rule.params.get(
                "architecture_catalog_path",
                "configs/architecture/service-architecture.yaml",
            )
        )
