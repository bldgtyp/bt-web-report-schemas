# bt-web-report-schemas

Shared schemas for the `bt-web-report` platform. Dual-published as a
Python package (`bt-web-report-schemas`) and an npm package
(`@bldgtyp/web-report-schemas`) from the same repo.

## Contents (planned)

- `phpp_schemas/phpp_v10_7/`, `phpp_v10_6/`, … — per-version PHPP row maps
- `project_yaml.schema.json` — JSON Schema for per-project `project.yaml`
- `manifest.schema.json` — JSON Schema for generated `data/manifest.json`

See [`../context/data-pipeline.html`](../context/data-pipeline.html) for the
data shapes this package validates.
