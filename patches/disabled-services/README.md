# disabled-services: turn off PostgreSQL and CUPS

**For:** DSM 4.2-3259.
**Files:** `/usr/syno/etc/rc.d/S20pgsql.sh` and `/usr/syno/etc/rc.d/S55cupsd.sh`, made non-executable.

## Why

The DS409slim has 128 MB of RAM. PostgreSQL supports Photo Station and similar DSM packages. CUPS is
printer sharing. If you use neither, they only take memory. DSM's start-up runs only the rc.d scripts that
are executable, so taking the execute bit away stops them from starting at boot.

**Don't do this if you use** Photo Station, the Media Server's database or other packages that need
PostgreSQL, or a USB printer shared by the NAS.

## Apply / undo

On the NAS, as root:

```sh
chmod a-x /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh   # disable
chmod a+x /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh   # enable again
```

This takes effect at the next boot. To stop one now, run `/usr/syno/etc/rc.d/<script> stop`.

**Check:** `ls -l /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh` shows `-rw-r--r--`, and
`ps w | grep -E 'postgres|cupsd' | grep -v grep` prints nothing.
