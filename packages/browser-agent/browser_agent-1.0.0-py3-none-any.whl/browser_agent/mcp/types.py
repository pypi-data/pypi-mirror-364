"""MCP (Model Context Protocol) type definitions"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json


class MCPMessageType(Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"


class MCPMethod(Enum):
    """MCP protocol methods"""
    INITIALIZE = "initialize"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"
    LIST_PROMPTS = "prompts/list"
    GET_PROMPT = "prompts/get"
    COMPLETE = "completion/complete"
    PING = "ping"


@dataclass
class MCPMessage:
    """Base MCP message"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            data["id"] = self.id
        if self.method is not None:
            data["method"] = self.method
        if self.params is not None:
            data["params"] = self.params
        if self.result is not None:
            data["result"] = self.result
        if self.error is not None:
            data["error"] = self.error
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPMessage':
        """Create from dictionary"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method"),
            params=data.get("params"),
            result=data.get("result"),
            error=data.get("error")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MCPMessage':
        """Create from JSON string"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class MCPToolParameter:
    """MCP tool parameter definition"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None
    enum: Optional[List[str]] = None


@dataclass
class MCPTool:
    """MCP tool definition"""
    name: str
    description: str
    parameters: List[MCPToolParameter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {
                    param.name: {
                        "type": param.type,
                        "description": param.description,
                        **({
                            "enum": param.enum
                        } if param.enum else {}),
                        **({
                            "default": param.default
                        } if param.default is not None else {})
                    }
                    for param in self.parameters
                },
                "required": [param.name for param in self.parameters if param.required]
            }
        }


@dataclass
class MCPResource:
    """MCP resource definition"""
    uri: str
    name: str
    description: str
    mimeType: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "uri": self.uri,
            "name": self.name,
            "description": self.description
        }
        if self.mimeType:
            data["mimeType"] = self.mimeType
        return data


@dataclass
class MCPPrompt:
    """MCP prompt definition"""
    name: str
    description: str
    arguments: List[MCPToolParameter] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "arguments": [
                {
                    "name": arg.name,
                    "description": arg.description,
                    "required": arg.required
                }
                for arg in self.arguments
            ]
        }


@dataclass
class MCPServerCapabilities:
    """MCP server capabilities"""
    tools: bool = False
    resources: bool = False
    prompts: bool = False
    completion: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        capabilities = {}
        if self.tools:
            capabilities["tools"] = {}
        if self.resources:
            capabilities["resources"] = {}
        if self.prompts:
            capabilities["prompts"] = {}
        if self.completion:
            capabilities["completion"] = {}
        return capabilities


@dataclass
class MCPServerInfo:
    """MCP server information"""
    name: str
    version: str
    capabilities: MCPServerCapabilities
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "version": self.version,
            "capabilities": self.capabilities.to_dict()
        }


@dataclass
class MCPServer:
    """MCP server configuration"""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    description: str = ""
    category: str = "general"
    author: str = ""
    version: str = "1.0.0"
    homepage: str = ""
    repository: str = ""
    license: str = ""
    tags: List[str] = field(default_factory=list)
    installed: bool = False
    enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "description": self.description,
            "category": self.category,
            "author": self.author,
            "version": self.version,
            "homepage": self.homepage,
            "repository": self.repository,
            "license": self.license,
            "tags": self.tags,
            "installed": self.installed,
            "enabled": self.enabled
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPServer':
        """Create from dictionary"""
        return cls(
            name=data["name"],
            command=data["command"],
            args=data.get("args", []),
            env=data.get("env", {}),
            description=data.get("description", ""),
            category=data.get("category", "general"),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            homepage=data.get("homepage", ""),
            repository=data.get("repository", ""),
            license=data.get("license", ""),
            tags=data.get("tags", []),
            installed=data.get("installed", False),
            enabled=data.get("enabled", False)
        )


@dataclass
class MCPToolCall:
    """MCP tool call request"""
    name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "arguments": self.arguments
        }


@dataclass
class MCPToolResult:
    """MCP tool call result"""
    content: List[Dict[str, Any]] = field(default_factory=list)
    isError: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "isError": self.isError
        }