"""Pure admission and deterministic selection over supplied accepted feature values."""
from __future__ import annotations

import operator
from typing import cast

from equity_feature_contracts import FeatureColumn, FeatureResult, QualityRow, Status
from . import _model as m
from ._codec import digest, feature_result_digest, input_semantic_digest

Cell = tuple[int | float | None, QualityRow]
COMPARISONS = {'lt': operator.lt, 'le': operator.le, 'eq': operator.eq, 'ge': operator.ge, 'gt': operator.gt}


def admit(request: m.StrategyRequest) -> tuple[dict[tuple[str, m.Entity], Cell], set[str]]:
    """Validate every supplied cell before considering availability or selection."""
    m.require(type(request) is m.StrategyRequest)
    m.require(request.availability.mode == 'known_at', 'inconsistent_identity')
    universe = set(request.universe)
    m.require(all(e.namespace == request.namespace and e.session_id == request.session_id for e in universe), 'inconsistent_identity')
    requirements = {p.requirement.feature_id: p.requirement for p in request.config.predicates}
    requirements[request.config.ranking.requirement.feature_id] = request.config.ranking.requirement
    cells: dict[tuple[str, m.Entity], Cell] = {}
    seen: set[str] = set()
    for result in request.feature_results:
        m.require(type(result) is FeatureResult)
        feature_result_digest(result)
        metadata = result.metadata
        m.require(metadata.namespace == request.namespace and metadata.session_id == request.session_id and
                  metadata.availability == request.availability, 'inconsistent_identity')
        quality = {(row.feature_id, row.entity): row for row in result.quality}
        semantic = input_semantic_digest(result)
        for column in result.values:
            m.require(type(column) is FeatureColumn)
            seen.add(column.feature_id)
            requirement = requirements.get(column.feature_id)
            if requirement is not None and column.entities:
                m.require(metadata.config_digest == requirement.expected_result_config_digest and
                          semantic == requirement.expected_input_semantic_digest, 'inconsistent_identity')
            for key, value in zip(column.entities, column.values, strict=True):
                entity = m.Entity(request.namespace, key.instrument_id, key.session_id)
                m.require(entity in universe, 'inconsistent_identity')
                identity = (column.feature_id, entity)
                m.require(identity not in cells, 'duplicate')
                q = quality.get((column.feature_id, key))
                m.require(q is not None)
                row = cast(QualityRow, q)
                m.require((row.status is Status.AVAILABLE) == (value is not None))
                cells[identity] = (cast(int | float | None, value), row)
    return cells, seen


def scan(request: m.StrategyRequest) -> m.StrategyResult:
    cells, seen = admit(request)
    def cell(feature: str, entity: m.Entity) -> tuple[int | float | None, str | None]:
        value = cells.get((feature, entity))
        if value is None:
            return None, 'absent_entity' if feature in seen else 'absent_feature'
        scalar, quality = value
        return (scalar, None) if quality.status is Status.AVAILABLE else (None, quality.status.value)

    staged: list[tuple[m.Entity, str, tuple[m.PredicateDisposition, ...], int | float | None, str | None]] = []
    ranking = request.config.ranking
    for entity in request.universe:
        dispositions = []
        for index, predicate in enumerate(request.config.predicates):
            value, reason = cell(predicate.requirement.feature_id, entity)
            if reason is not None:
                disposition = m.PredicateDisposition(index, predicate.requirement.feature_id, 'unavailable', reason)
            else:
                matches = COMPARISONS[predicate.operator](cast(int | float, value), predicate.threshold)
                disposition = m.PredicateDisposition(index, predicate.requirement.feature_id, 'pass' if matches else 'fail', None)
            dispositions.append(disposition)
        value, reason = cell(ranking.requirement.feature_id, entity)
        unavailable = reason is not None or any(d.state == 'unavailable' for d in dispositions)
        state = 'unavailable' if unavailable else 'nonmatching' if any(d.state == 'fail' for d in dispositions) else 'matching'
        staged.append((entity, state, tuple(dispositions), value, reason))
    # Stable numeric-only reverse preserves ascending entity ties, including signed-zero ties.
    matches = sorted((row for row in staged if row[1] == 'matching'), key=lambda row: row[0])
    matches.sort(key=lambda row: cast(int | float, row[3]), reverse=ranking.direction == 'descending')
    ranked = tuple(row[0] for row in matches)
    ranks = {entity: index + 1 for index, entity in enumerate(ranked)}
    rows = tuple(m.StrategyRow(entity, state, dispositions, value, reason, ranks.get(entity))
                 for entity, state, dispositions, value, reason in staged)
    expected = len(rows)
    eligible = sum(row.status != 'unavailable' for row in rows)
    return m.StrategyResult(digest('strategy-config:1', request.config), digest('strategy-request:1', request),
        tuple(sorted(feature_result_digest(result) for result in request.feature_results)), rows, ranked,
        ranked[:request.config.top_k], expected, eligible, len(ranked), eligible, expected,
        'empty_universe' if not expected else 'complete' if eligible == expected else 'incomplete')
