from pynicotine.pluginsystem import BasePlugin
from vpnControl import VpnControlServerApi
import threading
import os


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        G_HOST = os.environ.get('GLUETUN_HOST',"localhost")
        G_PORT = os.environ.get('GLUETUN_PORT',8000)
        self.glutun_api = VpnControlServerApi(G_HOST, G_PORT, self.log)
        # Set up the task to run daily
        self.setup_daily_task()

    def setup_daily_task(self):
        # Calculate the time until the next "daily" execution (24 hours from now)
        self.run_update_port()
    
    def run_update_port(self):
        """This method will be called to perform the task and then reschedule itself."""
        self.update_port()

        # Schedule the next run in 30 mins (1800 seconds)
        threading.Timer(1800, self.run_update_port).start()

    def update_port(self):
        current_port = self.config.sections["server"]["portrange"][0]
        if self.glutun_api.is_port_closed(port=current_port):
            try:
                self.log("Trying to get new port from gluetun")
                vpn_port = self.glutun_api.forwarded_port
            except Exception as e:
                self.log(f"Error fetching VPN port: {str(e)}")
                return
            try:
                self.config.sections["server"]["portrange"] = (vpn_port, vpn_port)
                self.core.reconnect()
            except Exception as e:
                self.log("Could not access settings or configuration. Required Nicotine version is 3.3.7+ for method reconnect")
                self.log(e)
                return
        else:
            self.log("Port is already open.")
        
        new_port_range = self.config.sections["server"]["portrange"]
        self.log(f"New port range is: {new_port_range}, success")
    
    def __del__(self):
        """Stop any pending scheduled tasks when the plugin is destroyed."""
        # No direct way to stop `threading.Timer` once started, but we can ignore errors on destruction.
        pass