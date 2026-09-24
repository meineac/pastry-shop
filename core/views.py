import calendar
import logging

import ipinfo
import pytz
import requests
from django.conf import settings
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def get_client_ip(request):
    """
    Return the real client IP, preferring X-Forwarded-For (set by proxies /
    load balancers).  Falls back to REMOTE_ADDR.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR", "")

    # In local development the address is loopback — use the configurable
    # TEST_IP fallback so the page still shows something meaningful.
    if ip in ("127.0.0.1", "::1", ""):
        ip = settings.TEST_IP
        logger.debug("Loopback address detected; using TEST_IP=%s", ip)

    return ip


def get_ipinfo(ip):
    """
    Query the IPinfo API for ``ip``.
    Returns a dict with at minimum ``timezone``, ``city``, ``country``.
    Returns an empty dict on any error.
    """
    token = settings.IPINFO_TOKEN
    try:
        handler = ipinfo.getHandler(token)
        details = handler.getDetails(ip)
        result = {
            "ip": ip,
            "city": getattr(details, "city", "Unknown"),
            "country": getattr(details, "country_name", getattr(details, "country", "Unknown")),
            "timezone": getattr(details, "timezone", "UTC"),
            "latitude": getattr(details, "latitude", None),
            "longitude": getattr(details, "longitude", None),
        }
        logger.info("IPinfo lookup for %s -> tz=%s city=%s", ip, result["timezone"], result["city"])
        return result
    except Exception as exc:
        logger.warning("IPinfo API error for IP %s: %s", ip, exc)
        return {}


def get_weather(city, country):
    """
    Query the OpenWeatherMap current-weather endpoint.
    Returns a dict with ``temperature``, ``description``, ``humidity``, ``wind_speed``.
    Returns an empty dict on any error.
    """
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        logger.warning("OPENWEATHER_API_KEY is not configured; skipping weather lookup.")
        return {}

    query = f"{city},{country}" if city and city != "Unknown" else "London,GB"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": query, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        weather = {
            "temperature": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "description": data["weather"][0]["description"].capitalize(),
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "city": data.get("name", city),
            "country": data.get("sys", {}).get("country", country),
        }
        logger.info(
            "OpenWeather for '%s': %s°C, %s",
            query, weather["temperature"], weather["description"],
        )
        return weather
    except requests.RequestException as exc:
        logger.warning("OpenWeather API error for query '%s': %s", query, exc)
        return {}


def build_text_calendar(year, month):
    """Return a plain-text calendar for *year*/*month* (uses Python stdlib)."""
    cal = calendar.TextCalendar(firstweekday=0)  # Monday first
    return cal.formatmonth(year, month)


def local_datetime(tz_name):
    """
    Return the current datetime in *tz_name* timezone.
    Falls back to UTC on unknown timezone names.
    """
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        logger.warning("Unknown timezone '%s', falling back to UTC.", tz_name)
        tz = pytz.utc
    return timezone.now().astimezone(tz)
# ---------------------------------------------------------------------------

def showcase_view(request):
    """View to demonstrate all required HTML elements for the task."""
    return render(request, "core/showcase.html")
