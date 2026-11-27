"""Numbers derived from data/contributions.json, shared by the live sheets."""
import datetime as dt

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def short(d):
    return f"{MONTHS[d.month - 1]} {d.day}"


def rng(r):
    if not r:
        return "—"
    a, b = r
    return short(a) if a == b else f"{short(a)} – {short(b)}"


def parse(days):
    """Chronological list of (date, count, level)."""
    return [(dt.date.fromisoformat(d["date"]), d["count"], d["level"])
            for d in sorted(days, key=lambda d: d["date"])]


def grid(days):
    """Place each day on the Sunday-first week grid GitHub uses."""
    cells, week, prev = [], 0, None
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        wd = (date.weekday() + 1) % 7
        if prev is not None and wd <= prev:
            week += 1
        prev = wd
        cells.append((week, wd, date, d))
    return cells, week + 1


def streaks(days):
    rows = parse(days)
    dates = [r[0] for r in rows]
    counts = [r[1] for r in rows]
    i = len(rows) - 1
    if counts[i] == 0:  # a still-empty "today" must not break the streak
        i -= 1
    cur, cur_end, cur_start = 0, dates[i] if i >= 0 else None, None
    while i >= 0 and counts[i] > 0:
        cur, cur_start, i = cur + 1, dates[i], i - 1
    best = run = 0
    best_start = best_end = run_start = None
    for j, c in enumerate(counts):
        if c > 0:
            run += 1
            run_start = dates[j] if run == 1 else run_start
            if run > best:
                best, best_start, best_end = run, run_start, dates[j]
        else:
            run = 0
    return dict(cur=cur, cur_range=(cur_start, cur_end) if cur else None,
                best=best, best_range=(best_start, best_end),
                active=sum(1 for c in counts if c), n=len(counts), top=max(counts))
