from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import fnmatch
import json
from math import log2
from pathlib import Path
from re import Pattern
import re
import tomllib
from typing import Any, Iterable
from xml.etree import ElementTree

import yaml

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


@dataclass(frozen=True)
class SecretPattern:
    """High-confidence provider or credential-format pattern."""

    name: str
    regex: str
    compiled: Pattern[str]


@dataclass(frozen=True)
class LiteralCandidate:
    """A literal assigned to a repository key or source-code identifier."""

    key: str
    value: str
    line_number: int | None
    origin: str


class RepositorySecretPatternsCheck:
    """Detect committed credential literals and insecure credential defaults.

    Design principles:
    1. Scan first-party source and runtime-configuration artifacts.
    2. Detect provider-specific credential formats independently of variable names.
    3. For generic findings, require a sensitive identifier and a literal value.
    4. Distinguish runtime references from repository-defined credential defaults.
    5. Detect well-known weak credential literals before entropy-based filtering.
    6. Exclude validation, policy, format, and message constants from credential
       classification even when their identifiers contain words such as password.
    """

    SOURCE_EXTENSIONS = {
        ".py",
        ".java",
        ".kt",
        ".kts",
        ".cs",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".go",
        ".rb",
        ".php",
        ".scala",
        ".rs",
        ".swift",
        ".c",
        ".cc",
        ".cpp",
        ".h",
        ".hpp",
    }
    STRUCTURED_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".xml"}
    FLAT_CONFIG_EXTENSIONS = {".properties", ".ini", ".conf"}

    # Assignment pattern requires a quoted literal on the right-hand side.
    # It intentionally does not match method calls, member access, DTO extraction,
    # environment access, or other runtime expressions.
    QUOTED_ASSIGNMENT_PATTERN = re.compile(
        r"""
        \b(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)\b
        \s*(?::|=)\s*
        (?:
            \"(?P<double_value>[^\"\r\n]+)\"
            |
            '(?P<single_value>[^'\r\n]+)'
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    SOURCE_CONSTANT_PATTERN = re.compile(
        r"""
        ^\s*(?:public\s+|private\s+|protected\s+|internal\s+)?
        (?:(?:static|final|const|readonly)\s+)+
        (?:[A-Za-z_][A-Za-z0-9_<>,.?\[\]]*\s+)?
        (?P<key>[A-Za-z_][A-Za-z0-9_.-]*)
        \s*=\s*
        (?:\"[^\"\r\n]+\"|'[^'\r\n]+')
        \s*;?
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    FLAT_CONFIG_ASSIGNMENT_PATTERN = re.compile(
        r"""
        ^\s*(?P<key>[A-Za-z_][A-Za-z0-9_.-]*)\s*(?::|=)\s*
        (?P<value>[^#;\r\n]+?)\s*$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    CI_CONTEXT_REFERENCE_PATTERN = re.compile(
        r"""
        ^\$\{\{\s*
        (?:secrets|vars|env|github|inputs|needs|steps|runner|matrix|strategy|job)
        \.[A-Za-z_][A-Za-z0-9_.-]*
        \s*\}\}$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    ENVIRONMENT_PLACEHOLDER_PATTERN = re.compile(
        r"""
        ^\$\{
        (?P<name>[A-Za-z_][A-Za-z0-9_.-]*)
        (?:(?P<operator>:-|:)(?P<default>[^{}]*))?
        \}$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    ENVIRONMENT_REFERENCE_PATTERN = re.compile(
        r"""
        ^
        (?:
            \$[A-Za-z_][A-Za-z0-9_]*
            |%[A-Za-z_][A-Za-z0-9_]*%
            |\{\{[^{}]+\}\}
            |\$\([^()]+\)
        )$
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    PLACEHOLDER_PATTERNS = (
        re.compile(r"(?i)^your(?:[_\s-].*)?(?:[_\s-]here)?$"),
        re.compile(r"(?i)^(?:example|sample|dummy|placeholder|fake|mock)(?:[_\s-].*)?$"),
        re.compile(r"(?i)^(?:test|testing|demo)(?:[_\s-].*)?$"),
        re.compile(r"(?i)^not[_\s-]?(?:a[_\s-]?)?real(?:[_\s-].*)?$"),
        re.compile(r"(?i)^<[^<>]+>$"),
        re.compile(r"(?i)^x{6,}$"),
        re.compile(r"(?i)^\*{6,}$"),
    )

    DEFAULT_NON_CREDENTIAL_IDENTIFIER_TERMS = {
        "message",
        "msg",
        "error",
        "exception",
        "validation",
        "validator",
        "validate",
        "rule",
        "policy",
        "requirement",
        "least",
        "minimum",
        "maximum",
        "min",
        "max",
        "length",
        "len",
        "char",
        "chars",
        "character",
        "characters",
        "regex",
        "pattern",
        "format",
        "description",
        "label",
        "prompt",
        "hint",
        "help",
    }

    DEFAULT_WEAK_CREDENTIAL_LITERALS = {
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "admin",
        "root",
        "guest",
        "default",
        "changeme",
        "change_me",
        "change-me",
        "letmein",
        "welcome",
        "qwerty",
        "123456",
        "admin123",
        "password123",
    }

    @property
    def check_type(self) -> str:
        return "repository_secret_patterns"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        include_paths = self._get_string_list_param(rule, "include_paths", ["."])
        exclude_paths = self._get_string_list_param(rule, "exclude_paths", [])
        file_patterns = self._get_string_list_param(rule, "file_patterns", ["*"])

        exclude_dir_names = {
            value.lower()
            for value in self._get_string_list_param(
                rule,
                "exclude_dir_names",
                [
                    ".git",
                    ".venv",
                    "venv",
                    "env",
                    "node_modules",
                    "vendor",
                    "vendors",
                    "third_party",
                    "third-party",
                    "external",
                    "deps",
                    "dependencies",
                    "generated",
                    "__generated__",
                    "target",
                    "build",
                    "dist",
                    "out",
                    "coverage",
                    "docs",
                    "documentation",
                    "examples",
                    "samples",
                    "demo",
                    "tests",
                    "test",
                ],
            )
        }

        exclude_file_names = {
            value.lower()
            for value in self._get_string_list_param(
                rule,
                "exclude_file_names",
                [
                    "readme",
                    "readme.md",
                    "readme.adoc",
                    "license",
                    "license.md",
                    "notice",
                    "changelog",
                    "pom.xml",
                    "build.gradle",
                    "settings.gradle",
                    "gradle.properties",
                    "mvnw",
                    "mvnw.cmd",
                    ".env",
                    ".env.example",
                    ".env.sample",
                ],
            )
        }

        exclude_file_patterns = self._get_string_list_param(
            rule,
            "exclude_file_patterns",
            [
                "*.md",
                "*.adoc",
                "*.rst",
                "*.txt",
                "*.sh",
                "*.bash",
                "*.zsh",
                "*.fish",
                "*.cmd",
                "*.bat",
                "*.ps1",
                "*.psm1",
                "*.gradle",
                "*.gradle.kts",
                "*.lock",
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
            ],
        )

        max_file_size_bytes = int(rule.params.get("max_file_size_bytes", 1048576))
        generic_min_length = int(rule.params.get("generic_min_length", 16))
        generic_min_entropy = float(rule.params.get("generic_min_entropy", 3.3))
        generic_min_character_classes = int(
            rule.params.get("generic_min_character_classes", 2)
        )

        sensitive_terms = {
            self._normalize_identifier(value)
            for value in self._get_string_list_param(
                rule,
                "sensitive_terms",
                [
                    "password",
                    "passwd",
                    "pwd",
                    "secret",
                    "token",
                    "api_key",
                    "access_token",
                    "auth_token",
                    "client_secret",
                    "private_key",
                    "signing_key",
                    "jwt_secret",
                    "credential",
                    "credentials",
                    "connection_string",
                ],
            )
        }

        reference_suffixes = tuple(
            self._normalize_identifier(value)
            for value in self._get_string_list_param(
                rule,
                "reference_key_suffixes",
                [
                    "file",
                    "path",
                    "name",
                    "ref",
                    "reference",
                    "id",
                    "identifier",
                    "mount",
                    "location",
                    "uri",
                    "url",
                    "hash",
                    "digest",
                    "salt",
                    "algorithm",
                    "enabled",
                    "required",
                    "field",
                    "column",
                ],
            )
        )

        non_credential_identifier_terms = {
            self._normalize_identifier(value)
            for value in self._get_string_list_param(
                rule,
                "non_credential_identifier_terms",
                sorted(self.DEFAULT_NON_CREDENTIAL_IDENTIFIER_TERMS),
            )
        }

        weak_credential_literals = {
            value.strip().lower()
            for value in self._get_string_list_param(
                rule,
                "weak_credential_literals",
                sorted(self.DEFAULT_WEAK_CREDENTIAL_LITERALS),
            )
            if value.strip()
        }

        secret_patterns = self._get_secret_patterns(rule)
        files, scope_skips = self._collect_files(
            repository_path=context.repository_path,
            include_paths=include_paths,
            exclude_paths=exclude_paths,
            file_patterns=file_patterns,
            exclude_dir_names=exclude_dir_names,
            exclude_file_names=exclude_file_names,
            exclude_file_patterns=exclude_file_patterns,
        )

        violations: list[dict[str, object]] = []
        skipped_files: list[dict[str, object]] = list(scope_skips)
        scanned_files = 0

        for file_path in files:
            try:
                file_size = file_path.stat().st_size
            except OSError as exc:
                skipped_files.append(
                    {
                        "path": self._relative_path(context.repository_path, file_path),
                        "reason": "stat_failed",
                        "message": str(exc),
                    }
                )
                continue

            if file_size > max_file_size_bytes:
                skipped_files.append(
                    {
                        "path": self._relative_path(context.repository_path, file_path),
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
                        "path": self._relative_path(context.repository_path, file_path),
                        "reason": "read_failed",
                        "message": str(exc),
                    }
                )
                continue

            if self._looks_binary(content_bytes):
                skipped_files.append(
                    {
                        "path": self._relative_path(context.repository_path, file_path),
                        "reason": "binary_file",
                    }
                )
                continue

            scanned_files += 1
            text = content_bytes.decode("utf-8", errors="ignore")
            violations.extend(
                self._scan_file(
                    repository_path=context.repository_path,
                    file_path=file_path,
                    text=text,
                    secret_patterns=secret_patterns,
                    sensitive_terms=sensitive_terms,
                    reference_suffixes=reference_suffixes,
                    non_credential_identifier_terms=non_credential_identifier_terms,
                    weak_credential_literals=weak_credential_literals,
                    generic_min_length=generic_min_length,
                    generic_min_entropy=generic_min_entropy,
                    generic_min_character_classes=generic_min_character_classes,
                )
            )

        violations = self._deduplicate_violations(violations)
        evidence = [
            Evidence(
                source="repository-secret-patterns",
                message="Repository committed-secret literal scan completed.",
                data={
                    "strategy": "first_party_high_confidence_literal_detection",
                    "include_paths": include_paths,
                    "exclude_paths": exclude_paths,
                    "exclude_dir_names": sorted(exclude_dir_names),
                    "exclude_file_names": sorted(exclude_file_names),
                    "exclude_file_patterns": exclude_file_patterns,
                    "file_patterns": file_patterns,
                    "candidate_file_count": len(files),
                    "scanned_file_count": scanned_files,
                    "skipped_file_count": len(skipped_files),
                    "max_file_size_bytes": max_file_size_bytes,
                    "generic_min_length": generic_min_length,
                    "generic_min_entropy": generic_min_entropy,
                    "generic_min_character_classes": generic_min_character_classes,
                    "non_credential_identifier_terms": sorted(
                        non_credential_identifier_terms
                    ),
                    "weak_credential_literals": sorted(weak_credential_literals),
                    "secret_pattern_names": [pattern.name for pattern in secret_patterns],
                    "violations": violations,
                    "skipped_files_sample": skipped_files[:50],
                },
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "High-confidence committed credential literals detected: "
                    f"{len(violations)}."
                ),
                category=rule.category,
                target=rule.target,
                check_type=rule.check_type,
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="No high-confidence committed credential literals were detected.",
            category=rule.category,
            target=rule.target,
            check_type=rule.check_type,
            evidence=evidence,
        )

    def _scan_file(
        self,
        repository_path: Path,
        file_path: Path,
        text: str,
        secret_patterns: list[SecretPattern],
        sensitive_terms: set[str],
        reference_suffixes: tuple[str, ...],
        non_credential_identifier_terms: set[str],
        weak_credential_literals: set[str],
        generic_min_length: int,
        generic_min_entropy: float,
        generic_min_character_classes: int,
    ) -> list[dict[str, object]]:
        violations = self._scan_high_confidence_patterns(
            repository_path=repository_path,
            file_path=file_path,
            text=text,
            secret_patterns=secret_patterns,
        )

        suffix = file_path.suffix.lower()
        if suffix in self.STRUCTURED_EXTENSIONS:
            candidates = self._extract_structured_candidates(file_path=file_path, text=text)
        elif suffix in self.SOURCE_EXTENSIONS:
            candidates = self._extract_source_literal_candidates(text)
        elif suffix in self.FLAT_CONFIG_EXTENSIONS:
            candidates = self._extract_flat_config_candidates(text)
        else:
            candidates = []

        for candidate in candidates:
            if not self._is_sensitive_identifier(candidate.key, sensitive_terms):
                continue
            if self._is_reference_identifier(candidate.key, reference_suffixes):
                continue
            if self._is_non_credential_identifier(
                candidate.key, non_credential_identifier_terms
            ):
                continue

            classification = self._classify_sensitive_value(
                candidate.value,
                weak_credential_literals=weak_credential_literals,
                min_length=generic_min_length,
                min_entropy=generic_min_entropy,
                min_character_classes=generic_min_character_classes,
            )
            if classification is None:
                continue

            pattern_name, effective_value, source_kind = classification
            violation: dict[str, object] = {
                "path": self._relative_path(repository_path, file_path),
                "line_number": candidate.line_number,
                "pattern_name": pattern_name,
                "key": candidate.key,
                "match_preview": self._redact(effective_value),
                "source_kind": source_kind,
                "candidate_origin": candidate.origin,
            }
            if pattern_name == "generic_hardcoded_credential_literal":
                violation["entropy"] = round(
                    self._shannon_entropy(effective_value), 3
                )
            violations.append(violation)

        return violations

    def _scan_high_confidence_patterns(
        self,
        repository_path: Path,
        file_path: Path,
        text: str,
        secret_patterns: list[SecretPattern],
    ) -> list[dict[str, object]]:
        violations: list[dict[str, object]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            for secret_pattern in secret_patterns:
                for match in secret_pattern.compiled.finditer(line):
                    violations.append(
                        {
                            "path": self._relative_path(repository_path, file_path),
                            "line_number": line_number,
                            "pattern_name": secret_pattern.name,
                            "match_preview": self._redact(match.group(0)),
                        }
                    )
        return violations

    def _extract_source_literal_candidates(self, text: str) -> list[LiteralCandidate]:
        candidates: list[LiteralCandidate] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in self.QUOTED_ASSIGNMENT_PATTERN.finditer(line):
                value = match.group("double_value") or match.group("single_value") or ""
                key = match.group("key")
                origin = (
                    "source_constant"
                    if self._is_source_constant_declaration(line=line, key=key)
                    else "source_assignment"
                )
                candidates.append(
                    LiteralCandidate(
                        key=key,
                        value=value,
                        line_number=line_number,
                        origin=origin,
                    )
                )
        return candidates

    @staticmethod
    def _is_source_constant_declaration(*, line: str, key: str) -> bool:
        """Return True only when the assigned identifier has a constant modifier.

        A normal declaration such as ``String password = "password"`` must remain
        a ``source_assignment``.  A declaration such as
        ``public static final String PASSWORD = "password"`` is a
        ``source_constant``.  Inspecting the declaration prefix directly avoids
        permissive regular expressions classifying ordinary assignments as constants.
        """
        assignment_match = re.search(
            rf"\b{re.escape(key)}\b\s*=",
            line,
            flags=re.IGNORECASE,
        )
        if assignment_match is None:
            return False

        declaration_prefix = line[: assignment_match.start()]
        modifier_tokens = {
            token.lower()
            for token in re.findall(
                r"\b(?:static|final|const|readonly)\b",
                declaration_prefix,
                flags=re.IGNORECASE,
            )
        }
        return bool(modifier_tokens)

    def _extract_flat_config_candidates(self, text: str) -> list[LiteralCandidate]:
        candidates: list[LiteralCandidate] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", ";")):
                continue
            match = self.FLAT_CONFIG_ASSIGNMENT_PATTERN.match(line)
            if match is None:
                continue
            candidates.append(
                LiteralCandidate(
                    key=match.group("key"),
                    value=self._strip_matching_quotes(match.group("value").strip()),
                    line_number=line_number,
                    origin="flat_config",
                )
            )
        return candidates

    def _extract_structured_candidates(
        self, file_path: Path, text: str
    ) -> list[LiteralCandidate]:
        suffix = file_path.suffix.lower()
        try:
            if suffix in {".yaml", ".yml"}:
                documents = list(yaml.safe_load_all(text))
                return self._walk_structured_documents(documents, text)
            if suffix == ".json":
                return self._walk_structured_documents([json.loads(text)], text)
            if suffix == ".toml":
                return self._walk_structured_documents([tomllib.loads(text)], text)
            if suffix == ".xml":
                root = ElementTree.fromstring(text)
                return self._walk_xml(root, text)
        except (
            yaml.YAMLError,
            json.JSONDecodeError,
            tomllib.TOMLDecodeError,
            ElementTree.ParseError,
        ):
            return []
        return []

    def _walk_structured_documents(
        self, documents: Iterable[Any], text: str
    ) -> list[LiteralCandidate]:
        candidates: list[LiteralCandidate] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                for raw_key, child in value.items():
                    key = str(raw_key)
                    if isinstance(child, (str, int, float)) and not isinstance(
                        child, bool
                    ):
                        string_value = str(child)
                        candidates.append(
                            LiteralCandidate(
                                key=key,
                                value=string_value,
                                line_number=self._find_line_number(
                                    text, key, string_value
                                ),
                                origin="structured_config",
                            )
                        )
                    walk(child)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        for document in documents:
            walk(document)
        return candidates

    def _walk_xml(
        self, root: ElementTree.Element, text: str
    ) -> list[LiteralCandidate]:
        candidates: list[LiteralCandidate] = []
        for element in root.iter():
            if element.text and element.text.strip():
                value = element.text.strip()
                candidates.append(
                    LiteralCandidate(
                        key=element.tag,
                        value=value,
                        line_number=self._find_line_number(text, element.tag, value),
                        origin="structured_config",
                    )
                )
            for key, value in element.attrib.items():
                candidates.append(
                    LiteralCandidate(
                        key=key,
                        value=value,
                        line_number=self._find_line_number(text, key, value),
                        origin="structured_config",
                    )
                )
        return candidates

    def _collect_files(
        self,
        repository_path: Path,
        include_paths: list[str],
        exclude_paths: list[str],
        file_patterns: list[str],
        exclude_dir_names: set[str],
        exclude_file_names: set[str],
        exclude_file_patterns: list[str],
    ) -> tuple[list[Path], list[dict[str, object]]]:
        resolved_exclude_paths = [
            self._resolve_path(repository_path, path) for path in exclude_paths
        ]
        files: list[Path] = []
        skipped: list[dict[str, object]] = []
        seen: set[Path] = set()

        for include_path in include_paths:
            resolved_include_path = self._resolve_path(repository_path, include_path)
            if self._is_excluded(resolved_include_path, resolved_exclude_paths):
                continue

            candidates: Iterable[Path]
            if resolved_include_path.is_file():
                candidates = [resolved_include_path]
            elif resolved_include_path.is_dir():
                candidates = (
                    path
                    for pattern in file_patterns
                    for path in resolved_include_path.rglob(pattern)
                )
            else:
                continue

            for candidate_file in candidates:
                if not candidate_file.is_file():
                    continue
                resolved_file = candidate_file.resolve()
                if resolved_file in seen:
                    continue
                seen.add(resolved_file)

                reason = self._scope_exclusion_reason(
                    repository_path=repository_path,
                    file_path=resolved_file,
                    resolved_exclude_paths=resolved_exclude_paths,
                    exclude_dir_names=exclude_dir_names,
                    exclude_file_names=exclude_file_names,
                    exclude_file_patterns=exclude_file_patterns,
                )
                if reason is not None:
                    skipped.append(
                        {
                            "path": self._relative_path(repository_path, resolved_file),
                            "reason": reason,
                        }
                    )
                    continue
                files.append(resolved_file)

        return sorted(files), skipped

    def _scope_exclusion_reason(
        self,
        repository_path: Path,
        file_path: Path,
        resolved_exclude_paths: list[Path],
        exclude_dir_names: set[str],
        exclude_file_names: set[str],
        exclude_file_patterns: list[str],
    ) -> str | None:
        if self._is_excluded(file_path, resolved_exclude_paths):
            return "excluded_path"

        try:
            relative = file_path.relative_to(repository_path.resolve())
        except ValueError:
            relative = file_path

        directory_parts = {part.lower() for part in relative.parts[:-1]}
        if not directory_parts.isdisjoint(exclude_dir_names):
            return "non_first_party_directory"

        if file_path.name.lower() in exclude_file_names:
            return "excluded_file_name"

        relative_posix = relative.as_posix()
        if any(
            fnmatch.fnmatch(file_path.name.lower(), pattern.lower())
            or fnmatch.fnmatch(relative_posix.lower(), pattern.lower())
            for pattern in exclude_file_patterns
        ):
            return "excluded_file_pattern"

        suffix = file_path.suffix.lower()
        supported = (
            suffix in self.SOURCE_EXTENSIONS
            or suffix in self.STRUCTURED_EXTENSIONS
            or suffix in self.FLAT_CONFIG_EXTENSIONS
        )
        if not supported:
            return "unsupported_file_type"
        return None

    def _is_sensitive_identifier(self, key: str, sensitive_terms: set[str]) -> bool:
        normalized = self._normalize_identifier(key)
        padded = f"_{normalized}_"
        return any(
            f"_{term}_" in padded or normalized.endswith(f"_{term}")
            for term in sensitive_terms
        )

    def _is_reference_identifier(
        self, key: str, reference_suffixes: tuple[str, ...]
    ) -> bool:
        normalized = self._normalize_identifier(key)
        return any(
            normalized == suffix or normalized.endswith(f"_{suffix}")
            for suffix in reference_suffixes
        )

    def _is_non_credential_identifier(
        self, key: str, non_credential_terms: set[str]
    ) -> bool:
        tokens = set(self._normalize_identifier(key).split("_"))
        return not tokens.isdisjoint(non_credential_terms)

    def _classify_sensitive_value(
        self,
        value: str,
        weak_credential_literals: set[str],
        min_length: int,
        min_entropy: float,
        min_character_classes: int,
    ) -> tuple[str, str, str] | None:
        candidate = value.strip()
        if not candidate:
            return None

        if self.CI_CONTEXT_REFERENCE_PATTERN.fullmatch(candidate):
            return None

        placeholder_match = self.ENVIRONMENT_PLACEHOLDER_PATTERN.fullmatch(candidate)
        if placeholder_match is not None:
            operator = placeholder_match.group("operator")
            default_value = placeholder_match.group("default")
            if operator is None:
                return None
            fallback = (default_value or "").strip()
            if not fallback or self._is_non_credential_default(fallback):
                return None
            if self.CI_CONTEXT_REFERENCE_PATTERN.fullmatch(fallback):
                return None
            if self.ENVIRONMENT_REFERENCE_PATTERN.fullmatch(fallback):
                return None
            return (
                "insecure_default_credential_literal",
                fallback,
                "environment_placeholder_default",
            )

        if self.ENVIRONMENT_REFERENCE_PATTERN.fullmatch(candidate):
            return None

        # Weak credentials are deliberately evaluated before placeholder and
        # entropy checks. Therefore PASSWORD = "password" is a finding.
        if candidate.lower() in weak_credential_literals:
            return (
                "weak_hardcoded_credential_literal",
                candidate,
                "direct_literal",
            )

        if not self._is_generic_secret_literal(
            candidate,
            min_length=min_length,
            min_entropy=min_entropy,
            min_character_classes=min_character_classes,
        ):
            return None

        return (
            "generic_hardcoded_credential_literal",
            candidate,
            "direct_literal",
        )

    def _is_generic_secret_literal(
        self,
        value: str,
        min_length: int,
        min_entropy: float,
        min_character_classes: int,
    ) -> bool:
        candidate = value.strip()
        if len(candidate) < min_length:
            return False
        if self._is_placeholder(candidate):
            return False
        if self._looks_like_path(candidate):
            return False
        if self._looks_like_non_secret_url(candidate):
            return False
        if self._character_class_count(candidate) < min_character_classes:
            return False
        return self._shannon_entropy(candidate) >= min_entropy

    def _is_non_credential_default(self, value: str) -> bool:
        return value.strip().lower() in {
            "",
            "null",
            "none",
            "nil",
            "false",
            "disabled",
            "unset",
        }

    def _is_placeholder(self, value: str) -> bool:
        return any(pattern.fullmatch(value.strip()) for pattern in self.PLACEHOLDER_PATTERNS)

    def _looks_like_path(self, value: str) -> bool:
        candidate = value.strip()
        if candidate.startswith(("/", "./", "../", "~/", "\\")):
            return True
        if re.match(r"^[A-Za-z]:[\\/]", candidate):
            return True
        return "/run/secrets/" in candidate or "/var/run/secrets/" in candidate

    def _looks_like_non_secret_url(self, value: str) -> bool:
        candidate = value.strip().lower()
        return candidate.startswith(("http://", "https://")) and "@" not in candidate

    def _character_class_count(self, value: str) -> int:
        return sum(
            [
                any(char.islower() for char in value),
                any(char.isupper() for char in value),
                any(char.isdigit() for char in value),
                any(not char.isalnum() for char in value),
            ]
        )

    def _shannon_entropy(self, value: str) -> float:
        if not value:
            return 0.0
        counts = Counter(value)
        length = len(value)
        return -sum(
            (count / length) * log2(count / length) for count in counts.values()
        )

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
                SecretPattern(name=name, regex=regex, compiled=re.compile(regex))
            )

        if patterns:
            return patterns

        defaults = {
            "private_key": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
            "aws_access_key_id": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
            "github_token": r"\bgh[pousr]_[A-Za-z0-9_]{30,255}\b",
            "google_api_key": r"\bAIza[0-9A-Za-z_-]{35}\b",
            "stripe_secret_key": r"\bsk_(?:live|test)_[0-9A-Za-z]{16,}\b",
            "slack_token": r"\bxox[baprs]-[0-9A-Za-z-]{10,}\b",
            "jwt_token": (
                r"\beyJ[A-Za-z0-9_-]{8,}\."
                r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"
            ),
            "credential_in_uri": (
                r"\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis)://"
                r"[^\s:/]+:[^\s@/]+@"
            ),
        }
        return [
            SecretPattern(name=name, regex=regex, compiled=re.compile(regex))
            for name, regex in defaults.items()
        ]

    def _get_string_list_param(
        self, rule: GovernanceRule, key: str, default: list[str]
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

    def _normalize_identifier(self, value: str) -> str:
        camel_split = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
        normalized = re.sub(r"[^A-Za-z0-9]+", "_", camel_split).strip("_").lower()
        return re.sub(r"_+", "_", normalized)

    def _strip_matching_quotes(self, value: str) -> str:
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            return value[1:-1]
        return value

    def _find_line_number(self, text: str, key: str, value: str) -> int | None:
        key_lower = key.lower()
        value_lower = value.lower()
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            if key_lower in lowered and value_lower in lowered:
                return line_number
        return None

    def _deduplicate_violations(
        self, violations: list[dict[str, object]]
    ) -> list[dict[str, object]]:
        deduplicated: list[dict[str, object]] = []
        seen: set[tuple[object, ...]] = set()
        for violation in violations:
            identity = (
                violation.get("path"),
                violation.get("line_number"),
                violation.get("pattern_name"),
                violation.get("match_preview"),
            )
            if identity in seen:
                continue
            seen.add(identity)
            deduplicated.append(violation)
        return deduplicated
