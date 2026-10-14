import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from pastry_shop.env import load_env


class LoadEnvTestCase(TestCase):
    def setUp(self):
        self.orig_environ = dict(os.environ)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.orig_environ)

    def test_load_env_sets_variables(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text(
                "TEST_LOAD_ENV_FOO=bar\n"
                "TEST_LOAD_ENV_NUM=12345\n",
                encoding="utf-8",
            )
            # Ensure not in environ before
            os.environ.pop("TEST_LOAD_ENV_FOO", None)
            os.environ.pop("TEST_LOAD_ENV_NUM", None)

            load_env(env_file)

            self.assertEqual(os.environ.get("TEST_LOAD_ENV_FOO"), "bar")
            self.assertEqual(os.environ.get("TEST_LOAD_ENV_NUM"), "12345")

    def test_load_env_does_not_overwrite_existing_variables(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text(
                "DEPLOY_CONFIG_VAR=from_file\n",
                encoding="utf-8",
            )
            os.environ["DEPLOY_CONFIG_VAR"] = "from_deploy_environment"

            load_env(env_file)

            self.assertEqual(os.environ.get("DEPLOY_CONFIG_VAR"), "from_deploy_environment")

    def test_load_env_missing_file_does_not_raise(self):
        missing_path = Path("/tmp/does_not_exist_pastry_test.env")
        # Should return silently without exception
        load_env(missing_path)

    def test_fallback_parser_without_dotenv(self):
        """Simulate environment where python-dotenv is not installed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_file = Path(tmp_dir) / ".env"
            env_file.write_text(
                "# Leading comment\n"
                "\n"
                "FALLBACK_VAR1=plain_value\n"
                'FALLBACK_VAR2="double_quoted"\n'
                "FALLBACK_VAR3='single_quoted'\n"
                "export FALLBACK_VAR4=exported\n",
                encoding="utf-8",
            )
            os.environ.pop("FALLBACK_VAR1", None)
            os.environ.pop("FALLBACK_VAR2", None)
            os.environ.pop("FALLBACK_VAR3", None)
            os.environ.pop("FALLBACK_VAR4", None)

            # Block import of dotenv to trigger fallback parser
            with patch.dict("sys.modules", {"dotenv": None}):
                load_env(env_file)

            self.assertEqual(os.environ.get("FALLBACK_VAR1"), "plain_value")
            self.assertEqual(os.environ.get("FALLBACK_VAR2"), "double_quoted")
            self.assertEqual(os.environ.get("FALLBACK_VAR3"), "single_quoted")
            self.assertEqual(os.environ.get("FALLBACK_VAR4"), "exported")
