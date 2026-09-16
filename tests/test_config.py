from unittest import TestCase

from coursecarry.config import AppConfig, validate_provider_url
from coursecarry.providers import BrightspaceProvider, NPBrightspaceProvider, create_provider


class ProviderConfigurationTests(TestCase):
    def test_np_preset_uses_tested_provider(self) -> None:
        config = AppConfig()
        self.assertIsInstance(create_provider(config), NPBrightspaceProvider)
        self.assertEqual(config.provider_label, "Ngee Ann Polytechnic (tested)")

    def test_custom_preset_is_explicitly_untested(self) -> None:
        config = AppConfig(
            provider_id="custom_brightspace",
            institution_name="Example Institute (untested)",
            base_url="https://portal.example.invalid/",
            lms_base_url="https://lms.example.invalid",
        )
        self.assertIsInstance(create_provider(config), BrightspaceProvider)
        self.assertEqual(config.provider_label, "Example Institute (untested)")

    def test_provider_urls_require_https_without_credentials(self) -> None:
        self.assertEqual(
            validate_provider_url("https://lms.example.invalid", "LMS"),
            "https://lms.example.invalid",
        )
        with self.assertRaises(ValueError):
            validate_provider_url("http://lms.example.invalid", "LMS")
        with self.assertRaises(ValueError):
            validate_provider_url("https://student:secret@lms.example.invalid", "LMS")
