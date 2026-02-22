#!/usr/bin/env python3
"""test_template_engine.py — 模板引擎单元测试"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import doc_workflow as dw


class TestSimpleVariables(unittest.TestCase):
    def test_basic_replace(self):
        self.assertEqual(dw.render_template("Hello {{name}}", {"name": "World"}), "Hello World")

    def test_missing_var_preserved(self):
        """未匹配变量保留原样"""
        self.assertEqual(dw.render_template("{{missing}}", {}), "{{missing}}")

    def test_dotted_path(self):
        ctx = {"summary": {"total": 42}}
        self.assertEqual(dw.render_template("Total: {{summary.total}}", ctx), "Total: 42")

    def test_chinese_field_name(self):
        self.assertEqual(dw.render_template("{{门店名称}}", {"门店名称": "北京01店"}), "北京01店")

    def test_number_formatting(self):
        self.assertEqual(dw.render_template("{{val}}", {"val": 3.0}), "3")
        self.assertEqual(dw.render_template("{{val}}", {"val": 3.14}), "3.14")

    def test_list_value(self):
        self.assertEqual(dw.render_template("{{tags}}", {"tags": ["a", "b"]}), "a, b")

    def test_none_value(self):
        self.assertEqual(dw.render_template("{{x}}", {"x": None}), "{{x}}")


class TestBuiltinVariables(unittest.TestCase):
    def test_today_format(self):
        result = dw.render_template("{{TODAY}}", {})
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2}")

    def test_now_format(self):
        result = dw.render_template("{{NOW}}", {})
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")

    def test_week_start_end(self):
        result = dw.render_template("{{WEEK_START}} ~ {{WEEK_END}}", {})
        self.assertIn("~", result)
        self.assertNotIn("{{", result)


class TestEachLoop(unittest.TestCase):
    def test_basic_loop(self):
        tpl = "{{#each items}}[{{name}}]{{/each}}"
        ctx = {"items": [{"name": "A"}, {"name": "B"}]}
        self.assertEqual(dw.render_template(tpl, ctx), "[A]\n[B]")

    def test_loop_with_index(self):
        tpl = "{{#each items}}{{@index}}.{{name}}{{/each}}"
        ctx = {"items": [{"name": "X"}, {"name": "Y"}]}
        self.assertEqual(dw.render_template(tpl, ctx), "0.X\n1.Y")

    def test_loop_simple_values(self):
        tpl = "{{#each tags}}- {{this}}{{/each}}"
        ctx = {"tags": ["alpha", "beta"]}
        self.assertEqual(dw.render_template(tpl, ctx), "- alpha\n- beta")

    def test_empty_list(self):
        tpl = "before{{#each items}}X{{/each}}after"
        self.assertEqual(dw.render_template(tpl, {"items": []}), "beforeafter")

    def test_missing_list(self):
        tpl = "{{#each nope}}X{{/each}}"
        self.assertEqual(dw.render_template(tpl, {}), "")

    def test_skip_all_empty_records(self):
        tpl = "{{#each items}}[{{a}}]{{/each}}"
        ctx = {"items": [{"a": None}, {"a": "ok"}]}
        self.assertEqual(dw.render_template(tpl, ctx), "[ok]")


class TestIfCondition(unittest.TestCase):
    def test_truthy(self):
        tpl = "{{#if show}}YES{{/if}}"
        self.assertEqual(dw.render_template(tpl, {"show": True}), "YES")

    def test_falsy_none(self):
        tpl = "{{#if show}}YES{{/if}}"
        self.assertEqual(dw.render_template(tpl, {"show": None}), "")

    def test_falsy_missing(self):
        tpl = "{{#if show}}YES{{/if}}"
        self.assertEqual(dw.render_template(tpl, {}), "")

    def test_falsy_empty_list(self):
        tpl = "{{#if items}}HAS{{/if}}"
        self.assertEqual(dw.render_template(tpl, {"items": []}), "")

    def test_chinese_field_if(self):
        tpl = "{{#if 状态}}有状态{{/if}}"
        self.assertEqual(dw.render_template(tpl, {"状态": "完成"}), "有状态")

    def test_inner_if_in_each(self):
        tpl = "{{#each items}}{{#if tag}}[{{tag}}]{{/if}}{{/each}}"
        ctx = {"items": [{"tag": "A"}, {"tag": ""}, {"tag": "C"}]}
        result = dw.render_template(tpl, ctx)
        self.assertIn("[A]", result)
        self.assertIn("[C]", result)
        self.assertNotIn("[]", result)


class TestResolveHelpers(unittest.TestCase):
    def test_to_str_none(self):
        self.assertEqual(dw._to_str(None), "")

    def test_to_str_int_float(self):
        self.assertEqual(dw._to_str(5.0), "5")
        self.assertEqual(dw._to_str(3.14), "3.14")

    def test_extract_display_value_rich_text(self):
        raw = [{"text": "hello "}, {"text": "world"}]
        self.assertEqual(dw._extract_display_value(raw, 1), "hello world")

    def test_extract_display_value_person(self):
        raw = [{"name": "Alice"}, {"name": "Bob"}]
        self.assertEqual(dw._extract_display_value(raw, 11), "Alice, Bob")

    def test_extract_display_value_url(self):
        raw = {"text": "Google", "link": "https://google.com"}
        self.assertEqual(dw._extract_display_value(raw, 15), "Google")


if __name__ == "__main__":
    unittest.main()
