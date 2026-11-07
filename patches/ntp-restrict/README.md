# ntp-restrict: make the clock actually sync (no patch needed)

**For:** DSM 4.2-3259.
**Fix:** a DSM setting. Control Panel → Regional Options → **NTP Service** → turn the NTP service on → Apply.

## The problem

With *Synchronize with a NTP server* set to `pool.ntp.org`, the clock still drifts or stays wrong, and
`/usr/sbin/ntpdc -c peers 127.0.0.1` never shows a `*` (synced) server. When the NAS is only an NTP
*client*, DSM writes this to `/etc/ntp.conf`:

```
restrict default ignore
restrict pool.ntp.org
```

`restrict pool.ntp.org` lets in only the address that name resolves to when ntpd starts. The `server
pool.ntp.org` line can pick another pool address, and ntpd then drops that server's replies. So the clock
gets set only by chance.

On an old DS409slim, a dead board battery (CR2032) makes this worse: the clock stops while the NAS is off,
so it boots behind by however long it was off.

## The fix: turn on DSM's NTP service

DSM's system library (`libsynosdk.so.4`) holds two sets of rules, and picks one by the
`run_ntp_server` setting:

```
restrict default ignore                                  NAS is an NTP client only
restrict default kod nomodify notrap nopeer noquery      NAS is also an NTP server
```

The second set is the usual safe client config: replies from any server count, and nobody can change or
query ntpd. So turning on **NTP Service** (Control Panel → Regional Options → NTP Service) makes DSM write
the right rules itself, every time you save. Nothing is patched, and saving the *Time* page stays safe.

The only side effect: devices on your network can also get the time from the NAS (UDP port 123). Don't
forward that port from your router.

**Check:**

```sh
grep restrict /etc/ntp.conf            # "restrict default kod nomodify notrap nopeer noquery", no "ignore"
/usr/sbin/ntpdc -c peers 127.0.0.1     # a "*" in front of a server = synced (takes up to a minute)
```

## If you don't want the NAS to serve time

Replace the `ignore` lines yourself, using [`ntp.conf`](ntp.conf) as the example:

```
restrict default nomodify notrap nopeer noquery
restrict -6 default nomodify notrap nopeer noquery
```

then run `/usr/syno/etc/rc.d/S23ntpd.sh restart` as root. DSM writes `ignore` back whenever the *Time* page
is saved with NTP Service off, so you'd have to redo it after each save.
