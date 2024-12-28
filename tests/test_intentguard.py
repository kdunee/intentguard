import logging
import unittest

from intentguard import IntentGuard, IntentGuardOptions

logging.basicConfig(level=logging.INFO)


class TestIntentGuard(unittest.TestCase):
    def setUp(self):
        self.options = IntentGuardOptions(num_evaluations=3)
        self.guard = IntentGuard(self.options)

    def test_assert_code_true(self):
        self.guard.assert_code(
            "{class} should provide a functionality of verifying code properties through natural language assertions",
            {"class": IntentGuard},
        )

    def test_assert_code_false(self):
        with self.assertRaises(AssertionError) as cm:
            self.guard.assert_code(
                "{class} should not have any methods", {"class": IntentGuard}
            )
        self.assertIn("Explanation:", str(cm.exception))

    def test_guard_options(self):
        self.guard.assert_code(
            "{options} should have a num_evaluations field",
            {"options": IntentGuardOptions},
        )

    def test_assert_code_with_multiple_objects(self):
        self.guard.assert_code(
            "{class} should use the num_evaluations field from {options} to perform multiple inferences",
            {
                "class": IntentGuard,
                "options": IntentGuardOptions,
            },
        )

    def test_different_num_evaluations(self):
        self.guard.assert_code(
            "{class} should determine consensus based on `num_evaluations` evaluations",
            {"class": IntentGuard},
        )

    def test_custom_options(self):
        custom_options = IntentGuardOptions(num_evaluations=5)
        self.guard.assert_code(
            "{class} should accept custom options",
            {"class": IntentGuard},
            options=custom_options,
        )


if __name__ == "__main__":
    unittest.main()
