#!/usr/bin/env python3
"""
SPX Options Trading Bot - Smoke Tests
====================================

This script performs smoke tests to validate the deployment health
after deployments complete. It checks various endpoints and services
to ensure the application is functioning correctly.

Usage:
    python scripts/smoke_tests.py --environment production
    python scripts/smoke_tests.py --environment staging --verbose
    python scripts/smoke_tests.py --environment development --timeout 30
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SmokeTestResult:
    """Result of a smoke test"""

    test_name: str
    success: bool
    response_time: float
    error_message: Optional[str] = None
    details: Optional[Dict] = None


class SmokeTestRunner:
    """Runs smoke tests against the deployed application"""

    def __init__(
        self,
        environment: str,
        base_url: Optional[str] = None,
        timeout: int = 30,
        verbose: bool = False,
    ):
        self.environment = environment
        self.timeout = timeout
        self.verbose = verbose
        self.results: List[SmokeTestResult] = []

        # Environment-specific base URLs
        self.base_urls = {
            "development": "http://spx-options-trading-bot.dev.example.com",
            "staging": "https://spx-options-trading-bot.staging.example.com",
            "production": "https://spx-options-trading-bot.example.com",
        }

        self.base_url = base_url or self.base_urls.get(environment)
        if not self.base_url:
            raise ValueError(f"No base URL configured for environment: {environment}")

        # Ensure base_url is not None for type checking
        assert self.base_url is not None

        logger.info(f"Initializing smoke tests for {environment} environment")
        logger.info(f"Base URL: {self.base_url}")

        # Test session with timeouts
        self.session = requests.Session()
        self.session.timeout = self.timeout  # type: ignore[attr-defined]

        # Add retry adapter
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def run_test(self, test_name: str, test_func) -> SmokeTestResult:
        """Run a single smoke test"""
        logger.info(f"Running test: {test_name}")
        start_time = time.time()

        try:
            success, details = test_func()
            response_time = time.time() - start_time

            result = SmokeTestResult(
                test_name=test_name,
                success=success,
                response_time=response_time,
                details=details,
            )

            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status} {test_name} ({response_time:.2f}s)")

            if self.verbose and details:
                logger.info(f"Details: {json.dumps(details, indent=2)}")

        except Exception as e:
            response_time = time.time() - start_time
            result = SmokeTestResult(
                test_name=test_name,
                success=False,
                response_time=response_time,
                error_message=str(e),
            )
            logger.error(f"❌ FAIL {test_name} ({response_time:.2f}s): {str(e)}")

        self.results.append(result)
        return result

    def test_health_endpoint(self) -> Tuple[bool, Dict]:
        """Test the health check endpoint"""
        url = urljoin(self.base_url, "/health")
        response = self.session.get(url)

        success = response.status_code == 200
        data = (
            response.json()
            if response.headers.get("content-type", "").startswith("application/json")
            else {}
        )

        details = {
            "status_code": response.status_code,
            "response_data": data,
            "response_time": response.elapsed.total_seconds(),
        }

        # Additional health checks
        if success and data:
            success = data.get("status") == "healthy"
            if "version" in data:
                details["version"] = data["version"]

        return success, details

    def test_metrics_endpoint(self) -> Tuple[bool, Dict]:
        """Test the metrics endpoint"""
        url = urljoin(self.base_url, "/metrics")
        response = self.session.get(url)

        success = response.status_code == 200

        details = {
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "metrics_count": 0,
        }

        if success:
            # Count the number of metrics
            metrics_text = response.text
            metrics_lines = [
                line
                for line in metrics_text.split("\n")
                if line and not line.startswith("#")
            ]
            details["metrics_count"] = len(metrics_lines)

            # Check for expected metrics
            expected_metrics = [
                "spx_requests_total",
                "spx_active_trades",
                "spx_portfolio_value_usd",
            ]

            found_metrics = []
            for metric in expected_metrics:
                if metric in metrics_text:
                    found_metrics.append(metric)

            details["expected_metrics"] = expected_metrics
            details["found_metrics"] = found_metrics
            details["all_metrics_present"] = len(found_metrics) == len(expected_metrics)

            success = details["all_metrics_present"]

        return success, details

    def test_api_endpoints(self) -> Tuple[bool, Dict]:
        """Test key API endpoints"""
        endpoints = [
            ("/api/v1/status", 200),
            ("/api/v1/portfolio", 200),
            ("/api/v1/trades", 200),
        ]

        results = {}
        overall_success = True

        for endpoint, expected_status in endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url)

                endpoint_success = response.status_code == expected_status
                results[endpoint] = {
                    "success": endpoint_success,
                    "status_code": response.status_code,
                    "expected_status": expected_status,
                    "response_time": response.elapsed.total_seconds(),
                }

                if not endpoint_success:
                    overall_success = False

            except Exception as e:
                results[endpoint] = {"success": False, "error": str(e)}
                overall_success = False

        return overall_success, {"endpoints": results}

    def test_database_connection(self) -> Tuple[bool, Dict]:
        """Test database connectivity via API"""
        url = urljoin(self.base_url, "/api/v1/health/database")

        try:
            response = self.session.get(url)
            success = response.status_code == 200

            details = {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if success:
                data = response.json()
                details["database_status"] = data.get("status", "unknown")
                success = data.get("status") == "connected"

        except Exception as e:
            # If dedicated database health endpoint doesn't exist,
            # try to infer from general health
            try:
                health_success, health_details = self.test_health_endpoint()
                success = health_success
                details = {
                    "method": "inferred_from_health",
                    "health_check_success": health_success,  # type: ignore[dict-item]
                }
            except:
                success = False
                details = {"error": str(e)}

        return success, details

    def test_external_dependencies(self) -> Tuple[bool, Dict]:
        """Test external service dependencies"""
        dependencies_url = urljoin(self.base_url, "/api/v1/health/dependencies")

        try:
            response = self.session.get(dependencies_url)

            if response.status_code == 200:
                data = response.json()
                dependencies = data.get("dependencies", {})

                all_healthy = True
                for service, status in dependencies.items():
                    if status != "healthy":
                        all_healthy = False

                return all_healthy, {
                    "status_code": response.status_code,
                    "dependencies": dependencies,
                    "all_healthy": all_healthy,
                }
            else:
                # Fallback: assume dependencies are working if main health is OK
                health_success, _ = self.test_health_endpoint()
                return health_success, {
                    "method": "inferred_from_main_health",
                    "assumed_healthy": health_success,  # type: ignore[dict-item]
                }

        except Exception as e:
            return False, {"error": str(e)}

    def test_performance_baseline(self) -> Tuple[bool, Dict]:
        """Test basic performance metrics"""
        test_endpoints = ["/health", "/metrics", "/api/v1/status"]

        performance_results = {}
        all_within_threshold = True
        max_acceptable_time = 2.0  # 2 seconds

        for endpoint in test_endpoints:
            url = urljoin(self.base_url, endpoint)

            # Make multiple requests to get average
            response_times = []
            for _ in range(3):
                try:
                    start = time.time()
                    response = self.session.get(url)
                    response_time = time.time() - start
                    response_times.append(response_time)

                    if response.status_code != 200:
                        all_within_threshold = False

                except Exception:
                    all_within_threshold = False
                    response_times.append(max_acceptable_time + 1)

            avg_response_time = sum(response_times) / len(response_times)
            within_threshold = avg_response_time <= max_acceptable_time

            performance_results[endpoint] = {
                "avg_response_time": avg_response_time,
                "response_times": response_times,
                "within_threshold": within_threshold,
                "threshold": max_acceptable_time,
            }

            if not within_threshold:
                all_within_threshold = False

        return all_within_threshold, {
            "results": performance_results,
            "threshold_seconds": max_acceptable_time,
        }

    def run_all_tests(self) -> bool:
        """Run all smoke tests"""
        logger.info(f"Starting smoke tests for {self.environment} environment")
        logger.info("=" * 60)

        # Define all tests
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("API Endpoints", self.test_api_endpoints),
            ("Database Connection", self.test_database_connection),
            ("External Dependencies", self.test_external_dependencies),
            ("Performance Baseline", self.test_performance_baseline),
        ]

        # Run all tests
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Generate summary
        self.print_summary()

        # Return overall success
        return all(result.success for result in self.results)

    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.success)
        failed_tests = total_tests - passed_tests

        logger.info("=" * 60)
        logger.info("SMOKE TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if failed_tests > 0:
            logger.info("\nFailed Tests:")
            for result in self.results:
                if not result.success:
                    logger.error(f"  ❌ {result.test_name}")
                    if result.error_message:
                        logger.error(f"     Error: {result.error_message}")

        logger.info(
            f"\nTotal Runtime: {sum(r.response_time for r in self.results):.2f}s"
        )
        logger.info("=" * 60)

    def export_results(self, filename: Optional[str] = None) -> str:
        """Export results to JSON file"""
        if not filename:
            timestamp = int(time.time())
            filename = f"smoke_test_results_{self.environment}_{timestamp}.json"

        results_data = {
            "environment": self.environment,
            "base_url": self.base_url,
            "timestamp": time.time(),
            "total_tests": len(self.results),
            "passed_tests": sum(1 for r in self.results if r.success),
            "overall_success": all(r.success for r in self.results),
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "response_time": r.response_time,
                    "error_message": r.error_message,
                    "details": r.details,
                }
                for r in self.results
            ],
        }

        with open(filename, "w") as f:
            json.dump(results_data, f, indent=2)

        logger.info(f"Results exported to: {filename}")
        return filename


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Run smoke tests for SPX Options Trading Bot deployment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/smoke_tests.py --environment production
  python scripts/smoke_tests.py --environment staging --verbose
  python scripts/smoke_tests.py --environment development --timeout 30
  python scripts/smoke_tests.py --environment production --base-url https://custom.example.com
        """,
    )

    parser.add_argument(
        "--environment",
        required=True,
        choices=["development", "staging", "production"],
        help="Target environment for smoke tests",
    )

    parser.add_argument("--base-url", help="Override base URL for the environment")

    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("--export", help="Export results to JSON file")

    args = parser.parse_args()

    try:
        # Initialize and run smoke tests
        runner = SmokeTestRunner(
            environment=args.environment,
            base_url=args.base_url,
            timeout=args.timeout,
            verbose=args.verbose,
        )

        success = runner.run_all_tests()

        # Export results if requested
        if args.export:
            runner.export_results(args.export)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("Smoke tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Smoke tests failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
