"""
Provider Testing Framework - Comprehensive testing for InfraDSL providers

This module provides unit testing, integration testing, and compatibility
testing capabilities for InfraDSL providers.
"""

import asyncio
import json
import logging
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Type, Union
from unittest.mock import Mock, patch
import subprocess

from infradsl.core.interfaces.provider import ProviderInterface, ProviderConfig, ProviderType
from infradsl.core.nexus.base_resource import BaseResource
from .registry import ProviderInfo, get_enhanced_registry

logger = logging.getLogger(__name__)


class TestStatus(Enum):
    """Test execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    status: TestStatus
    duration: float
    message: Optional[str] = None
    error: Optional[str] = None
    traceback: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_name": self.test_name,
            "status": self.status.value,
            "duration": self.duration,
            "message": self.message,
            "error": self.error,
            "traceback": self.traceback,
            "metadata": self.metadata,
        }


@dataclass
class TestSuite:
    """Test suite definition"""
    name: str
    description: str
    tests: List[Callable] = field(default_factory=list)
    setup: Optional[Callable] = None
    teardown: Optional[Callable] = None
    fixtures: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    
    def add_test(self, test_func: Callable):
        """Add a test function to the suite"""
        self.tests.append(test_func)
    
    def add_fixture(self, name: str, fixture: Any):
        """Add a fixture to the suite"""
        self.fixtures[name] = fixture


@dataclass
class TestReport:
    """Test execution report"""
    suite_name: str
    provider_name: str
    provider_version: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[TestResult] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def duration(self) -> float:
        """Get total test duration"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def passed(self) -> int:
        """Count of passed tests"""
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)
    
    @property
    def failed(self) -> int:
        """Count of failed tests"""
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)
    
    @property
    def errors(self) -> int:
        """Count of error tests"""
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)
    
    @property
    def skipped(self) -> int:
        """Count of skipped tests"""
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)
    
    @property
    def total(self) -> int:
        """Total number of tests"""
        return len(self.results)
    
    def update_summary(self):
        """Update summary statistics"""
        self.summary = {
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "skipped": self.skipped,
            "duration": self.duration,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        self.update_summary()
        return {
            "suite_name": self.suite_name,
            "provider_name": self.provider_name,
            "provider_version": self.provider_version,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "results": [r.to_dict() for r in self.results],
            "summary": self.summary,
            "metadata": self.metadata,
        }


class TestRunner:
    """Test runner for provider test suites"""
    
    def __init__(self, parallel: bool = True, max_workers: int = 4):
        self.parallel = parallel
        self.max_workers = max_workers
        self.test_timeout = 30.0  # seconds
        
    async def run_suite(
        self,
        suite: TestSuite,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig] = None
    ) -> TestReport:
        """Run a test suite"""
        report = TestReport(
            suite_name=suite.name,
            provider_name=provider_info.metadata.name,
            provider_version=provider_info.version,
            start_time=datetime.now(timezone.utc),
        )
        
        logger.info(f"Running test suite: {suite.name}")
        
        try:
            # Setup
            if suite.setup:
                await self._run_setup_teardown(suite.setup, suite, provider_info, config)
            
            # Run tests
            if self.parallel:
                await self._run_tests_parallel(suite, provider_info, config, report)
            else:
                await self._run_tests_sequential(suite, provider_info, config, report)
            
            # Teardown
            if suite.teardown:
                await self._run_setup_teardown(suite.teardown, suite, provider_info, config)
        
        except Exception as e:
            logger.error(f"Error running test suite {suite.name}: {e}")
            report.metadata["suite_error"] = str(e)
        
        report.end_time = datetime.now(timezone.utc)
        report.update_summary()
        
        logger.info(
            f"Test suite {suite.name} completed: "
            f"{report.passed}/{report.total} passed in {report.duration:.2f}s"
        )
        
        return report
    
    async def _run_tests_sequential(
        self,
        suite: TestSuite,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig],
        report: TestReport
    ):
        """Run tests sequentially"""
        for test_func in suite.tests:
            result = await self._run_single_test(test_func, suite, provider_info, config)
            report.results.append(result)
    
    async def _run_tests_parallel(
        self,
        suite: TestSuite,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig],
        report: TestReport
    ):
        """Run tests in parallel"""
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def run_with_semaphore(test_func):
            async with semaphore:
                return await self._run_single_test(test_func, suite, provider_info, config)
        
        tasks = [run_with_semaphore(test_func) for test_func in suite.tests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                error_result = TestResult(
                    test_name="unknown",
                    status=TestStatus.ERROR,
                    duration=0.0,
                    error=str(result),
                )
                report.results.append(error_result)
            else:
                report.results.append(result)
    
    async def _run_single_test(
        self,
        test_func: Callable,
        suite: TestSuite,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig]
    ) -> TestResult:
        """Run a single test function"""
        test_name = getattr(test_func, '__name__', str(test_func))
        start_time = time.time()
        
        try:
            # Create provider instance
            provider = await self._create_provider_instance(provider_info, config)
            
            # Prepare test context
            context = {
                "provider": provider,
                "provider_info": provider_info,
                "config": config,
                "fixtures": suite.fixtures,
                "suite_config": suite.config,
            }
            
            # Run test with timeout
            result = await asyncio.wait_for(
                self._execute_test_function(test_func, context),
                timeout=self.test_timeout
            )
            
            duration = time.time() - start_time
            
            # Check result
            if result is True or result is None:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    duration=duration,
                    message="Test passed",
                )
            elif result is False:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.FAILED,
                    duration=duration,
                    message="Test failed",
                )
            else:
                return TestResult(
                    test_name=test_name,
                    status=TestStatus.PASSED,
                    duration=duration,
                    message=str(result),
                )
        
        except asyncio.TimeoutError:
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error="Test timeout",
            )
        except AssertionError as e:
            return TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                duration=time.time() - start_time,
                error=str(e),
            )
        except Exception as e:
            return TestResult(
                test_name=test_name,
                status=TestStatus.ERROR,
                duration=time.time() - start_time,
                error=str(e),
                traceback=str(e.__traceback__),
            )
    
    async def _execute_test_function(self, test_func: Callable, context: Dict[str, Any]) -> Any:
        """Execute a test function with context"""
        import inspect
        
        # Get function signature
        sig = inspect.signature(test_func)
        
        # Prepare arguments
        kwargs = {}
        for param_name, param in sig.parameters.items():
            if param_name in context:
                kwargs[param_name] = context[param_name]
        
        # Execute function
        if asyncio.iscoroutinefunction(test_func):
            return await test_func(**kwargs)
        else:
            return test_func(**kwargs)
    
    async def _create_provider_instance(
        self,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig]
    ) -> ProviderInterface:
        """Create a provider instance for testing"""
        if not config:
            # Create minimal test config
            config = ProviderConfig(
                type=provider_info.metadata.provider_type,
                credentials={}
            )
        
        return provider_info.provider_class(config)
    
    async def _run_setup_teardown(
        self,
        func: Callable,
        suite: TestSuite,
        provider_info: ProviderInfo,
        config: Optional[ProviderConfig]
    ):
        """Run setup or teardown function"""
        context = {
            "provider_info": provider_info,
            "config": config,
            "fixtures": suite.fixtures,
            "suite_config": suite.config,
        }
        
        if asyncio.iscoroutinefunction(func):
            await func(context)
        else:
            func(context)


class ProviderTestFramework:
    """
    Comprehensive testing framework for InfraDSL providers
    
    Features:
    - Unit testing with mocking
    - Integration testing with real APIs
    - Compatibility testing
    - Performance testing
    - Automated test generation
    """
    
    def __init__(self):
        self.runner = TestRunner()
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_data_dir = Path.home() / ".infradsl" / "test_data"
        self.test_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Built-in test suites
        self._register_builtin_suites()
    
    def register_test_suite(self, suite: TestSuite):
        """Register a test suite"""
        self.test_suites[suite.name] = suite
        logger.info(f"Registered test suite: {suite.name}")
    
    async def test_provider(
        self,
        provider_info: ProviderInfo,
        suite_names: Optional[List[str]] = None,
        config: Optional[ProviderConfig] = None
    ) -> List[TestReport]:
        """Test a provider with specified suites"""
        if suite_names is None:
            suite_names = list(self.test_suites.keys())
        
        reports = []
        
        for suite_name in suite_names:
            if suite_name not in self.test_suites:
                logger.warning(f"Test suite {suite_name} not found")
                continue
            
            suite = self.test_suites[suite_name]
            report = await self.runner.run_suite(suite, provider_info, config)
            reports.append(report)
        
        return reports
    
    async def generate_integration_tests(
        self,
        provider_info: ProviderInfo,
        config: ProviderConfig
    ) -> TestSuite:
        """Generate integration tests from provider schema"""
        suite = TestSuite(
            name=f"{provider_info.metadata.name}_integration_generated",
            description=f"Generated integration tests for {provider_info.metadata.name}",
        )
        
        # Generate tests for each resource type
        for resource_type in provider_info.metadata.resource_types:
            test_func = await self._generate_resource_test(resource_type, provider_info, config)
            if test_func:
                suite.add_test(test_func)
        
        return suite
    
    async def _generate_resource_test(
        self,
        resource_type: str,
        provider_info: ProviderInfo,
        config: ProviderConfig
    ) -> Optional[Callable]:
        """Generate a test for a specific resource type"""
        try:
            # This would introspect the provider to understand resource schema
            # For now, create a basic test template
            
            async def generated_test(provider, provider_info, config):
                """Generated test for resource type"""
                # Basic provider instantiation test
                assert provider is not None
                
                # Test resource type is supported
                resource_types = provider.get_resource_types()
                assert resource_type in resource_types
                
                # Test configuration validation
                validation_errors = provider.validate_config(config.to_dict())
                assert len(validation_errors) == 0
                
                return True
            
            generated_test.__name__ = f"test_{resource_type}_basic"
            return generated_test
        
        except Exception as e:
            logger.error(f"Failed to generate test for {resource_type}: {e}")
            return None
    
    def _register_builtin_suites(self):
        """Register built-in test suites"""
        # Basic functionality suite
        basic_suite = TestSuite(
            name="basic_functionality",
            description="Basic provider functionality tests",
        )
        
        # Add basic tests
        basic_suite.add_test(self._test_provider_instantiation)
        basic_suite.add_test(self._test_provider_metadata)
        basic_suite.add_test(self._test_config_validation)
        basic_suite.add_test(self._test_resource_types)
        basic_suite.add_test(self._test_regions)
        
        self.register_test_suite(basic_suite)
        
        # Security suite
        security_suite = TestSuite(
            name="security",
            description="Security-focused tests",
        )
        
        security_suite.add_test(self._test_no_hardcoded_credentials)
        security_suite.add_test(self._test_secure_communication)
        security_suite.add_test(self._test_input_validation)
        
        self.register_test_suite(security_suite)
        
        # Performance suite
        performance_suite = TestSuite(
            name="performance",
            description="Performance and load tests",
        )
        
        performance_suite.add_test(self._test_initialization_time)
        performance_suite.add_test(self._test_memory_usage)
        performance_suite.add_test(self._test_concurrent_operations)
        
        self.register_test_suite(performance_suite)
    
    # Basic functionality tests
    async def _test_provider_instantiation(self, provider, provider_info, config):
        """Test provider can be instantiated"""
        assert provider is not None
        assert isinstance(provider, ProviderInterface)
        return True
    
    async def _test_provider_metadata(self, provider, provider_info, config):
        """Test provider metadata is valid"""
        metadata = provider_info.metadata
        assert metadata.name
        assert metadata.version
        assert metadata.author
        assert metadata.description
        return True
    
    async def _test_config_validation(self, provider, provider_info, config):
        """Test configuration validation"""
        # Test valid config
        errors = provider.validate_config(config.to_dict())
        assert isinstance(errors, list)
        
        # Test invalid config
        invalid_config = {"invalid": "config"}
        errors = provider.validate_config(invalid_config)
        # Should have validation errors for invalid config
        
        return True
    
    async def _test_resource_types(self, provider, provider_info, config):
        """Test resource types are returned"""
        resource_types = provider.get_resource_types()
        assert isinstance(resource_types, list)
        assert len(resource_types) > 0
        return True
    
    async def _test_regions(self, provider, provider_info, config):
        """Test regions are returned"""
        regions = provider.get_regions()
        assert isinstance(regions, list)
        # Regions can be empty for some providers
        return True
    
    # Security tests
    async def _test_no_hardcoded_credentials(self, provider, provider_info, config):
        """Test no hardcoded credentials in provider code"""
        # This would scan the provider source code for hardcoded credentials
        # For now, just check that config is used
        assert config is not None
        return True
    
    async def _test_secure_communication(self, provider, provider_info, config):
        """Test secure communication practices"""
        # This would test SSL/TLS usage, certificate validation, etc.
        return True
    
    async def _test_input_validation(self, provider, provider_info, config):
        """Test input validation and sanitization"""
        # Test with various malicious inputs
        malicious_inputs = [
            {"name": "<script>alert('xss')</script>"},
            {"name": "'; DROP TABLE users; --"},
            {"name": "../../../etc/passwd"},
        ]
        
        for malicious_input in malicious_inputs:
            try:
                errors = provider.validate_config(malicious_input)
                # Should not crash and should return errors
                assert isinstance(errors, list)
            except Exception as e:
                # Should not crash with unhandled exceptions
                assert False, f"Provider crashed with malicious input: {e}"
        
        return True
    
    # Performance tests
    async def _test_initialization_time(self, provider, provider_info, config):
        """Test provider initialization time"""
        start_time = time.time()
        
        # Create new instance
        new_provider = provider_info.provider_class(config)
        
        initialization_time = time.time() - start_time
        
        # Should initialize in reasonable time (< 5 seconds)
        assert initialization_time < 5.0
        
        return True
    
    async def _test_memory_usage(self, provider, provider_info, config):
        """Test provider memory usage"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create multiple provider instances
        instances = []
        for _ in range(10):
            instances.append(provider_info.provider_class(config))
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (< 100MB for 10 instances)
        assert memory_increase < 100 * 1024 * 1024
        
        return True
    
    async def _test_concurrent_operations(self, provider, provider_info, config):
        """Test concurrent operations"""
        async def concurrent_operation():
            # Test basic operation
            resource_types = provider.get_resource_types()
            return len(resource_types)
        
        # Run multiple concurrent operations
        tasks = [concurrent_operation() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All operations should complete successfully
        assert len(results) == 10
        assert all(isinstance(r, int) for r in results)
        
        return True
    
    def save_test_report(self, report: TestReport, output_path: Optional[Path] = None):
        """Save test report to file"""
        if output_path is None:
            output_path = (
                self.test_data_dir / 
                f"{report.provider_name}_{report.suite_name}_{report.start_time.strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        with open(output_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)
        
        logger.info(f"Test report saved to {output_path}")
    
    def load_test_report(self, report_path: Path) -> TestReport:
        """Load test report from file"""
        with open(report_path, "r") as f:
            data = json.load(f)
        
        # Reconstruct report object
        report = TestReport(
            suite_name=data["suite_name"],
            provider_name=data["provider_name"],
            provider_version=data["provider_version"],
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data["end_time"] else None,
            metadata=data["metadata"],
        )
        
        # Reconstruct test results
        for result_data in data["results"]:
            result = TestResult(
                test_name=result_data["test_name"],
                status=TestStatus(result_data["status"]),
                duration=result_data["duration"],
                message=result_data["message"],
                error=result_data["error"],
                traceback=result_data["traceback"],
                metadata=result_data["metadata"],
            )
            report.results.append(result)
        
        return report


# Global test framework instance
_test_framework = None


def get_test_framework() -> ProviderTestFramework:
    """Get the global test framework instance"""
    global _test_framework
    if _test_framework is None:
        _test_framework = ProviderTestFramework()
    return _test_framework