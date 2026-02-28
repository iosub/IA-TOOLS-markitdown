Documentation and comments in


THIS IS THE LATEST AND PRIORITY DOCUMENT. ANY OTHER DOCUMENT IS FOR INFORMATION ONLY.
1.- All documentation or comments must be in English. Interface messages must be in Spanish.
2.- Follow the existing coding best practices already used in the project.

4.- Before making any change in existing code, notify and explain the changes to be made.
5.- Create a separate document with the planned changes, include a checklist of completed changes, and explain why each change was made.

6.- A technical manual and a user manual are required, and both must be kept updated in realtime.
## Plan: Extend convert with dual JSON output

Extend the official MarkItDown API to support `markdown`, `json`, and `both` outputs without breaking compatibility, while preserving `result.markdown`/`result.text_content` and adding a standard path for basic JSON and structured JSON per converter.

**Steps**
1. Phase 1 - Output contract and compatibility (base). Define the JSON contract in internal technical documentation for this change: `basic_json` with `source`, `title`, `markdown`; `structured_json` with `schema_version`, `content_type`, `blocks`/`sections`, `metadata`; and `both` mode returning both. Include fallback rules when a converter cannot provide deep structure.
2. Phase 1 - Extend `DocumentConverterResult` with non-disruptive optional fields. Add `json_data: Optional[dict]` (final structure), `json_basic: Optional[dict]` (stable wrapper), and helpers (`to_dict`, `to_json(pretty=False)`) while keeping `markdown` and `text_content` unchanged. *Blocks steps 3-8*.
3. Phase 1 - Add serialization utilities. Create a dedicated module for JSON serialization and normalization (for example, `markitdown/_serialization.py`) that receives `DocumentConverterResult`, `source`, `output_format` and produces `markdown/json/both` consistently. Include format validation and clear errors for unsupported formats. *Depends on 2*.
4. Phase 2 - Thread the format parameter through the public API. Add `output_format: Literal['markdown','json','both']='markdown'` to `MarkItDown.convert`, `convert_local`, `convert_stream`, `convert_uri`, `convert_response`, propagating it via `kwargs` into `_convert` without breaking existing call signatures. *Depends on 3*.
5. Phase 2 - Integrate in the internal pipeline. Update `_markitdown.py::_convert` to always build `json_basic` when JSON is requested, and fill `json_data` with deep structure when provided by the converter; otherwise, use fallback to a minimal markdown-derived structure. Keep the current markdown post-processing unchanged. *Depends on 4*.
6. Phase 3 - Structured JSON support in priority converters (iterative). Start with converters that have natural structure: CSV/XLSX/HTML/IPYNB. Each converter must populate `json_data` with a stable per-type schema (`rows/columns`, `sheets`, `elements`, `cells`, etc.). *Parallel by converter after 5*.
7. Phase 3 - Gradual support in complex converters (PDF/DOCX/PPTX). Implement block-based structure with metadata (`page`, `bbox` when available, `heading`, `table`, `list`, `paragraph`) with safe degradation when no reliable signal exists. *Depends on 6 to finalize the common schema, but can begin in parallel once contracts are defined*.
8. Phase 4 - CLI. Add `--output-format` in `__main__.py` with options `markdown|json|both` and compatibility with `--output`; define stdout and file behavior per mode (for example: `json` writes JSON; `both` in stdout may prioritize JSON and optionally write markdown to an additional file, or vice versa depending on the final UX decision). *Depends on 5*.
9. Phase 4 - MCP and consumers. Review `packages/markitdown-mcp` to preserve the current contract (`markdown`) and add an explicit JSON option so existing clients are not broken. *Depends on 5*.
10. Phase 5 - Unit and integration tests. Add new tests without touching existing markdown expectations: API (`output_format`), serialization, structure fallback, CLI with `--output-format`, and regression for `result.markdown`/`result.text_content`. *Depends on 8 and 9*.
11. Phase 5 - Documentation. Update the main README and package README with Python/CLI usage examples for `markdown`, `json`, `both`, the JSON schema, and compatibility guarantees.

**Relevant files**
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/_base_converter.py` - extend `DocumentConverterResult` and serialization helpers.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/_markitdown.py` - `output_format` parameter in public API and `_convert` pipeline.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/__main__.py` - CLI flag `--output-format` and output rules.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/converters/_csv_converter.py` - first structured converter (tables).
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/converters/_xlsx_converter.py` - sheet and row/cell structure.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/converters/_html_converter.py` - structure by relevant HTML nodes/blocks.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/src/markitdown/converters/_ipynb_converter.py` - notebook cell structure.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/tests/test_module_misc.py` - result API regression.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/tests/test_module_vectors.py` - existing markdown compatibility + new JSON cases.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/tests/test_cli_misc.py` - CLI argument and JSON output tests.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/tests/test_cli_vectors.py` - vector validation with alternate formats.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown-mcp/src/markitdown_mcp/__main__.py` - MCP compatibility and JSON option.
- `c:/IA/tools/IA-TOOLS-markitdown/README.md` - end-user documentation.
- `c:/IA/tools/IA-TOOLS-markitdown/packages/markitdown/README.md` - package documentation and examples.

**Verification**
1. Run module tests to ensure compatibility: `uv run pytest packages/markitdown/tests/test_module_misc.py packages/markitdown/tests/test_module_vectors.py`.
2. Run CLI tests: `uv run pytest packages/markitdown/tests/test_cli_misc.py packages/markitdown/tests/test_cli_vectors.py`.
3. Add and run new JSON serialization tests (basic and structured) per priority converter.
4. Manual Python test: `result = md.convert(path, output_format='both')` and verify markdown + basic JSON + structured JSON are present.
5. Manual CLI test: `markitdown input.ext --output-format json` and `--output-format both`, validating parseable JSON (`json.loads`) and markdown regression behavior when applicable.
6. MCP test to confirm existing clients still receive markdown by default.

**Decisions**
- Confirmed scope: official library (`packages/markitdown`), not only local script.
- Confirmed output type: both (`basic_json` and `structured_json`).
- Compatibility: do not remove or rename `result.markdown` or `result.text_content`.
- Strategy: introduce JSON as an opt-in capability (`output_format`) to minimize breaking risk.
- Includes: Python API, CLI, tests, docs, MCP (compatibility + explicit JSON option).
- Excludes: full redesign of all converters in a single iteration; will be done by type priority.

**Further Considerations**
1. Define whether `output_format='json'` should return an enriched `DocumentConverterResult` or an alternate type; recommendation: keep `DocumentConverterResult` to avoid breakage.
2. Decide `both` format behavior in CLI (single combined JSON embedding markdown vs. separate artifacts); recommendation: combined JSON in stdout with future option for a secondary file.
3. Version the JSON schema (`schema_version`) from the first release to enable evolution without breaking changes.
