import asyncio
from typing import Any
from unittest.mock import Mock

from src.agent.plugins.models import CapabilityContext, CapabilityInfo, CapabilityResult


class MockTask:
    """Mock A2A Task for testing."""

    def __init__(self, user_input: str = "", task_id: str = "test-123"):
        """Initialize mock task."""
        self.id = task_id
        self.history = [Mock(parts=[Mock(text=user_input)])]
        self.metadata = {}


class PluginTestCase:
    """Base test case for plugin testing."""

    def create_context(
        self,
        user_input: str = "",
        config: dict[str, Any] | None = None,
        services: dict[str, Any] | None = None,
        state: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> CapabilityContext:
        """Create a test context."""
        task = MockTask(user_input)
        return CapabilityContext(
            task=task,
            config=config or {},
            services=services or {},
            state=state or {},
            metadata=metadata or {},
        )

    def assert_capability_info_valid(self, capability_info: CapabilityInfo) -> None:
        """Assert that skill info is valid."""
        assert isinstance(capability_info, CapabilityInfo)
        assert capability_info.id
        assert capability_info.name
        assert capability_info.version
        assert isinstance(capability_info.capabilities, list)

    def assert_result_success(self, result: CapabilityResult) -> None:
        """Assert that a skill result indicates success."""
        assert isinstance(result, CapabilityResult)
        assert result.success
        assert result.content
        assert result.error is None

    def assert_result_failure(self, result: CapabilityResult) -> None:
        """Assert that a skill result indicates failure."""
        assert isinstance(result, CapabilityResult)
        assert not result.success
        assert result.error is not None


class PluginTestRunner:
    """Test runner for plugins."""

    def __init__(self, plugin_class):
        """Initialize test runner."""
        self.plugin_class = plugin_class
        self.plugin = None

    def setup(self) -> None:
        """Set up the plugin for testing."""
        self.plugin = self.plugin_class()

    def teardown(self) -> None:
        """Clean up after testing."""
        self.plugin = None

    def test_registration(self) -> bool:
        """Test plugin registration."""
        try:
            capability_info = self.plugin.register_capability()
            assert isinstance(capability_info, CapabilityInfo)
            assert capability_info.id
            assert capability_info.name
            return True
        except Exception as e:
            print(f"Registration test failed: {e}")
            return False

    def test_validation(self, test_configs: list[dict[str, Any]]) -> bool:
        """Test configuration validation."""
        try:
            for config in test_configs:
                result = self.plugin.validate_config(config)
                # Just check it returns a result, not whether it's valid
                assert hasattr(result, "valid")
            return True
        except Exception as e:
            print(f"Validation test failed: {e}")
            return False

    def test_execution(self, test_inputs: list[str]) -> bool:
        """Test skill execution."""
        try:
            for user_input in test_inputs:
                task = MockTask(user_input)
                context = CapabilityContext(task=task)
                result = self.plugin.execute_capability(context)
                assert isinstance(result, CapabilityResult)
            return True
        except Exception as e:
            print(f"Execution test failed: {e}")
            return False

    def test_routing(self, test_cases: list[tuple[str, bool | float]]) -> bool:
        """Test skill routing."""
        try:
            for user_input, expected in test_cases:
                task = MockTask(user_input)
                context = CapabilityContext(task=task)
                result = self.plugin.can_handle_task(context)

                if isinstance(expected, bool):
                    assert bool(result) == expected
                else:
                    # For float expectations, check within tolerance
                    assert abs(float(result) - expected) < 0.01
            return True
        except Exception as e:
            print(f"Routing test failed: {e}")
            return False

    def run_all_tests(self) -> dict[str, bool]:
        """Run all tests and return results."""
        self.setup()

        results = {
            "registration": self.test_registration(),
            "validation": self.test_validation([{}, {"test": "config"}]),
            "execution": self.test_execution(["test input", "another test"]),
            "routing": self.test_routing([("test", True), ("unrelated", False)]),
        }

        self.teardown()
        return results


def create_test_plugin(skill_id: str, name: str) -> type:
    """Create a simple test plugin class."""

    class TestPlugin:
        def register_capability(self) -> CapabilityInfo:
            return CapabilityInfo(
                id=skill_id,
                name=name,
                version="1.0.0",
                description=f"Test plugin: {name}",
                capabilities=["text"],
            )

        def validate_config(self, config: dict) -> Any:
            from src.agent.plugins.models import ValidationResult

            return ValidationResult(valid=True)

        def can_handle_task(self, context: CapabilityContext) -> bool:
            return True

        def execute_capability(self, context: CapabilityContext) -> CapabilityResult:
            return CapabilityResult(
                content=f"Executed {skill_id}",
                success=True,
            )

    return TestPlugin


async def test_plugin_async(plugin_instance) -> dict[str, Any]:
    """Test a plugin with async methods."""
    results = {}

    # Test registration
    try:
        capability_info = plugin_instance.register_capability()
        results["registration"] = {
            "success": True,
            "capability_id": capability_info.id,
            "capability_name": capability_info.name,
        }
    except Exception as e:
        results["registration"] = {
            "success": False,
            "error": str(e),
        }

    # Test execution with various inputs
    test_inputs = [
        "Hello, plugin!",
        "Test message",
        "Complex query with multiple parts",
    ]

    execution_results = []
    for user_input in test_inputs:
        try:
            task = MockTask(user_input)
            context = CapabilityContext(task=task)

            # Handle both sync and async execute methods
            if asyncio.iscoroutinefunction(plugin_instance.execute_capability):
                result = await plugin_instance.execute_capability(context)
            else:
                result = plugin_instance.execute_capability(context)

            execution_results.append(
                {
                    "input": user_input,
                    "success": result.success,
                    "output": result.content[:100],  # Truncate for display
                }
            )
        except Exception as e:
            execution_results.append(
                {
                    "input": user_input,
                    "success": False,
                    "error": str(e),
                }
            )

    results["execution"] = execution_results

    # Test AI functions if available
    if hasattr(plugin_instance, "get_ai_functions"):
        try:
            ai_functions = plugin_instance.get_ai_functions()
            results["ai_functions"] = {
                "count": len(ai_functions),
                "names": [f.name for f in ai_functions],
            }
        except Exception as e:
            results["ai_functions"] = {
                "error": str(e),
            }

    return results
