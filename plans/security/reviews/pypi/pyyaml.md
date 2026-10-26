# PyYAML 6.0.3: Contributor-Only Dependency

Decision on 2026-10-26: adopt with bounded use. Already installed locally at
6.0.3; no installation was performed during corpus development. Python lacks a
standard-library YAML parser; a maintained parser avoids inventing one. This is
not needed by users who only run workflow specs with CLI+jq.

Evidence: [PyPI version metadata](https://pypi.org/pypi/PyYAML/6.0.3/json),
[official parser documentation](https://pyyaml.org/wiki/PyYAMLDocumentation),
[upstream changes](https://github.com/yaml/pyyaml/blob/main/CHANGES).
PyPI lists MIT, Python >=3.8 and distribution wheels. Release metadata dates
6.0.3 to 2025-09-25. Current installed metadata has no Requires-Dist entries.
No shallow commercial-license trap identified. Contributor/bus-factor analysis,
Scorecard and per-file attestations were not verified and are not claimed.

An exact-version OSV query returned `{}` on 2026-10-26 (no matched advisory in
that response). This is not proof of package safety or a full source audit.
Unsafe historical YAML constructors are a material risk: the harness uses
`yaml.safe_load` only and does not load Python object tags. Install pinned wheels
with `--only-binary=:all:`; no sdist build fallback. Keep package processing
bounded to repository fixtures and reviewed changes. A pin is not provenance.
