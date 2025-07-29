# Iron Book Python SDK

A Python SDK for interacting with Iron Book by Identity Machines. This SDK provides seamless integration with Iron Book's agent registration, authentication, and policy decision APIs.

## Features

- **Agent Registration**: Register new agents and obtain Verifiable Credentials
- **Authentication**: Get authentication tokens for agent operations
- **Policy Decisions**: Evaluate policy decisions for agent actions
- **Policy Upload**: Upload a new access control policy to enforce actions against
- **Async Support**: Full async/await support for high-performance applications
- **Type Safety**: Comprehensive type hints and dataclass definitions
- **Modern HTTP Client**: Built on httpx for reliable HTTP operations

## Installation

```bash
pip install ironbook-sdk
```

## Quick Start

```python
import asyncio
from ironbook_sdk import IronBookClient, RegisterAgentOptions, GetAuthTokenOptions, PolicyInput

async def main():
    # Initialize the client
    client = IronBookClient(api_key="your-api-key")
    
    # Register a new agent
    register_options = RegisterAgentOptions(
        agent_name="my-agent",
        capabilities=["query", "read"],
        developer_did="did:web:example.com"  # Optional
    )
    
    vc = await client.register_agent(register_options)
    print(f"Agent registered with VC: {vc}")
    
    # Get authentication token
    auth_options = GetAuthTokenOptions(
        agent_did="did:web:agent.example.com",
        vc=vc,
        audience="https://api.identitymachines.com",
        developer_did="did:web:example.com"  # Optional
    )
    
    token_data = await client.get_auth_token(auth_options)
    print(f"Auth token: {token_data}")
    
    # Make a policy decision
    policy_input = PolicyInput(
        did="did:web:agent.example.com",
        token=token_data["access_token"],
        action="query",
        resource="db://finance/tx"
    )
    
    decision = await client.policy_decision(policy_input)
    print(f"Policy decision: {decision.allow}")

# Run the async function
asyncio.run(main())
```

## API Reference

### IronBookClient

The main client class for interacting with Iron Book APIs.

#### Constructor

```python
IronBookClient(api_key: str, base_url: str = "https://dev.identitymachines.com")
```

**Parameters:**
- `api_key` (str): Your Iron Book API key
- `base_url` (str, optional): Base URL for the API. Defaults to development environment.

#### Methods

##### register_agent(opts: RegisterAgentOptions) -> str

Registers a new agent and returns a Verifiable Credential.

```python
vc = await client.register_agent(RegisterAgentOptions(
    agent_name="my-agent",
    capabilities=["query", "read"],
    developer_did="did:web:example.com"  # Optional
))
```

##### get_auth_token(opts: GetAuthTokenOptions) -> Dict[str, Any]

Gets an authentication token for an agent.

```python
token_data = await client.get_auth_token(GetAuthTokenOptions(
    agent_did="did:web:agent.example.com",
    vc=vc,
    audience="https://api.identitymachines.com",
    developer_did="did:web:example.com"  # Optional
))
```

##### policy_decision(opts: PolicyInput) -> PolicyDecision

Gets a policy decision for an agent action.

```python
decision = await client.policy_decision(PolicyInput(
    did="did:web:agent.example.com",
    token="jwt-token",
    action="query",
    resource="db://finance/tx",
    context={"amount": 1000, "ticker": "AAPL"}
))
```

## Data Types

### RegisterAgentOptions

Options for registering a new agent.

```python
@dataclass
class RegisterAgentOptions:
    agent_name: str              # Name of the agent
    capabilities: List[str]      # List of agent capabilities
    developer_did: Optional[str] # Developer's DID (optional)
```

### GetAuthTokenOptions

Options for getting an authentication token.

```python
@dataclass
class GetAuthTokenOptions:
    agent_did: str      # Agent's DID
    vc: str            # Verifiable Credential
    audience: str      # Token audience (e.g., API endpoint)
    developer_did: Optional[str] # Developer's DID (optional)
```

### PolicyInput

Input parameters for policy decision.

```python
@dataclass
class PolicyInput:
    did: str                      # Agent DID (subject)
    token: str                    # Short-lived access token (JWT)
    action: str                   # Action (e.g., "query")
    resource: str                 # Resource (e.g., "db://finance/tx")
    context: Optional[Dict[str, Any]] # Optional context (amount, ticker, etc.)
```

### PolicyDecision

Result of a policy decision evaluation.

```python
@dataclass
class PolicyDecision:
    allow: bool                    # Whether the action is allowed
    evaluation: Optional[List[Any]] # Policy evaluation details
    reason: Optional[str]          # Reason for the decision
```

### PolicyDecisionResult

Enumeration for policy decision results.

```python
class PolicyDecisionResult(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
```

### UploadPolicyOptions

Options for uploading a policy.

```python
@dataclass
class UploadPolicyOptions:
    agent_did: str                 # Agent's DID
    config_type: str               # Configuration type
    policy_content: str            # Policy content
    metadata: Any                  # Policy metadata
    developer_did: Optional[str]   # Developer's DID (optional)
```

## Advanced Usage

### Error Handling

```python
import asyncio
from ironbook_sdk import IronBookClient

async def safe_agent_operation():
    client = IronBookClient(api_key="your-api-key")
    
    try:
        # Your operations here
        vc = await client.register_agent(...)
        return vc
    except Exception as e:
        print(f"Error: {e}")
        return None

asyncio.run(safe_agent_operation())
```

### Custom Base URL

```python
# Use production environment
client = IronBookClient(
    api_key="your-api-key",
    base_url="https://api.identitymachines.com"
)
```

### Policy Decision with Context

```python
# Make a policy decision with rich context
decision = await client.policy_decision(PolicyInput(
    did="did:web:agent.example.com",
    token="jwt-token",
    action="transfer",
    resource="bank://account/123",
    context={
        "amount": 5000,
        "currency": "USD",
        "recipient": "alice@example.com",
        "timestamp": "2024-01-15T10:30:00Z"
    }
))

if decision.allow:
    print("Transfer approved")
    if decision.reason:
        print(f"Reason: {decision.reason}")
else:
    print("Transfer denied")
    if decision.reason:
        print(f"Reason: {decision.reason}")
```

### Upload Policy

```python
# Upload a new access control policy
upload_options = UploadPolicyOptions(
    agent_did="did:web:agent.example.com",
    config_type="opa",
    policy_content="package policy\nallow { input.action == \"read\" }",
    metadata={"version": "1.0", "description": "Read-only policy"},
    developer_did="did:web:example.com"  # Optional
)

result = await client.upload_policy(upload_options)
print(f"Policy uploaded: {result}")
```

## Development

### Setting up the development environment

```bash
# Clone the repository
git clone https://github.com/your-org/ironbook-sdk-python.git
cd ironbook-sdk-python

# Install development dependencies
pip install -e .
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Building and publishing

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Test upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI (when ready)
twine upload dist/*
```

## Support

- **Documentation**: [https://docs.identitymachines.com](https://docs.identitymachines.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/ironbook-sdk-python/issues)
- **Email**: devops@identitymachines.com

## Changelog

### 0.1.0
- Initial release
- Agent registration functionality
- Authentication token generation
- Policy decision evaluation
- Policy upload functionality
- Async/await support
- Comprehensive type hints
- Context manager support for client lifecycle management
- Convenience functions for simplified usage
