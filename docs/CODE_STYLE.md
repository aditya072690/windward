# CODE_STYLE — Windward

Consistency is a feature. The reviewer should be able to open any file and immediately know where things are and why.

## 1. Universal rules

- **Readable over clever.** Small functions (≤ 40 lines), small files (≤ 300 lines), one responsibility each.
- **Names carry units and meaning:** `forecast_mw`, `horizon_h`, `cutoff_utc` — never `value`, `data`, `tmp`.
- **No magic numbers.** Constants live in `config.py` / `lib/constants.ts` with a comment citing the PRD assumption ID.
- **Comments explain *why*, not *what*.** Reference assumptions (`# A3: inclusive boundary`).
- **No dead code, no commented-out code, no TODO without an issue-style note** (`# TODO(P2): ...`).
- **Pure functions in services**; I/O only in `repository/`, `ingestion/`, and API layer.
- **Fail loudly, early, with typed errors.** Never swallow exceptions.
- **UTF-8, LF line endings, final newline** (`.editorconfig` provided).
- **English, neutral tone** in code, docs and commits; no personal names/identifiers anywhere.

## 2. Python (backend)

| Topic | Rule |
|---|---|
| Version | 3.12 |
| Tooling | `ruff` (lint + format, line length 100), `mypy --strict`, `pytest` — all configured in `pyproject.toml` |
| Typing | Full annotations on every function; `Annotated[...]` + Pydantic for I/O; no `Any` without justification |
| Naming | `snake_case` funcs/vars, `PascalCase` classes, `UPPER_SNAKE` constants, `_private` helpers |
| Imports | stdlib → third-party → local; absolute imports (`from app.services import decision`) |
| Docstrings | Google style on public functions: summary, Args, Returns, Raises. Include units |
| Data | pandas confined to `services/`; repository returns typed DataFrames with documented columns; API layer returns Pydantic models only |
| Time | **Always timezone-aware.** Use `zoneinfo.ZoneInfo("Europe/London")`; never `datetime.utcnow()` or naive datetimes. All conversion in `core/time.py` |
| Errors | Domain exceptions in `core/errors.py` (`OutOfWindowError`, `NoDataError`); mapped to HTTP in one place |
| Logging | `logging` JSON formatter, never `print`; no sensitive data |
| FastAPI | Routers per resource; `response_model` on every route; dependencies for settings/DB; tags + summaries for OpenAPI |
| SQL | Parameterised, constants in `repository/queries.py`, formatted for readability |
| Tests | Arrange-Act-Assert; one behaviour per test; descriptive names `test_<unit>_<condition>_<expected>` |

**Layering rule:** `api → services → repository`. Never import upward. Services never import FastAPI.

## 3. TypeScript / React (frontend)

| Topic | Rule |
|---|---|
| Tooling | TypeScript `strict`, `noUncheckedIndexedAccess`, ESLint (`@typescript-eslint`, `react-hooks`, `jsx-a11y`), Prettier |
| Types | No `any`; API types in `lib/types.ts` mirror backend schemas (optionally generated from OpenAPI) |
| Components | Function components + hooks; one component per file; `PascalCase.tsx`; props typed via `interface XProps` |
| State | Server state → TanStack Query; UI/URL state → `useUrlState`; avoid global stores unless needed |
| Styling | Tailwind utilities mapped to **design tokens** (CSS variables). No hard-coded hex/px in components — see `docs/DESIGN_SYSTEM.md` |
| Structure | `features/<name>/` owns its components, hooks and tests; `components/ui` is presentation-only and reusable |
| Hooks | `useXxx`; stable dependencies; no data fetching in components directly |
| Effects | Minimise; derive data with `useMemo`; always clean up listeners |
| Charts | Wrapped in our own components exposing a small, typed prop API; colours from tokens; always provide a table alternative |
| A11y | Semantic HTML first; labels for every control; visible focus; `aria-live="polite"` for dynamic brief; hit targets ≥ 44 px |
| Performance | Lazy-load below-the-fold sections; memoise heavy chart data; avoid inline object props in hot paths |
| Formatting helpers | All number/time formatting via `lib/format.ts` — one place |
| Imports | Absolute alias `@/…`; no deep relative `../../..` |
| Tests | Co-located `*.test.tsx`; query by role/label, not test-id (use test-id only as last resort) |

## 4. Git and review conventions

- **Conventional Commits:** `feat(decision): …`, `fix(metrics): …`, `docs: …`, `test: …`, `chore: …`, `refactor: …`.
- Small, logical commits; each leaves tests green. No giant "initial everything" commit — commit history should tell the build story (reviewers read it).
- Commit author: use a neutral identity (e.g. `Windward Dev <dev@users.noreply.github.com>`) to keep the submission anonymous.
- Branch: `main` + short-lived `feat/*` branches (merge via fast-forward or squash).
- `.editorconfig`, `.gitignore`, `.dockerignore`, `.gitattributes` present.
- Pre-commit (optional): ruff, prettier, eslint on staged files.

## 5. Documentation standards

- README is the entry point; every other doc is linked from it.
- Each backend package folder has a short module docstring explaining its role.
- Public API documented via FastAPI OpenAPI (`/docs`) with examples on response models.
- Architecture decisions recorded in `docs/ARCHITECTURE.md` (ADR table) when something non-obvious is chosen.

## 6. Definition of "clean" (reviewer checklist)

- [ ] `make lint` passes with zero warnings
- [ ] No unused exports, imports, variables, files
- [ ] Every public function typed and documented
- [ ] No hard-coded colours/spacings outside tokens
- [ ] No timezone-naive datetimes
- [ ] No SQL string formatting
- [ ] No `console.log` / `print` left behind
