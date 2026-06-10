"""
Public holiday helpers for the customer availability calendar.
Merges admin-configured GlobalSpecialDay entries with standard Indian public holidays.
"""
from datetime import date, timedelta

# Fixed-date holidays (repeat every year)
RECURRING_PUBLIC_HOLIDAYS = [
    {'name': 'New Year', 'day': 1, 'month': 1},
    {'name': 'Republic Day', 'day': 26, 'month': 1},
    {'name': 'Independence Day', 'day': 15, 'month': 8},
    {'name': 'Gandhi Jayanti', 'day': 2, 'month': 10},
    {'name': 'Christmas', 'day': 25, 'month': 12},
]

# Variable holidays — update yearly (month, day)
YEAR_SPECIFIC_HOLIDAYS = {
    2026: [
        {'name': 'Holi', 'day': 3, 'month': 3},
        {'name': 'Gudi Padwa', 'day': 19, 'month': 3},
        {'name': 'Good Friday', 'day': 3, 'month': 4},
        {'name': 'Eid ul-Fitr', 'day': 21, 'month': 3},
        {'name': 'Raksha Bandhan', 'day': 28, 'month': 8},
        {'name': 'Janmashtami', 'day': 4, 'month': 9},
        {'name': 'Ganesh Chaturthi', 'day': 14, 'month': 9},
        {'name': 'Dussehra', 'day': 20, 'month': 10},
        {'name': 'Diwali', 'day': 8, 'month': 11},
    ],
    2027: [
        {'name': 'Holi', 'day': 22, 'month': 3},
        {'name': 'Diwali', 'day': 28, 'month': 10},
    ],
}


def _matches_special_day(day: date, sd) -> bool:
    if sd.day != day.day or sd.month != day.month:
        return False
    if getattr(sd, 'year', None):
        return sd.year == day.year
    return True


def _holiday_name_from_dict(day: date) -> str | None:
    for h in RECURRING_PUBLIC_HOLIDAYS:
        if h['day'] == day.day and h['month'] == day.month:
            return h['name']
    for h in YEAR_SPECIFIC_HOLIDAYS.get(day.year, []):
        if h['day'] == day.day and h['month'] == day.month:
            return h['name']
    return None


def resolve_holiday_name(day: date, global_special_days) -> str | None:
    """Return holiday label for a date (DB entries take priority)."""
    for sd in global_special_days:
        if _matches_special_day(day, sd):
            return sd.name
    return _holiday_name_from_dict(day)


def collect_holidays_in_range(start: date, end: date, global_special_days) -> dict[str, str]:
    """Map ISO date strings to holiday names within range."""
    holidays: dict[str, str] = {}
    current = start
    while current <= end:
        name = resolve_holiday_name(current, global_special_days)
        if name:
            holidays[current.isoformat()] = name
        current += timedelta(days=1)
    return holidays


def compute_long_weekend_dates(holiday_dates: set[date]) -> set[date]:
    """
    Expand public holidays into long-weekend date ranges customers often book.
    e.g. Friday holiday -> Fri-Sun, Thursday holiday -> Thu-Sun.
    """
    result: set[date] = set()
    for h in sorted(holiday_dates):
        wd = h.weekday()  # Mon=0 … Sun=6
        if wd == 3:  # Thursday
            offsets = range(0, 4)
        elif wd == 4:  # Friday
            offsets = range(0, 3)
        elif wd == 5:  # Saturday
            offsets = range(-1, 2)
        elif wd == 6:  # Sunday
            offsets = range(-1, 1)
        elif wd == 0:  # Monday
            offsets = range(-2, 1)
        elif wd == 1:  # Tuesday
            offsets = range(-3, 1)
        else:  # Wednesday
            offsets = range(0, 5)
        for offset in offsets:
            result.add(h + timedelta(days=offset))
    return result


def build_calendar_day_info(start: date, end: date, global_special_days) -> list[dict]:
    holidays = collect_holidays_in_range(start, end, global_special_days)
    holiday_date_objs = {date.fromisoformat(d) for d in holidays}
    long_weekend_dates = compute_long_weekend_dates(holiday_date_objs)

    days_payload = []
    current = start
    while current <= end:
        iso = current.isoformat()
        holiday_name = holidays.get(iso)
        is_long_weekend = current in long_weekend_dates and not holiday_name
        days_payload.append({
            'date': iso,
            'is_special_day': bool(holiday_name),
            'holiday_name': holiday_name,
            'is_long_weekend': is_long_weekend,
        })
        current += timedelta(days=1)
    return days_payload


def list_special_days_for_response(global_special_days) -> list[dict]:
    """All configured + built-in holidays for the legend panel."""
    seen = set()
    payload = []

    for sd in global_special_days:
        key = (sd.name, sd.day, sd.month, sd.year)
        if key not in seen:
            seen.add(key)
            payload.append({
                'name': sd.name,
                'day': sd.day,
                'month': sd.month,
                'year': sd.year,
            })

    for h in RECURRING_PUBLIC_HOLIDAYS:
        key = (h['name'], h['day'], h['month'], None)
        if key not in seen:
            seen.add(key)
            payload.append({**h, 'year': None})

    for year, holidays in sorted(YEAR_SPECIFIC_HOLIDAYS.items()):
        for h in holidays:
            key = (h['name'], h['day'], h['month'], year)
            if key not in seen:
                seen.add(key)
                payload.append({**h, 'year': year})

    payload.sort(key=lambda x: (x.get('year') or 9999, x['month'], x['day']))
    return payload
