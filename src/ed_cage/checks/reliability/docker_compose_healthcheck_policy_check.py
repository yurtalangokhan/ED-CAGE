from typing import Any

from ed_cage.checks.common.docker_compose_loader import (
    DockerComposeDocument,
    get_compose_services,
    load_docker_compose_files,
    stringify_paths,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class DockerComposeHealthcheckPolicyCheck:
    @property
    def check_type(self) -> str:
        return "docker_compose_healthcheck_policy"

    def evaluate(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        load_result = load_docker_compose_files(rule=rule, context=context)
        ignored_services = _get_string_list_param(rule, "ignored_services", [])

        service_evaluations: list[dict[str, Any]] = []
        violations: list[dict[str, Any]] = []

        for document in load_result.documents:
            self._evaluate_document(
                document=document,
                ignored_services=ignored_services,
                service_evaluations=service_evaluations,
                violations=violations,
            )

        evidence = [
            Evidence(
                source="docker-compose-healthcheck-policy",
                message="Docker Compose healthcheck policy evaluation completed.",
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
                    "ignored_services": ignored_services,
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

        if not service_evaluations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message="No Docker Compose services were found.",
                evidence=evidence,
            )

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "Docker Compose service healthcheck violations detected: "
                    f"{len(violations)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All evaluated Docker Compose services define healthchecks.",
            evidence=evidence,
        )

    def _evaluate_document(
        self,
        document: DockerComposeDocument,
        ignored_services: list[str],
        service_evaluations: list[dict[str, Any]],
        violations: list[dict[str, Any]],
    ) -> None:
        ignored_service_names = {
            service_name.strip()
            for service_name in ignored_services
            if service_name.strip()
        }

        services = get_compose_services(document)

        for service_name, service_definition in services.items():
            normalized_service_name = str(service_name)

            if normalized_service_name in ignored_service_names:
                continue

            service_evaluation = {
                "file": document.relative_path,
                "service": normalized_service_name,
                "has_healthcheck": False,
                "healthcheck_disabled": False,
                "has_test": False,
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

            healthcheck = service_definition.get("healthcheck")

            if not isinstance(healthcheck, dict):
                service_evaluations.append(service_evaluation)
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "missing_healthcheck",
                    }
                )
                continue

            service_evaluation["has_healthcheck"] = True

            if healthcheck.get("disable") is True:
                service_evaluation["healthcheck_disabled"] = True
                service_evaluations.append(service_evaluation)
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "healthcheck_disabled",
                    }
                )
                continue

            healthcheck_test = healthcheck.get("test")
            has_test = bool(healthcheck_test)
            service_evaluation["has_test"] = has_test
            service_evaluations.append(service_evaluation)

            if not has_test:
                violations.append(
                    {
                        "file": document.relative_path,
                        "service": normalized_service_name,
                        "reason": "missing_healthcheck_test",
                    }
                )


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