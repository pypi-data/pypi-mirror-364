#!/usr/bin/env python3
"""
Comprehensive tests for CLI module
Goal: Increase coverage from 20% to 80%+
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from click.testing import CliRunner
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock ensmallen before importing to avoid logger conflicts
sys.modules['ensmallen'] = MagicMock()

from claude_code_indexer.cli import cli, show_app_header, console
from claude_code_indexer import __version__, __app_name__
from claude_code_indexer.security import SecurityError


class TestCLI:
    """Test suite for CLI commands"""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner"""
        return CliRunner()
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_indexer(self):
        """Mock CodeGraphIndexer"""
        with patch('claude_code_indexer.cli.CodeGraphIndexer') as mock:
            yield mock
    
    def test_cli_version(self, runner):
        """Test version command"""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert __app_name__ in result.output
    
    def test_cli_help(self, runner):
        """Test help command"""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Claude Code Indexer' in result.output
        assert 'Index source code as graph database' in result.output
    
    def test_show_app_header(self):
        """Test app header display"""
        with patch.object(console, 'print') as mock_print:
            show_app_header()
            
            # Verify header was printed
            calls = mock_print.call_args_list
            assert len(calls) >= 2
            assert __app_name__ in str(calls[0])
            assert __version__ in str(calls[0])
    
    def test_init_command_new_project(self, runner, temp_dir):
        """Test init command in new project"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create template file
            template_dir = Path(__file__).parent.parent / "claude_code_indexer" / "templates"
            template_dir.mkdir(exist_ok=True)
            template_file = template_dir / "claude_md_template.md"
            template_file.write_text("## Code Indexing with Graph Database\nTemplate content")
            
            # Provide 'y' input for confirmation
            result = runner.invoke(cli, ['init'], input='y\n')
            
            assert result.exit_code == 0
            assert "Initializing project" in result.output
            assert Path("CLAUDE.md").exists()
            
            # Check CLAUDE.md content
            with open("CLAUDE.md") as f:
                content = f.read()
                assert "Code Indexing with Graph Database" in content
    
    def test_init_command_existing_file(self, runner, temp_dir):
        """Test init command with existing CLAUDE.md"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create existing CLAUDE.md
            existing_content = "# Existing Content\n\n## Code Indexing with Graph Database\nExisting section"
            Path("CLAUDE.md").write_text(existing_content)
            
            # Create template
            template_dir = Path(__file__).parent.parent / "claude_code_indexer" / "templates"
            template_dir.mkdir(exist_ok=True)
            template_file = template_dir / "claude_md_template.md"
            template_file.write_text("## Code Indexing with Graph Database\nNew template")
            
            result = runner.invoke(cli, ['init'])
            
            assert result.exit_code == 0
            assert "Code indexing section already exists" in result.output
    
    def test_init_command_force(self, runner, temp_dir):
        """Test init command with --force flag"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create existing CLAUDE.md
            existing_content = "# Existing\n\n## Code Indexing with Graph Database\nOld\n\n## Other Section\nKeep this"
            Path("CLAUDE.md").write_text(existing_content)
            
            # Create template
            template_dir = Path(__file__).parent.parent / "claude_code_indexer" / "templates"
            template_dir.mkdir(exist_ok=True)
            template_file = template_dir / "claude_md_template.md"
            template_file.write_text("## Code Indexing with Graph Database\nNew template")
            
            result = runner.invoke(cli, ['init', '--force'])
            
            assert result.exit_code == 0
            assert "Updating existing section" in result.output
            
            # Check content was updated
            with open("CLAUDE.md") as f:
                content = f.read()
                assert "New template" in content
                assert "Keep this" in content
    
    def test_index_command_basic(self, runner, temp_dir, mock_indexer):
        """Test basic index command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Create test files
            Path("test.py").write_text("def hello(): pass")
            
            # Mock indexer behavior
            mock_instance = Mock()
            mock_indexer.return_value = mock_instance
            mock_instance.index_directory.return_value = True
            mock_instance.parsing_errors = []  # Make it a list
            
            result = runner.invoke(cli, ['index', '.'])
            
            assert result.exit_code == 0
            mock_instance.index_directory.assert_called_once()
    
    def test_index_command_with_options(self, runner, temp_dir, mock_indexer):
        """Test index command with various options"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            Path("test.py").write_text("def hello(): pass")
            
            mock_instance = Mock()
            mock_indexer.return_value = mock_instance
            mock_instance.index_directory.return_value = True
            mock_instance.parsing_errors = []  # Make it a list
            
            result = runner.invoke(cli, ['index', '.', '--verbose', '--no-cache', '--workers', '2'])
            
            if result.exit_code != 0:
                print(f"CLI output: {result.output}")
                print(f"CLI exception: {result.exception}")
            assert result.exit_code == 0
            # Check that indexer was called with correct parameters
            call_args = mock_indexer.call_args
            assert call_args is not None
            assert call_args.kwargs['use_cache'] == False
            assert call_args.kwargs['parallel_workers'] == 2
    
    def test_query_command(self, runner, temp_dir, mock_indexer):
        """Test query command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Mock storage manager and indexer behavior
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_storage.return_value.get_project_from_cwd.return_value = Path('.')
                mock_storage.return_value.get_project_from_path.return_value = Path('.')
                
                # Mock the indexer instance
                mock_instance = Mock()
                mock_indexer.return_value = mock_instance
                mock_instance.db_path = Path('test.db')
                
                # Mock query_important_nodes method  
                mock_instance.query_important_nodes.return_value = [
                    {
                        'name': 'test_func',
                        'node_type': 'function',
                        'path': 'test.py',
                        'importance_score': 0.8,
                        'relevance_tags': []
                    }
                ]
                
                # Create empty db file so existence check passes
                Path('test.db').touch()
                
                result = runner.invoke(cli, ['query'])
                
                assert result.exit_code == 0
                assert 'test_func' in result.output
    
    def test_query_important_command(self, runner, temp_dir, mock_indexer):
        """Test query --important command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_storage.return_value.get_project_from_cwd.return_value = Path('.')
                
                # Mock the indexer instance
                mock_instance = Mock()
                mock_indexer.return_value = mock_instance
                mock_instance.db_path = Path('test.db')
                
                # Mock query_important_nodes method
                mock_instance.query_important_nodes.return_value = [
                    {
                        'name': 'important_func',
                        'node_type': 'function',
                        'path': 'test.py',
                        'importance_score': 0.9,
                        'relevance_tags': '["highly-used"]',
                        'summary': 'Important function'
                    }
                ]
                
                # Create empty db file so existence check passes
                Path('test.db').touch()
                
                result = runner.invoke(cli, ['query', '--important'])
                
                assert result.exit_code == 0
                assert 'important_func' in result.output
    
    def test_search_command(self, runner, temp_dir, mock_indexer):
        """Test search command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_storage.return_value.get_project_from_cwd.return_value = Path('.')
                
                # Mock the indexer instance
                mock_instance = Mock()
                mock_indexer.return_value = mock_instance
                mock_instance.db_path = Path('test.db')
                
                # Create actual database for search functionality
                import sqlite3
                conn = sqlite3.connect('test.db')
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE code_nodes (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    node_type TEXT,
                    path TEXT,
                    summary TEXT,
                    importance_score REAL,
                    relevance_tags TEXT
                )''')
                cursor.execute("INSERT INTO code_nodes VALUES (1, 'search_test', 'function', 'test.py', 'Function for testing search', 0.5, '[]')")
                conn.commit()
                conn.close()
                
                result = runner.invoke(cli, ['search', 'test'])
                
                assert result.exit_code == 0
                assert 'search_test' in result.output
    
    def test_stats_command(self, runner, temp_dir, mock_indexer):
        """Test stats command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_storage.return_value.get_project_from_cwd.return_value = Path('.')
                
                # Mock the indexer instance
                mock_instance = Mock()
                mock_indexer.return_value = mock_instance
                mock_instance.db_path = Path('test.db')
                
                # Mock get_stats to return proper dict with string values
                mock_instance.get_stats.return_value = {
                    'total_nodes': '2',
                    'total_edges': '1',
                    'last_indexed': '2024-01-01',
                    'node_types': {'function': 1, 'class': 1},
                    'relationship_types': {'calls': 1}
                }
                
                # Create actual database for stats functionality
                import sqlite3
                conn = sqlite3.connect('test.db')
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE code_nodes (
                    id INTEGER PRIMARY KEY,
                    node_type TEXT,
                    language TEXT
                )''')
                cursor.execute('''CREATE TABLE relationships (
                    source_id INTEGER,
                    target_id INTEGER,
                    relationship_type TEXT
                )''')
                cursor.execute('''CREATE TABLE indexing_metadata (
                    project_path TEXT PRIMARY KEY,
                    last_indexed TIMESTAMP,
                    indexing_time REAL,
                    total_files INTEGER
                )''')
                cursor.execute("INSERT INTO code_nodes VALUES (1, 'function', 'python')")
                cursor.execute("INSERT INTO code_nodes VALUES (2, 'class', 'python')")
                cursor.execute("INSERT INTO relationships VALUES (1, 2, 'calls')")
                cursor.execute("INSERT INTO indexing_metadata VALUES ('.', '2024-01-01', 1.5, 10)")
                conn.commit()
                conn.close()
                
                result = runner.invoke(cli, ['stats'])
                
                assert result.exit_code == 0
                # Check that stats were displayed
                assert 'nodes' in result.output.lower() or 'statistics' in result.output.lower()
    
    def test_enhance_command(self, runner, temp_dir, mock_indexer):
        """Test enhance command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_storage.return_value.get_project_from_cwd.return_value = Path('.')
                
                mock_instance = Mock()
                mock_indexer.return_value = mock_instance
                mock_instance.enhance_metadata.return_value = {'enhanced': 10, 'total': 20}
                
                result = runner.invoke(cli, ['enhance', '.', '--limit', '10'])
                
                assert result.exit_code == 0
                mock_instance.enhance_metadata.assert_called_once()
    
    def test_projects_command(self, runner):
        """Test projects command"""
        with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
            # Mock the storage methods
            mock_instance = mock_storage.return_value
            mock_instance.list_projects.return_value = [
                {'name': 'project1', 'path': '/project1', 'db_size': 1024000, 'last_indexed': '2024-01-01T10:00:00', 'exists': True},
                {'name': 'project2', 'path': '/project2', 'db_size': 2048000, 'last_indexed': '2024-01-02T15:30:00', 'exists': True}
            ]
            # Mock storage stats to avoid formatting issues
            mock_instance.get_storage_stats.return_value = {
                'app_home': '/home/user/.claude-code-indexer',
                'project_count': 2,
                'total_size_mb': 3.0
            }
            
            result = runner.invoke(cli, ['projects'])
            
            if result.exit_code != 0:
                print(f"Projects command output: {result.output}")
                print(f"Projects command exception: {result.exception}")
            assert result.exit_code == 0
            assert '/project1' in result.output
            assert '/project2' in result.output
    
    def test_cache_command(self, runner):
        """Test cache command"""
        result = runner.invoke(cli, ['cache'])
        assert result.exit_code == 0
        assert 'cache' in result.output.lower()
    
    def test_cache_stats_command(self, runner):
        """Test cache stats command"""
        with patch('claude_code_indexer.cache_manager.CacheManager') as mock_cache:
            mock_instance = Mock()
            mock_cache.return_value = mock_instance
            mock_instance.print_cache_stats = Mock()
            
            result = runner.invoke(cli, ['cache'])
            
            assert result.exit_code == 0
            mock_instance.print_cache_stats.assert_called_once()
    
    def test_clean_command(self, runner, temp_dir):
        """Test clean command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
                mock_instance = mock_storage.return_value
                mock_instance.clean_orphaned_projects.return_value = ['/path/to/orphaned']
                
                # User confirms deletion
                result = runner.invoke(cli, ['clean'], input='y\n')
                
                assert result.exit_code == 0
                mock_instance.clean_orphaned_projects.assert_called_once()
    
    def test_remove_command(self, runner):
        """Test remove command"""
        with patch('claude_code_indexer.storage_manager.get_storage_manager') as mock_storage:
            mock_instance = mock_storage.return_value
            mock_instance.find_project_by_name.return_value = {
                'path': '/test/project',
                'name': 'project'
            }
            mock_instance.remove_project.return_value = True
            
            result = runner.invoke(cli, ['remove', '/test/project'], input='y\n')
            
            assert result.exit_code == 0
            # The remove_project will be called with the path from find_project_by_name
            mock_instance.remove_project.assert_called_once()
    
    def test_background_command(self, runner):
        """Test background command group"""
        result = runner.invoke(cli, ['background', '--help'])
        assert result.exit_code == 0
        assert 'background' in result.output.lower()
    
    def test_background_status_command(self, runner):
        """Test background status command"""
        with patch('claude_code_indexer.background_service.get_background_service') as mock_service:
            mock_instance = Mock()
            mock_service.return_value = mock_instance
            mock_instance.get_status.return_value = {
                'enabled': True,
                'running': True,
                'projects': {
                    '/project1': {'interval': 300, 'last_indexed': '2024-01-01', 'next_index': '2024-01-02', 'indexing': False},
                    '/project2': {'interval': 600, 'last_indexed': '2024-01-02', 'next_index': '2024-01-03', 'indexing': True}
                },
                'default_interval': 3600
            }
            
            result = runner.invoke(cli, ['background', 'status'])
            
            assert result.exit_code == 0
            assert 'enabled' in result.output.lower()
    
    def test_mcp_command(self, runner):
        """Test mcp command group"""
        result = runner.invoke(cli, ['mcp', '--help'])
        assert result.exit_code == 0
        assert 'mcp' in result.output.lower()
    
    def test_mcp_install_command(self, runner):
        """Test mcp install command"""
        with patch('claude_code_indexer.mcp_installer.MCPInstaller') as mock_installer:
            mock_instance = Mock()
            mock_installer.return_value = mock_instance
            mock_instance.install.return_value = True
            
            result = runner.invoke(cli, ['mcp', 'install'])
            
            assert result.exit_code == 0
            mock_instance.install.assert_called_once()
    
    def test_llm_guide_command(self, runner):
        """Test llm-guide command"""
        result = runner.invoke(cli, ['llm-guide'])
        
        assert result.exit_code == 0
        assert 'LLM Usage Guide' in result.output or 'QUICK START' in result.output
        assert 'claude-code-indexer' in result.output
    
    def test_benchmark_command(self, runner, temp_dir):
        """Test benchmark command"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            with patch('claude_code_indexer.db_optimizer.DatabaseBenchmark') as mock_bench:
                mock_bench.benchmark_insert_performance.return_value = (1.0, 0.5)
                
                result = runner.invoke(cli, ['benchmark'])
                
                assert result.exit_code == 0
                assert 'Benchmark Results' in result.output
    
    def test_update_command(self, runner):
        """Test update command"""
        with patch('claude_code_indexer.cli.Updater') as mock_updater:
            mock_instance = Mock()
            mock_updater.return_value = mock_instance
            mock_instance.auto_update.return_value = True
            
            # Test check only
            result = runner.invoke(cli, ['update', '--check-only'])
            
            assert result.exit_code == 0
            mock_instance.auto_update.assert_called_with(check_only=True)
            
            # Reset mock
            mock_instance.reset_mock()
            
            # Test actual update
            mock_instance.auto_update.return_value = True
            result = runner.invoke(cli, ['update'])
            
            assert result.exit_code == 0
            mock_instance.auto_update.assert_called_with(check_only=False)
    
    def test_error_handling(self, runner, temp_dir):
        """Test error handling in CLI"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            # Test invalid path
            result = runner.invoke(cli, ['index', '/nonexistent/path'])
            
            assert result.exit_code != 0
            
            # Test security error
            with patch('claude_code_indexer.cli.validate_file_path') as mock_validate:
                mock_validate.side_effect = SecurityError("Invalid path")
                
                result = runner.invoke(cli, ['index', '../../../etc/passwd'])
                
                assert result.exit_code != 0
    
    def test_verbose_output(self, runner, temp_dir, mock_indexer):
        """Test verbose output flag"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            Path("test.py").write_text("def hello(): pass")
            
            mock_instance = Mock()
            mock_indexer.return_value = mock_instance
            mock_instance.index_directory.return_value = True
            mock_instance.parsing_errors = []  # Make it a list
            
            result = runner.invoke(cli, ['index', '.', '--verbose'])
            
            assert result.exit_code == 0
            # Should have more detailed output
    
    def test_parallel_workers_validation(self, runner, temp_dir, mock_indexer):
        """Test parallel workers validation"""
        with runner.isolated_filesystem(temp_dir=temp_dir):
            Path("test.py").write_text("def hello(): pass")
            
            # Test valid worker count
            mock_instance = Mock()
            mock_indexer.return_value = mock_instance
            mock_instance.index_directory.return_value = True
            mock_instance.parsing_errors = []  # Make it a list
            
            result = runner.invoke(cli, ['index', '.', '--workers', '4'])
            
            assert result.exit_code == 0
            # Check that indexer was called with correct parameters
            call_args = mock_indexer.call_args
            assert call_args is not None
            assert call_args.kwargs['use_cache'] == True
            assert call_args.kwargs['parallel_workers'] == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])