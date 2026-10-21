# Contributing to Matrix Rain and Lock

Write everything in English: code, docs, comments and commit messages.

Validate every change before you push:

```bash
omarchy plugin validate .
qmllint -I /usr/share/omarchy/shell MatrixBackground.qml MatrixRain.qml LockView.qml Service.qml
python3 -B -m unittest discover -s tests -v
```

The lock is a minimal derivation of the installed Omarchy lock. Keep the
derivation minimal:

- `Service.qml` adds exactly one `MatrixBackground` block. The PAM flow,
  the session lock handling and the timers stay identical to
  `/usr/share/omarchy/shell/plugins/lock/Service.qml`.
- `LockView.qml` replaces only the wallpaper background with `MatrixRain`.
  The password field, the fingerprint hint and the signals stay identical.
- `tests/test_contract.py` fails when the derivation drifts. Update the
  expected Omarchy version together with the code, never silently.
  Do not reorder, regroup or comment `Service.qml` and `LockView.qml`
  beyond their rain blocks: the test requires byte equality with upstream,
  so ordering work belongs in `MatrixRain.qml`, `MatrixBackground.qml`,
  tools and docs.

Do not add privilege escalation, network access, a self-updater, a theme, a screensaver, a
widget, a hook or a system file. This plugin draws rain on the desktop and
inside its own lock clone, nothing else.

Never commit `AGENTS.md`, `CLAUDE.md`, symlinks or agent files. Keep local
notes untracked through `.git/info/exclude`.
