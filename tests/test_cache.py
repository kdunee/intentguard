import unittest
import os
import json
import hashlib
from intentguard.cache import (
    read_cache,
    write_cache,
    generate_cache_key,
    ensure_cache_dir_exists,
    CachedResult,
)


class TestCache(unittest.TestCase):
    def setUp(self):
        ensure_cache_dir_exists()
        self.cache_key = "test_key"
        self.cache_file = os.path.join(".intentguard", self.cache_key)
        self.test_data = {"result": True}

    def tearDown(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def test_write_cache(self):
        write_cache(self.cache_key, self.test_data)
        self.assertTrue(os.path.exists(self.cache_file))
        with open(self.cache_file, "r") as f:
            data = json.load(f)
        self.assertEqual(data, self.test_data)

    def test_read_cache(self):
        write_cache(self.cache_key, self.test_data)
        data = read_cache(self.cache_key)
        self.assertEqual(data, self.test_data)

    def test_generate_cache_key(self):
        expectation = "test_expectation"
        objects_text = "test_objects_text"
        options = type(
            "Options", (object,), {"model": "test_model", "num_evaluations": 1}
        )
        expected_key = hashlib.sha256(
            f"v1:{expectation}:{objects_text}:test_model:1".encode()
        ).hexdigest()
        generated_key = generate_cache_key(expectation, objects_text, options)
        self.assertEqual(generated_key, expected_key)

    def test_cached_result_to_dict(self):
        cached_result = CachedResult(result=True, explanation="Test explanation")
        result_dict = cached_result.to_dict()
        expected_dict = {"result": True, "explanation": "Test explanation"}
        self.assertEqual(result_dict, expected_dict)

    def test_cached_result_from_dict(self):
        data = {"result": True, "explanation": "Test explanation"}
        cached_result = CachedResult.from_dict(data)
        self.assertTrue(cached_result.result)
        self.assertEqual(cached_result.explanation, "Test explanation")


if __name__ == "__main__":
    unittest.main()
