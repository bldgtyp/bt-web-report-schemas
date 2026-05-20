// @bldgtyp/web-report-schemas — JS half
//
// The canonical JSON Schemas live under ./schemas/ and are regenerated from
// the Pydantic models in ./src/bt_web_report_schemas/ via
// `uv run gen-json-schemas`. Consumers should import the schemas through
// the package's exports map:
//
//   import projectSchema from "@bldgtyp/web-report-schemas/project.schema.json";
//   import manifestSchema from "@bldgtyp/web-report-schemas/manifest.schema.json";

export const VERSION = "0.1.0";
export const PROJECT_SCHEMA_VERSION = "0.2.0";
export const MANIFEST_SCHEMA_VERSION = "1.0.0";

export { listVarKeyOptions } from "./var-keys";
export type { VarKeyOption, VarKeyOptionsConfig } from "./var-keys";
