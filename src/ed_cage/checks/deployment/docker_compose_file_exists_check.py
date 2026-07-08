from ed_cage.checks.common.docker_compose_loader import (
    load_docker_compose_files,
    stringify_paths,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class DockerComposeFileExistsCheck:
    @property
    def check_type(self) -> str:
        return "docker_compose_file_exists"

    def evaluate(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        load_result = load_docker_compose_files(rule=rule, context=context)

        evidence = [
            Evidence(
                source="docker-compose-file-exists",
                message="Docker Compose file discovery completed.",
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
                },
            )
        ]

        if not load_result.existing_files:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message="No Docker Compose file was found.",
                evidence=evidence,
            )

        if load_result.errors:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message="Docker Compose file exists but could not be parsed.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Docker Compose file exists and is parseable.",
            evidence=evidence,
        )