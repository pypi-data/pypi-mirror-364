"""MCP Marketplace for discovering and managing MCP servers"""

import asyncio
import json
import logging
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import asdict

from .types import MCPServer
from .server_manager import MCPServerManager

logger = logging.getLogger(__name__)


class MCPMarketplace:
    """MCP Marketplace for discovering and installing MCP servers"""
    
    def __init__(self, server_manager: MCPServerManager):
        self.server_manager = server_manager
        self.cache_dir = server_manager.config_dir / "marketplace_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Marketplace sources
        self.sources = [
            {
                "name": "Official MCP Registry",
                "url": "https://raw.githubusercontent.com/modelcontextprotocol/servers/main/registry.json",
                "type": "registry"
            },
            {
                "name": "Community Servers",
                "url": "https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/servers.json",
                "type": "community"
            }
        ]
        
        self.available_servers: Dict[str, MCPServer] = {}
        self.categories: Dict[str, List[str]] = {}
        self.featured_servers: List[str] = []
        
        # Load cached data
        self._load_cache()
    
    def _load_cache(self):
        """Load cached marketplace data"""
        cache_file = self.cache_dir / "marketplace.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Load available servers
                for server_data in cache_data.get("servers", []):
                    server = MCPServer.from_dict(server_data)
                    self.available_servers[server.name] = server
                
                # Load categories
                self.categories = cache_data.get("categories", {})
                
                # Load featured servers
                self.featured_servers = cache_data.get("featured", [])
                
                logger.info(f"Loaded {len(self.available_servers)} servers from marketplace cache")
                
            except Exception as e:
                logger.error(f"Failed to load marketplace cache: {e}")
    
    def _save_cache(self):
        """Save marketplace data to cache"""
        cache_file = self.cache_dir / "marketplace.json"
        
        try:
            cache_data = {
                "servers": [server.to_dict() for server in self.available_servers.values()],
                "categories": self.categories,
                "featured": self.featured_servers
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save marketplace cache: {e}")
    
    async def refresh_marketplace(self) -> bool:
        """Refresh marketplace data from sources"""
        try:
            new_servers = {}
            new_categories = {}
            
            for source in self.sources:
                try:
                    servers = await self._fetch_from_source(source)
                    for server in servers:
                        new_servers[server.name] = server
                        
                        # Update categories
                        category = server.category
                        if category not in new_categories:
                            new_categories[category] = []
                        if server.name not in new_categories[category]:
                            new_categories[category].append(server.name)
                            
                except Exception as e:
                    logger.error(f"Failed to fetch from source {source['name']}: {e}")
            
            if new_servers:
                self.available_servers = new_servers
                self.categories = new_categories
                self._update_featured_servers()
                self._save_cache()
                
                logger.info(f"Refreshed marketplace with {len(new_servers)} servers")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to refresh marketplace: {e}")
            return False
    
    async def _fetch_from_source(self, source: Dict[str, str]) -> List[MCPServer]:
        """Fetch servers from a marketplace source"""
        servers = []
        
        try:
            # Fetch data from URL
            response = requests.get(source["url"], timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if source["type"] == "registry":
                servers = self._parse_registry_format(data)
            elif source["type"] == "community":
                servers = self._parse_community_format(data)
            
        except Exception as e:
            logger.error(f"Error fetching from {source['url']}: {e}")
        
        return servers
    
    def _parse_registry_format(self, data: Dict[str, Any]) -> List[MCPServer]:
        """Parse official registry format"""
        servers = []
        
        for server_data in data.get("servers", []):
            try:
                server = MCPServer(
                    name=server_data["name"],
                    command=server_data["command"],
                    args=server_data.get("args", []),
                    env=server_data.get("env", {}),
                    description=server_data.get("description", ""),
                    category=server_data.get("category", "general"),
                    author=server_data.get("author", ""),
                    version=server_data.get("version", "1.0.0"),
                    homepage=server_data.get("homepage", ""),
                    repository=server_data.get("repository", ""),
                    license=server_data.get("license", ""),
                    tags=server_data.get("tags", [])
                )
                servers.append(server)
                
            except Exception as e:
                logger.error(f"Error parsing server data: {e}")
        
        return servers
    
    def _parse_community_format(self, data: Dict[str, Any]) -> List[MCPServer]:
        """Parse community format"""
        servers = []
        
        # Handle different community formats
        if "servers" in data:
            server_list = data["servers"]
        elif isinstance(data, list):
            server_list = data
        else:
            return servers
        
        for server_data in server_list:
            try:
                # Extract command and args from different formats
                command = server_data.get("command", "")
                args = server_data.get("args", [])
                
                # Handle npm package format
                if "package" in server_data:
                    command = "npx"
                    args = ["-y", server_data["package"]]
                    if "args" in server_data:
                        args.extend(server_data["args"])
                
                server = MCPServer(
                    name=server_data["name"],
                    command=command,
                    args=args,
                    env=server_data.get("env", {}),
                    description=server_data.get("description", ""),
                    category=server_data.get("category", "community"),
                    author=server_data.get("author", ""),
                    version=server_data.get("version", "1.0.0"),
                    homepage=server_data.get("homepage", ""),
                    repository=server_data.get("repository", ""),
                    license=server_data.get("license", ""),
                    tags=server_data.get("tags", [])
                )
                servers.append(server)
                
            except Exception as e:
                logger.error(f"Error parsing community server data: {e}")
        
        return servers
    
    def _update_featured_servers(self):
        """Update featured servers list"""
        # Featured servers based on popularity and usefulness
        featured_names = [
            "filesystem", "brave-search", "github", "memory", 
            "fetch", "puppeteer", "sqlite", "postgres"
        ]
        
        self.featured_servers = [
            name for name in featured_names 
            if name in self.available_servers
        ]
    
    def get_available_servers(self) -> List[MCPServer]:
        """Get all available servers"""
        return list(self.available_servers.values())
    
    def get_server(self, name: str) -> Optional[MCPServer]:
        """Get server by name"""
        return self.available_servers.get(name)
    
    def get_featured_servers(self) -> List[MCPServer]:
        """Get featured servers"""
        return [
            self.available_servers[name] 
            for name in self.featured_servers 
            if name in self.available_servers
        ]
    
    def get_servers_by_category(self, category: str) -> List[MCPServer]:
        """Get servers by category"""
        server_names = self.categories.get(category, [])
        return [
            self.available_servers[name] 
            for name in server_names 
            if name in self.available_servers
        ]
    
    def get_categories(self) -> List[str]:
        """Get all categories"""
        return list(self.categories.keys())
    
    def search_servers(self, query: str) -> List[MCPServer]:
        """Search servers by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for server in self.available_servers.values():
            if (query_lower in server.name.lower() or 
                query_lower in server.description.lower() or 
                any(query_lower in tag.lower() for tag in server.tags)):
                results.append(server)
        
        return results
    
    def install_server(self, name: str) -> bool:
        """Install a server from marketplace"""
        if name not in self.available_servers:
            logger.error(f"Server {name} not found in marketplace")
            return False
        
        server = self.available_servers[name].copy()
        server.installed = True
        
        return self.server_manager.add_server(server)
    
    def uninstall_server(self, name: str) -> bool:
        """Uninstall a server"""
        return self.server_manager.remove_server(name)
    
    def is_server_installed(self, name: str) -> bool:
        """Check if server is installed"""
        installed_server = self.server_manager.get_server(name)
        return installed_server is not None
    
    def is_server_enabled(self, name: str) -> bool:
        """Check if server is enabled"""
        installed_server = self.server_manager.get_server(name)
        return installed_server is not None and installed_server.enabled
    
    def get_installed_servers(self) -> List[MCPServer]:
        """Get all installed servers"""
        return self.server_manager.get_all_servers()
    
    def get_server_status(self, name: str) -> Dict[str, Any]:
        """Get comprehensive server status"""
        marketplace_server = self.available_servers.get(name)
        installed_server = self.server_manager.get_server(name)
        
        status = {
            "available": marketplace_server is not None,
            "installed": installed_server is not None,
            "enabled": False,
            "connected": False,
            "version": None,
            "description": ""
        }
        
        if marketplace_server:
            status["description"] = marketplace_server.description
            status["version"] = marketplace_server.version
        
        if installed_server:
            status["enabled"] = installed_server.enabled
            status["connected"] = self.server_manager.is_server_connected(name)
            if not status["version"]:
                status["version"] = installed_server.version
        
        return status
    
    async def enable_server(self, name: str) -> bool:
        """Enable and connect to a server"""
        if not self.is_server_installed(name):
            logger.error(f"Server {name} not installed")
            return False
        
        server = self.server_manager.get_server(name)
        if server:
            server.enabled = True
            self.server_manager.update_server(server)
            return await self.server_manager.connect_server(name)
        
        return False
    
    async def disable_server(self, name: str) -> bool:
        """Disable and disconnect from a server"""
        if not self.is_server_installed(name):
            return False
        
        server = self.server_manager.get_server(name)
        if server:
            server.enabled = False
            self.server_manager.update_server(server)
            return await self.server_manager.disconnect_server(name)
        
        return False
    
    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        total_available = len(self.available_servers)
        total_installed = len(self.get_installed_servers())
        total_enabled = len([s for s in self.get_installed_servers() if s.enabled])
        total_connected = len(self.server_manager.get_connected_servers())
        
        categories_count = {cat: len(servers) for cat, servers in self.categories.items()}
        
        return {
            "total_available": total_available,
            "total_installed": total_installed,
            "total_enabled": total_enabled,
            "total_connected": total_connected,
            "categories": categories_count,
            "featured_count": len(self.featured_servers)
        }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current server configuration"""
        return {
            "servers": [server.to_dict() for server in self.get_installed_servers()],
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def import_configuration(self, config: Dict[str, Any]) -> bool:
        """Import server configuration"""
        try:
            for server_data in config.get("servers", []):
                server = MCPServer.from_dict(server_data)
                self.server_manager.add_server(server)
            
            logger.info(f"Imported {len(config.get('servers', []))} server configurations")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import configuration: {e}")
            return False