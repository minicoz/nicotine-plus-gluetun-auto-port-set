# Nicotine Plus Port Forwarding Plugin

This plugin is designed to integrate **Nicotine+ version 3.3.7 or higher** with the **Gluten VPN Docker container**, automatically updating Nicotine+ with the latest port forwarding number from the Gluten control plane server. This is especially useful when port numbers are randomized due to a restart of the Gluten VPN container.

When used together, the plugin ensures that the Nicotine+ client always uses the correct port for communication, even if the VPN container’s port changes. It automatically retrieves the latest port information every 24 hours to keep your configuration up-to-date.

## Features

- **Automatic port forwarding update**: Retrieves the latest port forwarding number from Gluten VPN control plane.
- **Robust to VPN restarts**: Handles randomized port assignments caused by Gluten container restarts.
- **Daily updates**: The plugin queries the control plane server every 24 hours to ensure the port remains current.
- **Integration with Nicotine+ 3.3.7+**: Designed to work with Nicotine+ version 3.3.7 or later.

## Installation Instructions

### Step 1: Check Nicotine+ Version

1. Open Nicotine+ and click the **burger menu** (three horizontal lines) next to the gear icon at the top-right of your window.
2. Select **About Nicotine+** from the dropdown.
3. Verify that the version number is **3.3.7 or higher**.
   - If your version is **lower than 3.3.7**, update Nicotine+ by visiting the [latest release page](https://github.com/nicotine-plus/nicotine-plus/releases/latest/).

### Step 2: Install the Plugin

1. Open the **Settings** menu in Nicotine+.
2. Go to **General** > **Plugins**.
3. Click **+ Add Plugins** to open the plugin installation dialog.
4. Download the plugin folder and extract its contents into the **plugins** folder of your Nicotine+ installation.
   - On Linux, this is typically located at **~/.nicotine/plugins**.
   - On Windows, it will be within the Nicotine+ program files or your user profile directory.
   
   
### Step 3: Enable the Plugin

1. After the plugin is added, you should see it listed in the **Plugins** section of the settings.
2. Enable the plugin by checking the box next to its name.
3. The plugin will now run automatically in the background and check for updated port numbers every 24 hours.

## How It Works

The plugin connects to the **Gluten VPN Docker container’s control plane API** to retrieve the latest forwarded port used by the VPN container. This information is then used to update the Nicotine+ configuration, ensuring that the Nicotine+ client always uses the correct port, even if the VPN container restarts and the port number changes.

### Key Concepts

- **GLUETUN_HOST**: The hostname or IP address of the Gluten VPN container’s API server.
- **GLUETUN_PORT**: The port number where the Gluten VPN control plane API is accessible.
- **Port Range**: The plugin updates the Nicotine+ configuration's port range to match the VPN port obtained from the Gluten control plane server.

### Environment Variables

To configure the plugin, you can set the following environment variables for the Gluten VPN container API:

- **GLUETUN_HOST** (optional): Specifies the host address for the Gluten VPN API (default is `localhost`).
- **GLUETUN_PORT** (optional): Specifies the port for the Gluten VPN control plane API (default is `8000`).

These environment variables allow you to customize the connection to the Gluten VPN control plane if it is not running on the default host and port.

### Explanation of Code:

- **Environment Variables**: The plugin uses `GLUETUN_HOST` and `GLUETUN_PORT` environment variables to connect to the Gluten VPN control plane API. You can set these variables if your Gluten VPN server is not running on the default `localhost:8000`.
- **Daily Task**: The `setup_daily_task` method schedules a task to run every 24 hours. The `run_update_port` method fetches the new port and updates Nicotine+'s configuration.
- **Port Update**: The plugin fetches the current forwarded port from the Gluten VPN server and updates the `portrange` setting in the Nicotine+ configuration file.
- **Reconnection**: After updating the port, the plugin triggers a reconnect to Nicotine+ to apply the changes.

## Troubleshooting

- If the plugin fails to update the port number, check the following:
  - Ensure that the **Gluten VPN Docker container** is running and accessible.
  - Verify that your **Nicotine+ version** is 3.3.7 or higher.
  - Check the plugin's logs for any error messages related to the connection or updates.

## Example docker compose setup

You can use the `fletchto99/nicotine-plus-docker` that containerizes nicotine+ and gluetun to pass through the values to your VPN of choice. 

```
version: "3"
services:
  gluetun:
    image: qmcgaw/gluetun
    hostname: gluetunvpn
    container_name: gluetun-nictoine
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun:/dev/net/tun
    ports:
      - 8000:8000 # gluetun control server (IMPORTANT)
      - 6060:6080 # nicotine-proper
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
    restart: unless-stopped

  nicotine-plus:
    image: ghcr.io/fletchto99/nicotine-plus-docker:latest
    container_name: nicotine-plus
    security_opt:
      - seccomp:unconfined #optional
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=America/Los_Angeles
    volumes:
      - /mnt:/data/mnt
    restart: unless-stopped
    network_mode: "service:gluetun"
    depends_on:
      gluetun:
        condition: service_started
```