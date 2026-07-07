from dataclasses import dataclass
from pathlib import Path
from re import Pattern
import re

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


@dataclass(frozen=True)
class SecretPattern:
    name: str
    regex: str
    compiled: Pattern[str]


class RepositorySecretPatternsCheck:
    @property
    def check_type(self) -> str:
        return "repository_secret_patterns"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        include_paths = self._get_string_list_param(rule, "include_paths", ["."])
        exclude_paths = self._get_string_list_param(rule, "exclude_paths", [])
        file_patterns = self._get_string_list_param(rule, "file_patterns", ["*"])
        max_file_size_bytes = int(rule.params.get("max_file_size_bytes", 1048576))
        secret_patterns = self._get_secret_patterns(rule)

        files = self._collect_files(
            repository_path=context.repository_path,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_patterns=file_patterns,
        )

        violations: list[dict[str, object]] = []
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

            violations.extend(
                self._scan_text(
                    repository_path=context.repository_path,
                    file_path=file_path,
                    text=text,
                    secret_patterns=secret_patterns,
                )
            )

        evidence = [
            Evidence(
                source="repository-secret-patterns",
                message="Repository secret pattern scan completed.",
                data={
                    "include_paths": include_paths,
                    "exclude_paths": exclude_paths,
                    "file_patterns": file_patterns,
                    "candidate_file_count": len(files),
                    "scanned_file_count": scanned_files,
                    "skipped_file_count": len(skipped_files),
                    "max_file_size_bytes": max_file_size_bytes,
                    "secret_pattern_names": [
                        secret_pattern.name for secret_pattern in secret_patterns
                    ],
                    "violations": violations,
                    "skipped_files_sample": skipped_files[:20],
                },
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Potential committed secrets detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="No obvious committed secrets were detected.",
            evidence=evidence,
        )

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

    def _scan_text(
        self,
        repository_path: Path,
        file_path: Path,
        text: str,
        secret_patterns: list[SecretPattern],
    ) -> list[dict[str, object]]:
        violations: list[dict[str, object]] = []

        for line_number, line in enumerate(text.splitlines(), start=1):
            for secret_pattern in secret_patterns:
                match = secret_pattern.compiled.search(line)

                if match is None:
                    continue

                violations.append(
                    {
                        "path": self._relative_path(repository_path, file_path),
                        "line_number": line_number,
                        "pattern_name": secret_pattern.name,
                        "match_preview": self._redact(match.group(0)),
                    }
                )

        return violations

    def _get_secret_patterns(self, rule: GovernanceRule) -> list[SecretPattern]:
        raw_patterns = rule.params.get("secret_patterns", [])

        if not isinstance(raw_patterns, list):
            raw_patterns = []

        patterns: list[SecretPattern] = []

        for raw_pattern in raw_patterns:
            if not isinstance(raw_pattern, dict):
                continue

            name = str(raw_pattern.get("name", "unnamed_pattern"))
            regex = str(raw_pattern.get("regex", ""))

            if not regex:
                continue

            patterns.append(
                SecretPattern(
                    name=name,
                    regex=regex,
                    compiled=re.compile(regex),
                )
            )

        if patterns:
            return patterns

        return [
            SecretPattern(
                name="private_key",
                regex=r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
                compiled=re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
            ),
            SecretPattern(
                name="aws_access_key_id",
                regex=r"AKIA[0-9A-Z]{16}",
                compiled=re.compile(r"AKIA[0-9A-Z]{16}"),
            ),
        ]

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

    def _redact(self, value: str) -> str:
        stripped = value.strip()

        if len(stripped) <= 8:
            return "***"

        return f"{stripped[:4]}***{stripped[-2:]}"