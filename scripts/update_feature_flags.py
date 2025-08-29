#!/usr/bin/env python3
"""
SPX Options Trading Bot - Feature Flag Management
===============================================

This script manages feature flags for gradual rollouts and A/B testing.
It integrates with various feature flag services and can be used in
CI/CD pipelines for controlled deployments.

Usage:
    python scripts/update_feature_flags.py --environment production \
        --deployment-id abc123
    python scripts/update_feature_flags.py --environment staging \
        --enable-feature new-algo
    python scripts/update_feature_flags.py --rollback --environment production
"""

import argparse
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FeatureFlag:
    """Represents a feature flag configuration"""

    name: str
    enabled: bool
    percentage: float = 100.0  # Percentage of users to enable for
    environment: str = "all"
    conditions: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class FeatureFlagManager:
    """Manages feature flags across different providers"""

    def __init__(self, environment: str, provider: str = "configcat"):
        self.environment = environment
        self.provider = provider.lower()
        self.deployment_id = None

        # Provider-specific configurations
        self.providers = {
            "configcat": self._init_configcat,
            "launchdarkly": self._init_launchdarkly,
            "split": self._init_split,
            "unleash": self._init_unleash,
            "local": self._init_local,
        }

        if self.provider not in self.providers:
            raise ValueError(f"Unsupported provider: {provider}")

        self.client = self.providers[self.provider]()

        # Default feature flags for SPX Trading Bot
        self.default_flags = {
            "new-trading-algorithm": FeatureFlag(
                name="new-trading-algorithm",
                enabled=False,
                percentage=0.0,
                description="Enable new ML-based trading algorithm",
            ),
            "advanced-risk-management": FeatureFlag(
                name="advanced-risk-management",
                enabled=False,
                percentage=10.0,
                description="Enable advanced risk management features",
            ),
            "real-time-notifications": FeatureFlag(
                name="real-time-notifications",
                enabled=True,
                percentage=100.0,
                description="Enable real-time trading notifications",
            ),
            "paper-trading-mode": FeatureFlag(
                name="paper-trading-mode",
                enabled=True if environment != "production" else False,
                percentage=100.0,
                description="Enable paper trading mode for testing",
            ),
            "enhanced-ui": FeatureFlag(
                name="enhanced-ui",
                enabled=False,
                percentage=25.0,
                description="Enable new enhanced user interface",
            ),
            "api-rate-limiting": FeatureFlag(
                name="api-rate-limiting",
                enabled=True,
                percentage=100.0,
                description="Enable API rate limiting",
            ),
            "maintenance-mode": FeatureFlag(
                name="maintenance-mode",
                enabled=False,
                percentage=0.0,
                description="Enable maintenance mode",
            ),
        }

    def _init_configcat(self):
        """Initialize ConfigCat client"""
        api_key = os.getenv("CONFIGCAT_API_KEY")
        if not api_key:
            logger.warning("ConfigCat API key not found, using mock client")
            return MockFeatureFlagClient()

        try:
            import configcatclient

            return configcatclient.ConfigCatClient(api_key)
        except ImportError:
            logger.warning("ConfigCat client not installed, using mock client")
            return MockFeatureFlagClient()

    def _init_launchdarkly(self):
        """Initialize LaunchDarkly client"""
        sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
        if not sdk_key:
            logger.warning("LaunchDarkly SDK key not found, using mock client")
            return MockFeatureFlagClient()

        try:
            import ldclient

            ldclient.set_config(ldclient.Config(sdk_key=sdk_key))
            return ldclient.get()
        except ImportError:
            logger.warning("LaunchDarkly client not installed, using mock client")
            return MockFeatureFlagClient()

    def _init_split(self):
        """Initialize Split client"""
        api_key = os.getenv("SPLIT_API_KEY")
        if not api_key:
            logger.warning("Split API key not found, using mock client")
            return MockFeatureFlagClient()

        try:
            from splitio import get_factory

            factory = get_factory(api_key)
            return factory.client()
        except ImportError:
            logger.warning("Split client not installed, using mock client")
            return MockFeatureFlagClient()

    def _init_unleash(self):
        """Initialize Unleash client"""
        url = os.getenv("UNLEASH_URL")
        api_key = os.getenv("UNLEASH_API_KEY")

        if not url or not api_key:
            logger.warning("Unleash configuration not found, using mock client")
            return MockFeatureFlagClient()

        try:
            from UnleashClient import UnleashClient

            return UnleashClient(
                url=url,
                app_name="spx-trading-bot",
                custom_headers={"Authorization": api_key},
            )
        except ImportError:
            logger.warning("Unleash client not installed, using mock client")
            return MockFeatureFlagClient()

    def _init_local(self):
        """Initialize local file-based client"""
        return LocalFeatureFlagClient(self.environment)

    def set_deployment_id(self, deployment_id: str) -> None:
        """Set the current deployment ID"""
        self.deployment_id = deployment_id
        logger.info(f"Set deployment ID: {deployment_id}")

    def enable_feature(self, feature_name: str, percentage: float = 100.0) -> bool:
        """Enable a specific feature"""
        logger.info(f"Enabling feature '{feature_name}' at {percentage}%")

        try:
            if self.provider == "local":
                result = self.client.set_flag(feature_name, True, percentage)
                return result  # type: ignore[no-any-return]
            elif self.provider == "configcat":
                # ConfigCat doesn't support programmatic flag updates
                # This would typically be done via their dashboard or Management API
                logger.warning("ConfigCat requires manual flag updates via dashboard")
                return True
            elif self.provider == "launchdarkly":
                # LaunchDarkly would use their REST API for programmatic updates
                return self._update_launchdarkly_flag(feature_name, True, percentage)
            else:
                logger.warning(f"Feature enabling not implemented for {self.provider}")
                return True

        except Exception as e:
            logger.error(f"Failed to enable feature {feature_name}: {str(e)}")
            return False

    def disable_feature(self, feature_name: str) -> bool:
        """Disable a specific feature"""
        logger.info(f"Disabling feature '{feature_name}'")

        try:
            if self.provider == "local":
                result = self.client.set_flag(feature_name, False, 0.0)
                return result  # type: ignore[no-any-return]
            else:
                logger.warning(f"Feature disabling not implemented for {self.provider}")
                return True

        except Exception as e:
            logger.error(f"Failed to disable feature {feature_name}: {str(e)}")
            return False

    def gradual_rollout(
        self,
        feature_name: str,
        target_percentage: float = 100.0,
        step_size: float = 10.0,
        step_delay: int = 300,
    ) -> bool:
        """Gradually roll out a feature"""
        logger.info(
            f"Starting gradual rollout of '{feature_name}' to {target_percentage}%"
        )

        current_percentage = 0.0

        while current_percentage < target_percentage:
            next_percentage = min(current_percentage + step_size, target_percentage)

            logger.info(f"Rolling out '{feature_name}' to {next_percentage}%")

            if not self.enable_feature(feature_name, next_percentage):
                logger.error(
                    f"Failed to update feature '{feature_name}' to {next_percentage}%"
                )
                return False

            current_percentage = next_percentage

            if current_percentage < target_percentage:
                logger.info(f"Waiting {step_delay} seconds before next step...")
                time.sleep(step_delay)

        logger.info(
            f"Gradual rollout of '{feature_name}' completed at {target_percentage}%"
        )
        return True

    def rollback_deployment(self) -> bool:
        """Rollback features to previous safe state"""
        logger.info("Rolling back features to safe state")

        # Define safe rollback state
        rollback_flags = {
            "new-trading-algorithm": False,
            "advanced-risk-management": False,
            "enhanced-ui": False,
            "maintenance-mode": True,  # Enable maintenance mode during rollback
        }

        success = True
        for flag_name, enabled in rollback_flags.items():
            if enabled:
                if not self.enable_feature(flag_name):
                    success = False
            else:
                if not self.disable_feature(flag_name):
                    success = False

        if success:
            logger.info("Feature rollback completed successfully")
        else:
            logger.error("Some features failed to rollback")

        return success

    def deployment_strategy_flags(self, strategy: str) -> bool:
        """Set flags based on deployment strategy"""
        logger.info(f"Applying feature flags for {strategy} deployment")

        strategy_configs = {
            "canary": {
                "new-trading-algorithm": (True, 5.0),
                "advanced-risk-management": (True, 10.0),
                "enhanced-ui": (True, 15.0),
            },
            "blue-green": {
                "new-trading-algorithm": (True, 50.0),
                "advanced-risk-management": (True, 50.0),
                "enhanced-ui": (True, 50.0),
            },
            "rolling": {
                "new-trading-algorithm": (True, 100.0),
                "advanced-risk-management": (True, 25.0),
                "enhanced-ui": (True, 75.0),
            },
        }

        if strategy not in strategy_configs:
            logger.warning(f"No flag configuration for strategy: {strategy}")
            return True

        config = strategy_configs[strategy]
        success = True

        for flag_name, (enabled, percentage) in config.items():
            if enabled:
                if not self.enable_feature(flag_name, percentage):
                    success = False
            else:
                if not self.disable_feature(flag_name):
                    success = False

        return success

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on feature flag service"""
        logger.info("Performing feature flag service health check")

        try:
            if self.provider == "local":
                return self.client.health_check()  # type: ignore[no-any-return]
            else:
                # For external providers, try to fetch a flag
                test_flag = self.get_flag_status("health-check-test")
                return {
                    "status": "healthy",
                    "provider": self.provider,
                    "test_flag_accessible": test_flag is not None,
                }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "provider": self.provider}

    def get_flag_status(self, flag_name: str) -> Optional[bool]:
        """Get current status of a feature flag"""
        try:
            if self.provider == "local":
                return self.client.is_enabled(flag_name)  # type: ignore[no-any-return]
            elif self.provider == "configcat":
                result = self.client.get_value(flag_name, False)
                return result  # type: ignore[no-any-return]
            elif self.provider == "launchdarkly":
                user = {"key": f"deployment-{self.deployment_id}"}
                result = self.client.variation(flag_name, user, False)
                return result  # type: ignore[no-any-return]
            else:
                logger.warning(f"Flag status check not implemented for {self.provider}")
                return None
        except Exception as e:
            logger.error(f"Failed to get flag status for {flag_name}: {str(e)}")
            return None

    def list_all_flags(self) -> Dict[str, Any]:
        """List all feature flags and their current status"""
        logger.info("Listing all feature flags")

        flags_status = {}

        for flag_name in self.default_flags.keys():
            status = self.get_flag_status(flag_name)
            flags_status[flag_name] = {
                "enabled": status,
                "description": self.default_flags[flag_name].description,
            }

        return flags_status

    def _update_launchdarkly_flag(
        self, flag_key: str, enabled: bool, percentage: float
    ) -> bool:
        """Update LaunchDarkly flag via REST API"""
        # This would require the LaunchDarkly Management API
        # Implementation would depend on specific requirements
        logger.info(
            f"Would update LaunchDarkly flag {flag_key}: {enabled} at {percentage}%"
        )
        return True


class MockFeatureFlagClient:
    """Mock client for testing without external dependencies"""

    def __init__(self):
        self.flags = {}

    def set_flag(self, name: str, enabled: bool, percentage: float = 100.0) -> bool:
        self.flags[name] = {"enabled": enabled, "percentage": percentage}
        return True

    def is_enabled(self, name: str) -> bool:
        return self.flags.get(name, {}).get("enabled", False)

    def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock", "flags_count": len(self.flags)}


class LocalFeatureFlagClient:
    """Local file-based feature flag client"""

    def __init__(self, environment: str):
        self.environment = environment
        self.flags_file = f"config/feature_flags_{environment}.json"
        self.flags = self._load_flags()

    def _load_flags(self) -> Dict[str, Any]:
        """Load flags from local file"""
        try:
            if os.path.exists(self.flags_file):
                with open(self.flags_file, "r") as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f"Failed to load flags from {self.flags_file}: {str(e)}")
            return {}

    def _save_flags(self) -> bool:
        """Save flags to local file"""
        try:
            os.makedirs(os.path.dirname(self.flags_file), exist_ok=True)
            with open(self.flags_file, "w") as f:
                json.dump(self.flags, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save flags to {self.flags_file}: {str(e)}")
            return False

    def set_flag(self, name: str, enabled: bool, percentage: float = 100.0) -> bool:
        self.flags[name] = {
            "enabled": enabled,
            "percentage": percentage,
            "updated_at": time.time(),
        }
        return self._save_flags()

    def is_enabled(self, name: str) -> bool:
        return self.flags.get(name, {}).get("enabled", False)

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "local",
            "flags_file": self.flags_file,
            "flags_count": len(self.flags),
        }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Manage feature flags for SPX Options Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/update_feature_flags.py --environment production --deployment-id abc123
  python scripts/update_feature_flags.py --enable-feature \
      new-trading-algorithm --percentage 25
  python scripts/update_feature_flags.py --disable-feature enhanced-ui
  python scripts/update_feature_flags.py --rollout new-algorithm --target 50 --step 10
  python scripts/update_feature_flags.py --rollback --environment production
  python scripts/update_feature_flags.py --list-flags
        """,
    )

    parser.add_argument(
        "--environment",
        required=True,
        choices=["development", "staging", "production"],
        help="Target environment",
    )

    parser.add_argument(
        "--provider",
        default="local",
        choices=["configcat", "launchdarkly", "split", "unleash", "local"],
        help="Feature flag provider (default: local)",
    )

    parser.add_argument("--deployment-id", help="Deployment ID for tracking")

    parser.add_argument("--enable-feature", help="Enable a specific feature flag")

    parser.add_argument("--disable-feature", help="Disable a specific feature flag")

    parser.add_argument(
        "--percentage",
        type=float,
        default=100.0,
        help="Percentage of users for feature rollout (default: 100)",
    )

    parser.add_argument("--rollout", help="Gradually roll out a feature")

    parser.add_argument(
        "--target",
        type=float,
        default=100.0,
        help="Target percentage for gradual rollout (default: 100)",
    )

    parser.add_argument(
        "--step",
        type=float,
        default=10.0,
        help="Step size for gradual rollout (default: 10)",
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=300,
        help="Delay between rollout steps in seconds (default: 300)",
    )

    parser.add_argument(
        "--rollback", action="store_true", help="Rollback features to safe state"
    )

    parser.add_argument(
        "--strategy",
        choices=["canary", "blue-green", "rolling"],
        help="Apply flags for specific deployment strategy",
    )

    parser.add_argument(
        "--list-flags",
        action="store_true",
        help="List all feature flags and their status",
    )

    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Perform health check on feature flag service",
    )

    args = parser.parse_args()

    try:
        # Initialize feature flag manager
        manager = FeatureFlagManager(
            environment=args.environment, provider=args.provider
        )

        if args.deployment_id:
            manager.set_deployment_id(args.deployment_id)

        success = True

        # Execute requested actions
        if args.health_check:
            health = manager.health_check()
            print(json.dumps(health, indent=2))

        elif args.list_flags:
            flags = manager.list_all_flags()
            print(json.dumps(flags, indent=2))

        elif args.enable_feature:
            success = manager.enable_feature(args.enable_feature, args.percentage)

        elif args.disable_feature:
            success = manager.disable_feature(args.disable_feature)

        elif args.rollout:
            success = manager.gradual_rollout(
                args.rollout, args.target, args.step, args.delay
            )

        elif args.rollback:
            success = manager.rollback_deployment()

        elif args.strategy:
            success = manager.deployment_strategy_flags(args.strategy)

        else:
            # Default action: apply deployment-specific flags
            if args.deployment_id:
                logger.info(
                    f"Applying default feature flags for deployment "
                    f"{args.deployment_id}"
                )
                # Apply environment-specific defaults
                if args.environment == "production":
                    success = manager.deployment_strategy_flags("canary")
                elif args.environment == "staging":
                    success = manager.deployment_strategy_flags("blue-green")
                else:
                    success = manager.deployment_strategy_flags("rolling")
            else:
                parser.print_help()
                success = False

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Feature flag management failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
