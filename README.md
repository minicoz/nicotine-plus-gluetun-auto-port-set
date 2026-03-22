# Nicotine Plus Gluetun VPN AUTO Set Port Plugin

This plugin is designed to integrate **Nicotine+ version 3.3.7 or higher** with the **Gluetun VPN Docker container**, automatically updating Nicotine+ with the latest port forwarding number from the Gluetun control plane server. This is especially useful when port numbers are randomized due to a restart of the Gluetun VPN container.

When used together, the plugin ensures that the Nicotine+ client always uses the correct port for communication, even if the VPN container’s port changes. It automatically retrieves the latest port information every 24 hours to keep your configuration up-to-date.

---

## Features

- **Automatic port forwarding update**: Retrieves the latest port forwarding number from Gluetun VPN control plane.
- **Robust to VPN restarts**: Handles randomized port assignments caused by Gluetun container restarts.
- **Daily updates**: The plugin queries the control plane server every 24 hours to ensure the port remains current.
- **Authentication support**: Supports authenticated access to the Gluetun control server.
- **Integration with Nicotine+ 3.3.7+**: Designed to work with Nicotine+ version 3.3.7 or later.

---

## Installation Instructions

### Step 1: Check Nicotine+ Version

1. Open Nicotine+ and click the **burger menu** (three horizontal lines) next to the gear icon at the top-right of your window.
2. Select **About Nicotine+** from the dropdown.
3. Verify that the version number is **3.3.7 or higher**.
   - If your version is lower, update via the latest release page:  
     https://github.com/nicotine-plus/nicotine-plus/releases/latest/

---

### Step 2: Install the Plugin

1. Open the **Settings** menu in Nicotine+.
2. Go to **General** > **Plugins**.
3. Click **+ Add Plugins**.
4. Extract the plugin folder into your Nicotine+ plugins directory:
   - Linux: `~/.nicotine/plugins`
   - Windows: Nicotine+ install or user profile directory

---

### Step 3: Enable the Plugin

1. Locate the plugin in the Plugins list.
2. Enable it via the checkbox.
3. The plugin runs automatically and checks for updates periodically (default: hourly).

---

## How It Works

The plugin connects to the **Gluetun VPN Docker container’s control plane API** to retrieve the latest forwarded port. It then updates Nicotine+ so it always uses the correct port—even after VPN restarts.

---

## Key Concepts

- **GLUETUN_HOST**: Hostname or IP of the Gluetun API server  
- **GLUETUN_PORT**: Port where the API is exposed  
- **Authentication**: Gluetun control server now requires credentials  
- **Port Range**: Updated dynamically in Nicotine+ config  

---

## Environment Variables

### Nicotine+ Container (REQUIRED)

You must define authentication credentials:

- **GLUETUN_USER**: Username for Gluetun API  
- **GLUETUN_PASS**: Password for Gluetun API  

---

### Gluetun Container

Enable authentication on the control server:

```bash
HTTP_CONTROL_SERVER_AUTH_DEFAULT_ROLE='{"auth":"basic","username":"username","password":"mypassword"}'
```

Make sure these credentials match the ones defined in the Nicotine+ container:

```bash
GLUETUN_USER=username
GLUETUN_PASS=mypassword
```

---

### Optional Variables

- **GLUETUN_HOST** (default: `localhost`)
- **GLUETUN_PORT** (default: `8000`)

---

## Explanation of Code

- **Authenticated Requests**: The plugin uses `GLUETUN_USER` and `GLUETUN_PASS` to authenticate with the Gluetun API.
- **Environment Variables**: `GLUETUN_HOST` and `GLUETUN_PORT` define where the API is reached.
- **Scheduled Task**: Runs every 24 hours to fetch updated port info.
- **Port Update**: Updates Nicotine+ `portrange` setting.
- **Reconnect**: Forces Nicotine+ to reconnect after updating.

---

## Troubleshooting

- Ensure Gluetun container is running
- Verify authentication credentials match between containers
- Confirm port `8000` is exposed and reachable
- Check plugin logs for authentication or connection errors

---

## Example Docker Compose Setup

```yaml
version: "3"
services:
  gluetun:
    image: qmcgaw/gluetun
    hostname: gluetunvpn
    container_name: gluetun-nicotine
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    ports:
      - 8000:8000
      - 6060:6080
    volumes:
      - /home/Configs/nicotine/gluetun:/gluetun
    environment:
      - VPN_SERVICE_PROVIDER=protonvpn
      - VPN_TYPE=wireguard
      - WIREGUARD_PRIVATE_KEY=
      - SERVER_COUNTRIES='United States'
      - PORT_FORWARD_ONLY=on
      - TZ=America/Los_Angeles
      - UPDATER_PERIOD=24h
      - VPN_PORT_FORWARDING_STATUS_FILE=/gluetun/forwarded_port
      - HTTP_CONTROL_SERVER_AUTH_DEFAULT_ROLE={"auth":"basic","username":"username","password":"mypassword"}
    restart: unless-stopped

  nicotine-plus:
    image: ghcr.io/fletchto99/nicotine-plus-docker:latest
    container_name: nicotine-plus
    security_opt:
      - seccomp:unconfined
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
      - GLUETUN_USER=username
      - GLUETUN_PASS=mypassword
    volumes:
      - /mnt:/data/mnt
    restart: unless-stopped
    network_mode: "service:gluetun"
    depends_on:
      gluetun:
        condition: service_started
```
