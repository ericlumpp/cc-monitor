from collections import Counter

from sqlalchemy import text
from sqlalchemy.orm import Session

SPIKE_MULTIPLIER = 3
MIN_FAILURES = 5
MIN_SHARE = 0.6

COUNTS_SQL = text("""
SELECT endpoint,
       count(*) FILTER (WHERE occurred_at > now() - interval '1 hour') AS recent,
       count(*) FILTER (WHERE occurred_at <= now() - interval '1 hour') / 23.0 AS baseline
FROM cc_events
WHERE occurred_at > now() - interval '24 hours'
GROUP BY endpoint
""")

PAYLOADS_SQL = text("""
SELECT payload FROM cc_events
WHERE endpoint = :endpoint AND occurred_at > now() - interval '1 hour'
""")


def common_values(payloads, min_share=MIN_SHARE):
    """Payload key/value pairs present in at least min_share of the failures."""
    n = len(payloads)
    counts = Counter((k, str(v)) for p in payloads for k, v in p.items())
    return [(k, v, c / n) for (k, v), c in counts.most_common() if c / n >= min_share]


def find_anomalies(db: Session):
    found = []
    for row in db.execute(COUNTS_SQL).all():
        baseline = float(row.baseline)
        if row.recent >= MIN_FAILURES and row.recent > SPIKE_MULTIPLIER * baseline:
            rows = db.execute(PAYLOADS_SQL, {"endpoint": row.endpoint}).all()
            found.append({
                "endpoint": row.endpoint,
                "recent": row.recent,
                "baseline": baseline,
                "common": common_values([r.payload for r in rows]),
            })
    return found


def format_alert(a):
    lines = [
        f"CC failure spike: {a['endpoint']}",
        f"  {a['recent']} failures in the last hour (normal: {a['baseline']:.1f}/hour)",
    ]
    for key, value, share in a["common"]:
        lines.append(f"  {share:.0%} of failures have {key} = {value}")
    return "\n".join(lines)