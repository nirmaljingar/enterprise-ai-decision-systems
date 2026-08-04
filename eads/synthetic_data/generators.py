import random
from typing import ClassVar

from ..core.types import Signal


class BaseGenerator:
    """Deterministic base for synthetic enterprise signal generators."""

    source: str = "synthetic"
    templates: ClassVar[list[str]] = []

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def generate(self, n: int = 3) -> list[Signal]:
        signals = []
        for i in range(n):
            template = self.rng.choice(self.templates)
            signals.append(
                Signal(
                    id=f"{self.source}_{i}",
                    source=self.source,
                    content=template,
                    metadata={"index": i},
                )
            )
        return signals


class SupplyChainGenerator(BaseGenerator):
    """Generate synthetic, deterministic supply-chain signals for benchmarking."""

    source = "synthetic_supply_chain"
    templates: ClassVar[list[str]] = [
        "Supplier A reports 20% capacity reduction.",
        "Demand forecast increased by 15% for SKU-1001.",
        "Warehouse US-East has 500 units of SKU-1001 in stock.",
    ]


class HealthcareGenerator(BaseGenerator):
    """Generate synthetic, deterministic healthcare triage and capacity signals."""

    source = "synthetic_healthcare"
    templates: ClassVar[list[str]] = [
        "Patient reports chest pain; triage score urgent.",
        "ICU bed occupancy at 85% in Region North.",
        "Appointment no-show rate increased by 12% for cardiology.",
    ]


class FinanceGenerator(BaseGenerator):
    """Generate synthetic, deterministic finance compliance and risk signals."""

    source = "synthetic_finance"
    templates: ClassVar[list[str]] = [
        "Transaction flagged for anti-money-laundering review.",
        "Portfolio exposure to technology sector increased by 8%.",
        "Quarterly audit deadline is 5 business days away.",
    ]


class ITOperationsGenerator(BaseGenerator):
    """Generate synthetic, deterministic IT operations incident signals."""

    source = "synthetic_it_operations"
    templates: ClassVar[list[str]] = [
        "API gateway p99 latency exceeded 2 seconds for 10 minutes.",
        "Incident P1: database failover initiated in region us-east.",
        "Certificate for service payments-api expires in 3 days.",
    ]


class CustomerSupportGenerator(BaseGenerator):
    """Generate synthetic, deterministic customer support ticket signals."""

    source = "synthetic_customer_support"
    templates: ClassVar[list[str]] = [
        "Customer reports login failure on the mobile application.",
        "Refund request received for order #12345.",
        "VIP account escalated due to repeated service interruptions.",
    ]
