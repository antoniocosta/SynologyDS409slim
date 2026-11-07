# --- Synology CLI shutdown/reboot fix ---------------------------------------
# DSM's shutdown unmounts /volume1 and runs killps, which kills every process
# using it, including the ssh shell that started the shutdown (your home is
# on /volume1). That is why plain poweroff/reboot stalled with services
# stopped but the box still on.
# Fix: run detached (nohup) with cwd=/ so killps has nothing to kill.
# Drop /opt/bin/sudo if you log in as root.
poweroff() { /opt/bin/sudo sh -c 'cd /; nohup /usr/syno/bin/syno_poweroff_task -s </dev/null >/dev/null 2>&1 &'; echo "power-off launched (detached)"; }
reboot()   { /opt/bin/sudo sh -c 'cd /; nohup /sbin/reboot </dev/null >/dev/null 2>&1 &'; echo "reboot launched (detached)"; }
halt()     { poweroff; }
shutdown() { echo "(ignoring '$*')"; poweroff; }
# ---------------------------------------------------------------------------
