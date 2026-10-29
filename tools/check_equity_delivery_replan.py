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
    assert data["schema_version"] == 2
    assert [release["id"] for release in releases] == [f"EF{i}" for i in range(1, 9)]
    stories = [story for release in releases for story in release["existing_stories"]]
    expected = {f"EQ-{i}" for i in range(147, 182)}
    assert len(stories) == 35 and {story["story"] for story in stories} == expected
    assert len({story["issue"] for story in stories}) == 35
    owners = {story["story"]: release["id"] for release in releases for story in release["existing_stories"]}
    assert owners["EQ-164"] == "EF1"
    assert all(owners[f"EQ-{i}"] == "EF1" for i in range(164, 170))
    assert owners["EQ-170"] == "EF2" and owners["EQ-172"] == "EF4"
    assert owners["EQ-171"] == "EF5" and owners["EQ-173"] == "EF6"
    assert owners["EQ-174"] == owners["EQ-175"] == "EF7"
    assert all(owners[f"EQ-{i}"] == "EF8" for i in range(176, 182))
    tasks = [task for release in releases for task in release["proposed_tasks"]]
    assert len(tasks) == 18 and len({task["planning_key"] for task in tasks}) == 18
    for release in releases:
        assert release["state"] == "proposed_allocation_not_migrated"
        assert release["milestone_number"] is None and release["epic_issue"] is None
        assert set(release["layers"]) == {"libraries", "io", "workers"}
        assert release["demo_required"] and not release["api_required"]
        assert not release["ui_product_required"] and not release["public_deployment_required"]
        assert release["goal"] and release["demo_goal"]
        assert set(release["tracks"]) == {"libraries", "io", "workers"}
        assert all(track["deliverables"] and track["contract_first"] for track in release["tracks"].values())
        assert release["tracks"]["libraries"]["existing_stories"]
        assert release["parallel_after"]
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
        assert row["release_owners"] and set(row["release_owners"]) <= {"R18", *(f"EF{i}" for i in range(1, 9))}
    assert not data["shared_setup"]["standalone_release"]
    assert not any(task["planning_key"] in {"EF1-C", "EF1-A"} for task in tasks)
    assert all("EF1-A" not in row["add"] for row in data["dependency_amendments"])
    assert all(row.get("common_composition_dependency") != "EF1-A" for row in releases)
    text = (root / "docs/EQUITY_DELIVERY_REPLAN.md").read_text(encoding="utf-8")
    for link in re.findall(r"\]\(([^)]+)\)", text):
        if "://" in link or link.startswith("#"):
            continue
        assert (root / "docs" / link.split("#", 1)[0]).is_file(), link
    assert not re.search(r"(?<![A-Za-z])[A-Za-z]:[\\/]", text), "private filesystem path in public plan"
    _check_output_ownership(root, data, stories)
    return {"result": "PASS", "existing_stories": len(stories), "releases": len(releases), "proposed_tasks": len(tasks), "supplemental_stories": 1, "planned_outputs": 47}


def _check_output_ownership(root: Path, data: dict, stories: list[dict]) -> None:
    """Validate supplemental planning separately from the historical 35 stories."""
    reconciliation = data["ownership_reconciliation"]
    assert reconciliation["governance_issue"] == 504
    assert reconciliation["status"] == "accepted_planned_ownership_math_unaccepted"
    assert reconciliation["planned_output_count"] == 47
    assert reconciliation["original_35_story_allocation_preserved"]
    assert reconciliation["original_18_proposed_tasks_preserved"]
    assert reconciliation["math_api_accepted"] is False
    assert reconciliation["full_EQ164_complete"] is False
    assert (root / reconciliation["document"]).is_file()
    supplemental, = data["supplemental_stories"]
    assert supplemental["story"] == "EQ-220" and supplemental["issue"] == 598
    assert supplemental["story"] not in {row["story"] for row in stories}
    assert supplemental["issue"] not in {row["issue"] for row in stories}
    assert supplemental["url"] == "https://github.com/atulsrivas1/equity-features/issues/598"
    assert supplemental["ownership_status"] == "accepted_planned_ownership"
    assert supplemental["planned_release"] == "EF3"
    assert supplemental["observed_issue_state"] == "OPEN"
    assert supplemental["observed_project_status"] == "Backlog"
    assert supplemental["native_parent_issue"] == 468
    assert supplemental["actual_milestone_number"] == 24
    assert supplemental["assignees"] == [] and supplemental["due_date"] is None
    assert supplemental["required_dependencies"] == ["EQ-164", "EQ-169"]
    assert supplemental["layer_tasks_before_ready"] == ["EF3-IO", "EF3-W"]
    assert supplemental["release_acceptance_gate"] == "EQ-157"
    assert supplemental["planned_release_gate_additional_dependencies"] == ["EQ-220"]
    assert set(supplemental["tracks"]) == {"libraries", "io", "workers"}
    assert all(supplemental["tracks"].values())
    assert supplemental["math_api_accepted"] is False
    assert supplemental["implementation_admitted"] is False
    manifest = json.loads((root / reconciliation["output_manifest"]).read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1 and manifest["governance_issue"] == 504
    assert manifest["ownership_plan_accepted"] is True
    assert manifest["mathematics_api_accepted"] is False
    assert manifest["accepted_canonical_bindings"] == 0
    assert manifest["full_EQ164_complete"] is False
    assert manifest["supplemental_owner_readback"] == supplemental
    outputs = manifest["outputs"]
    assert len(outputs) == manifest["planned_ownership_count"] == 47
    assert len({row["canonical_name"] for row in outputs}) == 47
    owners = {
        row["story"]: (row["issue"], release["id"])
        for release in data["releases"] for row in release["existing_stories"]
    }
    owners["EQ-220"] = (598, "EF3")
    counts = {"EQ-153": 2, "EQ-159": 2, "EQ-165": 7, "EQ-166": 3,
              "EQ-167": 3, "EQ-168": 4, "EQ-171": 4, "EQ-172": 6, "EQ-220": 16}
    assert {row["primary_numerical_owner"] for row in outputs} == set(counts)
    for owner, count in counts.items():
        assert sum(row["primary_numerical_owner"] == owner for row in outputs) == count
    for row in outputs:
        assert re.fullmatch(r"[a-z][a-z0-9_.]*", row["canonical_name"])
        assert (row["issue"], row["planned_delivery"]) == owners[row["primary_numerical_owner"]]
        assert row["unit"] and row["operands"] and row["kind"]
        assert row["planned_ownership_accepted"] is True
        assert row["accepted"] is False and row["implemented_by_this_packet"] is False
    check_ef3_header_parity(root, manifest)
    check_ef4_header_parity(root, manifest)
    check_ef5_header_parity(root, manifest)
    check_dv1_header_parity(root, manifest)


# Owner decision pending (R9b): ownership entries with no merged header. Do not extend without an owner ruling.
STALE_EF3_ENTRIES = {
    "relative.session.primary.beta_residual_fraction",
    "relative.session.secondary.beta_residual_fraction",
}


def check_ef3_header_parity(root: Path, manifest: dict) -> None:
    """Merged EF3 contract headers and the output manifest must not drift apart."""
    headers: set[str] = set()
    for path in sorted((root / "docs/ef3").glob("*_CONTRACT_PROPOSAL.json")):
        headers |= {row["id"] for row in json.loads(path.read_text(encoding="utf-8"))["headers"]}
    delivered = manifest["ef3_delivered_outputs"]["entries"]
    delivered_names = [row["canonical_name"] for row in delivered]
    assert len(delivered_names) == len(set(delivered_names))
    planned = {row["canonical_name"] for row in manifest["outputs"]}
    assert not planned & set(delivered_names), "entry listed in both manifest sections"
    assert all(row["planned_delivery"] == "EF3" and row["accepted"] is False for row in delivered)
    assert all(row["implemented_by_this_packet"] is False for row in delivered)
    missing = headers - planned - set(delivered_names)
    assert not missing, f"EF3 headers with no manifest entry: {sorted(missing)}"
    orphans = (set(delivered_names) | {r["canonical_name"] for r in manifest["outputs"] if r["planned_delivery"] == "EF3"}) - headers
    assert orphans == STALE_EF3_ENTRIES, f"EF3 manifest entries with no header: {sorted(orphans ^ STALE_EF3_ENTRIES)}"
    for row in manifest["outputs"]:
        if row["canonical_name"] in STALE_EF3_ENTRIES:
            assert row.get("delivered") is False and row.get("superseded_note"), row["canonical_name"]


EF4_CONTRACTS = ("TAPE", "QUOTE_VWAP", "PATH_EFFICIENCY", "PATH_PROJECTIONS")


def check_ef4_header_parity(root: Path, manifest: dict) -> None:
    """Every EF4 contract header needs a manifest entry (planned output or ef4_delivered_outputs), and no EF4 entry may lack a header."""
    headers: set[str] = set()
    for name in EF4_CONTRACTS:
        path = root / f"docs/ef4/{name}_CONTRACT_PROPOSAL.json"
        rows = json.loads(path.read_text(encoding="utf-8"))["headers"]
        assert rows, f"EF4 contract {name} has no headers"
        headers |= {row["id"] for row in rows}
    delivered = manifest["ef4_delivered_outputs"]["entries"]
    names = [row["canonical_name"] for row in delivered]
    assert len(names) == len(set(names)), "duplicate ef4_delivered_outputs entry"
    planned = {row["canonical_name"] for row in manifest["outputs"]}
    assert not planned & set(names), "entry listed in both manifest sections"
    assert all(row["planned_delivery"] == "EF4" and row["accepted"] is False for row in delivered)
    assert all(row["implemented_by_this_packet"] is False for row in delivered)
    ef4_planned = {row["canonical_name"] for row in manifest["outputs"] if row["planned_delivery"] == "EF4"}
    missing = headers - planned - set(names)
    assert not missing, f"EF4 headers with no manifest entry: {sorted(missing)}"
    orphans = (set(names) | ef4_planned) - headers
    assert not orphans, f"EF4 manifest entries with no header: {sorted(orphans)}"


def check_ef5_header_parity(root: Path, manifest: dict) -> None:
    """EF5 contract headers need a manifest entry (EQ-171 planned output or ef5_delivered_outputs); units use the E9 slash spelling."""
    contract = json.loads((root / "docs/ef5/PRICE_STRUCTURES_CONTRACT_PROPOSAL.json").read_text(encoding="utf-8"))
    rows = contract["headers"]
    assert rows, "EF5 contract has no headers"
    headers = {row["id"] for row in rows}
    assert len(headers) == len(rows), "duplicate EF5 header id"
    entries = manifest["ef5_delivered_outputs"]["entries"]
    names = [row["canonical_name"] for row in entries]
    assert len(names) == len(set(names)), "duplicate ef5_delivered_outputs entry"
    planned = {row["canonical_name"] for row in manifest["outputs"]}
    assert not planned & set(names), "entry listed in both manifest sections"
    assert all(row["planned_delivery"] == "EF5" and row["accepted"] is False for row in entries)
    assert all(row["implemented_by_this_packet"] is False for row in entries)
    assert all(row["primary_numerical_owner"] == "EQ-171" and row["issue"] == 512 for row in entries)
    ef5_planned = {row["canonical_name"] for row in manifest["outputs"] if row["planned_delivery"] == "EF5"}
    missing = headers - planned - set(names)
    assert not missing, f"EF5 headers with no manifest entry: {sorted(missing)}"
    orphans = (set(names) | ef5_planned) - headers
    assert not orphans, f"EF5 manifest entries with no header: {sorted(orphans)}"
    units = {row["id"]: row["unit"] for row in rows}
    for row in entries + [r for r in manifest["outputs"] if r["canonical_name"] in headers]:
        assert row["unit"] == units[row["canonical_name"]], f"EF5 unit drift: {row['canonical_name']}"
    assert all("_per_" not in unit for unit in units.values()), "underscore unit form on an EF5 header (E9)"


def check_dv1_header_parity(root: Path, manifest: dict) -> None:
    """DV1 definition-variants headers need a dv1_delivered_outputs entry; units use the E9 slash spelling; not accepted, not implemented."""
    contract = json.loads((root / "docs/dv1/DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json").read_text(encoding="utf-8"))
    rows = contract["headers"]
    headers = {row["id"] for row in rows}
    assert rows and len(headers) == len(rows), "DV1 contract headers missing or duplicated"
    entries = manifest["dv1_delivered_outputs"]["entries"]
    names = [row["canonical_name"] for row in entries]
    assert len(names) == len(set(names)), "duplicate dv1_delivered_outputs entry"
    planned = {row["canonical_name"] for row in manifest["outputs"]}
    assert not planned & set(names), "entry listed in both manifest sections"
    assert all(row["planned_delivery"] == "DV1" and row["accepted"] is False for row in entries)
    assert all(row["implemented_by_this_packet"] is False for row in entries)
    assert set(names) == headers, f"DV1 header/manifest drift: {sorted(set(names) ^ headers)}"
    units = {row["id"]: row["unit"] for row in rows}
    for row in entries:
        assert row["unit"] == units[row["canonical_name"]], f"DV1 unit drift: {row['canonical_name']}"
    assert all("_per_" not in unit for unit in units.values()), "underscore unit form on a DV1 header (E9)"


if __name__ == "__main__":
    print(json.dumps(check(Path(__file__).resolve().parents[1]), sort_keys=True))
