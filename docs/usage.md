# Usage

## Example
```python
from pysigfox import Sigfox

client = Sigfox(
    username="test",
    password="test",
)

# Retrieve devices
client.devices(list_all=True)

# Retrieve device information
client.devices("device_1")

# Retrieve device messages from the newest to the latest
client.device_messages("device_1")
```

## Pagination

Some Sigfox API endpoints are paginated. A helper `next` is used to go through the pages:
```python
import datetime
from pysigfox import Sigfox

client = Sigfox(
    username="test",
    password="test",
)

# list all devices
devices = client.devices()
while client.next:
   devices += client.next()
len(devices)

# list all last 24 hours messages
since_dt = datetime.datetime.now() - datetime.timedelta(hours=24)
messages = client.device_messages("device_1", since=since_dt)
while client.next:
    messages += client.next()
len(messages)
```

## API rate limiting

For Cloud efficiency and security reasons, Sigfox API is [rate limited](https://support.sigfox.com/docs/api-rate-limiting) on some end points. 
In this case the HTTP response is `HTTP 429: too many requests`.
For the paginated endpoints when `list_all=True`, the client take care of sleeping in order to respect this api limitation 
