import unittest
from ailinttest import AILintTest, AILintTestOptions


class TestAILintTest(unittest.TestCase):
    def setUp(self):
        self.options = AILintTestOptions(quorum_size=3, model="gpt-4o-mini")
        self.ailint = AILintTest(self.options)

    def test_assert_code_true(self):
        self.ailint.assert_code(
            "{class} should provide a functionality of verifying code properties through natural language assertions",
            {"class": AILintTest},
        )

    def test_assert_code_false(self):
        with self.assertRaises(AssertionError):
            self.ailint.assert_code(
                "{class} should not have any methods", {"class": AILintTest}
            )

    def test_ailint_options(self):
        self.ailint.assert_code(
            "{options} should have a quorum_size field",
            {"options": AILintTestOptions},
        )

    def test_assert_code_with_multiple_objects(self):
        self.ailint.assert_code(
            "{class} should use the quorum_size field from {options} to perform multiple inferences",
            {
                "class": AILintTest,
                "options": AILintTestOptions,
            },
        )

    def test_different_quorum_sizes(self):
        for quorum_size in [1, 5, 10]:
            options = AILintTestOptions(quorum_size=quorum_size, model="gpt-4o-mini")
            ailint = AILintTest(options)
            ailint.assert_code(
                "{class} should work with different quorum sizes",
                {"class": AILintTest},
            )

    def test_custom_options(self):
        custom_options = AILintTestOptions(quorum_size=5, model="gpt-4o-mini")
        self.ailint.assert_code(
            "{class} should accept custom options",
            {"class": AILintTest},
            options=custom_options,
        )


if __name__ == "__main__":
    unittest.main()
