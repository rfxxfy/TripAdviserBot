import re
from typing import List

def is_valid_coordinate(text: str) -> bool:
    """
    Проверяет строку «lat,lon» или «lat lon».
    """
    pattern = r"^-?\d+(\.\d+)?[,\s]+-?\d+(\.\d+)?$"
    return bool(re.match(pattern, text.strip()))

def clamp(value: float, min_v: float, max_v: float) -> float:
    return max(min_v, min(max_v, value))

def chunk_text(text: str, size: int = 4000) -> List[str]:
    return [text[i:i+size] for i in range(0, len(text), size)]
