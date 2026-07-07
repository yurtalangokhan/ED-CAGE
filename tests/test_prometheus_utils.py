from ed_cage.checks.common.prometheus_utils import (
    find_metric_name_matches,
    has_error_signal,
    is_prometheus_compatible,
    parse_prometheus_metric_names,
)


def test_parse_prometheus_metric_names_extracts_metric_names() -> None:
    metrics_text = """
# HELP http_requests_total Total requests.
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 42
http_request_duration_seconds_sum{method="GET"} 1.5
"""

    metric_names = parse_prometheus_metric_names(metrics_text)

    assert metric_names == {
        "http_requests_total",
        "http_request_duration_seconds_sum",
    }


def test_is_prometheus_compatible_returns_true_for_metric_samples() -> None:
    metrics_text = "http_requests_total{status=\"200\"} 42\n"

    assert is_prometheus_compatible(metrics_text) is True


def test_is_prometheus_compatible_returns_false_for_empty_text() -> None:
    assert is_prometheus_compatible("") is False


def test_find_metric_name_matches() -> None:
    matches = find_metric_name_matches(
        metric_names={
            "http_requests_total",
            "process_cpu_seconds_total",
        },
        patterns=[
            "^http_requests_total$",
        ],
    )

    assert matches == ["http_requests_total"]


def test_has_error_signal_detects_5xx_label() -> None:
    metrics_text = 'http_requests_total{status="500"} 2\n'

    assert has_error_signal(
        metrics_text=metrics_text,
        metric_names={"http_requests_total"},
        patterns=[],
    ) is True