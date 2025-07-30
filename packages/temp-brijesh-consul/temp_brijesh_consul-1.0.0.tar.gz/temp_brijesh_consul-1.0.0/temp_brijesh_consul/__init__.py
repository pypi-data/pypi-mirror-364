"""Brijesh Consul Client Package

A Python client library for HashiCorp Consul with both synchronous and asynchronous support.
Provides service discovery, key-value store operations, and service registration capabilities.
"""

from .consul import (
    AsyncConsulClient,
    ConsulClient,
    DefaultConsulClient,
    AsyncDefaultConsulClient,
    BaseConsulClient
)

__version__ = "1.0.0"
__author__ = "Brijesh Turabit"
__email__ = "brijesh.turabit@gmail.com"

__all__ = [
    "AsyncConsulClient",
    "ConsulClient", 
    "DefaultConsulClient",
    "AsyncDefaultConsulClient",
    "BaseConsulClient"
]
