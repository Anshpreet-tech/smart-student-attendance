import math

def percentage(present: int, total: int) -> float:
    if present < 0 or total < 0 or present > total:
        raise ValueError("Attendance counts must satisfy 0 <= present <= total.")
    return (present / total * 100.0) if total else 0.0

def classes_can_bunk(present: int, total: int, threshold: float = 75.0) -> int:
    """Maximum future absences while maintaining at least threshold."""
    validate(present, total, threshold)
    # (present)/(total+x) >= threshold/100
    if total == 0:
        return 0
    return max(0, math.floor((present * 100.0 / threshold) - total + 1e-10))

def classes_to_recover(present: int, total: int, threshold: float = 75.0) -> int:
    """Minimum consecutive additional presents to reach threshold."""
    validate(present, total, threshold)
    if percentage(present, total) >= threshold:
        return 0
    # (present+x)/(total+x) >= t
    return max(0, math.ceil((threshold * total - 100.0 * present) /
                            (100.0 - threshold) - 1e-12))

def predict(present: int, total: int, future_present: int, future_absent: int):
    if min(present, total, future_present, future_absent) < 0 or present > total:
        raise ValueError("Counts must be non-negative and present cannot exceed total.")
    new_present = present + future_present
    new_total = total + future_present + future_absent
    return {"present": new_present, "total": new_total,
            "percentage": percentage(new_present, new_total)}

def validate(present, total, threshold):
    if present < 0 or total < 0 or present > total:
        raise ValueError("Invalid attendance counts.")
    if not 0 < threshold < 100:
        raise ValueError("Threshold must be greater than 0 and less than 100.")
