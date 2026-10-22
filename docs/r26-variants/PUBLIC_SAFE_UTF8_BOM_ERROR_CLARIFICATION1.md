# Strict UTF8 BOM error precedence

2026-10-21. Coordinator proposal for fresh independent review, refining the existing no-BOM canonical transport requirement. No record, formula, wire encoding, error token or stage is added. All earlier sealed inputs remain unchanged; no freeze or implementation authority follows.

A leading UTF8 BOM, bytes `EF BB BF`, is valid UTF8 but is not admitted JSON syntax in this strict wire profile. The decoder does not strip or ignore it. Report `VariantValidationError('invalid_json','/envelope')` at stage2, before closed-record field/scalar/reference/coherence/digest checks. A BOM followed by a second later defect retains this syntax error. Malformed UTF8 remains `invalid_utf8` at stage1. Ordinary syntactically valid JSON with noncanonical whitespace, member order or spelling retains the existing stage9 canonical-byte check and its existing precedence before digest comparison.

This concerns only a leading transport BOM outside the JSON text. It does not reinterpret a character inside a JSON string, relax the existing scalar/NFC rules, admit another character encoding or normalize any bytes. Independent raw-byte and compound-error fixtures plus independent review remain required before the final literal/implementation freeze.
