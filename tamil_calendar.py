"""
tamil_calendar.py
-----------------
Tamil Calendar backend using pyswisseph for accurate solar calculations.

Install:  pip install pyswisseph flask

Default location: Tiruchirappalli, Tamil Nadu
  Lat: 10°56'33.9"N  Lon: 78°25'04.5"E

13-Ghatika Rule:
  1 Ghatika = 24 minutes  →  13 Ghatikas = 312 minutes
  If sun transit occurs WITHIN 312 minutes after sunrise:
      → That day is Tamil month Day 1
  If sun transit occurs AFTER 312 minutes from sunrise:
      → Next day is Tamil month Day 1
"""

import datetime
import swisseph as swe

# ── Constants ──────────────────────────────────────────────────────────────────

RASI_ENGLISH = [
    "Chithirai", "Vaikasi", "Aani", "Aadi", "Aavani", "Purattasi",
    "Aippasi", "Karthigai", "Margazhi", "Thai", "Maasi", "Panguni"
]

TAMIL_MONTH_NAMES = [
    "சித்திரை", "வைகாசி", "ஆனி", "ஆடி", "ஆவணி", "புரட்டாசி",
    "ஐப்பசி", "கார்த்திகை", "மார்கழி", "தை", "மாசி", "பங்குனி"
]

TAMIL_YEARS = [
    "பிரபவ",        "விபவ",          "சுக்ல",         "பிரமோதூத",    "பிரஜோற்பத்தி",
    "ஆங்கீரஸ",     "ஸ்ரீமுக",       "பவ",            "யுவ",          "தாது",
    "ஈஸ்வர",       "வெகுதான்ய",     "பிரமாதி",       "விக்கிரம",     "விஷு",
    "சித்ரபானு",   "சுபானு",        "தாரண",          "பார்த்திப",    "விய",
    "சர்வஜித்",    "சர்வதாரி",      "விரோதி",        "விகிருதி",      "கர",
    "நந்தன",        "விஜய",          "ஜய",            "மன்மத",        "துர்முகி",
    "ஹேவிளம்பி",   "விளம்பி",       "விகாரி",        "சார்வரி",      "பிலவ",
    "சுபகிருது",   "சோபகிருது",     "குரோதி",        "விஸ்வாவசு",    "பராபவ",
    "பிலவங்க",     "கீலக",          "சௌம்ய",         "சாதாரண",       "விரோதகிருது",
    "பரிதாபி",     "பிரமாதீச",      "ஆனந்த",         "ராட்சஸ",       "நள",
    "பிங்கள",      "காளயுக்தி",     "சித்தார்த்தி",  "ரௌத்ரி",      "துன்மதி",
    "துந்துபி",     "ருத்ரோத்காரி",  "ரக்தாட்சி",     "குரோதன",      "அட்சய"
]

WEEKDAY_TAMIL   = ["திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி", "ஞாயிறு"]
WEEKDAY_ENGLISH = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MONTH_ENGLISH   = ["January","February","March","April","May","June",
                   "July","August","September","October","November","December"]

# Default location — Tiruchirappalli
DEFAULT_LAT = 10 + 56/60 + 33.9/3600   # 10°56'33.9"N
DEFAULT_LON = 78 + 25/60 +  4.5/3600   # 78°25'04.5"E
DEFAULT_ALT = 88.0                       # metres

IST_OFFSET = 5.5   # UTC + 5:30

GHATIKA_MINUTES = 13 * 24   # 312 minutes


# ── Ayanamsa ───────────────────────────────────────────────────────────────────

def set_ayanamsa(choice='lahiri'):
    c = choice.lower()
    if c.startswith('ram'):
        swe.set_sid_mode(swe.SIDM_RAMAN)
    elif c.startswith('kp'):
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)


# ── Solar longitude ────────────────────────────────────────────────────────────

def sun_longitude(jd, ayanamsa='lahiri'):
    """Sidereal sun longitude (degrees) at Julian Day (UTC)."""
    set_ayanamsa(ayanamsa)
    flags  = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    result = swe.calc_ut(jd, swe.SUN, flags)
    return result[0][0]


# ── JD ↔ IST helpers ──────────────────────────────────────────────────────────

def jd_to_ist(jd):
    """Return an IST-aware datetime from a Julian Day (UTC)."""
    y, m, d, h = swe.revjul(jd)
    utc_dt = datetime.datetime(int(y), int(m), int(d),
                               tzinfo=datetime.timezone.utc)
    utc_dt += datetime.timedelta(seconds=h * 3600)
    ist_tz  = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    return utc_dt.astimezone(ist_tz)


def date_to_jd_ut(date, hour_ut=0.0):
    """Gregorian date → Julian Day (UTC)."""
    return swe.julday(date.year, date.month, date.day, hour_ut)


# ── Binary search for transit ──────────────────────────────────────────────────

def find_transit_jd(start_jd, end_jd, target_rasi, ayanamsa='lahiri'):
    """
    Binary-search the exact JD when the sun enters *target_rasi*.
    50 iterations → sub-second accuracy.
    """
    target_lon = target_rasi * 30.0
    lo, hi = start_jd, end_jd

    for _ in range(50):
        mid = (lo + hi) / 2.0
        lon = sun_longitude(mid, ayanamsa)

        if target_rasi == 0:          # Pisces → Aries boundary crossing
            if lon > 330:
                lo = mid              # still in Pisces, move forward
            else:
                hi = mid              # already in Aries, move backward
        else:
            if lon < target_lon:
                lo = mid
            else:
                hi = mid

    return hi


# ── Collect all transits in a date range ──────────────────────────────────────

def get_transits_in_range(start_date, end_date, ayanamsa='lahiri'):
    """
    Return a list of transit dicts for every Rasi change between
    *start_date* and *end_date*.

    Each dict: {rasi_index, transit_jd, ist_dt, date}
    """
    transits = []

    start_jd = date_to_jd_ut(start_date)
    end_jd   = date_to_jd_ut(end_date)

    current_jd   = start_jd
    current_rasi = int(sun_longitude(current_jd, ayanamsa) / 30)

    while current_jd < end_jd:
        next_rasi = (current_rasi + 1) % 12

        # Estimate days until next rasi boundary
        cur_lon     = sun_longitude(current_jd, ayanamsa)
        next_lon    = next_rasi * 30.0
        deg_to_go   = (next_lon - cur_lon) % 360
        jump_days   = max(1.0, deg_to_go - 1.5)

        s_jd = current_jd + jump_days
        e_jd = s_jd + 4.0

        lon_s = sun_longitude(s_jd, ayanamsa)
        lon_e = sun_longitude(e_jd, ayanamsa)

        rasi_s = int(lon_s / 30)
        rasi_e = int(lon_e / 30)

        # Detect boundary crossing (including Pisces → Aries wrap)
        transit_in_window = False
        if next_rasi == 0:
            transit_in_window = (lon_s > 340 and lon_e < 20)
        else:
            transit_in_window = (rasi_s < next_rasi <= rasi_e)

        if transit_in_window:
            t_jd   = find_transit_jd(s_jd, e_jd, next_rasi, ayanamsa)
            ist_dt = jd_to_ist(t_jd)

            transits.append({
                'rasi_index': next_rasi,
                'transit_jd': t_jd,
                'ist_dt':     ist_dt,
                'date':       ist_dt.date(),
            })

            current_rasi = next_rasi
            current_jd   = t_jd + 1.0
        else:
            current_jd = e_jd

    return transits


# ── Sunrise / Sunset ───────────────────────────────────────────────────────────


def get_sunrise_sunset(date, lat=DEFAULT_LAT, lon=DEFAULT_LON, alt=DEFAULT_ALT):
    """
    Return (sunrise_ist, sunset_ist) as IST datetime objects using swisseph.

    Correct pyswisseph signature (confirmed via help(swe.rise_trans)):
        rise_trans(tjdut, body, rsmi, geopos, atpress=0.0, attemp=0.0, flags=FLG_SWIEPH)

    NOTE: rsmi comes BEFORE geopos — opposite of what the C docs show.
    Returns: (res, tret)
        res    = 0 success, -2 circumpolar
        tret   = tuple of 10 floats, tret[0] = JD of event
    """
    IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))

    # Search from midnight IST expressed as UTC JD
    jd_start = swe.julday(date.year, date.month, date.day, 0.0) - IST_OFFSET / 24.0
    geopos   = (lon, lat, alt)   # lon first, then lat, then alt

    try:
        # Sunrise
        res_rise, tret_rise = swe.rise_trans(
            jd_start, swe.SUN,
            swe.CALC_RISE,
            geopos, 1013.25, 15.0
        )
        if res_rise == -2:
            raise ValueError("Sun is circumpolar — no sunrise")

        # Sunset — search from sunrise JD onwards
        res_set, tret_set = swe.rise_trans(
            tret_rise[0], swe.SUN,
            swe.CALC_SET,
            geopos, 1013.25, 15.0
        )
        if res_set == -2:
            raise ValueError("Sun is circumpolar — no sunset")

        return jd_to_ist(tret_rise[0]), jd_to_ist(tret_set[0])

    except Exception as e:
        print(f"[sunrise error] {date}: {e}")
        sr = datetime.datetime(date.year, date.month, date.day, 6, 10, tzinfo=IST)
        ss = datetime.datetime(date.year, date.month, date.day, 18, 20, tzinfo=IST)
        return sr, ss


# ── 13-Ghatika rule ───────────────────────────────────────────────────────────

def apply_13_ghatika_rule(transit_ist, sunrise_ist):
    """
    13 Ghatikas = 312 minutes after sunrise.

    • transit ≤ sunrise + 312 min  →  transit day  = Tamil month Day 1
    • transit >  sunrise + 312 min →  next day     = Tamil month Day 1

    Handles both tz-aware (astral) and tz-naive datetimes.
    """
    if sunrise_ist is None:
        return transit_ist.date()

    # Normalise to tz-naive for safe arithmetic
    sr = sunrise_ist.replace(tzinfo=None) if sunrise_ist.tzinfo else sunrise_ist
    tr = transit_ist.replace(tzinfo=None) if transit_ist.tzinfo else transit_ist

    limit = sr + datetime.timedelta(minutes=GHATIKA_MINUTES)

    if tr <= limit:
        return tr.date()
    else:
        return tr.date() + datetime.timedelta(days=1)


# ── Tamil year from 60-year cycle ─────────────────────────────────────────────

def get_tamil_year(gregorian_year):
    """
    Map a Gregorian year (of the Chithirai start) to a Tamil 60-year cycle name.
    Anchor: April 2025 Chithirai begins 'Visvavasu / விஸ்வாவசு' (0-based index 38).
    """
    idx = (38 + gregorian_year - 2025) % 60
    return TAMIL_YEARS[idx], idx + 1   # (name, position-in-cycle)


# ── Build month calendar ───────────────────────────────────────────────────────

def build_tamil_calendar(gregorian_year, gregorian_month,
                          lat=DEFAULT_LAT, lon=DEFAULT_LON,
                          ayanamsa='lahiri'):
    """
    Build day-by-day Tamil calendar data for one Gregorian month.

    Returns a list of dicts, one per day, containing:
      gregorian_date, gregorian_day, gregorian_month, gregorian_year,
      weekday_english, weekday_tamil,
      tamil_month_index, tamil_month_english, tamil_month_tamil,
      tamil_day, tamil_year_name,
      sunrise, sunset,
      is_month_start, transit_info (or None)
    """
    # ── 1. Collect transits with a generous buffer ──────────────────────────
    buf_start = datetime.date(gregorian_year - 1,  1,  1)  # must reach prev Chithirai (April)
    buf_end   = datetime.date(gregorian_year + 1,  6,  1)
    all_transits = get_transits_in_range(buf_start, buf_end, ayanamsa)

    # ── 2. Apply 13-ghatika rule → actual Tamil month start dates ───────────
    tamil_month_starts = []
    for t in all_transits:
        sunrise_ist, _ = get_sunrise_sunset(t['date'], lat, lon)
        start_date = apply_13_ghatika_rule(t['ist_dt'], sunrise_ist)

        tamil_month_starts.append({
            'start_date':        start_date,
            'tamil_month_index': t['rasi_index'],
            'transit_date':      t['date'],
            'transit_time':      t['ist_dt'].strftime('%I:%M %p'),
        })

    tamil_month_starts.sort(key=lambda x: x['start_date'])

    # ── 3. Date range for the requested month ───────────────────────────────
    first_day = datetime.date(gregorian_year, gregorian_month, 1)
    if gregorian_month == 12:
        last_day = datetime.date(gregorian_year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        last_day = datetime.date(gregorian_year, gregorian_month + 1, 1) - datetime.timedelta(days=1)

    # ── 4. Walk each day ────────────────────────────────────────────────────
    days_data    = []
    current_date = first_day

    while current_date <= last_day:

        # Find the most recent Tamil month start ≤ current_date
        current_tms = None
        for tms in tamil_month_starts:
            if tms['start_date'] <= current_date:
                current_tms = tms
            else:
                break

        if current_tms:
            tamil_month_idx = current_tms['tamil_month_index']
            tamil_day       = (current_date - current_tms['start_date']).days + 1

            # Determine Tamil year: find the most recent Chithirai (index 0)
            tamil_year_greg = gregorian_year
            for tms in reversed(tamil_month_starts):
                if tms['start_date'] <= current_date and tms['tamil_month_index'] == 0:
                    tamil_year_greg = tms['start_date'].year
                    break
            tamil_year_name, _ = get_tamil_year(tamil_year_greg)
        else:
            tamil_month_idx = 0
            tamil_day       = 1
            tamil_year_name, _ = get_tamil_year(gregorian_year)

        # Sunrise / sunset
        sunrise_ist, sunset_ist = get_sunrise_sunset(current_date, lat, lon)
        sunrise_str = sunrise_ist.strftime('%I:%M %p') if sunrise_ist else "N/A"
        sunset_str  = sunset_ist.strftime('%I:%M %p')  if sunset_ist  else "N/A"

        weekday_idx   = current_date.weekday()   # Mon=0 … Sun=6
        is_month_start = bool(current_tms and current_tms['start_date'] == current_date)

        transit_info = None
        if is_month_start:
            transit_info = {
                'transit_date': current_tms['transit_date'].strftime('%Y-%m-%d'),
                'transit_time': current_tms['transit_time'],
            }

        days_data.append({
            'gregorian_date':    current_date.strftime('%Y-%m-%d'),
            'gregorian_day':     current_date.day,
            'gregorian_month':   MONTH_ENGLISH[current_date.month - 1],
            'gregorian_year':    current_date.year,
            'weekday_english':   WEEKDAY_ENGLISH[weekday_idx],
            'weekday_tamil':     WEEKDAY_TAMIL[weekday_idx],
            'tamil_month_index': tamil_month_idx,
            'tamil_month_english': RASI_ENGLISH[tamil_month_idx],
            'tamil_month_tamil': TAMIL_MONTH_NAMES[tamil_month_idx],
            'tamil_day':         tamil_day,
            'tamil_year_name':   tamil_year_name,
            'sunrise':           sunrise_str,
            'sunset':            sunset_str,
            'is_month_start':    is_month_start,
            'transit_info':      transit_info,
        })

        current_date += datetime.timedelta(days=1)

    return days_data


# ── Convenience: today's Tamil date ───────────────────────────────────────────

def get_today_tamil_date(lat=DEFAULT_LAT, lon=DEFAULT_LON, ayanamsa='lahiri'):
    today = datetime.date.today()
    days  = build_tamil_calendar(today.year, today.month, lat, lon, ayanamsa)
    today_str = today.strftime('%Y-%m-%d')
    for d in days:
        if d['gregorian_date'] == today_str:
            return d
    return None
