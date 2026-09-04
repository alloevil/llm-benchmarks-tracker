#!/usr/bin/env python3
"""LLM Benchmarks 数据校验脚本"""

import json
import sys
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"

REQUIRED_FIELDS_MODEL = ["id", "name", "year", "description", "metrics", "difficulty"]
REQUIRED_FIELDS_AGENT = REQUIRED_FIELDS_MODEL + ["tags"]
REQUIRED_FIELDS_HARNESS = ["id", "name", "maintainer", "repo", "year", "description"]
VALID_DIFFICULTIES = {"easy", "medium", "hard", "expert"}
VALID_TYPES = {"model", "agent", "harness"}


def load_json(path: Path) -> dict:
    """加载 JSON 文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {path} - {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {path}")
        sys.exit(1)


def validate_model_benchmarks(data: dict) -> list[str]:
    """校验模型 benchmark 数据"""
    errors = []
    benchmarks = data.get("benchmarks", [])

    for i, b in enumerate(benchmarks):
        prefix = f"[model_benchmarks][{i}] {b.get('id', '?')}"

        for field in REQUIRED_FIELDS_MODEL:
            if field not in b:
                errors.append(f"{prefix}: 缺少必填字段 '{field}'")

        if "difficulty" in b and b["difficulty"] not in VALID_DIFFICULTIES:
            errors.append(f"{prefix}: 无效的 difficulty '{b['difficulty']}'，可选: {VALID_DIFFICULTIES}")

        if "year" in b and not (2017 <= b["year"] <= 2027):
            errors.append(f"{prefix}: year {b['year']} 不在合理范围")

        if "metrics" in b and not isinstance(b["metrics"], list):
            errors.append(f"{prefix}: metrics 必须是数组")

        if "current_sota" in b:
            sota = b["current_sota"]
            if not isinstance(sota, dict):
                errors.append(f"{prefix}: current_sota 必须是对象")
            elif "score" not in sota or "model" not in sota:
                errors.append(f"{prefix}: current_sota 需要 score 和 model 字段")

    return errors


def validate_agent_benchmarks(data: dict) -> list[str]:
    """校验 Agent benchmark 数据"""
    errors = []
    benchmarks = data.get("benchmarks", [])

    for i, b in enumerate(benchmarks):
        prefix = f"[agent_benchmarks][{i}] {b.get('id', '?')}"

        for field in REQUIRED_FIELDS_AGENT:
            if field not in b:
                errors.append(f"{prefix}: 缺少必填字段 '{field}'")

        if "difficulty" in b and b["difficulty"] not in VALID_DIFFICULTIES:
            errors.append(f"{prefix}: 无效的 difficulty '{b['difficulty']}'")

        if "tags" in b and not isinstance(b["tags"], list):
            errors.append(f"{prefix}: tags 必须是数组")

    return errors


def validate_harnesses(data: dict) -> list[str]:
    """校验 Harness 数据"""
    errors = []
    harnesses = data.get("harnesses", [])

    for i, h in enumerate(harnesses):
        prefix = f"[harnesses][{i}] {h.get('id', '?')}"

        for field in REQUIRED_FIELDS_HARNESS:
            if field not in h:
                errors.append(f"{prefix}: 缺少必填字段 '{field}'")

        if "supported_benchmarks" in h and not isinstance(h["supported_benchmarks"], list):
            errors.append(f"{prefix}: supported_benchmarks 必须是数组")

    return errors


def validate_timeline(data: dict) -> list[str]:
    """校验时间线数据"""
    errors = []
    timeline = data.get("timeline", [])

    for entry in timeline:
        if "year" not in entry:
            errors.append("[timeline]: 缺少 year 字段")
            continue
        if "events" not in entry:
            errors.append(f"[timeline][{entry['year']}]: 缺少 events 字段")
            continue

        for event in entry["events"]:
            if "id" not in event:
                errors.append(f"[timeline][{entry['year']}]: event 缺少 id")
            if "type" not in event:
                errors.append(f"[timeline][{entry['year']}][{event.get('id', '?')}]: 缺少 type")
            elif event["type"] not in VALID_TYPES:
                errors.append(f"[timeline][{entry['year']}][{event.get('id', '?')}]: 无效 type '{event['type']}'")

    return errors


def validate_cross_references(model_data: dict, agent_data: dict, timeline_data: dict) -> list[str]:
    """校验跨文件引用一致性"""
    errors = []

    model_ids = {b["id"] for b in model_data.get("benchmarks", [])}
    agent_ids = {b["id"] for b in agent_data.get("benchmarks", [])}
    all_benchmark_ids = model_ids | agent_ids

    timeline_ids = set()
    for entry in timeline_data.get("timeline", []):
        for event in entry.get("events", []):
            if event.get("type") in ("model", "agent"):
                timeline_ids.add(event["id"])

    # 时间线中引用了不存在的 benchmark
    missing = timeline_ids - all_benchmark_ids
    if missing:
        errors.append(f"[timeline] 引用了不存在的 benchmark: {missing}")

    # benchmark 没在时间线中出现
    not_in_timeline = all_benchmark_ids - timeline_ids
    if not_in_timeline:
        errors.append(f"[timeline] 以下 benchmark 未在时间线中出现: {not_in_timeline}")

    # 检查 ID 唯一性
    model_id_list = [b["id"] for b in model_data.get("benchmarks", [])]
    agent_id_list = [b["id"] for b in agent_data.get("benchmarks", [])]

    for id_list, name in [(model_id_list, "model"), (agent_id_list, "agent")]:
        seen = set()
        for id_ in id_list:
            if id_ in seen:
                errors.append(f"[{name}] 重复 ID: {id_}")
            seen.add(id_)

    return errors


def main():
    all_errors = []

    print("🔍 校验 LLM Benchmarks 数据...\n")

    # 加载数据
    model_data = load_json(DATA_DIR / "model_benchmarks.json")
    agent_data = load_json(DATA_DIR / "agent_benchmarks.json")
    harness_data = load_json(DATA_DIR / "harnesses.json")
    timeline_data = load_json(DATA_DIR / "timeline.json")

    # 校验
    all_errors.extend(validate_model_benchmarks(model_data))
    all_errors.extend(validate_agent_benchmarks(agent_data))
    all_errors.extend(validate_harnesses(harness_data))
    all_errors.extend(validate_timeline(timeline_data))
    all_errors.extend(validate_cross_references(model_data, agent_data, timeline_data))

    # 统计
    model_count = len(model_data.get("benchmarks", []))
    agent_count = len(agent_data.get("benchmarks", []))
    harness_count = len(harness_data.get("harnesses", []))
    timeline_years = len(timeline_data.get("timeline", []))

    print(f"📊 统计:")
    print(f"   模型 Benchmark: {model_count}")
    print(f"   Agent Benchmark: {agent_count}")
    print(f"   Harness: {harness_count}")
    print(f"   时间线年份: {timeline_years}")
    print()

    if all_errors:
        print(f"❌ 发现 {len(all_errors)} 个错误:")
        for error in all_errors:
            print(f"   • {error}")
        sys.exit(1)
    else:
        print("✅ 所有数据校验通过!")
        sys.exit(0)


if __name__ == "__main__":
    main()
