# Demo

A fully **offline, safe** demo: a local mock host serves fake artifact files
(no real data), and `pkhunter` scans `127.0.0.1` for them. Nothing external is
contacted.

## Run it live

```bash
uv pip install -e .              # from the repo root, inside the venv
python demo/mock_server.py &     # local fake kit host on :8000
pkhunter scan --targets demo/targets.txt
cat captures/hits.log
kill %1                          # stop the mock host
```

Or just run the bundled script (starts/stops the mock host for you):

```bash
bash demo/run_demo.sh
```

## Record the animated SVG (no Homebrew needed)

Uses [asciinema](https://asciinema.org) (installed via `uv`) and
[svg-term-cli](https://github.com/marionebl/svg-term-cli) (run via `npx`):

```bash
uv tool install asciinema
asciinema rec demo/demo.cast -c "bash demo/run_demo.sh" --overwrite
npx svg-term-cli --in demo/demo.cast --out demo/demo.svg --window --width 90 --height 20
```

The main `README.md` already references `demo/demo.svg`.

## Prefer a real GIF?

With [VHS](https://github.com/charmbracelet/vhs) installed, `vhs demo/demo.tape`
writes `demo/demo.gif` (then point the README at it). VHS needs `ttyd` + `ffmpeg`,
which is why the SVG route above is the default on a Homebrew-less machine.
