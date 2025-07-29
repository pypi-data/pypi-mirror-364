# Workday RaaS Client

A Python client library for interacting with Workday Reports-as-a-Service APIs.

## Install


## Requirements

1. [A workday API client](https://doc.workday.com/reader/J1YvI9CYZUWl1U7_PSHyHA/qAugF2pRAGtECVLHKdMO_A).  These are used to initialize the RaaS client:
```py
IsuCredentials (
  client_id: str,
  client_secret: str,
  refresh_token: str,
)
```

2. A Workday REST API endpoint for a Workday RaaS report.

## Usage

The library provides two utility classes: `RaasClient` and `WorkdayRequest`.  These work together to build reusable requests.

```py
# Store the credentials as a JS object
credentials = IsuCredentials(
    client_id="myClientId",
    client_secret="myClientSecret",
    refresh_token="myRefreshToken",
)
authEndpoint = "authEndpoint"

# Initialize a client using the credentials and an auth endpoint
client = new RaasClient(credentials, authEndpoint)

# Build requests
raas_endpoint_1 = "https://myRaasEndpoint.com"
raas_endpoint_2
req_1 = client
    .request(raas_endpoint_1)
    .param("myParam", "myParamVal")
    .param("multiValParam", ["val1", "val2", "val3")
req2 = client
    .request(raas_endpoint_2)
    .param("myPrompt", "myPromptVal")

# Send the requests in different formats
json_res = await req_1.json()
xml_res = await req_1.xml()
csv = await req_2.csv()
```

