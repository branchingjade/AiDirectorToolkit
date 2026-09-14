# crane + mihomo: Docker Image Pull Without Daemon Proxy (NAS GFW)

When `docker pull` fails because Docker daemon can't reach docker.io (no sudo for daemon.json, no mirrors working), two patterns solve it:

## Pattern 1: crane binary (pull images without Docker daemon)

crane is a single Go binary that pulls OCI images using its own network stack — reads `HTTP_PROXY`/`HTTPS_PROXY` env vars, unlike Docker daemon.

```bash
# Download for target arch
curl -sL -o /tmp/crane.tar.gz https://github.com/google/go-containerregistry/releases/download/v0.20.3/go-containerregistry_Linux_arm64.tar.gz
tar xzf /tmp/crane.tar.gz crane -C /usr/local/bin/

# Pull with proxy (arm64 for NAS)
HTTP_PROXY=http://127.0.0.1:7890 crane pull --platform linux/arm64 ubuntu:24.04 /tmp/ubuntu.tar

# Load into Docker
docker load -i /tmp/ubuntu.tar
```

**Verified on UGOS aarch64 NAS**: crane v0.20.3 pulls arm64 images, `docker load` imports them. Multi-arch images need `--platform` flag.

## Pattern 2: mihomo proxy on NAS

When builds need outbound proxy (git clone, npm install, pip install during Docker build) but daemon proxy can't be configured:

1. Download mihomo binary: `https://github.com/metacubex/mihomo/releases/download/vX.X.X/mihomo-linux-arm64-vX.X.X.gz`
2. Download GeoIP.dat + GeoSite.dat: `https://cdn.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/`
3. Write config:
   ```yaml
   mixed-port: 7890
   allow-lan: true
   bind-address: '*'
   proxy-providers:
     sub:
       type: http
       url: "<subscription URL>"
       interval: 86400
       health-check: { enable: false }
   rules:
     - GEOIP,CN,DIRECT
     - MATCH,Proxy
   ```
4. Run: `nohup ./mihomo -m -d /path/to/config/ > mihomo.log 2>&1 &`
5. Docker build: `--build-arg HTTP_PROXY=http://127.0.0.1:7890 --build-arg HTTPS_PROXY=http://127.0.0.1:7890`
6. In Dockerfile, add proxy ENV for RUN commands:
   ```dockerfile
   ARG HTTP_PROXY
   ARG HTTPS_PROXY
   ENV http_proxy=${HTTP_PROXY} https_proxy=${HTTPS_PROXY}
   ```

**Verified**: mihomo on NAS routes GitHub (200, 1.7s), hf-mirror (200, 0.5s), Docker Hub (401 auth expected), npm (200).

## Key pitfall: container proxy address

Inside Docker build, `127.0.0.1` refers to the container, NOT the host. Use the host's LAN IP: `http://192.168.1.2:7890` (or `http://host.docker.internal:7890` if Docker supports it).

## Integration with ugreen-nas-deploy

These patterns complement the existing `ugreen-nas-deploy` skill's `hub.rat.dev` mirror approach:
- `hub.rat.dev` prefix works for base images (python, node, alpine) — simple, no extra process
- crane + mihomo are needed when builds require git clone / npm install / pip install FROM within Dockerfile RUN commands — the daemon can't use mirror prefixes for these
