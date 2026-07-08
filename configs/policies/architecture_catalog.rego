package ed_cage.architecture

import rego.v1

critical_services := object.get(input, "critical_services", [])
services := object.get(input, "services", [])

service_names := {service.name | some service in services}

service_by_name := {service.name: service | some service in services}

deny contains reason if {
	count(critical_services) == 0

	reason := {
		"code": "critical_services_missing",
		"message": "Architecture catalog must declare at least one critical service.",
		"resource": "critical_services",
	}
}

deny contains reason if {
	some critical_service in critical_services
	not critical_service in service_names

	reason := {
		"code": "critical_service_not_declared",
		"message": sprintf("Critical service is not declared in services: %s.", [critical_service]),
		"resource": critical_service,
	}
}

deny contains reason if {
	some service in services
	object.get(service, "owner", "") == ""

	reason := {
		"code": "service_owner_missing",
		"message": sprintf("Service owner is missing: %s.", [service.name]),
		"resource": service.name,
	}
}

deny contains reason if {
	some service in services
	object.get(service, "criticality", "") == ""

	reason := {
		"code": "service_criticality_missing",
		"message": sprintf("Service criticality is missing: %s.", [service.name]),
		"resource": service.name,
	}
}

deny contains reason if {
	some service in services
	object.get(service, "dependencies", null) == null

	reason := {
		"code": "dependencies_field_missing",
		"message": sprintf("Service must explicitly declare dependencies field: %s.", [service.name]),
		"resource": service.name,
	}
}

deny contains reason if {
	some service in services
	some dependency in object.get(service, "dependencies", [])
	object.get(dependency, "external", false) == true
	object.get(dependency, "owner", "") == ""

	reason := {
		"code": "external_dependency_owner_missing",
		"message": sprintf("External dependency owner is missing: %s -> %s.", [service.name, dependency.name]),
		"resource": sprintf("%s -> %s", [service.name, dependency.name]),
	}
}

deny contains reason if {
	some service in services
	some dependency in object.get(service, "dependencies", [])
	object.get(dependency, "external", false) == true
	not has_non_empty_value(dependency, "sla")

	reason := {
		"code": "external_dependency_sla_missing",
		"message": sprintf("External dependency SLA is missing: %s -> %s.", [service.name, dependency.name]),
		"resource": sprintf("%s -> %s", [service.name, dependency.name]),
	}
}

deny contains reason if {
	some service in services
	some dependency in object.get(service, "dependencies", [])
	object.get(dependency, "external", false) == false
	object.get(dependency, "dependency_type", "") == "service"
	service.name == dependency.name

	reason := {
		"code": "self_dependency_detected",
		"message": sprintf("Service must not depend on itself: %s.", [service.name]),
		"resource": service.name,
	}
}

deny contains reason if {
	some service in services
	some dependency in object.get(service, "dependencies", [])
	object.get(dependency, "external", false) == false
	object.get(dependency, "dependency_type", "") == "service"

	other_service := service_by_name[dependency.name]
	some reverse_dependency in object.get(other_service, "dependencies", [])
	object.get(reverse_dependency, "external", false) == false
	object.get(reverse_dependency, "dependency_type", "") == "service"
	reverse_dependency.name == service.name

	reason := {
		"code": "direct_circular_dependency_detected",
		"message": sprintf("Direct circular dependency detected: %s <-> %s.", [service.name, dependency.name]),
		"resource": sprintf("%s <-> %s", [service.name, dependency.name]),
	}
}

has_non_empty_value(item, key) if {
	value := object.get(item, key, null)
	value != null
	value != ""
}