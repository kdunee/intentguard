import unittest
from intentguard import IntentGuard, IntentGuardOptions
from intentguard.cache import generate_cache_key, read_cache, write_cache


class TestIntentGuard(unittest.TestCase):
    def setUp(self):
        self.options = IntentGuardOptions(quorum_size=3)
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
            "{options} should have a quorum_size field",
            {"options": IntentGuardOptions},
        )

    def test_assert_code_with_multiple_objects(self):
        self.guard.assert_code(
            "{class} should use the quorum_size field from {options} to perform multiple inferences",
            {
                "class": IntentGuard,
                "options": IntentGuardOptions,
            },
        )

    def test_different_quorum_sizes(self):
        for quorum_size in [1, 5, 10]:
            options = IntentGuardOptions(quorum_size=quorum_size)
            guard = IntentGuard(options)
            guard.assert_code(
                "{class} should work with different quorum sizes",
                {"class": IntentGuard},
            )

    def test_custom_options(self):
        custom_options = IntentGuardOptions(quorum_size=5, model="gpt-4o-mini")
        self.guard.assert_code(
            "{class} should accept custom options",
            {"class": IntentGuard},
            options=custom_options,
        )

    def test_cache_key_generation(self):
        expectation = "test_expectation"
        objects_text = "test_objects_text"
        options = IntentGuardOptions(model="test_model", quorum_size=1)
        cache_key = generate_cache_key(expectation, objects_text, options)
        self.assertIsInstance(cache_key, str)
        self.assertEqual(len(cache_key), 64)  # SHA-256 hash length

    def test_cache_retrieval(self):
        expectation = "test_expectation"
        objects_text = "test_objects_text"
        options = IntentGuardOptions(model="test_model", quorum_size=1)
        cache_key = generate_cache_key(expectation, objects_text, options)
        result = {"result": True}
        write_cache(cache_key, result)
        cached_result = read_cache(cache_key)
        self.assertEqual(cached_result, result)

    def test_cache_invalidation(self):
        expectation = "test_expectation"
        objects_text = "test_objects_text"
        options = IntentGuardOptions(model="test_model", quorum_size=1)
        cache_key = generate_cache_key(expectation, objects_text, options)
        result = {"result": True}
        write_cache(cache_key, result)
        cached_result = read_cache(cache_key)
        self.assertEqual(cached_result, result)

        # Simulate code change by modifying objects_text
        new_objects_text = "new_test_objects_text"
        new_cache_key = generate_cache_key(expectation, new_objects_text, options)
        new_cached_result = read_cache(new_cache_key)
        self.assertIsNone(new_cached_result)


if __name__ == "__main__":
    unittest.main()
