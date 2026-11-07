# terminfo: make modern terminals work over ssh

**For:** DSM 4.2-3259.
**File:** adds `/usr/share/terminfo/x/xterm-256color` (system-wide, so every user and root get it).

## The problem

Modern terminals (macOS Terminal, iTerm2, most Linux terminals) tell the server they are
`xterm-256color`. DSM 4.2 ships no description of that terminal type, so over ssh `vi`, `less`, `top`
and `clear` complain (`unknown terminal type`, `'xterm-256color': unknown terminal type`) or draw garbage.
Common workarounds are setting `TERM=xterm` by hand or exporting it in `~/.profile`, but those only cover
one user.

## The fix

Add the `xterm-256color` terminfo entry. It is a small compiled file, the same on every system, and
nearly every Linux machine already has one.

From a Linux computer (on a Mac, `infocmp -x xterm-256color` and `tic` produce a compatible file):

```sh
cat /usr/share/terminfo/x/xterm-256color | ssh nas 'cat > ~/xterm-256color'   # or /lib/terminfo/x/...
```

On the NAS, as root:

```sh
mkdir -p /usr/share/terminfo/x
cp ~<user>/xterm-256color /usr/share/terminfo/x/xterm-256color
chmod 644 /usr/share/terminfo/x/xterm-256color
```

ssh passes the terminal type through by itself, so nothing needs to set `TERM` afterwards. Any
`export TERM=…` lines in your dotfiles can go.

**Check:** log in again and run `clear` or `top`. **Undo:** `rm /usr/share/terminfo/x/xterm-256color`
