#!/usr/bin/env python3
"""test_bitable_engine.py — Bitable 引擎单元测试（纯本地逻辑，不调 API）"""

import csv
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import bitable_engine as be


class TestLoadRecordsFromCSV(unittest.TestCase):
    def _write_csv(self, rows, header):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        f.close()
        return f.name

    def test_basic_csv(self):
        path = self._write_csv([{"名称": "A", "价格": "100"}], ["名称", "价格"])
        records = be.load_records_from_file(path)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["名称"], "A")
        self.assertEqual(records[0]["价格"], 100)  # auto int conversion
        os.unlink(path)

    def test_float_csv(self):
        path = self._write_csv([{"val": "3.14"}], ["val"])
        records = be.load_records_from_file(path)
        self.assertAlmostEqual(records[0]["val"], 3.14)
        os.unlink(path)

    def test_text_csv(self):
        path = self._write_csv([{"name": "hello world"}], ["name"])
        records = be.load_records_from_file(path)
        self.assertEqual(records[0]["name"], "hello world")
        os.unlink(path)

    def test_empty_csv(self):
        path = self._write_csv([], ["a", "b"])
        records = be.load_records_from_file(path)
        self.assertEqual(records, [])
        os.unlink(path)


class TestLoadRecordsFromJSON(unittest.TestCase):
    def _write_json(self, data):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(data, f, ensure_ascii=False)
        f.close()
        return f.name

    def test_array_json(self):
        path = self._write_json([{"a": 1}, {"a": 2}])
        records = be.load_records_from_file(path)
        self.assertEqual(len(records), 2)
        os.unlink(path)

    def test_object_with_records_key(self):
        path = self._write_json({"records": [{"x": "y"}]})
        records = be.load_records_from_file(path)
        self.assertEqual(len(records), 1)
        os.unlink(path)

    def test_invalid_json_structure(self):
        path = self._write_json({"no_records": True})
        with self.assertRaises(ValueError):
            be.load_records_from_file(path)
        os.unlink(path)

    def test_unsupported_extension(self):
        f = tempfile.NamedTemporaryFile(suffix=".xml", delete=False)
        f.close()
        with self.assertRaises(ValueError):
            be.load_records_from_file(f.name)
        os.unlink(f.name)


class TestExtractTextValue(unittest.TestCase):
    def test_none(self):
        self.assertIsNone(be._extract_text_value(None))

    def test_string(self):
        self.assertEqual(be._extract_text_value("hello"), "hello")

    def test_number(self):
        self.assertEqual(be._extract_text_value(42), "42")
        self.assertEqual(be._extract_text_value(3.14), "3.14")

    def test_rich_text_list(self):
        val = [{"text": "hello "}, {"text": "world"}]
        self.assertEqual(be._extract_text_value(val), "hello world")

    def test_string_list(self):
        self.assertEqual(be._extract_text_value(["a", "b"]), "ab")

    def test_empty_list(self):
        self.assertIsNone(be._extract_text_value([]))

    def test_dict_with_text(self):
        self.assertEqual(be._extract_text_value({"text": "ok"}), "ok")

    def test_dict_with_value(self):
        self.assertEqual(be._extract_text_value({"value": "v"}), "v")


class TestFieldTypeName(unittest.TestCase):
    def test_known_types(self):
        self.assertEqual(be._field_type_name(1), "Text")
        self.assertEqual(be._field_type_name(2), "Number")
        self.assertEqual(be._field_type_name(3), "SingleSelect")
        self.assertEqual(be._field_type_name(5), "DateTime")

    def test_unknown_type(self):
        self.assertEqual(be._field_type_name(9999), "Unknown(9999)")


class TestBatchCreateDryRun(unittest.TestCase):
    def test_dry_run_returns_preview(self):
        result = be.batch_create("app", "table", [{"a": 1}, {"b": 2}], dry_run=True)
        self.assertEqual(result["would_create"], 2)
        self.assertIn("sample", result)

    def test_empty_records(self):
        result = be.batch_create("app", "table", [])
        self.assertEqual(result["created"], 0)


class TestBatchUpdateDryRun(unittest.TestCase):
    def test_dry_run(self):
        updates = [{"record_id": "r1", "fields": {"a": 1}}]
        result = be.batch_update("app", "table", updates, dry_run=True)
        self.assertEqual(result["would_update"], 1)

    def test_empty_updates(self):
        result = be.batch_update("app", "table", [])
        self.assertEqual(result["updated"], 0)


if __name__ == "__main__":
    unittest.main()
