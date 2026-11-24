# Glossary and exact search terms

- **Profile:** YAML under `config/profiles/<id>.yaml` describing one input format; deployed copy under `src/factoryprep/profiles/`.
- **Processor:** Python algorithm chosen by `processor`: `tabular` or `jz`.
- **Source:** unmodified workbook/CSV supplied to CLI.
- **Prepared candidate:** `.xlsx` or `.csv` generated only after passing the configured gate; **not proof of BW ingestion**.
- **Reconciliation:** advisory source totals computed using documented validation filters; no live BW comparison.
- **Reference:** single-sheet source of expected *column names/order* for `--reference`; no enforced types.
- **ADSO / DTP / BW / PBI:** SAP BW persistence/transfer/reporting concepts appearing in manual; **out of scope**.
- **Week ending:** Saturday; weekly range runs Sunday–Saturday per manual introduction. SQL examples elsewhere in manual vary.
- **HC:** JZ incoming workbook invoice-hours column referenced by manual; raw source mapping is **unverified**.
- **ExecPlan:** in-repo self-contained implementation plan with progress, decisions, and acceptance evidence.
- **Tech debt:** numbered, evidence-backed discrepancy/limitation with closure test; see tracker.
- **Provisional:** workflow modeled from manual but not certified against actual source/destination formats.
