# smtp-tls12: let DSM's email notifications use TLS 1.2

**For:** DSM 4.2-3259 (hotfix, 2017-06-14). `patch.py` refuses any other build.
**File:** `/usr/lib/libsynosmtp.so` (22,528 bytes, compiled ARM code)

## The problem

DSM's email notifications (Control Panel → Notification → Email) fail with mail servers that require
TLS 1.2, which more and more providers do. The send test does nothing, and `/var/log/messages` shows:

```
notification.cgi: ssl.c (105) Failed to SSL_connect()
```

The NAS's OpenSSL (1.0.1m) supports TLS 1.2, but DSM's `SYNOSSLInit()` turns it off:

```
SSLv23_client_method()                          best version available
SSL_CTX_ctrl(ctx, 32, 0x08000000, 0)            SSL_OP_NO_TLSv1_2
SSL_CTX_ctrl(ctx, 32, 0x10000000, 0)            SSL_OP_NO_TLSv1_1
```

So DSM speaks only TLS 1.0, which servers are dropping one by one. To see what your mail server accepts, run
this on the NAS (replace `smtp.example.com` with your server):

```sh
for v in tls1 tls1_1 tls1_2; do echo "== $v"; echo QUIT | /usr/syno/bin/openssl s_client -$v -starttls smtp -connect smtp.example.com:587 2>&1 | grep -E 'Protocol|Cipher'; done
```

`Cipher : 0000` means that version was refused.

## The patch

Two instructions change from `mov r2, #<option>` to `mov r2, #0`, at file offsets `0x16b8` and `0x16c4`:
4 bytes each, nothing else. Those two calls then turn nothing off, and OpenSSL agrees on the best version
both sides support: TLS 1.2 with current servers, still TLS 1.0 with an old one.

| | sha256 |
|---|---|
| original | `b887db8b93135040ba6c5a130accd2a5e2e5aeb9574bca3c40fa0a7cd36f143f` |
| patched | `96a7b8496c741ed475c04fd8a6b839fc5410019f4e8fc2423240929b48327498` |

`patch.py` needs Python 3. Run it on any computer that can ssh to the NAS; the NAS's own Python is too old.

## Apply

On your computer:

```sh
ssh nas 'cat /usr/lib/libsynosmtp.so' > libsynosmtp.so
./patch.py apply libsynosmtp.so libsynosmtp.so.tls12
cat libsynosmtp.so.tls12 | ssh nas 'cat > ~/libsynosmtp.so.tls12'
```

On the NAS, as root: keep a backup, then swap the file with `mv`.

```sh
cd /usr/lib
cp -p libsynosmtp.so libsynosmtp.so.orig
cp ~<user>/libsynosmtp.so.tls12 libsynosmtp.so.new
chown root:root libsynosmtp.so.new && chmod 644 libsynosmtp.so.new
mv libsynosmtp.so.new libsynosmtp.so
```

Or in one line from your computer: `ssh -t nas '/opt/bin/sudo sh -c "cd /usr/lib && cp -p libsynosmtp.so libsynosmtp.so.orig && cp ~<user>/libsynosmtp.so.tls12 libsynosmtp.so.new && chown root:root libsynosmtp.so.new && chmod 644 libsynosmtp.so.new && mv libsynosmtp.so.new libsynosmtp.so"'`

**Test:** DSM → email settings → *Send a test email*. `notification.cgi` loads the library fresh each
time, so the test uses the patch straight away. Real **alerts** are sent by `scemd`, which keeps the old
copy until the NAS reboots.

**Check:** `ssh nas 'cat /usr/lib/libsynosmtp.so' > l && ./patch.py check l`

## Undo

```sh
cd /usr/lib && cp libsynosmtp.so.orig libsynosmtp.so.new && mv libsynosmtp.so.new libsynosmtp.so
```

## Notes on the email settings

Use your provider's SMTP server, port 587, *Secure connection (SSL/TLS)* on, and your login. Many providers
want an **app password** here rather than your normal password, and some need SMTP access turned on in
their settings first.

**DSM 4.2 has no sender field:** it sends every notification *from* the Primary email address. Many
providers refuse to send as an address your account doesn't own: the log then shows
`smtp.c (154) … 550 … (require: 250)`. If so, set Primary email to an address of the sending account and put
the address you want to read in Secondary email. The sending address gets a copy too; a filter rule at the
provider can delete those.
