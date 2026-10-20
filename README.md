# Matrix Rain and Lock

Digital rain on the desktop and behind the session lock. This is a
single-purpose Omarchy plugin. It is independent of the Enter the Matrix
theme and its optional pack.

## Status

This is an initial development build. It passes static checks
(`omarchy plugin validate`, `qmllint`, contract tests) but has not passed a
live lock, unlock, multi-monitor, installation or removal test. Do not use
it to secure a session until those tests pass.

## Install

Requirements first: Omarchy 4.0.5 with Quickshell and the stock
`omarchy.lock` plugin installed.

Add the plugin, then enable it:

```bash
omarchy plugin add https://github.com/tymurbogach/omarchy-matrix-rain-lock --enable
omarchy restart shell
```

Do not enable this plugin while another clone of `omarchy.lock` is
enabled. Two active lock clones compete for the same lock IPC target. If
the Enter the Matrix theme pack installed its own lock clone, restore
Omarchy's own lock through that pack's documented removal procedure
first. Then enable this plugin, restart the shell if the previous lock
remains loaded, and check the lock preview before testing a real session
lock:

```bash
omarchy-shell lock preview
```

The plugin replaces `omarchy.lock` while enabled. It does not install a
theme, screensaver, widget, hook, boot splash or system file. The desktop
rain stays on while the plugin is enabled, regardless of the active
theme.

## Usage

Lock the session as usual. The desktop shows rain behind windows. The
lock shows rain behind the password field. Open the preview to check the
lock without locking the session:

```bash
omarchy-shell lock preview
omarchy-shell lock hidePreview
```

The desktop overlay takes no pointer and no keyboard input.

## Configure

There are no settings. Enable or disable the plugin through Setup >
Plugins. The rain runs while the plugin is enabled and stops when it is
disabled. The lock is a copy of Omarchy's lock. Omarchy updates do not
update this copy. Review the lock against each supported Omarchy release
before updating it.

## Remove

Remove the plugin through Setup > Plugins, or run:

```bash
omarchy plugin remove io.github.tymurbogach.matrix-rain-lock --yes
omarchy restart shell
```

Omarchy restores its original lock. Verify this on the target version.
Do not disable or remove a lock while the session is locked.

## Requirements

- Omarchy 4.0.5. Other versions are not verified.
- Quickshell, Qt Quick and the installed Omarchy shell modules.
- The stock `omarchy.lock` source at
  `/usr/share/omarchy/shell/plugins/lock`, used only at build time to
  check the derivation.

No privilege escalation. No network access. No self-updater. No theme,
screensaver, widget, hook or system file.

## License

MIT, see `LICENSE`.

`Service.qml` and `LockView.qml` derive from Omarchy 4.0.5, MIT licensed,
copyright David Heinemeier Hansson. The rain shader derives from
`bjarneo/quickshell`, MIT licensed, copyright bjarneo. The shader source
is in `tools/matrix.frag`. `tools/generate-atlas.py` documents how the
glyph atlas was generated.
