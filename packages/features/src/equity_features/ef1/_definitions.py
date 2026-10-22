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
    if context["producer"] == "regular_first_trade_price":
        requirements = tuple(InputRequirement(role, "canonical:1", ("known_at_ns",), kind,
            rule="fixed nullable role; independent causal regular trade membership; selected original numeric clock")
            for role, kind in (("calendar_provenance", DataKind.REFERENCE), ("trades", DataKind.TRADE),
                               ("population_proof", DataKind.REFERENCE)))
        return (EF1Definition("session.regular.first_trade_price", ValueType.FLOAT64, "currency/share",
            requirements, "float(Fraction(first_eligible.price,10**scale)); original order before numeric availability"),)
    if context["producer"] == "multivenue_status":
        from ._venue_status import ROLES, VENUE_FIELDS
        requirements = tuple(InputRequirement(role, "canonical:1", ("reference_id", "fact_kind", "effective_start_ns", "text", "known_at_ns"),
            DataKind.REFERENCE, rule="fixed nullable role; ef1-venue-map1 grammar; original publisher identity, sequence and order")
            for role in ROLES)
        return tuple(EF1Definition("session.venue_status." + name, dtype, unit, requirements, formula)
            for name, dtype, unit, formula in VENUE_FIELDS)
    if context["producer"] == "reference_close":
        requirements = tuple(InputRequirement(role, "canonical:1", fields, kind, rule=rule) for role, fields, kind, rule in (
            ("calendar_provenance", ("known_at_ns",), DataKind.REFERENCE, "fixed nullable role; causal supplied calendar"),
            ("bars", ("known_at_ns",), DataKind.BAR, "fixed nullable role; independent causal regular completed-bar membership"),
            ("population_proof", ("known_at_ns",), DataKind.REFERENCE, "fixed nullable role; independent causal regular completed-bar membership"),
            ("authoritative_close", ("reference_id", "fact_kind", "effective_start_ns", "text", "price", "known_at_ns"), DataKind.REFERENCE,
             "fixed nullable role; one supplied same-session close, never calculated or authenticated here")))
        return tuple(EF1Definition("reference.close." + name, dtype, unit, requirements, formula) for name, dtype, unit, formula in (
            ("absolute_difference_bps", ValueType.FLOAT64, "bps",
             "float(Fraction(10000*|Pc-Ps|,Ps)); Ps supplied close denominator, Pc exact EQ166 close coefficient; one final conversion"),
            ("comparison_state", ValueType.STRING, "state",
             "closed vocabulary; reference_future > reference_invalid > reference_unavailable > calculated_unavailable > tolerance verdict"),
            ("supplied_price", ValueType.DECIMAL128, "currency/share", "supplied same-session close coefficient at PriceUnit.scale"),
            ("within_tolerance", ValueType.BOOL, "boolean", "10000*|Pc-Ps|*den <= num*Ps exact inclusive integer test")))
    if context["producer"] == "regular_bar_prices":
        requirements = tuple(InputRequirement(role, "canonical:1", ("known_at_ns",), kind,
            rule="fixed nullable role; independent causal regular completed-bar membership")
            for role, kind in (("calendar_provenance", DataKind.REFERENCE), ("bars", DataKind.BAR),
                               ("population_proof", DataKind.REFERENCE)))
        return tuple(EF1Definition(name, ValueType.FLOAT64, "currency/share", requirements, formula)
            for name, formula in (("session.close.calculated_price", "float(Fraction(last_positive.close,10**scale)); provisional prefix"),
                                  ("session.regular.first_completed_bar_open", "float(Fraction(first_positive.open,10**scale))")))
    if context["producer"] == "path_gap_endpoint":
        kind = DataKind.TRADE if context["selection"]["sampling"] == "eligible_trade" else DataKind.BAR
        requirements = tuple(InputRequirement(role, "canonical:1", ("known_at_ns",), role_kind,
            rule="fixed nullable role; causal source-bound population and selected endpoint operands")
            for role, role_kind in (("calendar_provenance", DataKind.REFERENCE), ("path", kind),
                                    ("prior_close", DataKind.DAILY), ("population_proof", DataKind.REFERENCE)))
        return tuple(EF1Definition("session.gap_endpoint." + name, ValueType.FLOAT64, "fraction", requirements, formula)
            for name, formula in (("current_fill_fraction", "clamp((O-L)/(O-P),0,1); nonzero gap only"),
                                  ("opening_gap_fraction", "(O-P)/P")))
    if context["producer"] == "daily_observations":
        from ._daily_context import ROLES
        requirements = tuple(InputRequirement(role, "canonical:1",
            ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns"),
            DataKind.REFERENCE, rule="exact nullable source-bound daily observation role") for role in ROLES)
        return tuple(EF1Definition("session.daily_observations." + name,
            ValueType.INT64 if name == "selected_observed_count" else ValueType.FLOAT64,
            "observations" if name == "selected_observed_count" else "price", requirements, formula,
            "daily-observations-v2") for name, formula in (
                ("high", "maximum selected common high; earliest tie"),
                ("low", "minimum selected common low; earliest tie"),
                ("open", "first selected common open"),
                ("selected_observed_count", "count raw-admitted selected observations; independent of common basis")))
    if context["producer"] in ("opening_trade", "opening_trade_seconds", "status_history"):
        history = context["producer"] == "status_history"
        observable_roles: tuple[str, ...] = ("calendar_provenance", "history_events", "history_prefix", "history_seed", "source_capability") if history else (
            "calendar_provenance", "market_prefix", "source_capability", "trades")
        requirements = tuple(InputRequirement(role, "canonical:1", ("known_at_ns",),
            DataKind.TRADE if role == "trades" else DataKind.REFERENCE,
            rule="exact nullable positional original observable-v2 role; causal original identity/order") for role in observable_roles)
        if history:
            observable_fields: tuple[tuple[str, ValueType, str], ...] = (("admission_reason", ValueType.STRING, "reason"), ("admission_state", ValueType.STRING, "state"),
                      ("event_count", ValueType.INT64, "count"), ("halt_observed", ValueType.BOOL, "boolean"),
                      ("resume_observed", ValueType.BOOL, "boolean"), ("ssr_on_observed", ValueType.BOOL, "boolean"))
        elif context["producer"] == "opening_trade_seconds":
            observable_fields = (("delay_seconds", ValueType.INT64, "s"),)
        else:
            observable_fields = (("admission_reason", ValueType.STRING, "reason"), ("admission_state", ValueType.STRING, "state"),
                      ("delay_ns", ValueType.INT64, "ns"), ("first_trade_time_ns", ValueType.INT64, "utc_ns"),
                      ("observed", ValueType.BOOL, "boolean"))
        prefix = "session.status_history." if history else "session.open_observation."
        return tuple(EF1Definition(prefix + name, dtype, unit, requirements,
            "bounded complete original causal population; frozen observable-v2 dependency mathematics", "observable-v2")
            for name, dtype, unit in observable_fields)
    if context["producer"] in ("period", "extended"):
        period = context["producer"] == "period"
        requirements = (
            InputRequirement("calendar_provenance", "canonical:1",
                ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns"),
                DataKind.REFERENCE, rule="complete causal supplied calendar proof; all declared sessions/segments"),
            InputRequirement("daily_history" if period else "bars", "canonical:1",
                ("open", "high", "low", "close", "volume", "actual_notional", "known_at_ns"),
                DataKind.DAILY if period else DataKind.BAR,
                rule="exact nullable governed DAILY slots" if period else "exact nullable positive phase prefix"),
            InputRequirement("bars" if period else "prior_close", "canonical:1",
                ("open", "high", "low", "close", "volume", "actual_notional", "known_at_ns") if period else ("close", "known_at_ns"),
                DataKind.BAR if period else DataKind.DAILY,
                rule="exact nullable target regular prefix" if period else "immediate predecessor regular DAILY; only prior-close return depends on it"),
        )
        fields = (
            ("close", ValueType.FLOAT64, "currency/share", "last price-bearing original interval close"),
            ("high", ValueType.FLOAT64, "currency/share", "maximum supplied interval high; earliest tie"),
            ("low", ValueType.FLOAT64, "currency/share", "minimum supplied interval low; earliest tie"),
            ("notional", ValueType.DECIMAL128, "currency", "sum actual notional coefficients; known zero volume contributes zero"),
            ("open", ValueType.FLOAT64, "currency/share", "first price-bearing original interval open"),
            ("open_close_return", ValueType.FLOAT64, "fraction", "(last close-first open)/first open"),
            ("volume", ValueType.INT64, "shares", "sum delivered required interval volumes"),
        )
        if period:
            fields += (("scheduled_sessions", ValueType.INT64, "sessions", "supplied civil-period calendar membership count"),
                       ("completed_sessions", ValueType.INT64, "sessions", "members with actual regular close <= C"))
        else:
            fields += (("prior_close_return", ValueType.FLOAT64, "fraction", "(phase close-predecessor regular close)/predecessor regular close"),)
        prefix = "calendar.period." if period else "session.extended."
        return tuple(EF1Definition(prefix + name, dtype, unit, requirements, formula)
                     for name, dtype, unit, formula in sorted(fields))
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
