"""Optional EF1 discovery; the accepted default registry remains unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, InputRequirement, OutputField, ValueType,
)
from ._context import decode_ef1_context


@dataclass(frozen=True)
class EF1Definition:
    """Own discovery metadata; choose one complete alternative when present.

    requirements are common prerequisites when alternatives are declared.
    Existing canonical FeatureDefinition and InputRequirement remain unchanged.
    """

    feature_id: str
    dtype: ValueType
    unit: str
    requirements: tuple[InputRequirement, ...]
    formula: str
    algorithm_version: str = "v1"
    schema_version: str = "1"
    capabilities: Capabilities = Capabilities(batch=True)
    alternative_requirements: tuple[tuple[InputRequirement, ...], ...] = ()

    @property
    def outputs(self) -> tuple[OutputField, ...]:
        return (OutputField("value", self.dtype.value, self.unit),)


def ef1_definitions(config: ConfigSpec) -> tuple[EF1Definition, ...]:
    """Describe the complete selected executable producer; unsupported producers fail."""
    requirements: tuple[InputRequirement, ...]
    fields: tuple[tuple[str, ValueType, str, str], ...]
    context = decode_ef1_context(config)
    if context["producer"] in ("reference_classification", "reference_action"):
        classification = context["producer"] == "reference_classification"
        roles = ("classification_facts", "classification_history", "classification_projection") if classification else (
            "market", "action_facts", "action_history", "action_projection", "source_representation", "source_quantity_basis")
        requirements = tuple(InputRequirement(role, "canonical:1",
            ("reference_id", "fact_kind", "effective_start_ns", "known_at_ns"), DataKind.REFERENCE,
            rule="exact nullable role slot; complete causal population and actual source-bound proof")
            for role in roles if role != "market")
        alternatives = () if classification else tuple((InputRequirement("market", "canonical:1",
            ("known_at_ns",), kind, rule="choose exactly one complete alternative; one actual nullable market slot"),
            *requirements) for kind in (DataKind.TRADE, DataKind.BAR, DataKind.DAILY))
        fields = (("reference.classification.value", ValueType.STRING, "classification", "causal active membership with historical complete projection"),
                  ("reference.gate.classification_reason", ValueType.STRING, "reason", "first closed failed then unknown reason"),
                  ("reference.gate.classification_state", ValueType.STRING, "state", "failed dominates unknown; otherwise passed")) if classification else (
                  ("reference.gate.action_reason", ValueType.STRING, "reason", "first closed failed then unknown reason"),
                  ("reference.gate.action_state", ValueType.STRING, "state", "declaration/history admission only; never applies factors"))
        return tuple(EF1Definition(name, dtype, unit, requirements, formula, alternative_requirements=alternatives)
                     for name, dtype, unit, formula in fields)
    if context["producer"] in ("path_gap", "path_drive"):
        trades = context["selection"]["sampling"] == "eligible_trade"
        requirements = (
            InputRequirement("calendar_provenance", "canonical:1",
                ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns"),
                DataKind.REFERENCE, rule="causal supplied calendar proof covering all sessions/segments"),
            InputRequirement("path", "canonical:1", ("price", "size", "known_at_ns") if trades else
                ("open", "close", "volume", "known_at_ns"), DataKind.TRADE if trades else DataKind.BAR,
                rule="complete causal supplied half-open prefix; original delivered population"),
        )
        if context["producer"] == "path_gap":
            requirements += (InputRequirement("prior_close", "canonical:1", ("close", "known_at_ns"),
                DataKind.DAILY, rule="exact explicit preceding calendar slot and full session scope"),)
            fields = (("fill_fraction", ValueType.FLOAT64, "fraction", "max clamp((O-x)/(O-P),0,1)"),
                      ("filled", ValueType.BOOL, "boolean", "exists sample (x-P)*(O-P)<=0"),
                      ("first_fill_ns", ValueType.INT64, "ns", "earliest sampled hit event time"),
                      ("remaining_fraction", ValueType.FLOAT64, "fraction", "max(0,(last-P)/(O-P))"))
            prefix = "session.gap."
        else:
            fields = (("excursion_down", ValueType.FLOAT64, "fraction", "max(0,1-minsample/O)"),
                      ("excursion_up", ValueType.FLOAT64, "fraction", "max(0,maxsample/O-1)"),
                      ("return", ValueType.FLOAT64, "fraction", "last/O-1; completed drive only"))
            prefix = "session.opening_drive."
        return tuple(EF1Definition(prefix + name, dtype, unit, requirements, formula)
                     for name, dtype, unit, formula in fields)
    if context["producer"] == "status":
        requirements = tuple(InputRequirement(role, "canonical:1",
            ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns"),
            DataKind.REFERENCE, rule="actual causal supplied status/calendar declaration")
            for role in ("calendar_provenance", "status_states", "status_prefix", "status_validity"))
        dimension = context["selection"]["dimension"]
        return (
            EF1Definition("session.status.admission_reason", ValueType.STRING, "reason", requirements,
                          "first applicable closed status admission reason"),
            EF1Definition("session.status.admission_state", ValueType.STRING, "state", requirements,
                          "ready iff the selected current state is proved and admitted"),
            EF1Definition("session.status." + dimension + "_age_ns", ValueType.INT64, "ns", requirements,
                          "C minus original effective time of proved current event"),
            EF1Definition("session.status." + dimension + "_state", ValueType.STRING, "state", requirements,
                          "last event strictly before C in the proved causal supplied prefix"),
        )
    if context["producer"] == "clock":
        requirements = (InputRequirement("calendar_provenance", "canonical:1",
                        ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
                         "text", "known_at_ns"), DataKind.REFERENCE,
                        rule="actual causal finite supplied-calendar hash declaration"),)
        return (
            EF1Definition("session.clock.early_close", ValueType.BOOL, "boolean", requirements,
                          "actual_close < supplied_scheduled_close; equal to SessionSpec declaration"),
            EF1Definition("session.clock.phase", ValueType.STRING, "state", requirements,
                          "supplied half-open segment containing C, otherwise closed"),
            EF1Definition("session.clock.regular_elapsed_ns", ValueType.INT64, "ns", requirements,
                          "clamp(C-open,0,close-open)"),
            EF1Definition("session.clock.regular_fraction", ValueType.FLOAT64, "fraction", requirements,
                          "clamp(C-open,0,close-open)/(close-open)"),
            EF1Definition("session.clock.regular_remaining_ns", ValueType.INT64, "ns", requirements,
                          "close-open-clamp(C-open,0,close-open)"),
        )
    trades = context["selection"]["mode"] == "trades"
    primary = InputRequirement("trades" if trades else "bars", "canonical:1",
                               ("price", "size") if trades else ("volume", "actual_notional"),
                               DataKind.TRADE if trades else DataKind.BAR,
                               rule="exact supplied positive-duration anchor window; field-independent readiness")
    proof = InputRequirement("anchor_provenance", "canonical:1",
                             ("reference_id", "fact_kind", "effective_start_ns", "text", "known_at_ns"),
                             DataKind.REFERENCE, rule="actual causal supplied anchor hash declaration")
    requirements = (primary, proof)
    return (
        EF1Definition("session.anchor.notional", ValueType.DECIMAL128, "currency", requirements,
                      "N=sum(price_coefficient*shares) or actual_notional; coefficient at PriceUnit.scale"),
        EF1Definition("session.anchor.volume", ValueType.INT64, "shares", requirements, "V=sum(shares)"),
        EF1Definition("session.anchor.vwap", ValueType.FLOAT64, "currency/share", requirements,
                      "N/(V*10**PriceUnit.scale), undefined for V=0"),
    )
