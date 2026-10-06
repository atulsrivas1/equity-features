"""Pure collection of supplied immutable family results."""
from equity_feature_contracts.composition import CompositionSpec, FamilyResult, FeatureBundle
from equity_feature_contracts import ContractError, ErrorCode
from . import __version__


def compose_features(components: tuple[FamilyResult, ...], *, spec: CompositionSpec) -> FeatureBundle:
    """Preserve whole supplied results and explicitly report missing instances."""
    if type(spec) is not CompositionSpec or type(components) not in (tuple, list) or any(type(c) is not FamilyResult for c in components):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned composition and concrete result instances required")
    supplied = {c.instance_id: c for c in components}
    if len(supplied) != len(components):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate supplied instance")
    if any(i not in spec.instance_ids for i in supplied):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "undeclared supplied instance")
    if any(c.result.metadata.backend_version != __version__ for c in components):
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "composition needs current qualified backend versions")
    return FeatureBundle(spec, tuple(supplied[i] for i in spec.instance_ids if i in supplied),
                         tuple(i for i in spec.instance_ids if i not in supplied))
