# shutdown-profile: make `poweroff` and `reboot` work over ssh

**For:** DSM 4.2-3259.
**File:** `/etc/profile` (system-wide, so root and every user get it). DSM only restores this file from
`/etc.defaults/profile` during a DSM upgrade, and DSM 4.2-3259 is the last one.

## The problem

Over ssh, plain `poweroff` or `reboot` stalls: every service stops but the NAS stays on, and the DSM web
page disappears. DSM's shutdown unmounts `/volume1` and runs `killps`, which kills every process using it.
That includes the ssh shell that started the shutdown, because the user's home folder is on `/volume1`.

## The fix

Shell functions that run the real command detached (`nohup`) from `/`, so `killps` has nothing of ours to
kill: [`profile-snippet.sh`](profile-snippet.sh), appended to `/etc/profile`. They use `/opt/bin/sudo`
(Optware); drop that prefix if you log in as root.

They work in any **login shell** (`ssh nas`, then type `reboot`). `ssh nas reboot` runs no login shell, so it
doesn't read `/etc/profile` and stalls as before. From a script, use the full command:

```sh
ssh -t nas "/opt/bin/sudo sh -c 'cd /; nohup /sbin/reboot </dev/null >/dev/null 2>&1 &'"
```

## Apply

First check that the snippet isn't already there: `grep -c "shutdown/reboot fix" /etc/profile` should print `0`.

```sh
cat profile-snippet.sh | ssh nas 'cat > ~/profile-snippet.sh'
```

On the NAS, as root:

```sh
cp -p /etc/profile /etc/profile.bak
cat ~<user>/profile-snippet.sh >> /etc/profile
```

**Check:** log in again and run `type reboot`. It should say `reboot is a shell function`.

**Undo:** `cp /etc/profile.bak /etc/profile`

## If a shutdown is already stuck

Services are stopped but the box is still on. As root:

```sh
rm -f /var/run/scemd.pid; scemd                        # bring back the service that runs fans and beeps
cd /; nohup /sbin/reboot </dev/null >/dev/null 2>&1 &
```
