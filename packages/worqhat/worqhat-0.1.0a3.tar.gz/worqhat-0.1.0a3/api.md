# Worqhat

Types:

```python
from worqhat.types import RetrieveServerInfoResponse
```

Methods:

- <code title="get /">client.<a href="./src/worqhat/_client.py">retrieve_server_info</a>() -> <a href="./src/worqhat/types/retrieve_server_info_response.py">RetrieveServerInfoResponse</a></code>

# Health

Types:

```python
from worqhat.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/worqhat/resources/health.py">check</a>() -> <a href="./src/worqhat/types/health_check_response.py">HealthCheckResponse</a></code>

# Flows

Types:

```python
from worqhat.types import FlowRetrieveMetricsResponse
```

Methods:

- <code title="get /flows/metrics">client.flows.<a href="./src/worqhat/resources/flows.py">retrieve_metrics</a>(\*\*<a href="src/worqhat/types/flow_retrieve_metrics_params.py">params</a>) -> <a href="./src/worqhat/types/flow_retrieve_metrics_response.py">FlowRetrieveMetricsResponse</a></code>
