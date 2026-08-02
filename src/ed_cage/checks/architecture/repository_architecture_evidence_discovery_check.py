from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

import yaml

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)


@dataclass(frozen=True)
class EvidenceCandidate:
    path: str
    evidence_kind: str
    confidence: str
    reason: str
    matched_filename_indicators: list[str]
    matched_content_markers: list[str]
    matched_quality_attributes: list[str]
    line_numbers: list[int]
    preview: str


class RepositoryArchitectureEvidenceDiscoveryCheck:
    """Discover architecture-decision and quality-scenario evidence.

    The check does not require one repository layout. It searches configured
    paths and classifies candidate files using document structure rather than
    isolated prose keywords.
    """

    _SUPPORTED_EVIDENCE_TYPES = {"adr", "quality_scenario"}

    @property
    def check_type(self) -> str:
        return "repository_architecture_evidence_discovery"

    def evaluate(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        try:
            evidence_kind = self._resolve_evidence_type(rule)
        except ValueError as exc:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=str(exc),
                category=rule.category,
                target=rule.target,
                check_type=rule.check_type,
                evidence=[
                    Evidence(
                        source="repository-architecture-evidence-discovery",
                        message=(
                            "Architecture evidence discovery configuration "
                            "is invalid."
                        ),
                        data={
                            "evidence_type": rule.params.get("evidence_type"),
                            "legacy_evidence_kind": rule.params.get(
                                "evidence_kind"
                            ),
                        },
                    )
                ],
            )

        required = bool(rule.params.get("required", False))
        min_confidence = str(
            rule.params.get("min_confidence", "medium")
        ).strip().lower()
        include_paths = self._get_string_list_param(
            rule,
            "include_paths",
            ["."],
        )
        exclude_paths = self._get_string_list_param(
            rule,
            "exclude_paths",
            [
                ".git",
                ".venv",
                "node_modules",
                "target",
                "build",
                "dist",
                "out",
                "coverage",
                ".pytest_cache",
                ".mypy_cache",
                ".ruff_cache",
            ],
        )
        candidate_paths = self._get_string_list_param(
            rule,
            "candidate_paths",
            [],
        )
        file_patterns = self._get_string_list_param(
            rule,
            "file_patterns",
            [
                "*.md",
                "*.adoc",
                "*.rst",
                "*.txt",
                "*.yaml",
                "*.yml",
                "*.json",
            ],
        )
        max_file_size_bytes = int(
            rule.params.get("max_file_size_bytes", 1_048_576)
        )

        files = self._collect_files(
            repository_path=context.repository_path,
            include_paths=include_paths,
            candidate_paths=candidate_paths,
            exclude_paths=exclude_paths,
            file_patterns=file_patterns,
        )

        candidates: list[EvidenceCandidate] = []
        skipped_files: list[dict[str, object]] = []
        scanned_files = 0

        for file_path in files:
            try:
                file_size = file_path.stat().st_size
            except OSError as exc:
                skipped_files.append(
                    {
                        "path": self._relative_path(
                            context.repository_path,
                            file_path,
                        ),
                        "reason": "stat_failed",
                        "message": str(exc),
                    }
                )
                continue

            if file_size > max_file_size_bytes:
                skipped_files.append(
                    {
                        "path": self._relative_path(
                            context.repository_path,
                            file_path,
                        ),
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
                        "path": self._relative_path(
                            context.repository_path,
                            file_path,
                        ),
                        "reason": "read_failed",
                        "message": str(exc),
                    }
                )
                continue

            if self._looks_binary(content_bytes):
                skipped_files.append(
                    {
                        "path": self._relative_path(
                            context.repository_path,
                            file_path,
                        ),
                        "reason": "binary_file",
                    }
                )
                continue

            scanned_files += 1
            text = content_bytes.decode("utf-8", errors="ignore")
            candidate = self._classify_file(
                rule=rule,
                repository_path=context.repository_path,
                file_path=file_path,
                text=text,
                evidence_kind=evidence_kind,
            )

            if candidate is not None and self._meets_min_confidence(
                candidate.confidence,
                min_confidence,
            ):
                candidates.append(candidate)

        candidate_payload = [
            self._candidate_to_dict(candidate)
            for candidate in candidates
        ]
        evidence_data: dict[str, object] = {
            "evidence_type": evidence_kind,
            # Kept for backward compatibility with existing report consumers.
            "evidence_kind": evidence_kind,
            "required": required,
            "min_confidence": min_confidence,
            "include_paths": include_paths,
            "candidate_paths": candidate_paths,
            "exclude_paths": exclude_paths,
            "file_patterns": file_patterns,
            "candidate_file_count": len(files),
            "scanned_file_count": scanned_files,
            "skipped_file_count": len(skipped_files),
            "discovered_evidence_count": len(candidates),
            "discovered_evidence": candidate_payload,
            "skipped_files_sample": skipped_files[:20],
        }
        evidence = [
            Evidence(
                source="repository-architecture-evidence-discovery",
                message="Repository architecture evidence discovery completed.",
                data=evidence_data,
            )
        ]


        if candidates:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.PASSED,
                message=(
                    "Architecture evidence discovery found "
                    f"{len(candidates)} candidate artifact(s) for "
                    f"evidence type '{evidence_kind}'."
                ),
                category=rule.category,
                target=rule.target,
                check_type=rule.check_type,
                evidence=evidence,
            )

        if required:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    f"Architecture evidence of type '{evidence_kind}' is "
                    "required, but no compatible artifact was discovered."
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
            status=CheckStatus.SKIPPED,
            message=(
                f"No architecture evidence of type '{evidence_kind}' was "
                "discovered; this evidence type is not required by the "
                "current evidence profile."
            ),
            category=rule.category,
            target=rule.target,
            check_type=rule.check_type,
            evidence=evidence,
        )

    def _resolve_evidence_type(self, rule: GovernanceRule) -> str:
        configured_type = rule.params.get("evidence_type")
        legacy_kind = rule.params.get("evidence_kind")

        if configured_type is None and legacy_kind is None:
            raise ValueError(
                "Architecture evidence discovery requires the parameter "
                "'evidence_type'. No implicit ADR default is applied."
            )

        selected_value = (
            configured_type
            if configured_type is not None
            else legacy_kind
        )
        canonical_type = self._canonicalize_evidence_type(selected_value)

        if canonical_type is None:
            raise ValueError(
                "Unsupported architecture evidence type: "
                f"{selected_value!r}. Supported values are 'adr' and "
                "'quality_scenario'."
            )

        if configured_type is not None and legacy_kind is not None:
            canonical_legacy_kind = self._canonicalize_evidence_type(
                legacy_kind
            )
            if canonical_legacy_kind != canonical_type:
                raise ValueError(
                    "Conflicting architecture evidence parameters: "
                    f"evidence_type={configured_type!r}, "
                    f"evidence_kind={legacy_kind!r}."
                )

        return canonical_type

    def _canonicalize_evidence_type(
        self,
        value: object,
    ) -> str | None:
        normalized = str(value).strip().lower().replace("-", "_")
        aliases = {
            "adr": "adr",
            "architecture_decision": "adr",
            "architecture_decision_record": "adr",
            "quality_scenario": "quality_scenario",
            "quality_attribute_scenario": "quality_scenario",
            "scenario": "quality_scenario",
        }
        return aliases.get(normalized)

    def _classify_file(
        self,
        rule: GovernanceRule,
        repository_path: Path,
        file_path: Path,
        text: str,
        evidence_kind: str,
    ) -> EvidenceCandidate | None:
        if evidence_kind == "adr":
            return self._classify_adr_candidate(
                rule,
                repository_path,
                file_path,
                text,
            )

        if evidence_kind == "quality_scenario":
            return self._classify_quality_scenario_candidate(
                rule,
                repository_path,
                file_path,
                text,
            )

        return None

    def _classify_adr_candidate(
        self,
        rule: GovernanceRule,
        repository_path: Path,
        file_path: Path,
        text: str,
    ) -> EvidenceCandidate | None:
        filename_indicators = self._get_string_list_param(
            rule,
            "filename_indicators",
            [
                "adr",
                "adrs",
                "architecture-decision",
                "architecture-decision-record",
                "decision-record",
                "design-decision",
            ],
        )
        marker_groups = self._get_adr_marker_groups(rule)
        required_marker_groups = set(
            self._get_string_list_param(
                rule,
                "required_adr_marker_groups",
                ["context", "decision", "consequences"],
            )
        )
        record_phrases = self._get_string_list_param(
            rule,
            "record_phrases",
            [
                "architecture decision record",
                "architectural decision record",
            ],
        )
        min_marker_count = int(rule.params.get("min_marker_count", 3))

        relative_path = self._relative_path(repository_path, file_path)
        normalized_path = relative_path.lower().replace("\\", "/")
        normalized_name = file_path.name.lower()
        lower_lines = [line.lower() for line in text.splitlines()]

        matched_filename_indicators = [
            indicator
            for indicator in filename_indicators
            if (
                indicator.lower() in normalized_name
                or indicator.lower() in normalized_path
            )
        ]

        all_marker_aliases = sorted(
            {
                alias
                for aliases in marker_groups.values()
                for alias in aliases
            }
        )
        matched_content_markers, line_numbers = (
            self._find_structural_markers(
                lower_lines,
                all_marker_aliases,
            )
        )
        matched_record_phrases, phrase_line_numbers = self._find_markers(
            lower_lines,
            record_phrases,
        )

        normalized_matched_markers = {
            self._normalize_marker(marker)
            for marker in matched_content_markers
        }
        matched_marker_groups = {
            group_name
            for group_name, aliases in marker_groups.items()
            if normalized_matched_markers.intersection(
                {
                    self._normalize_marker(alias)
                    for alias in aliases
                }
            )
        }

        has_filename_signal = bool(matched_filename_indicators)
        has_record_phrase = bool(matched_record_phrases)
        has_required_structure = (
            required_marker_groups.issubset(matched_marker_groups)
            and len(matched_content_markers) >= min_marker_count
        )
        has_partial_filename_structure = (
            has_filename_signal
            and "decision" in matched_marker_groups
            and len(matched_marker_groups) >= 2
            and len(matched_content_markers) >= 2
        )

        # Isolated prose such as "discuss this design decision" is not
        # architecture-decision evidence. Structure is mandatory for medium
        # or high confidence.
        if has_required_structure:
            if has_filename_signal or has_record_phrase:
                confidence = "high"
                reason = "adr_identity_and_required_structure"
            else:
                confidence = "medium"
                reason = "required_adr_structure"
        elif has_partial_filename_structure:
            confidence = "medium"
            reason = "adr_filename_and_partial_structure"
        elif has_filename_signal or has_record_phrase:
            confidence = "low"
            reason = "adr_identity_without_sufficient_structure"
        else:
            return None

        return EvidenceCandidate(
            path=relative_path,
            evidence_kind="adr",
            confidence=confidence,
            reason=reason,
            matched_filename_indicators=matched_filename_indicators,
            matched_content_markers=sorted(
                set(
                    [
                        *matched_content_markers,
                        *matched_record_phrases,
                    ]
                )
            ),
            matched_quality_attributes=[],
            line_numbers=sorted(
                set([*line_numbers, *phrase_line_numbers])
            )[:20],
            preview=self._preview(text),
        )

    def _classify_quality_scenario_candidate(
        self,
        rule: GovernanceRule,
        repository_path: Path,
        file_path: Path,
        text: str,
    ) -> EvidenceCandidate | None:
        filename_indicators = self._get_string_list_param(
            rule,
            "filename_indicators",
            [
                "scenario",
                "scenarios",
                "quality",
                "quality-attribute",
                "nfr",
                "requirements",
            ],
        )
        scenario_markers = self._get_string_list_param(
            rule,
            "scenario_markers",
            [
                "source",
                "stimulus",
                "environment",
                "artifact",
                "response",
                "response measure",
                "response_measure",
                "quality attribute scenario",
            ],
        )
        quality_attribute_markers = self._get_string_list_param(
            rule,
            "quality_attribute_markers",
            [
                "availability",
                "modifiability",
                "performance",
                "security",
                "reliability",
                "scalability",
                "maintainability",
                "observability",
            ],
        )
        min_scenario_marker_count = int(
            rule.params.get("min_scenario_marker_count", 3)
        )
        min_quality_marker_count = int(
            rule.params.get("min_quality_marker_count", 1)
        )

        relative_path = self._relative_path(repository_path, file_path)
        normalized_path = relative_path.lower().replace("\\", "/")
        normalized_name = file_path.name.lower()
        lower_text = text.lower()
        lower_lines = [line.lower() for line in text.splitlines()]

        matched_filename_indicators = [
            indicator
            for indicator in filename_indicators
            if (
                indicator.lower() in normalized_name
                or indicator.lower() in normalized_path
            )
        ]

        structural_scenario_markers = [
            marker
            for marker in scenario_markers
            if self._normalize_marker(marker)
            != "quality attribute scenario"
        ]
        matched_scenario_markers, scenario_line_numbers = (
            self._find_structural_markers(
                lower_lines,
                structural_scenario_markers,
            )
        )
        matched_quality_markers, quality_line_numbers = (
            self._find_markers(
                lower_lines,
                quality_attribute_markers,
            )
        )
        structured_data_matches = (
            self._detect_structured_quality_scenario_data(
                text,
                file_path,
                min_scenario_marker_count,
            )
        )

        has_strong_phrase = "quality attribute scenario" in lower_text
        has_structured_scenario = (
            len(matched_scenario_markers)
            >= min_scenario_marker_count
            and len(matched_quality_markers)
            >= min_quality_marker_count
        )
        has_structured_data = bool(structured_data_matches)
        has_filename_and_markers = (
            bool(matched_filename_indicators)
            and has_structured_scenario
        )
        has_phrase_supported_structure = (
            has_strong_phrase
            and len(matched_scenario_markers)
            >= min_scenario_marker_count
            and len(matched_quality_markers)
            >= min_quality_marker_count
        )

        # A prose mention of "quality attribute scenario" is insufficient.
        # The candidate must expose scenario fields/headings plus a quality
        # attribute, or contain a structured YAML/JSON scenario object.
        if (
            not has_structured_scenario
            and not has_structured_data
            and not has_phrase_supported_structure
        ):
            return None

        if has_structured_data or (
            has_filename_and_markers
            and len(matched_scenario_markers) >= 4
        ):
            confidence = "high"
            reason = "structured_quality_scenario_evidence"
        else:
            confidence = "medium"
            reason = "quality_scenario_structural_markers"

        return EvidenceCandidate(
            path=relative_path,
            evidence_kind="quality_scenario",
            confidence=confidence,
            reason=reason,
            matched_filename_indicators=matched_filename_indicators,
            matched_content_markers=sorted(
                set(
                    [
                        *matched_scenario_markers,
                        *structured_data_matches,
                    ]
                )
            ),
            matched_quality_attributes=sorted(
                set(matched_quality_markers)
            ),
            line_numbers=sorted(
                set(
                    [
                        *scenario_line_numbers,
                        *quality_line_numbers,
                    ]
                )
            )[:20],
            preview=self._preview(text),
        )

    def _detect_structured_quality_scenario_data(
        self,
        text: str,
        file_path: Path,
        min_scenario_marker_count: int,
    ) -> list[str]:
        if file_path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            return []

        try:
            if file_path.suffix.lower() == ".json":
                parsed: Any = json.loads(text)
            else:
                parsed = yaml.safe_load(text)
        except (
            yaml.YAMLError,
            json.JSONDecodeError,
            TypeError,
            ValueError,
        ):
            return []

        scenario_dicts = self._flatten_dicts(parsed)
        scenario_field_aliases = {
            "source": {"source"},
            "stimulus": {"stimulus"},
            "environment": {"environment"},
            "artifact": {"artifact"},
            "response": {"response"},
            "response_measure": {
                "response_measure",
                "response measure",
                "measure",
            },
        }
        quality_field_aliases = {
            "quality_attribute",
            "quality attribute",
            "quality",
            "attribute",
        }

        matches: list[str] = []
        for item in scenario_dicts:
            normalized_keys = {
                self._normalize_mapping_key(key)
                for key in item.keys()
            }
            matched_scenario_fields = [
                canonical
                for canonical, aliases in scenario_field_aliases.items()
                if normalized_keys.intersection(
                    {
                        self._normalize_mapping_key(alias)
                        for alias in aliases
                    }
                )
            ]
            has_quality_field = bool(
                normalized_keys.intersection(
                    {
                        self._normalize_mapping_key(alias)
                        for alias in quality_field_aliases
                    }
                )
            )

            if (
                len(matched_scenario_fields)
                >= min_scenario_marker_count
                and has_quality_field
            ):
                matches.extend(matched_scenario_fields)
                matches.append("quality_attribute")

        return sorted(set(matches))

    def _get_adr_marker_groups(
        self,
        rule: GovernanceRule,
    ) -> dict[str, list[str]]:
        defaults = {
            "status": ["status"],
            "context": [
                "context",
                "problem statement",
                "issue",
                "decision drivers",
            ],
            "decision": [
                "decision",
                "chosen option",
                "decision outcome",
            ],
            "consequences": [
                "consequences",
                "rationale",
                "alternatives",
                "considered options",
                "pros and cons",
            ],
        }
        raw_groups = rule.params.get("adr_marker_groups", defaults)
        if not isinstance(raw_groups, dict):
            return defaults

        parsed_groups: dict[str, list[str]] = {}
        for raw_group_name, raw_aliases in raw_groups.items():
            if not isinstance(raw_aliases, list):
                continue

            aliases = [
                str(alias).strip().lower()
                for alias in raw_aliases
                if str(alias).strip()
            ]
            if aliases:
                parsed_groups[
                    str(raw_group_name).strip().lower()
                ] = aliases

        return parsed_groups or defaults

    def _find_structural_markers(
        self,
        lower_lines: list[str],
        markers: list[str],
    ) -> tuple[list[str], list[int]]:
        matched_markers: list[str] = []
        line_numbers: list[int] = []

        for line_number, line in enumerate(lower_lines, start=1):
            for marker_text in markers:
                if self._structural_marker_matches(line, marker_text):
                    matched_markers.append(marker_text)
                    line_numbers.append(line_number)

        return (
            sorted(set(matched_markers)),
            sorted(set(line_numbers)),
        )

    def _structural_marker_matches(
        self,
        line: str,
        marker_text: str,
    ) -> bool:
        escaped_marker = re.escape(marker_text.strip().lower())
        patterns = [
            # Markdown headings.
            rf"^\s{{0,3}}#{{1,6}}\s+{escaped_marker}(?:\s|:|$)",
            # AsciiDoc headings.
            rf"^\s*=+\s+{escaped_marker}(?:\s|:|$)",
            # Bold labels in Markdown.
            (
                rf"^\s*(?:\*\*|__){escaped_marker}"
                rf"(?:\*\*|__)\s*:?.*$"
            ),
            # YAML/JSON/plain key-value labels.
            rf"^\s*[\"']?{escaped_marker}[\"']?\s*:\s*.*$",
            # Standalone labels or numbered headings.
            rf"^\s*(?:\d+[.)]\s*)?{escaped_marker}\s*:?[\s]*$",
        ]
        return any(
            re.search(pattern, line) is not None
            for pattern in patterns
        )

    def _flatten_dicts(self, value: Any) -> list[dict[str, Any]]:
        dictionaries: list[dict[str, Any]] = []

        if isinstance(value, dict):
            dictionaries.append(value)
            for nested_value in value.values():
                dictionaries.extend(self._flatten_dicts(nested_value))
        elif isinstance(value, list):
            for item in value:
                dictionaries.extend(self._flatten_dicts(item))

        return dictionaries

    def _collect_files(
        self,
        repository_path: Path,
        include_paths: list[str],
        candidate_paths: list[str],
        exclude_paths: list[str],
        file_patterns: list[str],
    ) -> list[Path]:
        resolved_exclude_paths = [
            self._resolve_path(repository_path, path)
            for path in exclude_paths
        ]
        search_paths = [*candidate_paths, *include_paths]
        files: list[Path] = []
        seen: set[Path] = set()

        for search_path in search_paths:
            resolved_search_path = self._resolve_path(
                repository_path,
                search_path,
            )

            if self._is_excluded(
                resolved_search_path,
                resolved_exclude_paths,
            ):
                continue

            if resolved_search_path.is_file():
                resolved_file = resolved_search_path.resolve()
                if (
                    resolved_file not in seen
                    and not self._is_excluded(
                        resolved_file,
                        resolved_exclude_paths,
                    )
                ):
                    files.append(resolved_file)
                    seen.add(resolved_file)
                continue

            if not resolved_search_path.is_dir():
                continue

            for file_pattern in file_patterns:
                for candidate_file in resolved_search_path.rglob(
                    file_pattern
                ):
                    if not candidate_file.is_file():
                        continue

                    resolved_file = candidate_file.resolve()
                    if self._is_excluded(
                        resolved_file,
                        resolved_exclude_paths,
                    ):
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

        return [
            str(item).strip()
            for item in raw_value
            if str(item).strip()
        ]

    def _resolve_path(
        self,
        repository_path: Path,
        path: str,
    ) -> Path:
        raw_path = Path(path)
        if raw_path.is_absolute():
            return raw_path.resolve()
        return (repository_path / raw_path).resolve()

    def _is_excluded(
        self,
        path: Path,
        exclude_paths: list[Path],
    ) -> bool:
        resolved_path = path.resolve()
        for exclude_path in exclude_paths:
            resolved_exclude_path = exclude_path.resolve()
            if resolved_path == resolved_exclude_path:
                return True
            if resolved_exclude_path in resolved_path.parents:
                return True
        return False

    def _relative_path(
        self,
        repository_path: Path,
        file_path: Path,
    ) -> str:
        try:
            return str(
                file_path.resolve().relative_to(repository_path.resolve())
            )
        except ValueError:
            return str(file_path)

    def _looks_binary(self, content: bytes) -> bool:
        return b"\x00" in content[:1024]

    def _find_markers(
        self,
        lower_lines: list[str],
        markers: list[str],
    ) -> tuple[list[str], list[int]]:
        matched_markers: list[str] = []
        line_numbers: list[int] = []

        for line_number, line in enumerate(lower_lines, start=1):
            for marker in markers:
                marker_text = marker.lower()
                if self._marker_matches(line, marker_text):
                    matched_markers.append(marker)
                    line_numbers.append(line_number)

        return (
            sorted(set(matched_markers)),
            sorted(set(line_numbers)),
        )

    def _marker_matches(self, line: str, marker: str) -> bool:
        if " " in marker:
            return marker in line

        pattern = (
            rf"(^|[^a-z0-9_]){re.escape(marker)}"
            rf"([^a-z0-9_]|$)"
        )
        return re.search(pattern, line) is not None

    def _normalize_marker(self, marker_text: str) -> str:
        normalized = marker_text.strip().lower().replace("-", " ")
        return re.sub(r"\s+", " ", normalized)

    def _normalize_mapping_key(self, value: object) -> str:
        normalized = str(value).strip().lower().replace("-", "_")
        return re.sub(r"\s+", "_", normalized)

    def _preview(self, text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:160]
        return ""

    def _candidate_to_dict(
        self,
        candidate: EvidenceCandidate,
    ) -> dict[str, object]:
        return {
            "path": candidate.path,
            "evidence_kind": candidate.evidence_kind,
            "confidence": candidate.confidence,
            "reason": candidate.reason,
            "matched_filename_indicators": (
                candidate.matched_filename_indicators
            ),
            "matched_content_markers": (
                candidate.matched_content_markers
            ),
            "matched_quality_attributes": (
                candidate.matched_quality_attributes
            ),
            "line_numbers": candidate.line_numbers,
            "preview": candidate.preview,
        }

    def _meets_min_confidence(
        self,
        confidence: str,
        min_confidence: str,
    ) -> bool:
        ranking = {"low": 1, "medium": 2, "high": 3}
        return ranking.get(confidence, 0) >= ranking.get(
            min_confidence,
            2,
        )
