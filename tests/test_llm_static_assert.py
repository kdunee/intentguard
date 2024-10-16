import unittest
from llm_static_assert.llm_static_assert import LLMStaticAssert
from llm_static_assert.llm_static_assert_options import LLMStaticAssertOptions


class TestLLMStaticAssert(unittest.TestCase):
    def setUp(self):
        self.options = LLMStaticAssertOptions(quorum_size=3, model="gpt-4o-mini")
        self.lsa = LLMStaticAssert(self.options)

    def test_static_assert_true(self):
        try:
            self.lsa.static_assert(
                "{class} should provide a functionality of performing static analysis using an LLM",
                {"class": LLMStaticAssert},
            )
        except AssertionError:
            self.fail("static_assert raised AssertionError unexpectedly")

    def test_static_assert_false(self):
        with self.assertRaises(AssertionError):
            self.lsa.static_assert(
                "{class} should not have any methods", {"class": LLMStaticAssert}
            )

    def test_static_assert_options(self):
        try:
            self.lsa.static_assert(
                "{options} should have a quorum_size field",
                {"options": LLMStaticAssertOptions},
            )
        except AssertionError:
            self.fail("static_assert raised AssertionError unexpectedly")

    def test_static_assert_with_multiple_objects(self):
        try:
            self.lsa.static_assert(
                "{class} should use the quorum_size field from {options} to perform multiple inferences",
                {
                    "class": LLMStaticAssert,
                    "options": LLMStaticAssertOptions,
                },
            )
        except AssertionError:
            self.fail("static_assert raised AssertionError unexpectedly")

    def test_different_quorum_sizes(self):
        for quorum_size in [1, 5, 10]:
            options = LLMStaticAssertOptions(
                quorum_size=quorum_size, model="gpt-4o-mini"
            )
            lsa = LLMStaticAssert(options)
            try:
                lsa.static_assert(
                    "{class} should work with different quorum sizes",
                    {"class": LLMStaticAssert},
                )
            except AssertionError:
                self.fail(f"static_assert failed with quorum_size {quorum_size}")

    def test_custom_options_in_static_assert(self):
        custom_options = LLMStaticAssertOptions(quorum_size=5, model="gpt-4o-mini")
        try:
            self.lsa.static_assert(
                "{class} should accept custom options",
                {"class": LLMStaticAssert},
                options=custom_options,
            )
        except AssertionError:
            self.fail("static_assert failed with custom options")


if __name__ == "__main__":
    unittest.main()
