# NAS Deployment Pitfalls (2026-08-26 session)

## Windows line endings → Linux shell

`.sh` files created on Windows have `\r\n` which breaks Linux shell. Fix: write in binary mode with `\n` only:
```python
with open('script.sh', 'wb') as f:
    f.write(b'#!/bin/sh\necho hello\n')
```

## paramiko SSH background processes

`ssh.exec_command('nohup ... &')` blocks because paramiko waits for the channel. Solutions:
- Write script to NAS, then `setsid sh /path/script.sh </dev/null >/dev/null 2>&1 &`
- Or use `docker compose up -d` which daemonizes natively
- Never rely on `&` alone in paramiko exec_command

## Plugin deployment: download ALL files

When manually installing plugins (not via `hermes plugins install`), download every file `__init__.py` imports. Missing files cause silent `ModuleNotFoundError`:
```python
import re
imports = re.findall(r'from \.(\w+) import', open('__init__.py').read())
# Download: __init__.py, plugin.yaml, README.md, plus every module in imports
```

## Plugin environment variables

Some plugins (e.g. `memory_tencentdb`) read from `os.environ`, NOT from `config.yaml`. Even if config.yaml has the values, the plugin won't see them unless they're in the process environment.

For Hermes gateway: use `hermes config set` with custom keys — they get bridged to environment variables. Or set via `setx` in Windows registry (affects new processes).

## Feishu adapter requires credentials

Feishu adapter validation requires `FEISHU_APP_ID` and `FEISHU_APP_SECRET` environment variables. Without these, the adapter fails with "config validation failed" even if the SDK is installed.

## Docker build with proxy

When Docker daemon can't reach external registries, pass proxy to build containers:
```bash
docker build --build-arg HTTP_PROXY=http://192.168.1.2:7890 \
             --build-arg HTTPS_PROXY=http://192.168.1.2:7890 \
             -f Dockerfile -t image:tag .
```
Note: use host LAN IP (`192.168.1.2`), not `127.0.0.1` (which refers to the container).


## mihomo GeoIP dat vs mmdb format (2026-08-26)

mihomo `-m` (mat mode) needs GeoIP/GeoSite in **dat format**, not mmdb. The `cdn.jsdelivr.net` mirror serves both — pick the right URL:

```python
# CORRECT - .dat format
"https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geoip.dat"   # 17MB dat
"https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/geosite.dat"  # 4MB dat

# WRONG - mmdb will be rejected with "failed to decode geoip file"
"https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/country.mmdb"
```

**Verify format before use**:
```python
with open('/volume1/docker/.../GeoIP.dat', 'rb') as f:
    head = f.read(2)
is_dat = head in (b'\x0a\x00', b'\x0b\x00')  # dat magic
```

**Symptoms of wrong format**:
- `failed to decode geoip file: proto: cannot parse invalid wire-format data`
- `GeoIP.dat invalid, remove and download`
- mihomo logs warn then fall back to "original ReadFile method" (geo routing broken silently)

**Also**: use `-m` flag (mat mode) when running mihomo. Without `-m`, mihomo uses mmdb format and rejects dat files.
