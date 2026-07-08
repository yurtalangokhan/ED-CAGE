from ed_cage.ports.tool_adapter import ToolAdapter


class ToolAdapterRegistry:
    def __init__(self, adapters: list[ToolAdapter] | None = None) -> None:
        self._adapters: dict[str, ToolAdapter] = {}

        for adapter in adapters or []:
            self.register(adapter)

    @classmethod
    def default(cls) -> "ToolAdapterRegistry":
        from ed_cage.adapters.tools.kube_linter_tool_adapter import (
            KubeLinterToolAdapter,
        )
        from ed_cage.adapters.tools.opa_tool_adapter import OpaToolAdapter
        from ed_cage.adapters.tools.trivy_tool_adapter import TrivyToolAdapter

        return cls(
            adapters=[
                OpaToolAdapter(),
                KubeLinterToolAdapter(),
                TrivyToolAdapter(),
            ]
        )

    def register(self, adapter: ToolAdapter) -> None:
        normalized_name = self._normalize_tool_name(adapter.tool_name)

        if normalized_name in self._adapters:
            raise ValueError(f"Duplicate tool adapter registered: {adapter.tool_name}")

        self._adapters[normalized_name] = adapter

    def get(self, tool_name: str) -> ToolAdapter | None:
        return self._adapters.get(self._normalize_tool_name(tool_name))

    def names(self) -> list[str]:
        return sorted(self._adapters)

    def _normalize_tool_name(self, tool_name: str) -> str:
        return tool_name.strip().lower()