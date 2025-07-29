from dataclasses import dataclass
from typing import Optional

from rubpy.bot.enums.payment_status import PaymentStatusEnum


@dataclass
class PaymentStatus:
    payment_id: Optional[str] = None
    status: Optional[PaymentStatusEnum] = None