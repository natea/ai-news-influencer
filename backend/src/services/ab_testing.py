"""A/B testing infrastructure for content optimization."""
import random
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel

from src.database.models import ABTest


class VariantType(str, Enum):
    """Types of A/B test variants."""
    POST_STYLE = "post_style"
    HASHTAG_COUNT = "hashtag_count"
    CTA_TYPE = "cta_type"
    POSTING_TIME = "posting_time"
    IMAGE_STYLE = "image_style"


class Variant(BaseModel):
    """A test variant configuration."""
    name: str
    config: dict
    impressions: int = 0
    conversions: int = 0

    @property
    def conversion_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return self.conversions / self.impressions


class ABTestResult(BaseModel):
    """Result of an A/B test."""
    test_id: int
    test_name: str
    variant_a: Variant
    variant_b: Variant
    winner: Optional[str]
    statistical_significance: float
    recommendation: str


class ABTestingService:
    """Service for managing A/B tests."""

    MIN_SAMPLE_SIZE = 100  # Minimum samples per variant
    SIGNIFICANCE_THRESHOLD = 0.95

    def __init__(self):
        self._active_tests: dict[int, ABTest] = {}
        self._variant_data: dict[int, dict[str, Variant]] = {}

    def create_test(
        self,
        name: str,
        variant_type: VariantType,
        variant_a_config: dict,
        variant_b_config: dict
    ) -> ABTest:
        """Create a new A/B test."""
        test_id = len(self._active_tests) + 1

        test = ABTest(
            id=test_id,
            test_name=name,
            variant_a=variant_a_config,
            variant_b=variant_b_config,
            start_date=datetime.utcnow(),
            status="active"
        )

        self._active_tests[test_id] = test
        self._variant_data[test_id] = {
            "A": Variant(name="A", config=variant_a_config),
            "B": Variant(name="B", config=variant_b_config)
        }

        return test

    def get_variant(self, test_id: int) -> tuple[str, dict]:
        """Get a variant for a test (50/50 random assignment)."""
        if test_id not in self._active_tests:
            raise ValueError(f"Test {test_id} not found")

        variant_name = random.choice(["A", "B"])
        variant = self._variant_data[test_id][variant_name]
        variant.impressions += 1

        return variant_name, variant.config

    def record_conversion(self, test_id: int, variant_name: str) -> None:
        """Record a conversion (engagement) for a variant."""
        if test_id in self._variant_data:
            self._variant_data[test_id][variant_name].conversions += 1

    def analyze_test(self, test_id: int) -> ABTestResult:
        """Analyze test results and determine winner."""
        test = self._active_tests.get(test_id)
        if not test:
            raise ValueError(f"Test {test_id} not found")

        variants = self._variant_data[test_id]
        variant_a = variants["A"]
        variant_b = variants["B"]

        # Calculate statistical significance (simplified)
        significance = self._calculate_significance(variant_a, variant_b)

        # Determine winner
        winner = None
        recommendation = "Continue testing - insufficient data"

        if variant_a.impressions >= self.MIN_SAMPLE_SIZE and variant_b.impressions >= self.MIN_SAMPLE_SIZE:
            if significance >= self.SIGNIFICANCE_THRESHOLD:
                if variant_a.conversion_rate > variant_b.conversion_rate:
                    winner = "A"
                    recommendation = f"Variant A wins with {variant_a.conversion_rate:.2%} vs {variant_b.conversion_rate:.2%}"
                else:
                    winner = "B"
                    recommendation = f"Variant B wins with {variant_b.conversion_rate:.2%} vs {variant_a.conversion_rate:.2%}"
            else:
                recommendation = "No significant difference detected"

        return ABTestResult(
            test_id=test_id,
            test_name=test.test_name,
            variant_a=variant_a,
            variant_b=variant_b,
            winner=winner,
            statistical_significance=significance,
            recommendation=recommendation
        )

    def _calculate_significance(self, a: Variant, b: Variant) -> float:
        """Calculate statistical significance using simplified z-test."""
        if a.impressions == 0 or b.impressions == 0:
            return 0.0

        # Pooled proportion
        p_pool = (a.conversions + b.conversions) / (a.impressions + b.impressions)

        if p_pool == 0 or p_pool == 1:
            return 0.0

        # Standard error
        se = (p_pool * (1 - p_pool) * (1/a.impressions + 1/b.impressions)) ** 0.5

        if se == 0:
            return 0.0

        # Z-score
        z = abs(a.conversion_rate - b.conversion_rate) / se

        # Approximate p-value to confidence (simplified)
        # z=1.96 corresponds to 95% confidence
        confidence = min(0.99, z / 1.96 * 0.95)

        return round(confidence, 3)

    def end_test(self, test_id: int) -> ABTestResult:
        """End a test and record final results."""
        result = self.analyze_test(test_id)

        test = self._active_tests[test_id]
        test.status = "completed"
        test.end_date = datetime.utcnow()
        test.winner = result.winner
        test.statistical_significance = result.statistical_significance

        return result

    def get_active_tests(self) -> list[ABTest]:
        """Get all active A/B tests."""
        return [t for t in self._active_tests.values() if t.status == "active"]


# Global instance
ab_testing_service = ABTestingService()
