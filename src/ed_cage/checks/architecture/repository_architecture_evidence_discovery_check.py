from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any

import yaml

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


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
    """Discover ADR-like and quality-attribute-scenario-like architecture evidence.

    This check intentionally does not require a single repository convention such as
    docs/adr or docs/quality-attributes/scenarios.yaml. It searches candidate paths,
    file names, and content markers. If evidence is not found, the rule can either
    fail or skip depending on the rule parameter `required`.
    """

    @property
    def check_type(self) -> str:
        return "repository_architecture_evidence_discovery"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        evidence_kind = str(rule.params.get("evidence_kind", "adr")).strip().lower()
        required = bool(rule.params.get("required", False))
        min_confidence = str(rule.params.get("min_confidence", "medium")).strip().lower()
        include_paths = self._get_string_list_param(rule, "include_paths", ["."])
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
        candidate_paths = self._get_string_list_param(rule, "candidate_paths", [])
        file_patterns = self._get_string_list_param(
            rule,
            "file_patterns",
            ["*.md", "*.adoc", "*.rst", "*.txt", "*.yaml", "*.yml", "*.json"],
        )
        max_file_size_bytes = int(rule.params.get("max_file_size_bytes", 1048576))

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
            candidate = self._classify_file(
                rule=rule,
                repository_path=context.repository_path,
                file_path=file_path,
                text=text,
                evidence_kind=evidence_kind,
            )
            if candidate is not None and self._meets_min_confidence(candidate.confidence, min_confidence):
                candidates.append(candidate)

        candidate_payload = [self._candidate_to_dict(candidate) for candidate in candidates]
        evidence_data: dict[str, object] = {
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
                    f"Architecture evidence discovery found {len(candidates)} "
                    f"candidate artifact(s) for evidence kind '{evidence_kind}'."
                ),
                evidence=evidence,
            )

        if required:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    f"Architecture evidence of kind '{evidence_kind}' is required, "
                    "but no compatible artifact was discovered."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.SKIPPED,
            message=(
                f"No architecture evidence of kind '{evidence_kind}' was discovered; "
                "this evidence type is not required by the current evidence profile."
            ),
            evidence=evidence,
        )

    def _classify_file(
        self,
        rule: GovernanceRule,
        repository_path: Path,
        file_path: Path,
        text: str,
        evidence_kind: str,
    ) -> EvidenceCandidate | None:
        if evidence_kind in {"adr", "architecture_decision", "architecture-decision"}:
            return self._classify_adr_candidate(rule, repository_path, file_path, text)
        if evidence_kind in {
            "quality_scenario",
            "quality-attribute-scenario",
            "quality_attribute_scenario",
            "scenario",
        }:
            return self._classify_quality_scenario_candidate(
                rule, repository_path, file_path, text
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
        content_markers = self._get_string_list_param(
            rule,
            "content_markers",
            ["status", "context", "decision", "consequences", "rationale", "alternatives"],
        )
        strong_phrases = self._get_string_list_param(
            rule,
            "strong_phrases",
            [
                "architecture decision record",
                "architectural decision record",
                "architecture decision",
                "design decision",
            ],
        )
        min_marker_count = int(rule.params.get("min_marker_count", 3))

        relative_path = self._relative_path(repository_path, file_path)
        normalized_path = relative_path.lower().replace("\\", "/")
        normalized_name = file_path.name.lower()
        lower_text = text.lower()
        lower_lines = [line.lower() for line in text.splitlines()]

        matched_filename_indicators = [
            indicator
            for indicator in filename_indicators
            if indicator.lower() in normalized_name or indicator.lower() in normalized_path
        ]
        matched_content_markers, line_numbers = self._find_markers(
            lower_lines, content_markers
        )
        matched_strong_phrases, strong_line_numbers = self._find_markers(
            lower_lines, strong_phrases
        )

        has_filename_signal = bool(matched_filename_indicators)
        has_structural_markers = len(matched_content_markers) >= min_marker_count
        has_strong_phrase = bool(matched_strong_phrases) or any(
            phrase.lower() in lower_text for phrase in strong_phrases
        )

        if not has_filename_signal and not has_structural_markers and not has_strong_phrase:
            return None

        if has_filename_signal and has_structural_markers:
            confidence = "high"
            reason = "filename_and_adr_content_markers"
        elif has_structural_markers or has_strong_phrase:
            confidence = "medium"
            reason = "adr_content_markers"
        else:
            confidence = "low"
            reason = "filename_indicator_only"

        return EvidenceCandidate(
            path=relative_path,
            evidence_kind="adr",
            confidence=confidence,
            reason=reason,
            matched_filename_indicators=matched_filename_indicators,
            matched_content_markers=sorted(set([*matched_content_markers, *matched_strong_phrases])),
            matched_quality_attributes=[],
            line_numbers=sorted(set([*line_numbers, *strong_line_numbers]))[:20],
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
            ["scenario", "scenarios", "quality", "quality-attribute", "nfr", "requirements"],
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
        min_scenario_marker_count = int(rule.params.get("min_scenario_marker_count", 3))
        min_quality_marker_count = int(rule.params.get("min_quality_marker_count", 1))

        relative_path = self._relative_path(repository_path, file_path)
        normalized_path = relative_path.lower().replace("\\", "/")
        normalized_name = file_path.name.lower()
        lower_text = text.lower()
        lower_lines = [line.lower() for line in text.splitlines()]

        matched_filename_indicators = [
            indicator
            for indicator in filename_indicators
            if indicator.lower() in normalized_name or indicator.lower() in normalized_path
        ]
        matched_scenario_markers, scenario_line_numbers = self._find_markers(
            lower_lines, scenario_markers
        )
        matched_quality_markers, quality_line_numbers = self._find_markers(
            lower_lines, quality_attribute_markers
        )
        structured_yaml_matches = self._detect_structured_quality_scenario_yaml(text, file_path)

        has_strong_phrase = "quality attribute scenario" in lower_text
        has_structured_scenario = (
            len(matched_scenario_markers) >= min_scenario_marker_count
            and len(matched_quality_markers) >= min_quality_marker_count
        )
        has_structured_yaml = bool(structured_yaml_matches)
        has_filename_and_markers = bool(matched_filename_indicators) and has_structured_scenario

        if not has_strong_phrase and not has_structured_scenario and not has_structured_yaml:
            return None

        if has_structured_yaml or (has_filename_and_markers and len(matched_scenario_markers) >= 4):
            confidence = "high"
            reason = "structured_quality_scenario_evidence"
        elif has_structured_scenario or has_strong_phrase:
            confidence = "medium"
            reason = "quality_scenario_content_markers"
        else:
            confidence = "low"
            reason = "filename_indicator_only"

        return EvidenceCandidate(
            path=relative_path,
            evidence_kind="quality_scenario",
            confidence=confidence,
            reason=reason,
            matched_filename_indicators=matched_filename_indicators,
            matched_content_markers=sorted(set([*matched_scenario_markers, *structured_yaml_matches])),
            matched_quality_attributes=sorted(set(matched_quality_markers)),
            line_numbers=sorted(set([*scenario_line_numbers, *quality_line_numbers]))[:20],
            preview=self._preview(text),
        )

    def _detect_structured_quality_scenario_yaml(self, text: str, file_path: Path) -> list[str]:
        if file_path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            return []

        try:
            if file_path.suffix.lower() == ".json":
                parsed: Any = json.loads(text)
            else:
                parsed = yaml.safe_load(text)
        except (yaml.YAMLError, json.JSONDecodeError, TypeError, ValueError):
            return []

        scenario_dicts = self._flatten_dicts(parsed)
        required_field_aliases = {
            "source": {"source"},
            "stimulus": {"stimulus"},
            "environment": {"environment"},
            "artifact": {"artifact"},
            "response": {"response"},
            "response_measure": {"response_measure", "response measure", "measure"},
            "quality_attribute": {"quality_attribute", "quality attribute", "quality", "attribute"},
        }
        matches: list[str] = []

        for item in scenario_dicts:
            normalized_keys = {str(key).strip().lower().replace("-", "_") for key in item.keys()}
            matched_fields = [
                canonical
                for canonical, aliases in required_field_aliases.items()
                if normalized_keys.intersection({alias.replace("-", "_") for alias in aliases})
            ]
            if len(matched_fields) >= 5 and "quality_attribute" in matched_fields:
                matches.extend(matched_fields)

        return sorted(set(matches))

    def _flatten_dicts(self, value: Any) -> list[dict[str, Any]]:
        dicts: list[dict[str, Any]] = []
        if isinstance(value, dict):
            dicts.append(value)
            for nested_value in value.values():
                dicts.extend(self._flatten_dicts(nested_value))
        elif isinstance(value, list):
            for item in value:
                dicts.extend(self._flatten_dicts(item))
        return dicts

    def _collect_files(
        self,
        repository_path: Path,
        include_paths: list[str],
        candidate_paths: list[str],
        exclude_paths: list[str],
        file_patterns: list[str],
    ) -> list[Path]:
        resolved_exclude_paths = [self._resolve_path(repository_path, path) for path in exclude_paths]
        search_paths = [*candidate_paths, *include_paths]
        files: list[Path] = []
        seen: set[Path] = set()

        for search_path in search_paths:
            resolved_search_path = self._resolve_path(repository_path, search_path)

            if self._is_excluded(resolved_search_path, resolved_exclude_paths):
                continue

            if resolved_search_path.is_file():
                resolved_file = resolved_search_path.resolve()
                if resolved_file not in seen and not self._is_excluded(resolved_file, resolved_exclude_paths):
                    files.append(resolved_file)
                    seen.add(resolved_file)
                continue

            if not resolved_search_path.is_dir():
                continue

            for file_pattern in file_patterns:
                for candidate_file in resolved_search_path.rglob(file_pattern):
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
        return [str(item) for item in raw_value if str(item).strip()]

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
            return str(file_path.resolve().relative_to(repository_path.resolve()))
        except ValueError:
            return str(file_path)

    def _looks_binary(self, content: bytes) -> bool:
        return b"\x00" in content[:1024]

    def _find_markers(self, lower_lines: list[str], markers: list[str]) -> tuple[list[str], list[int]]:
        matched_markers: list[str] = []
        line_numbers: list[int] = []
        for line_number, line in enumerate(lower_lines, start=1):
            for marker in markers:
                marker_text = marker.lower()
                if self._marker_matches(line, marker_text):
                    matched_markers.append(marker)
                    line_numbers.append(line_number)
        return sorted(set(matched_markers)), sorted(set(line_numbers))

    def _marker_matches(self, line: str, marker: str) -> bool:
        if " " in marker:
            return marker in line
        pattern = rf"(^|[^a-z0-9_]){re.escape(marker)}([^a-z0-9_]|$)"
        return re.search(pattern, line) is not None

    def _preview(self, text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:160]
        return ""

    def _candidate_to_dict(self, candidate: EvidenceCandidate) -> dict[str, object]:
        return {
            "path": candidate.path,
            "evidence_kind": candidate.evidence_kind,
            "confidence": candidate.confidence,
            "reason": candidate.reason,
            "matched_filename_indicators": candidate.matched_filename_indicators,
            "matched_content_markers": candidate.matched_content_markers,
            "matched_quality_attributes": candidate.matched_quality_attributes,
            "line_numbers": candidate.line_numbers,
            "preview": candidate.preview,
        }

    def _meets_min_confidence(self, confidence: str, min_confidence: str) -> bool:
        ranking = {"low": 1, "medium": 2, "high": 3}
        return ranking.get(confidence, 0) >= ranking.get(min_confidence, 2)
