# SolarEdge Home Automation
API wrapper for SolarEdge Home Automation service.

This is an undocumented api.

## Create a new connection by supplying your Solaredge HA token
```
service = solaredgeha.SolarEdgeHa(username, password)
```

## API Requests
2 API requests are supported. The methods return the parsed JSON response as a dict.

```
def login(self):

def get_sites(self):

def get_devices(self):

def activate_device(self, reporterId, level, duration=None):

```

