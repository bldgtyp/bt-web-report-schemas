// Derive the <Var k="..." /> dropdown options from the generated JSON Schema
// for project.yaml. Walks every string-typed leaf and emits a dot-path value
// plus a hierarchical label. Used by tina/config.ts so editors get a
// dropdown that automatically picks up new fields added to the Pydantic
// schema.

import projectSchemaJson from "../schemas/project.schema.json";

export interface VarKeyOption {
  /** Dot-path passed to <Var k="..." /> — matches resolveVar() in the template. */
  value: string;
  /** Hierarchical, " > " separated label shown to editors. */
  label: string;
}

export interface VarKeyOptionsConfig {
  /**
   * Label segments to omit when building the human-readable label. The
   * dot-path value is never modified. Use to flatten "passthrough" container
   * names like "Narrative" that don't add meaning for editors.
   */
  stripLabelSegments?: string[];
}

interface SchemaNode {
  type?: string | string[];
  title?: string;
  const?: unknown;
  anyOf?: SchemaNode[];
  properties?: Record<string, SchemaNode>;
  $ref?: string;
  $defs?: Record<string, SchemaNode>;
}

const projectSchema = projectSchemaJson as SchemaNode;

function isStringLeaf(node: SchemaNode): boolean {
  if (node.const !== undefined) return false; // const fields are fixed; not useful as Var targets
  if (node.type === "string") return true;
  if (Array.isArray(node.type) && node.type.includes("string")) return true;
  if (node.anyOf) {
    // Pydantic emits `str | None` as `anyOf: [{type: "string"}, {type: "null"}]`.
    return node.anyOf.some((alt) => alt.type === "string" && alt.const === undefined);
  }
  return false;
}

function resolveRef(ref: string, defs: Record<string, SchemaNode>): SchemaNode {
  const name = ref.replace(/^#\/\$defs\//, "");
  const def = defs[name];
  if (!def) {
    throw new Error(`Unknown $ref in project schema: ${ref}`);
  }
  return def;
}

function humanizeSnakeCase(name: string): string {
  return name.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function labelSegment(name: string, node: SchemaNode, defs: Record<string, SchemaNode>): string {
  if (node.title) return node.title;
  if (node.$ref) {
    const target = resolveRef(node.$ref, defs);
    if (target.title) return target.title;
  }
  return humanizeSnakeCase(name);
}

function walk(
  node: SchemaNode,
  defs: Record<string, SchemaNode>,
  pathSegments: string[],
  labelSegments: string[],
  out: VarKeyOption[],
): void {
  const expanded = node.$ref ? resolveRef(node.$ref, defs) : node;
  if (!expanded.properties) return;

  for (const [name, child] of Object.entries(expanded.properties)) {
    const childPath = [...pathSegments, name];
    const childLabel = [...labelSegments, labelSegment(name, child, defs)];

    if (isStringLeaf(child)) {
      out.push({ value: childPath.join("."), label: childLabel.join(" > ") });
      continue;
    }

    const target = child.$ref ? resolveRef(child.$ref, defs) : child;
    if (target.properties) {
      walk(target, defs, childPath, childLabel, out);
    }
  }
}

export function listVarKeyOptions(config: VarKeyOptionsConfig = {}): VarKeyOption[] {
  const defs = projectSchema.$defs ?? {};
  const out: VarKeyOption[] = [];
  walk(projectSchema, defs, [], [], out);

  const stripSet = new Set(config.stripLabelSegments ?? []);
  if (stripSet.size === 0) return out;

  return out.map((opt) => ({
    value: opt.value,
    label: opt.label
      .split(" > ")
      .filter((segment) => !stripSet.has(segment))
      .join(" > "),
  }));
}
