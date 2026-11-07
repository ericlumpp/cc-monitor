from collections import Counter

from sqlalchemy import text
from sqlalchemy.orm import Session

SPIKE_MULTIPLIER = 3
MIN_FAILURES = 5
MIN_SHARE = 0.6
MIN_LIFT = 2
BASELINE_FLOOR = 0.05

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

BASELINE_SQL = text("""
SELECT payload FROM cc_events
WHERE occurred_at <= now() - interval '1 hour'
  AND occurred_at > now() - interval '24 hours'
""")


def shares(payloads):
    """Fraction of payloads containing each (key, value) pair."""
    n = len(payloads) or 1
    counts = Counter((k, str(v)) for p in payloads for k, v in p.items())
    return {kv: c / n for kv, c in counts.items()}


def common_values(payloads, baseline_payloads):
    """Pairs that are common in these failures AND unusually common vs the baseline."""
    base = shares(baseline_payloads)
    found = []
    for (k, v), share in sorted(shares(payloads).items(), key=lambda kv: -kv[1]):
        base_share = base.get((k, v), 0)
        if share >= MIN_SHARE and share >= MIN_LIFT * max(base_share, BASELINE_FLOOR):
            found.append((k, v, share, base_share))
    return found


def find_anomalies(db: Session):
    baseline = [r.payload for r in db.execute(BASELINE_SQL).all()]
    found = []
    for row in db.execute(COUNTS_SQL).all():
        avg = float(row.baseline)
        if row.recent >= MIN_FAILURES and row.recent > SPIKE_MULTIPLIER * avg:
            rows = db.execute(PAYLOADS_SQL, {"endpoint": row.endpoint}).all()
            found.append({
                "endpoint": row.endpoint,
                "recent": row.recent,
                "baseline": avg,
                "common": common_values([r.payload for r in rows], baseline),
            })
    return found


def format_alert(a):
    lines = [
        f"CC failure spike: {a['endpoint']}",
        f"  {a['recent']} failures in the last hour (normal: {a['baseline']:.1f}/hour)",
    ]
    for key, value, share, base in a["common"]:
        lines.append(f"  {share:.0%} of failures have {key} = {value} (normally {base:.0%})")
    return "\n".join(lines)