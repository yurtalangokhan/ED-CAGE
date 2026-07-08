import sys

from ed_cage.adapters.tools.command_line_tool_runner import CommandLineToolRunner


def test_command_line_tool_runner_captures_stdout() -> None:
    result = CommandLineToolRunner().run(
        command=[
            sys.executable,
            "-c",
            "print('hello-ed-cage')",
        ],
        timeout_seconds=5,
    )

    assert result.exit_code == 0
    assert "hello-ed-cage" in result.stdout
    assert not result.timed_out
    assert not result.executable_not_found


def test_command_line_tool_runner_handles_executable_not_found() -> None:
    result = CommandLineToolRunner().run(
        command=[
            "definitely-not-existing-ed-cage-tool",
            "--version",
        ],
        timeout_seconds=5,
    )

    assert result.exit_code is None
    assert result.executable_not_found