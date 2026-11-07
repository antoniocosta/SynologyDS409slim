# Synology DS409slim: patches for DSM 4.2

Keep your **Synology DS409slim** (4 × 2.5" bays, 2009; Marvell Kirkwood, 128 MB RAM) working, safe and
useful on its last firmware, **DSM 4.2-3259**, long after Synology stopped updating it. This repo holds
**small, documented patches** for problems that appeared as the rest of the world moved on, or that were
never fixed. Every patch comes with:

- the symptom, so you can recognise the problem;
- the cause, found by reading DSM's config files and, where needed, its compiled code;
- the exact change, and how to apply, check and undo it.

Nothing here needs Synology's servers, a newer DSM, or new hardware.

If you like this or find it useful, support the project by buying me a coffee.

<a href="https://www.buymeacoffee.com/antoniocosta" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 140px !important;" ></a>

## Why this repo exists

I own a DS409slim. It still does its job: a small, quiet, low-power RAID5 box for files and backups. But
Synology's last update for it came out in 2017, and the world around it keeps changing:

- **Mail servers** now refuse the old encryption DSM uses, so **disk and RAID alerts silently stop
  arriving.** That's the one warning you can't afford to lose on a NAS.
- **The clock** drifts, because DSM's own NTP config throws away most time-server replies.
- **Shutting it down** from the command line leaves it half off.

None of this is a hardware fault. The box is fine; only its software has aged. I don't accept that working
hardware should become e-waste, or quietly stop protecting your data, because its maker moved on.

So this repo does two things:

- **It fixes, minimally.** Each patch changes as little as possible: a config line, a file permission, or,
  for compiled code, a few bytes. Each one is checked against a known checksum and has a backup and an undo.
- **It documents.** Each problem is written up with its symptoms, cause and evidence, so other owners can
  recognise it, and so the fixes can be checked, repeated after a reset, or carried to similar models
  (DS409, DS209, DS109 and other DSM 4.x boxes).

It is a small act of **right to repair** and **keeping old hardware alive**: in the same spirit as
community firmware projects for routers and phones, it keeps a working device in service and out of
landfill.

## Quick start

1. **Check your DSM version.** Every patch here was made and tested on DSM 4.2-3259. On the NAS:

   ```sh
   cat /etc.defaults/VERSION
   # majorversion="4"  minorversion="2"  buildphase="hotfix"  buildnumber="3259"  builddate="2017/06/14"
   ```

2. **Get ssh and root.** Turn on SSH in Control Panel → Terminal. DSM 4.2 has no `sudo`: log in as `root`,
   or install `sudo` from Optware, which the commands here use as `/opt/bin/sudo`.

3. **Pick a patch** below and follow its README. In the commands, `nas` is your NAS's ssh host and `<user>`
   your login on it.

## Patches

| Patch | Symptom | Changes |
|---|---|---|
| [`smtp-tls12`](patches/smtp-tls12/) | Email notifications never arrive; *Send a test email* does nothing; `Failed to SSL_connect()` in the log. The mail server requires TLS 1.2, as more and more do | `/usr/lib/libsynosmtp.so`, 2 × 4 bytes |
| [`ntp-restrict`](patches/ntp-restrict/) | The clock drifts or stays wrong although NTP is on | nothing: a DSM setting (NTP Service on) |
| [`shutdown-profile`](patches/shutdown-profile/) | `poweroff` / `reboot` over ssh stop every service but leave the box on | `/etc/profile` |
| [`disabled-services`](patches/disabled-services/) | Low memory: PostgreSQL and CUPS run even when nothing uses them | 2 start-up scripts, `chmod a-x` |

**Status:** all four run on one real DS409slim (DSM 4.2-3259). `smtp-tls12` was checked by disassembling
the patched library, then tested end to end: DSM's test email went out over TLS 1.2. These
patches change system files on an unsupported device, so use them at your own risk and keep the backups.

## The DS409slim at a glance

| | |
|---|---|
| CPU | Marvell Kirkwood 88F6281, 1.2 GHz (Feroceon 88FR131, ARMv5, `armv5tel`) |
| RAM | 128 MB |
| Drives | 4 × 2.5" SATA (laptop drives) |
| Last DSM | 4.2-3259 hotfix, built 2017-06-14 |
| OpenSSL | system 1.0.1m (`/usr/lib/libssl.so.1.0.0`, `/usr/syno/bin/openssl`): supports TLS 1.2 |
| Shell | BusyBox 1.16.1 |

## Troubleshooting

- **Missing commands:** DSM's BusyBox is minimal: there's no `od`, `tr`, `strings`, `xxd` or `setsid`,
  and `cat`/`grep` have fewer options. The commands here avoid all of these.
- **Can't copy system files:** `scp` can't read DSM 4.2's system folders. Use `ssh nas 'cat <file>' > <file>`
  instead, and write back the same way into your home folder, then move the file into place as root.
- **Replacing a library:** never write over a library that is in use. Copy the new one to
  `<file>.new`, then `mv` it over the original. Running programs keep the old copy, and nothing reads a
  half-written file. A service picks up the new library when it restarts.
- **DSM undoes changes:** some DSM settings pages rewrite their config file when saved. Each patch's
  README says if it is affected.
- **The clock is wrong after power-off:** the board's CR2032 battery is probably dead. NTP corrects the
  clock once the NAS is online (with [`ntp-restrict`](patches/ntp-restrict/)). Changing the battery means
  opening the case.

## Layout

```
README.md
LICENSE                          GPL-3.0-or-later (this repo's own work)
patches/smtp-tls12/              README.md, patch.py (verifies checksums, patches 2 instructions)
patches/ntp-restrict/            README.md, ntp.conf
patches/shutdown-profile/        README.md, profile-snippet.sh
patches/disabled-services/       README.md
```

## Legal

- **This repo's own work** (the READMEs, `patch.py`, `ntp.conf` and `profile-snippet.sh`) is licensed
  under the **GNU General Public License v3.0 or later** (see [`LICENSE`](LICENSE)). It was written to let
  owners maintain hardware they own, through interoperability with a discontinued product.
- **Synology's software is not included.** No DSM files or binaries are in this repo. `patch.py` patches
  the copy on your own NAS, and checks it first by checksum. Synology and DSM are trademarks of Synology
  Inc. This project is not affiliated with or endorsed by Synology.
- **No warranty:** use these patches at your own risk. Each one keeps a backup and has an undo.
