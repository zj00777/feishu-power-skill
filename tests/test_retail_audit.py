#!/usr/bin/env python3
"""test_retail_audit.py — 零售审计引擎单元测试"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import retail_audit as ra


def _store(**kw):
    """快速构造门店数据"""
    defaults = {
        "门店名称": "测试店", "期初库存": 100, "销售数量": 50,
        "当前库存": 50, "上架天数": 14, "实际销售额": 10000,
        "目标销售额": 20000, "总SKU数": 100, "有销SKU数": 70,
        "平均库存金额": 50000, "日均销售成本": 1000, "营业状态": "营业",
    }
    defaults.update(kw)
    return defaults


class TestRuleCheckers(unittest.TestCase):
    """测试各审计规则的触发逻辑"""

    def setUp(self):
        self.cfg = ra.load_config()
        self.fm = self.cfg["field_mapping"]

    def test_sell_through_high_triggers(self):
        store = _store(期初库存=100, 销售数量=95, 当前库存=5)
        t = {"sell_through_min": 0.85, "days_left_max": 3}
        result = ra.RULE_CHECKERS["sell_through_high"](store, {"daily_avg_sold": 10}, t, self.fm)
        self.assertIsNotNone(result)
        self.assertIn("售罄率", result["指标"])

    def test_sell_through_high_no_trigger(self):
        store = _store(期初库存=100, 销售数量=50, 当前库存=50)
        t = {"sell_through_min": 0.85, "days_left_max": 3}
        result = ra.RULE_CHECKERS["sell_through_high"](store, {"daily_avg_sold": 5}, t, self.fm)
        self.assertIsNone(result)

    def test_sell_through_low_triggers(self):
        store = _store(期初库存=100, 销售数量=10, 上架天数=20)
        t = {"sell_through_max": 0.20, "days_on_shelf_min": 14}
        result = ra.RULE_CHECKERS["sell_through_low"](store, {}, t, self.fm)
        self.assertIsNotNone(result)

    def test_sell_through_low_no_trigger_short_shelf(self):
        store = _store(期初库存=100, 销售数量=10, 上架天数=5)
        t = {"sell_through_max": 0.20, "days_on_shelf_min": 14}
        result = ra.RULE_CHECKERS["sell_through_low"](store, {}, t, self.fm)
        self.assertIsNone(result)

    def test_target_achievement_low_triggers(self):
        store = _store(实际销售额=5000, 目标销售额=20000)
        t = {"achievement_min": 0.60}
        result = ra.RULE_CHECKERS["target_achievement_low"](store, {}, t, self.fm)
        self.assertIsNotNone(result)
        self.assertIn("达成率", result["指标"])

    def test_target_achievement_ok(self):
        store = _store(实际销售额=15000, 目标销售额=20000)
        t = {"achievement_min": 0.60}
        result = ra.RULE_CHECKERS["target_achievement_low"](store, {}, t, self.fm)
        self.assertIsNone(result)

    def test_negative_inventory(self):
        store = _store(当前库存=-10)
        result = ra.RULE_CHECKERS["negative_inventory"](store, {}, {}, self.fm)
        self.assertIsNotNone(result)

    def test_positive_inventory_ok(self):
        result = ra.RULE_CHECKERS["negative_inventory"](_store(), {}, {}, self.fm)
        self.assertIsNone(result)

    def test_zero_sales_triggers(self):
        store = _store(实际销售额=0, 营业状态="营业")
        result = ra.RULE_CHECKERS["zero_sales"](store, {}, {}, self.fm)
        self.assertIsNotNone(result)

    def test_zero_sales_closed_store_ok(self):
        store = _store(实际销售额=0, 营业状态="停业")
        result = ra.RULE_CHECKERS["zero_sales"](store, {}, {}, self.fm)
        self.assertIsNone(result)

    def test_inventory_turnover_slow(self):
        store = _store(平均库存金额=100000, 日均销售成本=1000)
        t = {"turnover_days_max": 45}
        result = ra.RULE_CHECKERS["inventory_turnover_slow"](store, {}, t, self.fm)
        self.assertIsNotNone(result)  # 100 days > 45

    def test_inventory_turnover_ok(self):
        store = _store(平均库存金额=30000, 日均销售成本=1000)
        t = {"turnover_days_max": 45}
        result = ra.RULE_CHECKERS["inventory_turnover_slow"](store, {}, t, self.fm)
        self.assertIsNone(result)  # 30 days < 45

    def test_low_sell_rate(self):
        store = _store(总SKU数=100, 有销SKU数=40)
        t = {"sell_rate_min": 0.60}
        result = ra.RULE_CHECKERS["low_sell_rate"](store, {}, t, self.fm)
        self.assertIsNotNone(result)

    def test_sell_rate_ok(self):
        store = _store(总SKU数=100, 有销SKU数=80)
        t = {"sell_rate_min": 0.60}
        result = ra.RULE_CHECKERS["low_sell_rate"](store, {}, t, self.fm)
        self.assertIsNone(result)


class TestRunAudit(unittest.TestCase):
    def test_healthy_store(self):
        stores = [_store(
            期初库存=100, 销售数量=60, 当前库存=40, 上架天数=14,
            实际销售额=15000, 目标销售额=20000,
            总SKU数=100, 有销SKU数=80,
            平均库存金额=30000, 日均销售成本=1000,
        )]
        result = ra.run_audit(stores)
        self.assertEqual(result["summary"]["healthy"], 1)
        self.assertEqual(len(result["alerts"]), 0)

    def test_multiple_alerts(self):
        stores = [_store(
            期初库存=100, 销售数量=5, 当前库存=-3, 上架天数=20,
            实际销售额=0, 目标销售额=20000,
            总SKU数=100, 有销SKU数=30,
            平均库存金额=100000, 日均销售成本=500,
        )]
        result = ra.run_audit(stores)
        self.assertGreater(len(result["alerts"]), 3)
        self.assertEqual(result["summary"]["healthy"], 0)

    def test_scoring(self):
        stores = [_store(当前库存=-5)]  # negative inventory = critical = -25
        result = ra.run_audit(stores)
        scores = result["store_scores"]
        self.assertEqual(len(scores), 1)
        self.assertLessEqual(scores[0]["评分"], 75)

    def test_demo_data_runs(self):
        stores = ra.generate_demo_data(10)
        result = ra.run_audit(stores)
        self.assertEqual(result["total_stores"], 10)
        self.assertEqual(len(result["store_scores"]), 10)


class TestReportGeneration(unittest.TestCase):
    def test_markdown_report_structure(self):
        stores = ra.generate_demo_data(5)
        result = ra.run_audit(stores)
        md = ra.generate_report_markdown(result)
        self.assertIn("门店运营诊断报告", md)
        self.assertIn("总览", md)
        self.assertIn("门店健康排名", md)

    def test_empty_stores(self):
        result = ra.run_audit([])
        md = ra.generate_report_markdown(result)
        self.assertIn("门店总数：0", md)


class TestConfigLoading(unittest.TestCase):
    def test_default_config(self):
        cfg = ra.load_config()
        self.assertIn("rules", cfg)
        self.assertIn("field_mapping", cfg)
        self.assertEqual(cfg["industry"], "服装零售")

    def test_fmcg_config(self):
        fmcg_path = os.path.join(os.path.dirname(__file__), "..", "configs", "fmcg.yaml")
        cfg = ra.load_config(fmcg_path)
        self.assertEqual(cfg["industry"], "快消零售")
        self.assertEqual(cfg["rules"]["inventory_turnover_slow"]["thresholds"]["turnover_days_max"], 21)

    def test_missing_config_uses_builtin(self):
        cfg = ra.load_config("/nonexistent/path.yaml")
        self.assertIn("rules", cfg)

    def test_disabled_rule_skipped(self):
        cfg = ra.load_config()
        cfg["rules"]["negative_inventory"]["enabled"] = False
        stores = [_store(当前库存=-10)]
        result = ra.run_audit(stores, config=cfg)
        types = [a["异常类型"] for a in result["alerts"]]
        self.assertNotIn("负库存", types)


if __name__ == "__main__":
    unittest.main()
