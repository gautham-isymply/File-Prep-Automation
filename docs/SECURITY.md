# Security and data handling

## Data classifications and boundaries

The manual identifies internal factory/employee-hour processing. Source files can include employee identifiers, paid hours, overtime, cost centers and commercial operational details. Treat as confidential business data. The repository distribution intentionally **does not include the original DOCX manual or production inputs**; synthetic examples are retained.

- CLI is local; no network clients or BW credentials are used by application code.
- The input remains read-only; results are written to operator-chosen filesystem paths.
- JSON report can contain sensitive values in messages (e.g. cell contents or labels) and absolute local paths. Protect the report at the **same classification** as input, apply retention/access controls outside this CLI.
- Overrides are operational changes to data: review them, keep row keys, verify old value, and record approval in a governed change ticket. The CLI verifies uniqueness, not human authorization.
- Do not put unredacted employee names, personal data, proprietary templates, credentials or raw source files into issues, chat prompts, repository fixtures, or public CI.
- YAML profiles and batch manifests are *trusted configuration*, not to be downloaded from untrusted source messages; avoid running the CLI against unknown files on privileged hosts.

## Gaps

No sandboxing of malformed Excel/CSV beyond library parsing; no encrypted artifact storage; no audit signature/hash; no built-in report redaction or permission setting. These are tracked as operational limitations in [debt](exec-plans/tech-debt-tracker.md) and [reliability](RELIABILITY.md).
