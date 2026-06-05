from collections import defaultdict
from datetime import datetime, timedelta

requests = defaultdict(list)

LIMIT = 30
WINDOW = timedelta(hours=1)


def is_rate_limited(ip: str):

    now = datetime.now()

    requests[ip] = [
        t
        for t in requests[ip]
        if now - t < WINDOW
    ]

    if len(requests[ip]) >= LIMIT:
        return True

    requests[ip].append(now)

    return False