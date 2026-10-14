"""
Tests for core helper utilities (used by cms.views.home_view).

All external HTTP calls (IPinfo SDK and requests.get for OpenWeather) are
mocked so the test suite runs offline and deterministically.
"""

import calendar
from unittest.mock import MagicMock, patch

from django.test import Client, TestCase, override_settings
from django.urls import reverse


# ---------------------------------------------------------------------------
# Helper: a fake ipinfo "details" object
# ---------------------------------------------------------------------------

class FakeIPInfoDetails:
    """Mimics the object returned by ipinfo.Handler.getDetails()."""

    def __init__(self, **kwargs):
        defaults = {
            "ip": "8.8.8.8",
            "city": "Mountain View",
            "country": "US",
            "country_name": "United States",
            "timezone": "America/Los_Angeles",
            "latitude": "37.3860",
            "longitude": "-122.0838",
        }
        defaults.update(kwargs)
        for key, value in defaults.items():
            setattr(self, key, value)


# ---------------------------------------------------------------------------
# Helper: fake OpenWeather JSON response
# ---------------------------------------------------------------------------

FAKE_WEATHER_JSON = {
    "name": "Mountain View",
    "sys": {"country": "US"},
    "main": {
        "temp": 18.5,
        "feels_like": 17.0,
        "humidity": 65,
    },
    "weather": [{"description": "clear sky"}],
    "wind": {"speed": 3.2},
}


# ---------------------------------------------------------------------------
# Tests: helper functions
# ---------------------------------------------------------------------------

class GetClientIPTests(TestCase):
    """Unit tests for get_client_ip helper."""

    def _call(self, remote_addr=None, x_forwarded_for=None):
        from core.views import get_client_ip
        request = MagicMock()
        meta = {}
        if remote_addr:
            meta["REMOTE_ADDR"] = remote_addr
        if x_forwarded_for:
            meta["HTTP_X_FORWARDED_FOR"] = x_forwarded_for
        request.META = meta
        return get_client_ip(request)

    @override_settings(TEST_IP="1.2.3.4")
    def test_loopback_returns_test_ip(self):
        ip = self._call(remote_addr="127.0.0.1")
        self.assertEqual(ip, "1.2.3.4")

    @override_settings(TEST_IP="1.2.3.4")
    def test_ipv6_loopback_returns_test_ip(self):
        ip = self._call(remote_addr="::1")
        self.assertEqual(ip, "1.2.3.4")

    def test_real_ip_returned_as_is(self):
        ip = self._call(remote_addr="203.0.113.42")
        self.assertEqual(ip, "203.0.113.42")

    def test_x_forwarded_for_takes_priority(self):
        ip = self._call(remote_addr="10.0.0.1", x_forwarded_for="203.0.113.42, 10.0.0.1")
        self.assertEqual(ip, "203.0.113.42")


class BuildTextCalendarTests(TestCase):
    """Unit tests for build_text_calendar helper."""

    def test_returns_string_with_month_name(self):
        from core.views import build_text_calendar
        cal_str = build_text_calendar(2025, 5)
        self.assertIn("May", cal_str)
        self.assertIn("2025", cal_str)

    def test_calendar_contains_day_numbers(self):
        from core.views import build_text_calendar
        cal_str = build_text_calendar(2025, 1)
        # January must show day 31
        self.assertIn("31", cal_str)

    def test_output_matches_stdlib(self):
        from core.views import build_text_calendar
        expected = calendar.TextCalendar(firstweekday=0).formatmonth(2024, 12)
        self.assertEqual(build_text_calendar(2024, 12), expected)


class LocalDatetimeTests(TestCase):
    """Unit tests for local_datetime helper."""

    def test_valid_timezone(self):
        from core.views import local_datetime
        dt = local_datetime("Europe/London")
        self.assertIsNotNone(dt)
        self.assertEqual(str(dt.tzinfo), "Europe/London")

    def test_invalid_timezone_falls_back_to_utc(self):
        from core.views import local_datetime
        dt = local_datetime("Invalid/Zone")
        self.assertIn("UTC", str(dt.tzinfo))


# ---------------------------------------------------------------------------
# Tests: _get_ipinfo helper
# ---------------------------------------------------------------------------

class GetIPInfoTests(TestCase):

    @patch("core.views.ipinfo.getHandler")
    @override_settings(IPINFO_TOKEN="test-token")
    def test_successful_lookup(self, mock_get_handler):
        mock_handler = MagicMock()
        mock_handler.getDetails.return_value = FakeIPInfoDetails()
        mock_get_handler.return_value = mock_handler

        from core.views import get_ipinfo
        result = get_ipinfo("8.8.8.8")

        self.assertEqual(result["city"], "Mountain View")
        self.assertEqual(result["timezone"], "America/Los_Angeles")
        self.assertEqual(result["country"], "United States")

    @patch("core.views.ipinfo.getHandler")
    def test_api_error_returns_empty_dict(self, mock_get_handler):
        mock_get_handler.side_effect = Exception("network error")

        from core.views import get_ipinfo
        result = get_ipinfo("8.8.8.8")
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# Tests: _get_weather helper
# ---------------------------------------------------------------------------

class GetWeatherTests(TestCase):

    @patch("core.views.requests.get")
    @override_settings(OPENWEATHER_API_KEY="test-key")
    def test_successful_weather_fetch(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = FAKE_WEATHER_JSON
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        from core.views import get_weather
        result = get_weather("Mountain View", "US")

        self.assertEqual(result["temperature"], 18)  # round(18.5) == 18 (banker's rounding)
        self.assertEqual(result["description"], "Clear sky")
        self.assertEqual(result["humidity"], 65)
        self.assertEqual(result["wind_speed"], 3.2)

    @patch("core.views.requests.get")
    @override_settings(OPENWEATHER_API_KEY="test-key")
    def test_network_error_returns_empty_dict(self, mock_get):
        import requests as req_lib
        mock_get.side_effect = req_lib.RequestException("timeout")

        from core.views import get_weather
        result = get_weather("London", "GB")
        self.assertEqual(result, {})

    @override_settings(OPENWEATHER_API_KEY="")
    def test_missing_api_key_returns_empty_dict(self):
        from core.views import get_weather
        result = get_weather("London", "GB")
        self.assertEqual(result, {})


# ---------------------------------------------------------------------------
# Tests: home_view integration (using core helpers)
# ---------------------------------------------------------------------------

@override_settings(
    IPINFO_TOKEN="test-token",
    OPENWEATHER_API_KEY="test-key",
    TEST_IP="8.8.8.8",
)
class HomeLocationViewTests(TestCase):
    """
    Integration tests for the home page, which now includes location,
    timezone, weather, and calendar alongside the latest news.
    All external API calls are mocked.
    """

    def setUp(self):
        self.client = Client()
        self.url = reverse("cms:home")

    def _mock_ipinfo(self, details=None):
        """Return a context manager that patches ipinfo.getHandler."""
        mock_handler = MagicMock()
        mock_handler.getDetails.return_value = details or FakeIPInfoDetails()
        return patch("core.views.ipinfo.getHandler", return_value=mock_handler)

    def _mock_weather(self, json_data=None, raise_exc=None):
        """Return a context manager that patches requests.get."""
        if raise_exc:
            return patch("core.views.requests.get", side_effect=raise_exc)
        mock_response = MagicMock()
        mock_response.json.return_value = json_data or FAKE_WEATHER_JSON
        mock_response.raise_for_status = MagicMock()
        return patch("core.views.requests.get", return_value=mock_response)

    # ── Basic response ───────────────────────────────────────────────────────

    def test_returns_200(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_uses_home_template(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertTemplateUsed(response, "cms/home.html")

    # ── Context data ─────────────────────────────────────────────────────────

    def test_timezone_in_context(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertEqual(response.context["timezone"], "America/Los_Angeles")

    def test_local_date_format_ddmmyyyy(self):
        """Date must be in DD/MM/YYYY format."""
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        date_str = response.context["local_date"]
        parts = date_str.split("/")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[0]), 2)  # DD
        self.assertEqual(len(parts[1]), 2)  # MM
        self.assertEqual(len(parts[2]), 4)  # YYYY

    def test_utc_date_format_ddmmyyyy(self):
        """UTC date must also be in DD/MM/YYYY format."""
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        date_str = response.context["utc_date"]
        parts = date_str.split("/")
        self.assertEqual(len(parts), 3)
        self.assertEqual(len(parts[2]), 4)

    def test_city_and_country_in_context(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertEqual(response.context["city"], "Mountain View")
        self.assertEqual(response.context["country"], "United States")

    def test_calendar_in_context(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        cal = response.context["text_calendar"]
        self.assertIsInstance(cal, str)
        self.assertGreater(len(cal), 0)

    def test_weather_in_context(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        weather = response.context["weather"]
        self.assertIn("temperature", weather)
        self.assertIn("description", weather)

    # ── Rendered HTML ────────────────────────────────────────────────────────

    def test_timezone_rendered_on_page(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertContains(response, "America/Los_Angeles")

    def test_calendar_rendered_on_page(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertContains(response, "<pre>")

    def test_weather_rendered_on_page(self):
        with self._mock_ipinfo(), self._mock_weather():
            response = self.client.get(self.url)
        self.assertContains(response, "Clear sky")

    # ── Graceful degradation ─────────────────────────────────────────────────

    def test_ipinfo_failure_still_returns_200(self):
        """Home page must not crash when IPinfo is unavailable."""
        with patch("core.views.ipinfo.getHandler", side_effect=Exception("offline")):
            with self._mock_weather():
                response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_weather_failure_still_returns_200(self):
        """Home page must not crash when OpenWeather is unavailable."""
        import requests as req_lib
        with self._mock_ipinfo():
            with self._mock_weather(raise_exc=req_lib.RequestException("timeout")):
                response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_weather_unavailable_message_shown(self):
        """When weather lookup fails, an informative message is shown."""
        import requests as req_lib
        with self._mock_ipinfo():
            with self._mock_weather(raise_exc=req_lib.RequestException("timeout")):
                response = self.client.get(self.url)
        self.assertContains(response, "unavailable")

    def test_unknown_timezone_falls_back_gracefully(self):
        """If IPinfo returns a bogus timezone, home page still loads."""
        bad_details = FakeIPInfoDetails(timezone="Mars/Olympus")
        with self._mock_ipinfo(details=bad_details), self._mock_weather():
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    # ── X-Forwarded-For header ───────────────────────────────────────────────

    def test_x_forwarded_for_used_for_ip(self):
        """The home view should respect X-Forwarded-For when present."""
        with self._mock_ipinfo() as mock_handler_factory, self._mock_weather():
            self.client.get(
                self.url,
                HTTP_X_FORWARDED_FOR="203.0.113.42, 10.0.0.1",
            )
        mock_handler_factory.return_value.getDetails.assert_called_with("203.0.113.42")


# ---------------------------------------------------------------------------
# Tests: management command seed_catalog
# ---------------------------------------------------------------------------

class PopulateDbCommandTests(TestCase):

    def test_command_runs_and_creates_manufacturers(self):
        from io import StringIO
        from django.core.management import call_command
        from catalog.models import Manufacturer

        out = StringIO()
        call_command("seed_catalog", stdout=out)

        self.assertGreater(Manufacturer.objects.count(), 0)
        self.assertIn("Catalog seeded successfully!", out.getvalue())

    def test_command_creates_categories(self):
        from io import StringIO
        from django.core.management import call_command
        from catalog.models import Category

        out = StringIO()
        call_command("seed_catalog", stdout=out)

        self.assertGreater(Category.objects.count(), 0)

    def test_command_creates_products(self):
        from io import StringIO
        from django.core.management import call_command
        from catalog.models import Product

        out = StringIO()
        call_command("seed_catalog", stdout=out)

        self.assertGreater(Product.objects.count(), 0)

    def test_command_is_idempotent(self):
        """Running the command twice must not create duplicates."""
        from io import StringIO
        from django.core.management import call_command
        from catalog.models import Manufacturer, Category, Product

        call_command("seed_catalog", stdout=StringIO())
        count_m = Manufacturer.objects.count()
        count_c = Category.objects.count()
        count_p = Product.objects.count()

        call_command("seed_catalog", stdout=StringIO())
        self.assertEqual(Manufacturer.objects.count(), count_m)
        self.assertEqual(Category.objects.count(), count_c)
        self.assertEqual(Product.objects.count(), count_p)

