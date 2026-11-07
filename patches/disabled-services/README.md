# disabled-services: turn off PostgreSQL, CUPS and the print port

**For:** DSM 4.2-3259.
**Files:** `/usr/syno/etc/rc.d/S20pgsql.sh`, `/usr/syno/etc/rc.d/S55cupsd.sh` and `/usr/syno/sbin/cups-lpd`,
made non-executable, plus one line removed from `/etc/inetd.conf`.

## Why

The DS409slim has 128 MB of RAM. PostgreSQL supports Photo Station and similar DSM packages. CUPS is
printer sharing. If you use neither, they only take memory. DSM's start-up runs only the rc.d scripts that
are executable, so taking the execute bit away stops them from starting at boot.

Disabling CUPS doesn't close the **LPD print port (TCP 515)**. At every boot, DSM's inetd start script
(`S03inetd.sh`) adds a `printer … cups-lpd` line to `/etc/inetd.conf` whenever `/usr/syno/sbin/cups-lpd`
is executable. So the port keeps accepting print jobs that go nowhere. Take the execute bit off `cups-lpd`
too, and remove the line once: DSM then stops adding it back.

**Don't do this if you use** Photo Station, the Media Server's database or other packages that need
PostgreSQL, or a printer shared by the NAS.

## Apply

On the NAS, as root:

```sh
chmod a-x /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh /usr/syno/sbin/cups-lpd
cp -p /etc/inetd.conf /etc/inetd.conf.bak
grep -v '^printer' /etc/inetd.conf.bak > /etc/inetd.conf
kill -HUP $(cat /var/run/inetd.pid)          # inetd re-reads its config: port 515 closes now
```

PostgreSQL and CUPS stop at the next boot. To stop one now, run `/usr/syno/etc/rc.d/<script> stop`.

## Check

```sh
ls -l /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh /usr/syno/sbin/cups-lpd   # -rw-r--r--
ps w | grep -E 'postgres|cupsd' | grep -v grep                                              # nothing
netstat -ltn | grep ':515 '                                                                  # nothing
```

## Undo

```sh
chmod a+x /usr/syno/etc/rc.d/S20pgsql.sh /usr/syno/etc/rc.d/S55cupsd.sh /usr/syno/sbin/cups-lpd
```

DSM adds the `printer` line back at the next boot.
