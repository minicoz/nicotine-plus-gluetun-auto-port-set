from pynicotine.pluginsystem import BasePlugin
from vpnControl import VpnControlServerApi
import threading
import os


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        G_HOST = os.environ.get('GLUETUN_HOST',"localhost")
        G_PORT = os.environ.get('GLUETUN_PORT',8000)
        self.gluetun_api = VpnControlServerApi(G_HOST, G_PORT, self.log)
        # Set up the task to run daily
        self.setup_daily_task()

    def setup_daily_task(self):
        # Calculate the time until the next "daily" execution (24 hours from now)
        self.run_update_port()
    
    def run_update_port(self):
        """This method will be called to perform the task and then reschedule itself."""
        self.update_port()

        # Schedule the next run in 24 hours (86400 seconds)
        threading.Timer(86400, self.run_update_port).start()

    def update_port(self):
        # Get port from gluetun
        try:
            vpn_port = self.gluetun_api.forwarded_port
        except Exception as e:
            self.log(f"Error fetching VPN port: {str(e)}")
            return
        
        # Get the current port range in Nicotine
        old_port_range = self.config.sections["server"]["portrange"]

        # If the port range has changed, set the new one
        new_port_range = (vpn_port, vpn_port)
        if old_port_range != new_port_range:
            self.log("The forwarded port has changed, setting new port...")
            self.log(f"Current port range is: {old_port_range}")
            try:
                self.config.sections["server"]["portrange"] = new_port_range
                self.core.reconnect()
            except Exception as e:
                self.log("Could not access settings or configuration. Required Nicotine version is 3.3.7+ for method reconnect")
                self.log(e)
                return
        
            self.log(f"New port range is: {new_port_range}, success")
    
    def __del__(self):
        """Stop any pending scheduled tasks when the plugin is destroyed."""
        # No direct way to stop `threading.Timer` once started, but we can ignore errors on destruction.
        pass