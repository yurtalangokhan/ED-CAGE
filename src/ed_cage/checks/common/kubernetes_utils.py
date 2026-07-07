from typing import Any

WORKLOAD_KINDS = {
    "Deployment",
    "StatefulSet",
    "DaemonSet",
    "ReplicaSet",
    "ReplicationController",
    "Job",
    "CronJob",
}


def get_manifest_paths(params: dict[str, Any]) -> list[str]:
    raw_paths = params.get(
        "manifest_paths",
        [
            "k8s",
            "kubernetes",
            "deploy",
            "deployments",
            "manifests",
            "examples/kubernetes",
        ],
    )

    if not isinstance(raw_paths, list) or not raw_paths:
        return [
            "k8s",
            "kubernetes",
            "deploy",
            "deployments",
            "manifests",
            "examples/kubernetes",
        ]

    return [str(path) for path in raw_paths]


def get_file_patterns(params: dict[str, Any]) -> list[str]:
    raw_patterns = params.get("file_patterns", ["*.yaml", "*.yml"])

    if not isinstance(raw_patterns, list) or not raw_patterns:
        return ["*.yaml", "*.yml"]

    return [str(pattern) for pattern in raw_patterns]


def get_required_for_kinds(params: dict[str, Any], default: list[str]) -> set[str]:
    raw_kinds = params.get("required_for_kinds", default)

    if not isinstance(raw_kinds, list) or not raw_kinds:
        return set(default)

    return {str(kind) for kind in raw_kinds}


def get_pod_spec(manifest: dict[str, Any]) -> dict[str, Any] | None:
    kind = manifest.get("kind")
    spec = manifest.get("spec")

    if not isinstance(spec, dict):
        return None

    if kind == "CronJob":
        job_template = spec.get("jobTemplate")

        if not isinstance(job_template, dict):
            return None

        job_spec_wrapper = job_template.get("spec")

        if not isinstance(job_spec_wrapper, dict):
            return None

        template = job_spec_wrapper.get("template")

        return _extract_template_spec(template)

    if kind == "Job":
        template = spec.get("template")
        return _extract_template_spec(template)

    template = spec.get("template")
    return _extract_template_spec(template)


def get_containers(pod_spec: dict[str, Any]) -> list[dict[str, Any]]:
    containers = pod_spec.get("containers", [])

    if not isinstance(containers, list):
        return []

    return [container for container in containers if isinstance(container, dict)]


def get_init_containers(pod_spec: dict[str, Any]) -> list[dict[str, Any]]:
    containers = pod_spec.get("initContainers", [])

    if not isinstance(containers, list):
        return []

    return [container for container in containers if isinstance(container, dict)]


def get_all_containers(pod_spec: dict[str, Any]) -> list[dict[str, Any]]:
    return [*get_containers(pod_spec), *get_init_containers(pod_spec)]


def get_container_name(container: dict[str, Any]) -> str:
    return str(container.get("name", "unknown-container"))


def _extract_template_spec(template: object) -> dict[str, Any] | None:
    if not isinstance(template, dict):
        return None

    pod_spec = template.get("spec")

    if not isinstance(pod_spec, dict):
        return None

    return pod_spec