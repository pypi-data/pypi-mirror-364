# bucket.py
# Maps DPD to 7 buckets: 0/30/60/90/120/150/WO

def assign_state(dpd: int) -> str:
    """Assigns a DPD value to a bucket label."""
    if dpd < 30:
        return "C0"
    elif dpd < 60:
        return "C1"
    elif dpd < 90:
        return "C2"
    elif dpd < 120:
        return "C3"
    elif dpd < 150:
        return "C4"
    elif dpd < 180:
        return "C5"
    else:
        return "WO" 