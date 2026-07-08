from typing import Any

from ed_cage.checks.common.docker_compose_loader import (
    DockerComposeDocument,
    get_compose_services,
    load_docker_compose_files,
    stringify_paths,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


DEFAULT_DISALLOWED_CAPABILITIES = [
    "ALL",
    "SYS_ADMIN",
    "NET_ADMIN",
]


class DockerComposeSecurityPolicyCheck:
    @property
    def check_type(self) -> str:
        return "docker_compose_security_policy"

    def evaluate(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        load_result = load_docker_compose_files(rule=rule, context=context)
        disallowed_capabilities = _get_string_list_param(
            rule=rule,
            key="disallowed_capabilities",
            default=DEFAULT_DISALLOWED_CAPABILITIES,
        )

        service_evaluations: list[dict[str, Any]] = []
        violations: list[dict[str, Any]] = []

        for document in load_result.documents:
            self._evaluate_document(
                document=document,
                disallowed_capabilities=disallowed_capabilities,
                service_evaluations=service_evaluations,
                violations=violations,
            )

        evidence = [
            Evidence(
                source="docker-compose-security-policy",
                message="Docker Compose security policy evaluation completed.",
                data={
                    "candidate_files": stringify_paths(
                        context.repository_path,
                        load_result.candidate_files,
                    ),
                    "existing_files": stringify_paths(
                        context.repository_path,
                        load_result.existing_files,
                    ),
                    "missing_files": stringify_paths(
                        context.repository_path,
                        load_result.missing_files,
                    ),
                    "parse_errors": load_result.errors,
                    "disallowed_capabilities": disallowed_capabilities,
                    "service_count": len(service_evaluations),
                    "service_evaluations": service_evaluations,
                    "violations": violations,
                },
            )
        ]

        if not load_result.documents:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message="No parseable Docker Compose document was found.",
                evidence=evidence,
            )

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "Docker Compose security policy violations detected: "
                    f"{len(violations)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Docker Compose security policy passed.",
            evidence=evidence,
        )

    def _evaluate_document(
        self,
        document: DockerComposeDocument,
        disallowed_capabilities: list[str],
        service_evaluations: list[dict[str, Any]],
        violations: list[dict[str, Any]],
    ) -> None:
        services = get_compose_services(document)
        disallowed_capability_set = {
            capability.strip().upper()
            for capability in disallowed_capabilities
            if capability.strip()
        }

        for service_name, service_definition in services.items():
            normalized_service_name = str(service_name)

            service_evaluation: dict[str, Any] = {
                "file": document.relative_path,
                "service": normalized_service_name,
                "privileged": False,
                "network_mode": None,
                "pid": None,
                "ipc": None,
                "cap_add": [],
            }

            if not isinstance(service_definition, dict):
                service_evaluations.append(service_evaluation)
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "invalid_service_definition",
                    }
                )
                continue

            privileged = service_definition.get("privileged") is True
            network_mode = service_definition.get("network_mode")
            pid = service_definition.get("pid")
            ipc = service_definition.get("ipc")
            cap_add = _normalize_list(service_definition.get("cap_add"))

            service_evaluation["privileged"] = privileged
            service_evaluation["network_mode"] = network_mode
            service_evaluation["pid"] = pid
            service_evaluation["ipc"] = ipc
            service_evaluation["cap_add"] = cap_add

            service_evaluations.append(service_evaluation)

            if privileged:
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "privileged_container",
                    }
                )

            if str(network_mode).strip().lower() == "host":
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "host_network_mode",
                    }
                )

            if str(pid).strip().lower() == "host":
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "host_pid_mode",
                    }
                )

            if str(ipc).strip().lower() == "host":
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "host_ipc_mode",
                    }
                )

            for capability in cap_add:
                if capability.upper() in disallowed_capability_set:
                    violations.append(
                        {
                            "file": document.relative_path,
                            "service": normalized_service_name,
                            "reason": "disallowed_capability",
                            "capability": capability,
                        }
                    )


def _normalize_list(value: object) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            str(item)
            for item in value
        ]

    return [
        str(value)
    ]


def _get_string_list_param(
    rule: GovernanceRule,
    key: str,
    default: list[str],
) -> list[str]:
    raw_value = rule.params.get(key, default)

    if not isinstance(raw_value, list):
        return default

    return [
        str(item)
        for item in raw_value
    ]