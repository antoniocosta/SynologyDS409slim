# optware: how `/opt`, `sudo` and friends come up at boot

**For:** DSM 4.2-3259.
**Files:** `/etc/rc.local`, `/etc/rc.optware`, `/etc/profile` (one PATH line), and the Optware tree in `/volume1/@optware`.

This one isn't a fix. It records how Optware, the old community package system for Synology NASes, is
hooked into DSM. Every other patch here uses its `sudo` (`/opt/bin/sudo`), and these hooks are the first
thing lost if DSM is reinstalled or reset. Optware's package feeds are long gone, so it can't install
anything new, but what is already installed keeps working: `sudo`, bash, coreutils, perl, python 2.5, rsync,
and a gcc toolchain.

## How it is wired

1. **The packages live on the data volume:** `/volume1/@optware`. That survives a DSM reinstall, because a
   reinstall rewrites only the system partition.
2. **At boot, `/etc/rc.local` runs `/etc/rc.optware start`:**

   ```sh
   [ -x /etc/rc.optware ] && /etc/rc.optware start
   ```

3. **`/etc/rc.optware`** bind-mounts the volume folder onto `/opt`, then runs `/opt/etc/rc.optware`, which
   starts every `/opt/etc/init.d/S??*` script:

   ```sh
   REAL_OPT_DIR=/volume1/@optware
   if ! grep ' /opt ' /proc/mounts >/dev/null 2>&1; then
       mkdir -p /opt
       mount -o bind ${REAL_OPT_DIR} /opt
   fi
   [ -x /opt/etc/rc.optware ] && /opt/etc/rc.optware
   ```

4. **`/etc/profile`** puts Optware's tools first on the PATH:

   ```sh
   PATH=/opt/bin:/opt/sbin:$PATH
   ```

5. **`sudo`** is `/opt/bin/sudo` (setuid root), configured in `/opt/etc/sudoers`.

**Turn off Optware's rsync start-up script.** Optware's rsync package installs
`/opt/etc/init.d/S57rsyncd`, which runs at every boot. With its server disabled (the default,
`RSYNC_ENABLE=false`), it still runs `killall rsync` whenever no rsync server is running, killing *any*
rsync running at that moment, DSM's own included. DSM already ships the same rsync (`/usr/syno/bin/rsync`,
3.0.9), so nothing needs Optware's. The package can't simply be removed (`optware-devel` depends on it),
but Optware runs only `S??*` scripts, so renaming the script is enough. As root:

```sh
mv /opt/etc/init.d/S57rsyncd /opt/etc/init.d/disabled-S57rsyncd     # undo: rename it back
```

## Check

```sh
mount | grep ' /opt '          # /volume1/@optware on /opt type bind
ls -l /opt/bin/sudo            # -rwsr-xr-x root
```

## Restore after a DSM reinstall or reset

`/opt/bin/sudo` is gone until `/opt` is mounted again, so log in as `root` (DSM 4.2 uses the `admin`
password for root over ssh) and put the hooks back:

```sh
cat > /etc/rc.optware <<'EOF'
#!/bin/sh
REAL_OPT_DIR=/volume1/@optware
case "$1" in
    start)
        if ! grep ' /opt ' /proc/mounts >/dev/null 2>&1; then
            mkdir -p /opt
            mount -o bind ${REAL_OPT_DIR} /opt
        fi
        [ -x /opt/etc/rc.optware ] && /opt/etc/rc.optware
        ;;
esac
EOF
chmod 755 /etc/rc.optware
grep -q rc.optware /etc/rc.local || sed -i 's#^exit 0#[ -x /etc/rc.optware ] \&\& /etc/rc.optware start\n\nexit 0#' /etc/rc.local
/etc/rc.optware start
```

Then re-add the PATH line to `/etc/profile`, and reapply [`shutdown-profile`](../shutdown-profile/).
