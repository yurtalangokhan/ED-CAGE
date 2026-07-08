import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandLineExecutionResult:
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool = False
    executable_not_found: bool = False


class CommandLineToolRunner:
    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        try:
            completed_process = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
            )

            return CommandLineExecutionResult(
                command=command,
                exit_code=completed_process.returncode,
                stdout=completed_process.stdout,
                stderr=completed_process.stderr,
            )

        except FileNotFoundError as exc:
            return CommandLineExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr=str(exc),
                executable_not_found=True,
            )

        except subprocess.TimeoutExpired as exc:
            return CommandLineExecutionResult(
                command=command,
                exit_code=None,
                stdout=self._to_text(exc.stdout),
                stderr=self._to_text(exc.stderr),
                timed_out=True,
            )

    def _to_text(self, value: str | bytes | None) -> str:
        if value is None:
            return ""

        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace")

        return value