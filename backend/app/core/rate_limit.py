from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self.hits: dict[str, deque] = defaultdict(deque)

    def check(self, key: str) -> None:
        now = datetime.now(timezone.utc)
        bucket = self.hits[key]
        cutoff = now - timedelta(minutes=1)
        while bucket and bucket[0] < cutoff:
            bucket.popleft()
        if len(bucket) >= self.per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        bucket.append(now)

    async def __call__(self, request: Request) -> None:
        client = request.client.host if request.client else "unknown"
        self.check(client)
