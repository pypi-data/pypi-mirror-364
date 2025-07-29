# ironbook/client.py
import httpx
import json
from typing import Dict, Any, Optional
from .types import (
    RegisterAgentOptions, 
    GetAuthTokenOptions, 
    PolicyDecision, 
    PolicyInput,
    UploadPolicyOptions
)

class IronBookError(Exception):
    """Base exception for IronBook SDK errors"""
    pass

class IronBookClient:
    """IronBook Trust Service client"""
    
    def __init__(self, api_key: str, base_url: str = "https://dev.identitymachines.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'x-ironbook-key': self.api_key
        }
    
    async def register_agent(self, opts: RegisterAgentOptions) -> Dict[str, Any]:
        """
        Registers a new agent with the Iron Book Trust Service
        
        Args:
            opts: Registration options including agent name, capabilities, and developer DID
            
        Returns:
            Dict[str, Any]: Response containing vc (Verifiable Credential as a compact-format signed JWT string for this agent), agentDid, and developerDid
            
        Raises:
            IronBookError: If registration fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/agents/register",
                headers=self._get_headers(),
                json={
                    'agentName': opts.agent_name,
                    'capabilities': opts.capabilities,
                    'developerDID': opts.developer_did
                }
            )
            
            if not response.is_success:
                raise IronBookError(f"Agent registration error: {response.status_code}")
            
            return response.json()  # Returns Verifiable Credential (compact-format signed JWT string)
            
        except httpx.RequestError as e:
            raise IronBookError(f"Network error during agent registration: {e}")
        except json.JSONDecodeError as e:
            raise IronBookError(f"Invalid JSON response during agent registration: {e}")
    
    async def get_auth_token(self, opts: GetAuthTokenOptions) -> Dict[str, Any]:
        """
        Gets a short-lived one-shot JIT access token for the agent to perform an action
        
        Args:
            opts: Authentication options including agent DID, developer DID, VC, and audience
            
        Returns:
            Dict[str, Any]: Response containing access_token and expires_in
            
        Raises:
            IronBookError: If authentication fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/auth/token",
                headers=self._get_headers(),
                json={
                    'agentDid': opts.agent_did,
                    'developerDid': opts.developer_did,
                    'vc': opts.vc,
                    'audience': opts.audience
                }
            )
            
            if not response.is_success:
                raise IronBookError(f"Auth token error: {response.status_code}")
            
            return response.json()  # { access_token, expires_in, … }
            
        except httpx.RequestError as e:
            raise IronBookError(f"Network error during authentication: {e}")
        except json.JSONDecodeError as e:
            raise IronBookError(f"Invalid JSON response during authentication: {e}")
    
    async def policy_decision(self, opts: PolicyInput) -> PolicyDecision:
        """
        Gets a policy decision from the Iron Book Trust Service and consumes the one-shot JIT access token
        
        Args:
            opts: Policy decision input including agent DID, token, action, resource, and context
            
        Returns:
            PolicyDecision: Policy decision result with allow/deny and additional details
            
        Raises:
            IronBookError: If policy decision fails
        """
        try:
            headers = self._get_headers()
            headers['Authorization'] = f'Bearer {opts.token}'
            
            response = await self.client.post(
                f"{self.base_url}/policy/decision",
                headers=headers,
                json={
                    'agentDid': opts.agent_did,  # agent DID
                    'policyId': opts.policy_id,   # policy ID
                    'action': opts.action,  # e.g. "query"
                    'resource': opts.resource,  # e.g. "db://finance/tx"
                    'context': opts.context or {}  # optional: amount, ticker, etc.
                }
            )
            
            if not response.is_success:
                error_msg = response.text
                raise IronBookError(f"Policy decision error: {response.status_code}: {error_msg}")
            
            data = response.json()
            return PolicyDecision(
                allow=data.get('allow', False),
                evaluation=data.get('evaluation'),
                reason=data.get('reason')
            )
            
        except httpx.RequestError as e:
            raise IronBookError(f"Network error during policy decision: {e}")
        except json.JSONDecodeError as e:
            raise IronBookError(f"Invalid JSON response during policy decision: {e}")

    async def upload_policy(self, opts: UploadPolicyOptions) -> Dict[str, Any]:
        """
        Uploads a new access control policy to the Iron Book Trust Service
        
        Args:
            opts: Policy upload options including developer DID, agent DID, 
                config type, policy content, metadata, and API key
            
        Returns:
            Response from the policy upload endpoint
            
        Raises:
            IronBookError: If the upload fails
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/policies",
                headers=self._get_headers(),
                json={
                    'developerDid': opts.developer_did,
                    'agentDid': opts.agent_did,
                    'configType': opts.config_type,
                    'policyContent': opts.policy_content,
                    'metadata': opts.metadata
                }
            )
            
            if not response.is_success:
                raise IronBookError(f"Policy upload error: {response.text}")
            
            return response.json()  # { access_token, expires_in, … }      

        except httpx.RequestError as e:
            raise IronBookError(f"Network error during agent registration: {e}")
        except json.JSONDecodeError as e:
            raise IronBookError(f"Invalid JSON response during agent registration: {e}")    

# Convenience functions for backward compatibility and simpler usage
async def register_agent(opts: RegisterAgentOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for registering an agent"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.register_agent(opts)

async def get_auth_token(opts: GetAuthTokenOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for getting one-shot JIT authentication token"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.get_auth_token(opts)

async def policy_decision(opts: PolicyInput, api_key: str, base_url: str = "https://dev.identitymachines.com") -> PolicyDecision:
    """Convenience function for getting policy decision"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.policy_decision(opts)

async def upload_policy(opts: UploadPolicyOptions, api_key: str, base_url: str = "https://dev.identitymachines.com") -> Dict[str, Any]:
    """Convenience function for uploading a new policy"""
    async with IronBookClient(api_key, base_url) as client:
        return await client.upload_policy(opts)