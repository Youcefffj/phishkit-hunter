# Demo

A fully **offline, safe** demo: a local mock host serves fake artifact files
(no real data), and `pkhunter` scans `127.0.0.1` for them. Nothing external is
contacted.

## Run it live

```bash
pip install -e .                 # from the repo root
python demo/mock_server.py &     # local fake kit host on :8000
pkhunter scan --targets demo/targets.txt
cat captures/hits.log
kill %1                          # stop the mock host
```

## Record the GIF

Uses [VHS](https://github.com/charmbracelet/vhs) (`brew install vhs`):

```bash
vhs demo/demo.tape               # writes demo/demo.gif
```

Then reference it at the top of the main `README.md`:

```markdown
![demo](demo/demo.gif)
```
