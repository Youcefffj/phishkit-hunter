# PhishKit-Hunter

Defensive scanner that hunts **exposed phishing-kit exfiltration files** — the
`FULLZ.html`, `captured.txt`, `visits.txt`, `SMS.html` drops where kits stash
what they steal. Point it at a suspected kit URL and it finds those artifacts so
defenders can **identify victims and drive takedowns**.

![demo](demo/demo.gif)

> ⚠️ **Authorized use only.** Run this against infrastructure you're allowed to
> investigate. Captured data is victim data — handle it under your org's rules,
> minimize retention, never redistribute.

## Features

- Concurrent probing with a configurable worker pool
- **Catch-all guard** — a decoy path filters out hosts that answer `200` to everything
- Optional **parent-directory walk**
- Retries, custom User-Agent, per-request timeout
- `prepare` subcommand to clean/de-dupe raw URL lists
- Packaged, typed, unit-tested

## Install

```bash
pip install -e .          # provides the `pkhunter` command
```

## Usage

```bash
cp data/targets.example.txt data/targets.txt   # add your base URLs
pkhunter scan                                  # scan them
pkhunter scan --parent --workers 40            # walk parent dirs, more concurrency
pkhunter prepare raw_urls.txt -o data/targets.txt
```

Full flags: `pkhunter scan --help`. Try it offline with the [demo](demo/).

## How it works

1. Expand each target (and its parent dirs with `--parent`), de-duplicated.
2. Drop catch-all hosts using the sentinel path.
3. Probe the wordlist concurrently; save every genuine `200` artifact to `captures/`.

## Develop

```bash
pip install -e ".[dev]" && pytest
```

## License

MIT — see [LICENSE](LICENSE).
