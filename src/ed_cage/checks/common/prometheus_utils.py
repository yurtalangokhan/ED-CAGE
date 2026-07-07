import re


_PROMETHEUS_SAMPLE_PATTERN = re.compile(
    r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{[^}]*\})?\s+[-+]?(?:\d+(?:\.\d*)?|\.\d+|NaN|Inf|-Inf)(?:\s+\d+)?$"
)


def parse_prometheus_metric_names(metrics_text: str) -> set[str]:
    metric_names: set[str] = set()

    for raw_line in metrics_text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        match = _PROMETHEUS_SAMPLE_PATTERN.match(line)

        if match is not None:
            metric_names.add(match.group(1))

    return metric_names


def is_prometheus_compatible(metrics_text: str) -> bool:
    if not metrics_text.strip():
        return False

    return bool(parse_prometheus_metric_names(metrics_text))


def find_metric_name_matches(
    metric_names: set[str],
    patterns: list[str],
) -> list[str]:
    matches: list[str] = []

    for metric_name in sorted(metric_names):
        for pattern in patterns:
            if re.search(pattern, metric_name):
                matches.append(metric_name)
                break

    return matches


def has_error_signal(
    metrics_text: str,
    metric_names: set[str],
    patterns: list[str],
) -> bool:
    if find_metric_name_matches(metric_names, patterns):
        return True

    status_label_patterns = [
        r'status="5\d\d"',
        r'code="5\d\d"',
        r'response_code="5\d\d"',
        r'outcome="SERVER_ERROR"',
        r'exception="[^"]+"',
    ]

    return any(re.search(pattern, metrics_text) for pattern in status_label_patterns)