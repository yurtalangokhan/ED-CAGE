from pathlib import Path

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class RepositoryRequiredPathsCheck:
    @property
    def check_type(self) -> str:
        return "repository_required_paths"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        required_paths = self._get_required_paths(rule)

        violations: list[dict[str, object]] = []
        evaluated_paths: list[dict[str, object]] = []

        for required_path in required_paths:
            relative_path = str(required_path["path"])
            expected_type = str(required_path.get("type", "any"))
            resolved_path = self._resolve_path(context.repository_path, relative_path)

            exists = resolved_path.exists()
            actual_type = self._actual_type(resolved_path)

            evaluated_paths.append(
                {
                    "path": relative_path,
                    "resolved_path": str(resolved_path),
                    "expected_type": expected_type,
                    "exists": exists,
                    "actual_type": actual_type,
                }
            )

            if not exists:
                violations.append(
                    {
                        "path": relative_path,
                        "expected_type": expected_type,
                        "reason": "path_does_not_exist",
                    }
                )
                continue

            if expected_type == "file" and not resolved_path.is_file():
                violations.append(
                    {
                        "path": relative_path,
                        "expected_type": expected_type,
                        "actual_type": actual_type,
                        "reason": "path_is_not_file",
                    }
                )
                continue

            if expected_type == "directory" and not resolved_path.is_dir():
                violations.append(
                    {
                        "path": relative_path,
                        "expected_type": expected_type,
                        "actual_type": actual_type,
                        "reason": "path_is_not_directory",
                    }
                )

        evidence = [
            Evidence(
                source="repository-required-paths",
                message="Repository required path evaluation completed.",
                data={
                    "required_paths": required_paths,
                    "evaluated_paths": evaluated_paths,
                    "violations": violations,
                },
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Required repository path violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All required repository paths exist.",
            evidence=evidence,
        )

    def _get_required_paths(self, rule: GovernanceRule) -> list[dict[str, object]]:
        raw_paths = rule.params.get("required_paths", [])

        if not isinstance(raw_paths, list):
            return []

        required_paths: list[dict[str, object]] = []

        for raw_path in raw_paths:
            if isinstance(raw_path, str):
                required_paths.append(
                    {
                        "path": raw_path,
                        "type": "any",
                    }
                )
                continue

            if isinstance(raw_path, dict) and raw_path.get("path") is not None:
                required_paths.append(
                    {
                        "path": str(raw_path["path"]),
                        "type": str(raw_path.get("type", "any")),
                    }
                )

        return required_paths

    def _resolve_path(self, repository_path: Path, path: str) -> Path:
        raw_path = Path(path)

        if raw_path.is_absolute():
            return raw_path.resolve()

        return (repository_path / raw_path).resolve()

    def _actual_type(self, path: Path) -> str:
        if path.is_file():
            return "file"

        if path.is_dir():
            return "directory"

        if path.exists():
            return "other"

        return "missing"