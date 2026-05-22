# bt-web-report-schemas

Shared schemas for the `bt-web-report` platform. Dual-published as a Python
package (`bt-web-report-schemas`) and an npm package
(`@bldgtyp/web-report-schemas`) from the same repo so the Python CLI, the
Astro renderer, the TinaCMS editor, and the Manager UI all validate against
identical shapes.

The **Pydantic models in `src/bt_web_report_schemas/` are the single source
of truth.** JSON Schemas under `schemas/` are generated artifacts; ajv-side
and Tina-side consumers read them via the npm package's `exports` map. A
drift test in `tests/test_json_schema_generation.py` fails CI if the
on-disk JSON ever falls out of sync with the Pydantic source.

## Contents

```
bt-web-report-schemas/
├── src/bt_web_report_schemas/         Python (source of truth)
│   ├── project.py                     project.yaml — top-level metadata
│   │                                  + narrative block (grouped per-section
│   │                                  prose-facing values plus user_defined)
│   ├── manifest.py                    data/manifest.json — scrape output
│   ├── phpp/                          per-version PHPP row maps (v10.6, …)
│   └── gen_json_schemas.py            CLI: `uv run gen-json-schemas`
│
├── schemas/                           Generated; DO NOT hand-edit
│   ├── project.schema.json
│   └── manifest.schema.json
│
├── src-js/                            JS half
│   ├── index.ts                       VERSION constants + helpers re-export
│   └── var-keys.ts                    walks project.schema.json → dropdown
│                                      options for the <Var> shortcode
│
└── tests/                             pytest
    ├── test_project_schema.py         Pydantic validation rules
    ├── test_json_schema_generation.py drift guard
    └── test_phpp_schema.py            PHPP row-map regression
```

## Regenerating the JSON Schemas

After editing any Pydantic model, regenerate:

```bash
uv run gen-json-schemas
```

This writes both `schemas/project.schema.json` and
`schemas/manifest.schema.json` deterministically (sorted keys, trailing
newline). Commit the diff alongside the model change. CI fails if you forget.

## JS consumers

Imports flow through the npm package's `exports` map:

```ts
// Static schema for ajv / validation
import projectSchema from "@bldgtyp/web-report-schemas/project.schema.json";
import manifestSchema from "@bldgtyp/web-report-schemas/manifest.schema.json";

// Helper: dot-path dropdown options for the <Var> shortcode
import { listVarKeyOptions } from "@bldgtyp/web-report-schemas";
const options = listVarKeyOptions({ stripLabelSegments: ["Narrative"] });
// → [{ value: "client_name", label: "Client Name" },
//    { value: "narrative.climate.weather_station_name",
//      label: "Climate > Weather Station Name" }, …]
```

The `bt-web-report-template` package consumes both: ajv reads
`project.schema.json` in `src/data/project-schema.mjs`, and Tina's
`tina/config.ts` feeds `listVarKeyOptions()` into the `<Var>` rich-text
template.

## Python consumers

```python
from bt_web_report_schemas.project import Project

with open("project.yaml") as f:
    project = Project.model_validate(yaml.safe_load(f))
```

`Project` is a frozen Pydantic v2 model with `extra="forbid"` — unknown
keys (e.g. typos like `mechancial`) fail loudly instead of silently
dropping values.

## Adding a new project.yaml field

For one-off project prose values, put them under `narrative.user_defined.*`
instead of changing the schema:

```yaml
narrative:
  user_defined:
    cad_received_date: May 1, 2026
```

For a reusable standard field:

1. Add the field to the appropriate model in `src/bt_web_report_schemas/project.py`.
   For narrative prose values, that's one of `CertificationNarrative`,
   `ClimateNarrative`, `EnergyCodeNarrative`, `Co2Narrative`,
   `WindowsNarrative`, or `MechanicalNarrative`. All narrative fields are
   `str | None` — values flow into prose, never into calculations.
2. Run `uv run gen-json-schemas` and commit the regenerated JSON.
3. Add the value to the relevant `project.yaml` files.

The Tina dropdown picks up the new field automatically — no hand-editing
of `tina/config.ts` required.

## Versioning

| Schema | Current | Pinned via |
|---|---|---|
| `Project` | `0.2.0` | `Literal["0.2.0"]` on `schema_version` |
| `Manifest` | `1.0.0` | default in `manifest.py` |

Schema version is a hard equality check — bump it whenever the shape
changes in a way that an existing `project.yaml` wouldn't validate against.

See [`../context/data-pipeline.html`](../context/data-pipeline.html) for
how these schemas fit into the broader data flow.
