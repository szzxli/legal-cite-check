# Privacy

- **Web page (`web/`)**: paste text or open a `.txt` file. Extraction
  runs in your browser. The page makes **no API calls** (no `fetch`,
  no `XMLHttpRequest` — asserted by tests), stores no brief text in
  localStorage, and sends nothing anywhere. The only third-party script
  is GoatCounter, a cookie-free page-view counter.
- **CLI**: by default, the only thing sent to CourtListener is the list
  of extracted citation strings, one per line. Your brief text is not
  sent. `--send-full-text` exists as an explicit opt-in and is off by
  default; use it only if you understand it sends your full text.
- **Token**: read from `COURTLISTENER_TOKEN` (environment / Actions
  secret). It is masked in Actions (`::add-mask::`) and never printed,
  logged, cached, or written into reports, artifacts, or test output.
- **Reports**: written only to the paths you pass (`--md`, `--json`,
  `--html`). No telemetry beyond GoatCounter page views.
- **Benchmark**: seed files contain only citation strings, case names,
  and links — no brief text, no user data.
