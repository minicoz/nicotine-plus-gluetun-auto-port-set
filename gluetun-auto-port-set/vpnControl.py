from typing import Dict
from typing import Final
import json
import urllib.request
import urllib.error
import base64


class VpnControlServerApi(object):
    def __init__(self,
                 host: str,
                 port: int,
                 username: str = None,
                 password: str = None,
                 log = None):
        self._log = log
        self._host: Final[str] = host
        self._port: Final[int] = port

        # Set up the base URI for API
        self._API_BASE: Final[str] = f"http://{self._host}:{self._port}/v1"
        
        # Set up headers
        self._headers = {
            "Content-Type": "application/json"
        }
        
        # Add basic auth if credentials provided
        if username and password:
            credentials = f"{username}:{password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self._headers["Authorization"] = f"Basic {encoded_credentials}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass  # No need to close anything for urllib

    def _query(self, endpoint) -> Dict:
        uri = self._API_BASE + endpoint
        self._log(f"Query to {uri}")

        req = urllib.request.Request(uri, headers=self._headers)
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    self._log("API query completed")
                    data = response.read()
                    return json.loads(data)
                else:
                    self._log(f"API returned {response.status} for {endpoint} endpoint")
                    raise Exception("VpnServerHttpCodeException")
        except urllib.error.HTTPError as e:
            self._log(f"HTTP error occurred: {e.code} - {e.reason}")
            raise Exception("VpnServerHttpCodeException")
        except urllib.error.URLError as e:
            self._log(f"URL error occurred: {e.reason}")
            raise Exception("VpnServerHttpCodeException")
        except Exception as e:
            self._log(f"Unexpected error: {e}")
            raise Exception("VpnServerHttpCodeException")

    @property
    def forwarded_port(self) -> int:
        endpoint = "/openvpn/portforwarded"
        data = self._query(endpoint)
        if "port" in data:
            vpn_forwarded_port: int = int(data["port"])
            self._log(f"VPN Port is {vpn_forwarded_port}")
            if 1023 < vpn_forwarded_port < 65535:
                return vpn_forwarded_port
            else:
                self._log(f"VPN Port invalid: {vpn_forwarded_port}")
                raise Exception("VpnServerInvalidPortException")
        else:
            self._log("Missing port data")
            raise Exception("VpnServerInvalidPortException")
        
    def is_port_closed(self, port):
        """Use the Slsknet port test to check that the port is open"""
        try:
            # Form the URL to check the port
            url = f"https://www.slsknet.org/porttest.php?port={port}"
            
            # Open the URL and read the response
            with urllib.request.urlopen(url, timeout=5) as response:
                # Read the response and decode it to a string
                response_body = response.read().lower()
                
                # Check if the port status is open
                if f"{port}/tcp open".encode() in response_body:
                    result = False
                elif f"{port}/tcp closed".encode() in response_body:
                    self._log(f"Port {port} is closed")
                    result = True
                else:
                    self._log(f"Unknown response from port checker: {response_body}")

                return result

        except urllib.error.URLError as e:
            self._log(f"Error: {e}")
            return 1
