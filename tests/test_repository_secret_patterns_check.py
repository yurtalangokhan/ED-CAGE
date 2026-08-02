from pathlib import Path

from ed_cage.checks.security.repository_secret_patterns_check import (
    RepositorySecretPatternsCheck,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext


def _rule() -> GovernanceRule:
    return GovernanceRule(
        id="SEC-001",
        title="First-party source and runtime configuration must not contain committed credential literals",
        description="Test rule",
        category="security",
        severity="critical",
        target="repository",
        check_type="repository_secret_patterns",
        params={
            "include_paths": ["."],
            "exclude_paths": [".git"],
            "file_patterns": [
                "*.py",
                "*.java",
                "*.cs",
                "*.js",
                "*.ts",
                "*.yaml",
                "*.yml",
                "*.json",
                "*.toml",
                "*.xml",
                "*.properties",
            ],
            "exclude_dir_names": [
                ".git",
                "node_modules",
                "vendor",
                "third_party",
                "generated",
                "target",
                "build",
                "dist",
                "docs",
                "examples",
                "tests",
            ],
            "exclude_file_names": [
                "README.md",
                "pom.xml",
                "build.gradle",
                ".env",
            ],
            "exclude_file_patterns": [
                "*.md",
                "*.sh",
                "*.ps1",
                "*.gradle",
            ],
            "generic_min_length": 16,
            "generic_min_entropy": 3.3,
            "generic_min_character_classes": 2,
            "sensitive_terms": [
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
                "connection_string",
            ],
            "reference_key_suffixes": [
                "file",
                "path",
                "name",
                "ref",
                "reference",
                "id",
                "hash",
                "salt",
            ],
            "secret_patterns": [
                {
                    "name": "private_key",
                    "regex": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
                },
                {
                    "name": "aws_access_key_id",
                    "regex": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
                },
                {
                    "name": "github_token",
                    "regex": r"\bgh[pousr]_[A-Za-z0-9_]{30,255}\b",
                },
            ],
        },
    )


def _context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test-project",
        repository_path=repository_path,
        config_path=repository_path / "case.yaml",
    )


def _violations(finding) -> list[dict[str, object]]:
    return finding.evidence[0].data["violations"]


def test_runtime_request_and_dto_expressions_are_not_violations(tmp_path: Path) -> None:
    java_file = tmp_path / "src" / "TokenService.java"
    java_file.parent.mkdir(parents=True)
    java_file.write_text(
        """
        String token = headers.getFirst(HttpHeaders.AUTHORIZATION);
        String password = dto.getPassword();
        String secret = secretManager.getSecret(secretName);
        """,
        encoding="utf-8",
    )

    cs_file = tmp_path / "src" / "TokenService.cs"
    cs_file.write_text(
        """
        var token = httpContext.Request.Headers.Authorization;
        var password = request.Password;
        var secret = command.Credentials.Secret;
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_kubernetes_token_file_reference_is_not_a_violation(tmp_path: Path) -> None:
    manifest = tmp_path / "deployment" / "prometheus-configmap.yml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        """
        scrape_configs:
          - job_name: kubernetes
            bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_secret_resource_name_is_not_a_violation(tmp_path: Path) -> None:
    manifest = tmp_path / "deployment" / "alloydb.yml"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(
        "ALLOYDB_SECRET_NAME: alloydb-secret\n",
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_nested_dependency_directory_is_not_scanned(tmp_path: Path) -> None:
    dependency_file = (
        tmp_path
        / "ts-ticket-office-service"
        / "node_modules"
        / "mongodb"
        / "src"
        / "constants.ts"
    )
    dependency_file.parent.mkdir(parents=True)
    dependency_file.write_text(
        'const apiKey = "ghp_1234567890abcdefghijklmnopqrstuvwxyzABCDE";\n',
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []
    skipped = finding.evidence[0].data["skipped_files_sample"]
    assert any(item["reason"] == "non_first_party_directory" for item in skipped)


def test_documentation_and_shell_scripts_are_out_of_scope(tmp_path: Path) -> None:
    readme = tmp_path / "README.md"
    readme.write_text(
        'export OPENAI_API_KEY="your_api_key_here"\n', encoding="utf-8"
    )

    script = tmp_path / "scripts" / "deploy.sh"
    script.parent.mkdir()
    script.write_text(
        "ALLOYDB_SECRET_NAME=alloydb-secret\n", encoding="utf-8"
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_hardcoded_source_literal_is_a_violation(tmp_path: Path) -> None:
    source = tmp_path / "src" / "CredentialService.java"
    source.parent.mkdir(parents=True)
    source.write_text(
        'String password = "D3v!Only-Real-Secret-9341";\n',
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.FAILED
    violations = _violations(finding)
    assert len(violations) == 1
    assert violations[0]["pattern_name"] == "generic_hardcoded_credential_literal"
    assert violations[0]["key"] == "password"


def test_hardcoded_structured_config_literal_is_a_violation(tmp_path: Path) -> None:
    config = tmp_path / "config" / "application.yml"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
        database:
          username: app_user
          password: "Q7!mZ2@xP9#vR4&nL8"
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.FAILED
    violations = _violations(finding)
    assert any(
        item["pattern_name"] == "generic_hardcoded_credential_literal"
        and item["key"] == "password"
        for item in violations
    )


def test_provider_specific_token_is_detected_without_sensitive_variable_name(
    tmp_path: Path,
) -> None:
    source = tmp_path / "src" / "config.py"
    source.parent.mkdir(parents=True)
    source.write_text(
        'value = "ghp_1234567890abcdefghijklmnopqrstuvwxyzABCDE"\n',
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.FAILED
    assert any(item["pattern_name"] == "github_token" for item in _violations(finding))


def test_github_actions_secret_reference_is_not_a_violation(tmp_path: Path) -> None:
    workflow = tmp_path / ".github" / "workflows" / "deploy-docker-images.yaml"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """
        jobs:
          deploy:
            steps:
              - uses: docker/login-action@v3
                with:
                  username: ${{ secrets.DOCKER_HUB_USERNAME }}
                  password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_environment_reference_without_default_is_not_a_violation(
    tmp_path: Path,
) -> None:
    config = tmp_path / "src" / "main" / "resources" / "application.yml"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
        datasource:
          username: ${ASSURANCE_MYSQL_USER}
          password: ${ASSURANCE_MYSQL_PASSWORD}
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.PASSED
    assert _violations(finding) == []


def test_environment_credential_default_is_a_violation(tmp_path: Path) -> None:
    config = tmp_path / "src" / "main" / "resources" / "application.yml"
    config.parent.mkdir(parents=True)
    config.write_text(
        """
        datasource:
          username: ${ASSURANCE_MYSQL_USER:root}
          password: ${ASSURANCE_MYSQL_PASSWORD:root}
        """,
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.FAILED
    violations = _violations(finding)
    assert len(violations) == 1
    assert violations[0]["pattern_name"] == "insecure_default_credential_literal"
    assert violations[0]["key"] == "password"
    assert violations[0]["source_kind"] == "environment_placeholder_default"


def test_shell_style_environment_credential_default_is_a_violation(
    tmp_path: Path,
) -> None:
    config = tmp_path / "application.yml"
    config.write_text(
        'password: "${DATABASE_PASSWORD:-changeme}"\n',
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(_rule(), _context(tmp_path))

    assert finding.status == CheckStatus.FAILED
    violations = _violations(finding)
    assert violations[0]["pattern_name"] == "insecure_default_credential_literal"
