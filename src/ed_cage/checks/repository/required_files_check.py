from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class RequiredFilesCheck:
    @property
    def check_type(self) -> str:
        return "required_files"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        required_files = rule.params.get("files", [])

        if not isinstance(required_files, list) or not required_files:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message="Rule parameter 'files' must be a non-empty list.",
                evidence=[
                    Evidence(
                        source="rule.params",
                        message="Invalid required_files configuration.",
                        data={"params": rule.params},
                    )
                ],
            )

        missing_files: list[str] = []
        existing_files: list[str] = []

        for relative_file in required_files:
            file_path = context.repository_path / str(relative_file)

            if file_path.exists():
                existing_files.append(str(relative_file))
            else:
                missing_files.append(str(relative_file))

        if missing_files:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Missing required file(s): {', '.join(missing_files)}",
                evidence=[
                    Evidence(
                        source=str(context.repository_path),
                        message="Required repository files check failed.",
                        data={
                            "missing_files": missing_files,
                            "existing_files": existing_files,
                        },
                    )
                ],
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All required file(s) exist.",
            evidence=[
                Evidence(
                    source=str(context.repository_path),
                    message="Required repository files check passed.",
                    data={"existing_files": existing_files},
                )
            ],
        )