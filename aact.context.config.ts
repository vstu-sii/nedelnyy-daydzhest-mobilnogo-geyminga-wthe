import type { AactConfig } from "aact";

const config: AactConfig = {
  // Source of architecture description
  source: {
    type: "plantuml", // "plantuml" | "structurizr" | "model-json" | "kubernetes" | "compose"
    path: "./context.puml",
  },

  // Validation rules. Built-in rules are opt-in: only the ones listed
  // here run (true = on with defaults, an object = on with options,
  // false = off). Drop a line to silence that rule.
  rules: {
    acl: true, // Anti-Corruption Layer: only tagged containers depend on externals
    acyclic: true, // No circular dependencies
    apiGateway: true, // External calls go through an API gateway
    crud: true, // Only repo/relay containers access databases
    dbPerService: true, // Each database accessed by a single service
    cohesion: false, // Boundary cohesion > coupling
    stableDependencies: false, // Depend on more stable components — off by default until you tag stability
    commonReuse: true, // Reuse all of a context's public API or none
  },

  // -----------------------------------------------------------------------
  // Project-specific (custom) rules
  //
  // After `npm install aact` locally, switch from this type-only import to
  // `defineConfig` to register your own checks alongside the built-ins:
  //
  //   import { defineConfig } from "aact";
  //   import { bcIsolationRule } from "./rules/bcIsolation";
  //
  //   export default defineConfig({
  //     source: { type: "plantuml", path: "./architecture.puml" },
  //
  //     customRules: [bcIsolationRule],
  //
  //     rules: {
  //       acl: true,
  //       // Configure custom rules with the same syntax as built-ins.
  //       // TypeScript autocompletes options based on the rule definition.
  //       bcIsolation: { apiSuffix: "_api" },
  //     },
  //   });
  //
  // Worked example with two rules and tests:
  //   https://github.com/Byndyusoft/aact/tree/main/examples/custom-rules
  // -----------------------------------------------------------------------

  // PlantUML generation from Kubernetes configs (aact generate)
  // generate: {
  //   kubernetes: { path: "./fixtures/kubernetes" },
  //   boundaryLabel: "Our system",
  // },

  // Default output mode. CLI `--json` always overrides per-invocation.
  // Set to "json" for CI / agent pipelines that always want the envelope.
  // output: {
  //   mode: "json",
  // },
};

export default config;
