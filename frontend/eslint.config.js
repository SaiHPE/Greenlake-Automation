// The frontend rules of docs/STANDARD.md that a linter can check. `npm run lint` runs them (the
// `ui-lint` step of scripts/check.py). Today's violations are in eslint-suppressions.json, which is
// eslint's own list: a new violation fails, and so does an entry whose violation is gone (delete
// it with `npx eslint src --prune-suppressions`). Never add an entry and never run --suppress-all.
import reactHooks from "eslint-plugin-react-hooks";
import tseslint from "typescript-eslint";

const BACKEND_ONLY = "STANDARD F1: only api.ts (HTTP) and useRunEvents.ts (SSE) talk to the backend. " +
  "Add a function to api.ts, or take the events from useRunEvents.";
const backend = (...names) => [
  ...names.map((name) => ({ name, message: BACKEND_ONLY })),
];
const backendProperties = (...names) => names.flatMap((property) =>
  ["window", "globalThis", "self"].map((object) => ({ object, property, message: BACKEND_ONLY })));

export default [
  { ignores: ["dist/**", "node_modules/**", "mockups/**"] },
  {
    files: ["src/**/*.{ts,tsx}"],
    languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } },
    linterOptions: { reportUnusedDisableDirectives: "error" },
    plugins: { "@typescript-eslint": tseslint.plugin, "react-hooks": reactHooks },
    rules: {
      // T4: the frontend has no `any` and no `as unknown as`.
      "@typescript-eslint/no-explicit-any": "error",
      "no-restricted-syntax": ["error", {
        selector: "TSAsExpression > TSAsExpression > TSUnknownKeyword.typeAnnotation",
        message: "STANDARD T4: no `as unknown as`. Give the value its real type where it enters " +
          "(the API types in api.ts), or narrow it with a check.",
      }],
      // T3: no @ts-ignore, @ts-nocheck or bare @ts-expect-error.
      "@typescript-eslint/ban-ts-comment": "error",
      // F1
      "no-restricted-globals": ["error", ...backend("fetch", "EventSource")],
      "no-restricted-properties": ["error", ...backendProperties("fetch", "EventSource")],
      // F3
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "error",
    },
  },
  {
    files: ["src/api.ts"],
    rules: {
      "no-restricted-globals": ["error", ...backend("EventSource")],
      "no-restricted-properties": ["error", ...backendProperties("EventSource")],
    },
  },
  {
    files: ["src/useRunEvents.ts"],
    rules: {
      "no-restricted-globals": ["error", ...backend("fetch")],
      "no-restricted-properties": ["error", ...backendProperties("fetch")],
    },
  },
  {
    // F2. A test importing the page it tests is not a page importing a page.
    files: ["src/steps/**/*.{ts,tsx}"],
    ignores: ["**/*.test.{ts,tsx}"],
    rules: {
      "no-restricted-imports": ["error", {
        patterns: [{
          regex: "^(\\./|(\\.\\./)+steps/)",
          message: "STANDARD F2: a step page does not import another step page. Move the shared piece to ui/.",
        }],
      }],
    },
  },
];
