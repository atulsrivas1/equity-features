# R26 variants: restore CP3 error pointer proposal

Status: coordinator proposal for independent review, October 21, 2026. This supplements boundary draft3; it does not freeze fixtures or authorize implementation.

After checkpoint CP0, CP1a, CP1b and CP2 succeed, CP3 validates current admission, suffix/current request and immutable merge before numerical evaluation. For a current Request cursor position below the retained prior cursor of the same stream, return `VariantValidationError('checkpoint_cut_mismatch','/request/cut_cursors/{i}/position')`, where i is the actual index in the current Request's canonical cursor list. Scan current cursor indices in order. Earlier shape, missing stream, scalar or admission errors retain their existing precedence. This specifies the pointer for an already prohibited regression; it permits no shortened history.

During immutable merge, a suffix static fact or stamped record reusing a retained identity with different canonical record bytes returns `identity_conflict` at the suffix collection item: `/snapshot/{collection}/{i}`. The virtual snapshot here is the supplied suffix, not the merged history. Collection declaration order, then suffix index, breaks ties; byte-identical permitted static facts remain reusable. Existing new-stamped-position and known-at rules remain unchanged. No new record identity may conceal a changed retained identity.

The worker translates either validation failure to `VariantWorkerError('input_invalid',cause_code=code,cause_path=path)` with the same typed code/path. No calculation, sink call, publication, checkpoint advancement or retry claim follows these failures. Mathematical results, evaluator identity, producer admission rules and old-family codecs are unchanged.
