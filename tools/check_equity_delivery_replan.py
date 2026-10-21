"""Check the equity-only planning allocation; does not run feature code."""

from __future__ import annotations

import json
from pathlib import Path
import re


def check(root: Path) -> dict[str, int | str]:
    data = json.loads((root / "docs/plans/equity-delivery-replan.json").read_text(encoding="utf-8"))
    assert data["status"] == "draft_proposal_tracker_migration_pending"
    assert data["scope"] == "equity_only" and data["governance_issue"] == 567
    assert data["active_r18_preserved"] and data["r18_dependencies_unchanged"]
    assert data["historical_releases_preserved"]
    releases = data["releases"]
    assert [release["id"] for release in releases] == [f"EF{i}" for i in range(1, 10)]
    stories = [story for release in releases for story in release["existing_stories"]]
    expected = {f"EQ-{i}" for i in range(147, 182)}
    assert len(stories) == 35 and {story["story"] for story in stories} == expected
    assert len({story["issue"] for story in stories}) == 35
    owners = {story["story"]: release["id"] for release in releases for story in release["existing_stories"]}
    assert owners["EQ-164"] == "EF1"
    assert owners["EQ-170"] == "EF3" and owners["EQ-172"] == "EF5"
    assert owners["EQ-171"] == "EF6" and owners["EQ-173"] == "EF7"
    assert owners["EQ-174"] == owners["EQ-175"] == "EF8"
    assert all(owners[f"EQ-{i}"] == "EF9" for i in range(176, 182))
    tasks = [task for release in releases for task in release["proposed_tasks"]]
    assert len(tasks) == 22 and len({task["planning_key"] for task in tasks}) == 22
    for release in releases:
        assert release["state"] == "proposed_allocation_not_migrated"
        assert release["milestone_number"] is None and release["epic_issue"] is None
        assert set(release["layers"]) == {"libraries", "io", "workers"}
        assert release["demo_required"] and not release["api_required"]
        own_keys = {task["planning_key"] for task in release["proposed_tasks"]}
        own_stories = {story["story"] for story in release["existing_stories"]}
        assert release["acceptance_gate"] in own_keys | own_stories
        assert {"io", "workers"} <= {task["layer"] for task in release["proposed_tasks"]}
    for story in stories:
        assert story["observed_status"] == "Backlog"
        assert story["url"] == f"https://github.com/atulsrivas1/equity-features/issues/{story['issue']}"
        assert story["story"] in story["title"]
        assert all(re.fullmatch(r"EQ-\d+", dep) for dep in story["existing_dependencies"])
    for task in tasks:
        assert task["github_issue"] is None and task["state"] == "proposed_not_created"
        assert task["acceptance"] and task["before_ready"]
    for amendment in data["dependency_amendments"]:
        assert amendment["story"] in expected
        assert amendment["effective"] == "only_after_reviewed_publication_and_explicit_tracker_migration"
        assert not any(dep in {"EQ-142", "EQ-143", "EQ-144", "EQ-145"} for dep in amendment["remove"])
    reconciliation = next(story for story in stories if story["story"] == "EQ-164")
    assert "GOV032_planning_publication" in reconciliation["existing_governance_dependencies"]
    assert data["governance_amendments"][0]["story"] == "EQ-164"
    assert {row["story"] for row in data["deferred_policy_amendments"]} == {"EQ-176", "EQ-177"}
    assert all(row["retain_dependency"] == "EQ-175" for row in data["deferred_policy_amendments"])
    assert not {"EQ-176", "EQ-177"} & {row["story"] for row in data["dependency_amendments"]}
    for release in releases:
        assert set(release["release_gate_additional_dependencies"]) == {
            task["planning_key"] for task in release["proposed_tasks"] if task["layer"] in ("io", "workers")
        }
    final = {row["story"]: row for row in data["final_audits"]}
    assert "EQ-146" in final["EQ-180"]["retain_dependencies"]
    assert "EQ-175" in final["EQ-180"]["retain_dependencies"]
    assert {f"EQ-{i}" for i in range(170, 175)} <= set(final["EQ-175"]["retain_dependencies"])
    assert "options releases/stories" in data["unchanged_exclusions"]
    inventory = data["primary_inventory"]
    assert inventory["original_accounting"] == {
        "feature_groups": 78, "eod_scanner_identities": 357, "watchlist_identities": 25,
        "exported_fields": 721, "principal_structs": 30, "original_core_feature_ids": 39,
    }
    assert not inventory["counts_are_unique_math_features"] and not inventory["private_rows_published"]
    assert inventory["pr463_readback"]["merged"]
    assert {row["id"] for row in inventory["findings"]} == {
        "original_dispatch_gaps", "optional_prior_close", "batch_history_and_intraday",
        "coarse_sharding", "resource_topology", "inventory_coverage",
    }
    for row in inventory["findings"]:
        assert (root / row["accepted_evidence"]).is_file(), row["accepted_evidence"]
        assert row["release_owners"] and set(row["release_owners"]) <= {"R18", *(f"EF{i}" for i in range(1, 10))}
    text = (root / "docs/EQUITY_DELIVERY_REPLAN.md").read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in link or link.startswith("#"):
            continue
        assert (root / "docs" / link.split("#", 1)[0]).is_file(), link
    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", text), "private filesystem path in public plan"
    return {"result": "PASS", "existing_stories": len(stories), "releases": len(releases), "proposed_tasks": len(tasks)}


if __name__ == "__main__":
    print(json.dumps(check(Path(__file__).resolve().parents[1]), sort_keys=True))
