#!/usr/bin/env python3
"""
MCP Installation Helper for Claude Desktop
Automatically configures Claude Desktop to use claude-code-indexer
"""

import json
import os
import platform
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

console = Console()


class MCPInstaller:
    """Handle MCP installation for Claude Desktop"""
    
    def __init__(self):
        self.platform = platform.system()
        self.config_path = self._get_config_path()
        
    def _get_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path based on platform"""
        if self.platform == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
        elif self.platform == "Windows":
            return Path.home() / "AppData/Roaming/Claude/claude_desktop_config.json"
        elif self.platform == "Linux":
            return Path.home() / ".config/Claude/claude_desktop_config.json"
        else:
            return None
    
    def check_claude_desktop(self) -> bool:
        """Check if Claude Desktop is installed"""
        if not self.config_path:
            return False
            
        # Check if Claude Desktop directory exists
        claude_dir = self.config_path.parent
        return claude_dir.exists()
    
    def load_config(self) -> Dict[str, Any]:
        """Load existing Claude Desktop config"""
        if not self.config_path or not self.config_path.exists():
            return {"mcpServers": {}}
            
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"mcpServers": {}}
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save Claude Desktop config"""
        if not self.config_path:
            return False
            
        # Create directory if needed
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing config
        if self.config_path.exists():
            backup_path = self.config_path.with_suffix('.json.backup')
            shutil.copy2(self.config_path, backup_path)
            console.print(f"💾 Backed up existing config to: {backup_path}")
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            console.print(f"[red]❌ Failed to save config: {e}[/red]")
            return False
    
    def install(self, force: bool = False) -> bool:
        """Install MCP server configuration"""
        # Check platform support
        if not self.config_path:
            console.print(f"[red]❌ Platform '{self.platform}' is not supported[/red]")
            return False
        
        # Check Claude Desktop
        if not self.check_claude_desktop():
            console.print("[yellow]⚠️  Claude Desktop not found at expected location[/yellow]")
            console.print(f"Expected location: {self.config_path.parent}")
            if not force and not Confirm.ask("Continue anyway?"):
                return False
        
        # Load existing config
        config = self.load_config()
        
        # Check if already installed
        if "claude-code-indexer" in config.get("mcpServers", {}):
            console.print("[yellow]⚠️  claude-code-indexer MCP server already configured[/yellow]")
            if not force and not Confirm.ask("Update existing configuration?"):
                return False
        
        # Add our MCP server
        if "mcpServers" not in config:
            config["mcpServers"] = {}
            
        config["mcpServers"]["claude-code-indexer"] = {
            "command": "cci-mcp-server",
            "args": [],
            "env": {},
            "autoStart": True,
            "capabilities": {
                "tools": True,
                "resources": True
            }
        }
        
        # Save config
        if self.save_config(config):
            console.print("[green]✅ MCP server configured successfully![/green]")
            console.print(f"📁 Config location: {self.config_path}")
            return True
        else:
            return False
    
    def uninstall(self) -> bool:
        """Remove MCP server configuration"""
        if not self.config_path or not self.config_path.exists():
            console.print("[yellow]No configuration found[/yellow]")
            return True
            
        config = self.load_config()
        
        if "claude-code-indexer" not in config.get("mcpServers", {}):
            console.print("[yellow]claude-code-indexer not found in config[/yellow]")
            return True
        
        # Remove our server
        del config["mcpServers"]["claude-code-indexer"]
        
        # Save config
        if self.save_config(config):
            console.print("[green]✅ MCP server removed successfully[/green]")
            return True
        else:
            return False
    
    def status(self) -> None:
        """Show MCP installation status"""
        table = Table(title="MCP Installation Status")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details")
        
        # Platform check
        platform_supported = self.config_path is not None
        table.add_row(
            "Platform",
            "✅ Supported" if platform_supported else "❌ Not Supported",
            self.platform
        )
        
        # Claude Desktop check
        claude_installed = self.check_claude_desktop()
        table.add_row(
            "Claude Desktop",
            "✅ Found" if claude_installed else "❌ Not Found",
            str(self.config_path.parent) if self.config_path else "N/A"
        )
        
        # Config check
        config_exists = self.config_path and self.config_path.exists()
        table.add_row(
            "Config File",
            "✅ Exists" if config_exists else "❌ Not Found",
            str(self.config_path) if self.config_path else "N/A"
        )
        
        # MCP server check
        if config_exists:
            config = self.load_config()
            mcp_configured = "claude-code-indexer" in config.get("mcpServers", {})
            table.add_row(
                "MCP Server",
                "✅ Configured" if mcp_configured else "❌ Not Configured",
                "cci-mcp-server" if mcp_configured else "Not installed"
            )
        else:
            table.add_row("MCP Server", "❌ Not Configured", "Config not found")
        
        console.print(table)
        
        # Show instructions if not fully configured
        if not platform_supported:
            console.print("\n[yellow]Your platform is not supported for automatic installation.[/yellow]")
            console.print("Please manually configure Claude Desktop.")
        elif not claude_installed:
            console.print("\n[yellow]Claude Desktop not found. Please install it first:[/yellow]")
            console.print("https://claude.ai/desktop")
        elif not config_exists or not mcp_configured:
            console.print("\n[cyan]To install MCP server:[/cyan]")
            console.print("claude-code-indexer mcp install")


def install_mcp(force: bool = False) -> None:
    """Install MCP server for Claude Desktop"""
    installer = MCPInstaller()
    
    console.print("[bold cyan]🤖 Claude Code Indexer MCP Installer[/bold cyan]\n")
    
    # Check if MCP dependencies are installed
    try:
        import mcp
        console.print("✅ MCP SDK is installed")
    except ImportError:
        console.print("[red]❌ MCP SDK not installed[/red]")
        console.print("\nInstall with: pip install 'claude-code-indexer[mcp]'")
        return
    
    # Run installation
    if installer.install(force=force):
        console.print("\n[green]🎉 Installation complete![/green]")
        console.print("\nNext steps:")
        console.print("1. Restart Claude Desktop")
        console.print("2. Open a Python project")
        console.print("3. Claude will have access to code indexing tools automatically!")
    else:
        console.print("\n[red]Installation failed[/red]")


def uninstall_mcp() -> None:
    """Uninstall MCP server from Claude Desktop"""
    installer = MCPInstaller()
    
    console.print("[bold cyan]🤖 Claude Code Indexer MCP Uninstaller[/bold cyan]\n")
    
    if Confirm.ask("Remove claude-code-indexer from Claude Desktop?"):
        if installer.uninstall():
            console.print("\n[green]Successfully removed![/green]")
        else:
            console.print("\n[red]Uninstall failed[/red]")


def show_mcp_status() -> None:
    """Show MCP installation status"""
    installer = MCPInstaller()
    installer.status()


if __name__ == "__main__":
    # Test the installer
    show_mcp_status()