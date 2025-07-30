"""Consul client module for both synchronous and asynchronous interactions.

This module provides AsyncConsulClient and ConsulClient classes for interacting 
with Consul in both asynchronous and synchronous ways respectively.
"""

import asyncio
import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union
import os
from consul import Consul as SyncConsul
from consul.aio import Consul as AsyncConsul


T = TypeVar('T')  # Return type for operations

class DefaultConsulClient:

    filename = "default_consul_data.json"

    def __init__(self):
        _get_path = lambda x: os.path.dirname(x)
        filepath = _get_path(_get_path(os.getcwd()))
        fullpath = os.path.join(filepath, self.filename)

        assert os.path.exists(fullpath), f"File not found at {fullpath}"

        with open(fullpath, 'r') as file:
            default_data = json.load(file)

        self.default_data = default_data

    def start(self) -> None:
        # This method is intentionally left blank.
        # It should be implemented by subclasses.
        pass

    def close(self) -> None:
        # This method is intentionally left blank.
        # It should be implemented by subclasses.
        pass

    def get_kv(self, key: str, index=None, recurse=False) -> Dict:
        return self.default_data["KV"][key]

    def get_service(self, service_name: str, index=None, tag=None):
        return self.default_data["Services"][service_name]

    def get_services(self) -> Dict:
        return {}

    def register_service(self,name,address,port,tags=None,check=None,service_id=None) -> bool:
        return True

    def get_kv_tree(self, prefix: str) -> Dict[str, str]:
        return {}

    def deregister_service(self, service_id):
        return None

class AsyncDefaultConsulClient(DefaultConsulClient):
    def __init__(self):
        super().__init__()

    async def start(self):
        return super().start()

    async def close(self):
        return super().close()

    async def get_kv(self, key: str, index=None, recurse=False):
        return super().get_kv(key, index, recurse)

    async def get_service(self, service_name: str, index=None, tag=None):
        return super().get_service(service_name, index, tag)

    async def get_services(self):
        return super().get_services()

    async def register_service(self, name, address, port, tags=None, check=None, service_id=None):
        return super().register_service(name, address, port, tags, check, service_id)

    async def get_kv_tree(self, prefix: str):
        return super().get_kv_tree(prefix)

    async def deregister_service(self, service_id):
        return super().deregister_service(service_id)

class BaseConsulClient(ABC, Generic[T]):
    """Base class for Consul clients defining common interface and shared logic.

    This provides the shared structure for both synchronous and asynchronous implementations.
    """

    def __init__(
            self,
            host: str,
            port: int,
            timeout: int = 3,
            max_retries: int = 3,
            retry_delay: float = 0.5
    ) -> None:
        """Initialize a Consul client.

        Args:
            host: Consul host address
            port: Consul port
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
        """
        self._consul: Union[AsyncConsul, SyncConsul] = None
        self.host = host
        self.port = port
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._running: bool = False

    @abstractmethod
    def start(self) -> None:
        """Initialize the Consul client connection."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the client session."""
        pass

    @abstractmethod
    def _retry_operation(self, operation: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Retry an operation with exponential backoff."""
        pass


class AsyncConsulClient(BaseConsulClient[T]):
    """Asynchronous client for Consul with read-only operations (except service registration).

    This client provides methods for service discovery and key-value operations.
    It uses consul.aio.Consul as the underlying client.
    """

    def start(self) -> None:
        """Initialize the Consul client connection."""
        self._consul = AsyncConsul(
            host=self.host,
            port=self.port,
        )
        self._running = True

    async def close(self) -> None:
        """Close the client session."""
        if self._consul is not None:
            self._running = False
            try:
                await self._consul.close()
            except Exception:
                pass
        self._consul = None

    async def _retry_operation(self, operation: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Retry an operation with exponential backoff.

        Args:
            operation: Async operation to retry
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            Result of the operation

        Raises:
            Exception: If all retries fail
        """
        if not self._running:
            self.start()
        last_error = None
        retry_delay = self._retry_delay

        for attempt in range(self._max_retries):
            try:
                return await operation(*args, **kwargs)
            except RuntimeError:
                self.start()
            except Exception as e:
                last_error = e
                # Only sleep if this is not the last attempt
                if attempt < self._max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Proper exponential backoff

        raise last_error if last_error else RuntimeError("Operation failed after retries")

    async def get_service(
            self,
            service_name: str,
            index: Optional[int] = None,
            tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all instances of a service.

        Args:
            service_name: Name of the service to discover
            index: Blocking query index
            tag: Filter by tag

        Returns:
            Service instance data
        """

        async def _get_service() -> Dict[str, Any]:
            _, service = await self._consul.health.service(
                service=service_name,
                index=index,
                tag=tag,
            )

            if service:
                return service[0]['Service']

            return {}

        return await self._retry_operation(_get_service)

    async def get_services(self) -> Dict[str, List[str]]:
        """Get all registered services.

        Returns:
            Dictionary mapping service names to their tags
        """

        async def _get_services() -> Dict[str, List[str]]:
            _, services = await self._consul.catalog.services()
            return services

        return await self._retry_operation(_get_services)

    # KV Store Methods
    async def get_kv(
            self,
            key: str,
            index: Optional[int] = None,
            recurse: bool = False,
    ) -> Dict[str, Any]:
        """Get a value from the KV store.

        Args:
            key: Key to retrieve
            index: Blocking query index
            recurse: If True, return all keys with the given prefix

        Returns:
            Value as string or None if key doesn't exist
        """

        async def _get_kv() -> Dict[str, Any]:
            _, data = await self._consul.kv.get(key, index=index, recurse=recurse)
            if data is None:
                return {}
            if recurse:
                return data  # Return raw data for recursive queries
            return json.loads(data.get("Value", b"").decode("utf-8")) if data.get("Value") else None

        return await self._retry_operation(_get_kv)

    async def get_kv_tree(self, prefix: str) -> Dict[str, str]:
        """Get all keys and values under a prefix.

        Args:
            prefix: Key prefix to retrieve

        Returns:
            Dictionary mapping keys to values
        """

        async def _get_kv_tree() -> Dict[str, str]:
            _, data = await self._consul.kv.get(prefix, recurse=True)
            if not data:
                return {}

            result = {}
            for item in data:
                key = item["Key"]
                value = item.get("Value", b"").decode("utf-8") if item.get("Value") else ""
                result[key] = value

            return result

        return await self._retry_operation(_get_kv_tree)

    async def register_service(
            self,
            name: str,
            address: str,
            port: int,
            tags: Optional[List[str]] = None,
            check: Optional[Dict[str, Any]] = None,
            service_id: Optional[str] = None,
    ) -> bool:
        """Register a service with Consul.

        Args:
            name: Service name
            address: Service address
            port: Service port
            tags: List of tags for the service
            check: Health check definition (dict with at least "http" or "tcp" key)
            service_id: Unique ID for the service (defaults to name)

        Returns:
            True if successful, False otherwise
        """
        service_id = service_id or f"{name}-{address}-{port}"

        async def _register_service() -> bool:
            result = await self._consul.agent.service.register(
                name=name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=check,
            )
            return result

        try:
            return await self._retry_operation(_register_service)
        except Exception:
            return False


class ConsulClient(BaseConsulClient[T]):
    """Synchronous client for Consul with read-only operations (except service registration).

    This client provides methods for service discovery and key-value operations.
    It uses consul.Consul as the underlying client.
    """

    def start(self) -> None:
        """Initialize the Consul client connection."""
        self._consul = SyncConsul(
            host=self.host,
            port=self.port,
        )
        self._running = True

    def close(self) -> None:
        """Close the client session."""
        if self._consul is not None:
            self._running = False
        self._consul = None

    def _retry_operation(self, operation: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Retry an operation with exponential backoff.

        Args:
            operation: Sync operation to retry
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            Result of the operation

        Raises:
            Exception: If all retries fail
        """
        if not self._running:
            self.start()
        last_error = None
        retry_delay = self._retry_delay

        for attempt in range(self._max_retries):
            try:
                return operation(*args, **kwargs)
            except RuntimeError:
                self.start()
            except Exception as e:
                last_error = e
                # Only sleep if this is not the last attempt
                if attempt < self._max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Proper exponential backoff

        raise last_error if last_error else RuntimeError("Operation failed after retries")

    def get_service(
            self,
            service_name: str,
            index: Optional[int] = None,
            tag: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get all instances of a service.

        Args:
            service_name: Name of the service to discover
            index: Blocking query index
            tag: Filter by tag

        Returns:
            Service instance data
        """

        def _get_service() -> Dict[str, Any]:
            _, service = self._consul.health.service(
                service=service_name,
                index=index,
                tag=tag,
            )

            if service:
                return service[0]['Service']

            return {}

        return self._retry_operation(_get_service)

    def get_services(self) -> Dict[str, List[str]]:
        """Get all registered services.

        Returns:
            Dictionary mapping service names to their tags
        """

        def _get_services() -> Dict[str, List[str]]:
            _, services = self._consul.catalog.services()
            return services

        return self._retry_operation(_get_services)

    def get_kv(
            self,
            key: str,
            index: Optional[int] = None,
            recurse: bool = False,
    ) -> Dict[str, Any]:
        """Get a value from the KV store.

        Args:
            key: Key to retrieve
            index: Blocking query index
            recurse: If True, return all keys with the given prefix

        Returns:
            Value as string or None if key doesn't exist
        """

        def _get_kv() -> Dict[str, Any]:
            _, data = self._consul.kv.get(key, index=index, recurse=recurse)
            if data is None:
                return {}
            if recurse:
                return data  # Return raw data for recursive queries
            return json.loads(data.get("Value", b"").decode("utf-8")) if data.get("Value") else None

        return self._retry_operation(_get_kv)

    def get_kv_tree(self, prefix: str) -> Dict[str, str]:
        """Get all keys and values under a prefix.

        Args:
            prefix: Key prefix to retrieve

        Returns:
            Dictionary mapping keys to values
        """

        def _get_kv_tree() -> Dict[str, str]:
            _, data = self._consul.kv.get(prefix, recurse=True)
            if not data:
                return {}

            result = {}
            for item in data:
                key = item["Key"]
                value = json.loads(item.get("Value", b"").decode("utf-8")) if item.get("Value") else ""
                result[key] = value

            return result

        return self._retry_operation(_get_kv_tree)

    def register_service(
            self,
            name: str,
            address: str,
            port: int,
            tags: Optional[List[str]] = None,
            check: Optional[Dict[str, Any]] = None,
            service_id: Optional[str] = None,
    ) -> bool:
        """Register a service with Consul.

        Args:
            name: Service name
            address: Service address
            port: Service port
            tags: List of tags for the service
            check: Health check definition (dict with at least "http" or "tcp" key)
            service_id: Unique ID for the service (defaults to name)

        Returns:
            True if successful, False otherwise
        """
        service_id = service_id or f"{name}-{address}-{port}"

        def _register_service() -> bool:
            result = self._consul.agent.service.register(
                name=name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=check,
            )
            return result

        try:
            return self._retry_operation(_register_service)
        except Exception:
            return False

    def deregister_service(self, service_id):
        self._consul.agent.service.deregister(service_id=service_id)