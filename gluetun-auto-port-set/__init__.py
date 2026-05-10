from pynicotine.pluginsystem import BasePlugin
from vpnControl import VpnControlServerApi
import threading
import os


class Plugin(BasePlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.host = os.environ.get('GLUETUN_HOST', "localhost")
        self.port = int(os.environ.get('GLUETUN_PORT', 8000))
        self.user = os.environ.get('GLUETUN_USER')
        self.password = os.environ.get('GLUETUN_PASS')
        self.gluetun_api = VpnControlServerApi(self.host, self.port, self.user, self.password, self.log)
        
        # Initialize timers
        self.port_check_timer = None
        self.reschedule_timer = None
        
        # Set up the task to run on a schedule
        self.setup_scheduled_task()

    def setup_scheduled_task(self):
        # Calculate the time until the next execution
        self.run_update_port()
    
    def run_update_port(self):
        """This method will be called to perform the task and then reschedule itself."""
        self.update_port()
        # Check that the port is open
        self.port_check_timer = threading.Timer(300, self.check_port_open)
        self.port_check_timer.start()

        # Schedule the next run in X seconds
        self.reschedule_timer = threading.Timer(3600, self.run_update_port)
        self.reschedule_timer.start()

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

    def check_port_open(self):
        port = self.config.sections["server"]["portrange"][0]
        if self.gluetun_api.is_port_closed(port):
            self.log(f"Port {port} is closed, will check again in 5 minutes")
    
    def __del__(self):
        """Stop any pending scheduled tasks when the plugin is destroyed."""
        if self.port_check_timer is not None:
            self.port_check_timer.cancel()
        if self.reschedule_timer is not None:
            self.reschedule_timer.cancel()
