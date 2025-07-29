from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    file_id: Optional[str] = None
    file_name: Optional[str] = None  # یا هر فیلد دیگه که در مدل File داری
    size: Optional[str] = None