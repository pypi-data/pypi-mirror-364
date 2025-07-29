# spounge-proto-py

Generated protobuf Python packages for Spounge AI ecosystem microservices.

## Installation

```bash
pip install spounge-proto-py
```

## Usage

```python
# Import your generated protobuf modules
from api.v2 import auth_gateway_service_pb2
from auth.v2 import auth_service_pb2
from common.v1 import common_pb2

# Create requests
auth_request = auth_service_pb2.LoginRequest(
    email="user@example.com", 
    password="password"
)

# Use with gRPC
import grpc
from api.v2 import auth_gateway_service_pb2_grpc

channel = grpc.insecure_channel('localhost:8080')
client = auth_gateway_service_pb2_grpc.AuthGatewayServiceStub(channel)
```

## Package Structure

Your protobuf modules are organized by domain and version:
- `api.v*` - API Gateway interfaces
- `auth.v*` - Authentication services
- `common.v*` - Shared definitions  
- `workflow.v*` - Workflow orchestration
- `dashboard.v*` - Analytics

## License

MIT License