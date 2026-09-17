# VHS tape — generates demo/demo.gif
# Install VHS: https://github.com/charmbracelet/vhs   (brew install vhs)
# Then, from the repo root:  vhs demo/demo.tape
#
# Prereq: pip install -e .   (so the `pkhunter` command exists)

Output demo/demo.gif

Set Shell "bash"
Set FontSize 18
Set Width 1200
Set Height 700
Set Theme "Catppuccin Mocha"
Set Padding 20

# Start the local mock kit host in the background (fully offline).
Hide
Type "python demo/mock_server.py >/dev/null 2>&1 &" Enter
Sleep 1s
Ctrl+L
Show

Type "# PhishKit-Hunter — scan a (local, fake) phishing kit" Enter
Sleep 1s
Type "pkhunter scan --targets demo/targets.txt" Enter
Sleep 3s

Type "# what did we capture?" Enter
Sleep 1s
Type "cat captures/hits.log" Enter
Sleep 3s

Hide
Type "kill %1 2>/dev/null" Enter
Sleep 500ms
