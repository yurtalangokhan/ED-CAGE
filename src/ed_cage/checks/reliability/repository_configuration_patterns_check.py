from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Any
import re

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


@dataclass(frozen=True)
class ConfigurationPattern:
    group_name: str
    pattern: str
    compiled: Pattern[str]


class RepositoryConfigurationPatternsCheck:
    @property
    def check_type(self) -> str:
        return "repository_configuration_patterns"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        include_paths = self._get_string_list_param(rule, "include_paths", ["."])
        exclude_paths = self._get_string_list_param(rule, "exclude_paths", [])
        file_patterns = self._get_string_list_param(rule, "file_patterns", ["*.yaml", "*.yml"])
        max_file_size_bytes = int(rule.params.get("max_file_size_bytes", 1048576))
        required_groups = self._get_required_groups(rule)
        compiled_patterns = self._compile_patterns(required_groups)

        files = self._collect_files(
            repository_path=context.repository_path,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_patterns=file_patterns,
        )

        matched_groups: dict[str, list[dict[str, object]]] = {
            group_name: [] for group_name in required_groups
        }
        skipped_files: list[dict[str, object]] = []
        scanned_files = 0

        for file_path in files:
            try:
                file_size = file_path.stat().st_size
            except OSError as exc:
                skipped_files.append(
                    {
                        "path": str(file_path),
                        "reason": "stat_failed",
                        "message": str(exc),
                    }
                )
                continue

            if file_size > max_file_size_bytes:
                skipped_files.append(
                    {
                        "path": str(file_path),
                        "reason": "file_too_large",
                        "file_size_bytes": file_size,
                    }
                )
                continue

            try:
                content_bytes = file_path.read_bytes()
            except OSError as exc:
                skipped_files.append(
                    {
                        "path": str(file_path),
                        "reason": "read_failed",
                        "message": str(exc),
                    }
                )
                continue

            if self._looks_binary(content_bytes):
                skipped_files.append(
                    {
                        "path": str(file_path),
                        "reason": "binary_file",
                    }
                )
                continue

            scanned_files += 1
            text = content_bytes.decode("utf-8", errors="ignore")

            self._scan_text(
                repository_path=context.repository_path,
                file_path=file_path,
                text=text,
                compiled_patterns=compiled_patterns,
                matched_groups=matched_groups,
            )

        missing_groups = [
            group_name
            for group_name, matches in matched_groups.items()
            if not matches
        ]

        evidence = [
            Evidence(
                source="repository-configuration-patterns",
                message="Repository configuration pattern scan completed.",
                data={
                    "include_paths": include_paths,
                    "exclude_paths": exclude_paths,
                    "file_patterns": file_patterns,
                    "candidate_file_count": len(files),
                    "scanned_file_count": scanned_files,
                    "skipped_file_count": len(skipped_files),
                    "max_file_size_bytes": max_file_size_bytes,
                    "required_groups": required_groups,
                    "matched_groups": {
                        group_name: matches[:20]
                        for group_name, matches in matched_groups.items()
                    },
                    "missing_groups": missing_groups,
                    "skipped_files_sample": skipped_files[:20],
                },
            )
        ]

        if missing_groups:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "Required repository configuration pattern group(s) missing: "
                    f"{', '.join(missing_groups)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Required repository configuration pattern group(s) were found.",
            evidence=evidence,
        )

    def _scan_text(
        self,
        repository_path: Path,
        file_path: Path,
        text: str,
        compiled_patterns: list[ConfigurationPattern],
        matched_groups: dict[str, list[dict[str, object]]],
    ) -> None:
        for line_number, line in enumerate(text.splitlines(), start=1):
            for configuration_pattern in compiled_patterns:
                match = configuration_pattern.compiled.search(line)

                if match is None:
                    continue

                matched_groups[configuration_pattern.group_name].append(
                    {
                        "path": self._relative_path(repository_path, file_path),
                        "line_number": line_number,
                        "pattern": configuration_pattern.pattern,
                        "match_preview": self._preview(line),
                    }
                )

    def _get_required_groups(
        self,
        rule: GovernanceRule,
    ) -> dict[str, dict[str, Any]]:
        raw_groups = rule.params.get("required_pattern_groups", {})

        if not isinstance(raw_groups, dict):
            return {}

        required_groups: dict[str, dict[str, Any]] = {}

        for group_name, group_config in raw_groups.items():
            if not isinstance(group_config, dict):
                continue

            patterns = group_config.get("patterns", [])

            if not isinstance(patterns, list) or not patterns:
                continue

            required_groups[str(group_name)] = {
                "description": str(group_config.get("description", "")),
                "patterns": [str(pattern) for pattern in patterns],
            }

        return required_groups

    def _compile_patterns(
        self,
        required_groups: dict[str, dict[str, Any]],
    ) -> list[ConfigurationPattern]:
        compiled_patterns: list[ConfigurationPattern] = []

        for group_name, group_config in required_groups.items():
            raw_patterns = group_config.get("patterns", [])

            if not isinstance(raw_patterns, list):
                continue

            for raw_pattern in raw_patterns:
                pattern = str(raw_pattern)

                compiled_patterns.append(
                    ConfigurationPattern(
                        group_name=group_name,
                        pattern=pattern,
                        compiled=re.compile(pattern),
                    )
                )

        return compiled_patterns

    def _collect_files(
        self,
        repository_path: Path,
        include_paths: list[str],
        exclude_paths: list[str],
        file_patterns: list[str],
    ) -> list[Path]:
        resolved_exclude_paths = [
            self._resolve_path(repository_path, path) for path in exclude_paths
        ]

        files: list[Path] = []
        seen: set[Path] = set()

        for include_path in include_paths:
            resolved_include_path = self._resolve_path(repository_path, include_path)

            if self._is_excluded(resolved_include_path, resolved_exclude_paths):
                continue

            if resolved_include_path.is_file():
                resolved_file = resolved_include_path.resolve()

                if resolved_file not in seen:
                    files.append(resolved_file)
                    seen.add(resolved_file)

                continue

            if not resolved_include_path.is_dir():
                continue

            for file_pattern in file_patterns:
                for candidate_file in resolved_include_path.rglob(file_pattern):
                    if not candidate_file.is_file():
                        continue

                    resolved_file = candidate_file.resolve()

                    if self._is_excluded(resolved_file, resolved_exclude_paths):
                        continue

                    if resolved_file not in seen:
                        files.append(resolved_file)
                        seen.add(resolved_file)

        return sorted(files)

    def _get_string_list_param(
        self,
        rule: GovernanceRule,
        key: str,
        default: list[str],
    ) -> list[str]:
        raw_value = rule.params.get(key, default)

        if not isinstance(raw_value, list):
            return default

        return [str(item) for item in raw_value]

    def _resolve_path(self, repository_path: Path, path: str) -> Path:
        raw_path = Path(path)

        if raw_path.is_absolute():
            return raw_path.resolve()

        return (repository_path / raw_path).resolve()

    def _is_excluded(self, path: Path, exclude_paths: list[Path]) -> bool:
        resolved_path = path.resolve()

        for exclude_path in exclude_paths:
            resolved_exclude_path = exclude_path.resolve()

            if resolved_path == resolved_exclude_path:
                return True

            if resolved_exclude_path in resolved_path.parents:
                return True

        return False

    def _relative_path(self, repository_path: Path, file_path: Path) -> str:
        try:
            return str(file_path.relative_to(repository_path.resolve()))
        except ValueError:
            return str(file_path)

    def _looks_binary(self, content: bytes) -> bool:
        return b"\x00" in content[:1024]

    def _preview(self, line: str) -> str:
        stripped = line.strip()

        if len(stripped) <= 160:
            return stripped

        return f"{stripped[:157]}..."