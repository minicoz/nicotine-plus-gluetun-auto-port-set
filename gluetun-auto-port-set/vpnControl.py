from typing import Dict
from typing import Final
import json
import urllib.request
import urllib.error

class VpnControlServerApi(object):
    def __init__(self,
                 host: str,
                 port: int,
                 log):
        self._log = log
        self._host: Final[str] = host
        self._port: Final[int] = port

        # Set up the base URI for API
        self._API_BASE: Final[str] = f"http://{self._host}:{self._port}/v1"
        self._headers = {
            "Content-Type": "application/json"
        }

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
