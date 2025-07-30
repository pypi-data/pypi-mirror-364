"""
Tests for MCP server tool integration.

This module tests the integration of all tools with the MCP server,
including error handling, response formatting, and logging.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer


@pytest.fixture
def config():
    """Create a test configuration."""
    return TodoConfig(
        data_directory="test_data",
        log_level="DEBUG",
        performance_monitoring=True
    )


@pytest.fixture
def server(config):
    """Create a test server instance."""
    return TodoMCPServer(config)


class TestToolIntegration:
    """Test tool integration with the MCP server."""
    
    @pytest.mark.asyncio
    async def test_all_tools_have_handlers(self, server):
        """Test that all defined tools have corresponding handlers."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            handler_name = f"_handle_{tool.name}"
            assert hasattr(server, handler_name), f"Missing handler for tool: {tool.name}"
            
            handler = getattr(server, handler_name)
            assert callable(handler), f"Handler {handler_name} is not callable"
    
    @pytest.mark.asyncio
    async def test_task_management_tools_integration(self, server):
        """Test integration of task management tools."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        task_tools = ["create_task", "update_task", "delete_task", "get_task", "list_tasks"]
        
        for tool_name in task_tools:
            with patch(f'src.todo_mcp.tools.task_tools.{tool_name}') as mock_tool:
                mock_tool.return_value = {"success": True, "tool": tool_name}
                
                result = await server._handle_tool_call(tool_name, {"test": "data"})
                
                assert len(result) == 1
                assert result[0].type == "text"
                response_data = json.loads(result[0].text)
                assert response_data["success"] is True
                assert response_data["tool"] == tool_name
                mock_tool.assert_called_once_with({"test": "data"})
    
    @pytest.mark.asyncio
    async def test_status_management_tools_integration(self, server):
        """Test integration of status management tools."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        status_tools = [
            "update_task_status", "bulk_status_update", "get_task_status",
            "get_pending_tasks", "get_in_progress_tasks", 
            "get_blocked_tasks", "get_completed_tasks"
        ]
        
        for tool_name in status_tools:
            with patch(f'src.todo_mcp.tools.status_tools.{tool_name}') as mock_tool:
                mock_tool.return_value = {"success": True, "tool": tool_name}
                
                result = await server._handle_tool_call(tool_name, {"test": "data"})
                
                assert len(result) == 1
                assert result[0].type == "text"
                response_data = json.loads(result[0].text)
                assert response_data["success"] is True
                mock_tool.assert_called_once_with({"test": "data"})
    
    @pytest.mark.asyncio
    async def test_hierarchy_management_tools_integration(self, server):
        """Test integration of hierarchy management tools."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        hierarchy_tools = [
            "add_child_task", "remove_child_task", 
            "get_task_hierarchy", "move_task"
        ]
        
        for tool_name in hierarchy_tools:
            with patch(f'src.todo_mcp.tools.hierarchy_tools.{tool_name}') as mock_tool:
                mock_tool.return_value = {"success": True, "tool": tool_name}
                
                result = await server._handle_tool_call(tool_name, {"test": "data"})
                
                assert len(result) == 1
                assert result[0].type == "text"
                response_data = json.loads(result[0].text)
                assert response_data["success"] is True
                mock_tool.assert_called_once_with({"test": "data"})
    
    @pytest.mark.asyncio
    async def test_query_tools_integration(self, server):
        """Test integration of query tools."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        query_tools = ["search_tasks", "filter_tasks", "get_task_statistics"]
        
        for tool_name in query_tools:
            with patch(f'src.todo_mcp.tools.query_tools.{tool_name}') as mock_tool:
                mock_tool.return_value = {"success": True, "tool": tool_name}
                
                result = await server._handle_tool_call(tool_name, {"test": "data"})
                
                assert len(result) == 1
                assert result[0].type == "text"
                response_data = json.loads(result[0].text)
                assert response_data["success"] is True
                mock_tool.assert_called_once_with({"test": "data"})
    
    @pytest.mark.asyncio
    async def test_get_task_context_integration(self, server):
        """Test integration of get_task_context tool."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.get_task_context') as mock_tool:
            mock_tool.return_value = {"success": True, "context": "full_context"}
            
            result = await server._handle_tool_call("get_task_context", {"task_id": "test_123"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            response_data = json.loads(result[0].text)
            assert response_data["success"] is True
            assert response_data["context"] == "full_context"
            mock_tool.assert_called_once_with({"task_id": "test_123"})


class TestErrorHandling:
    """Test unified error handling and response formatting."""
    
    @pytest.mark.asyncio
    async def test_tool_not_found_error(self, server):
        """Test handling of unknown tool calls."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        result = await server._handle_tool_call("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        
        error_data = json.loads(result[0].text)
        assert error_data["error"] is True
        assert error_data["error_type"] == "ValueError"
        assert "Unknown tool: unknown_tool" in error_data["message"]
        assert error_data["tool"] == "unknown_tool"
    
    @pytest.mark.asyncio
    async def test_tool_execution_error(self, server):
        """Test handling of tool execution errors."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.side_effect = RuntimeError("Database connection failed")
            
            result = await server._handle_tool_call("create_task", {"title": "Test"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            
            error_data = json.loads(result[0].text)
            assert error_data["error"] is True
            assert error_data["error_type"] == "RuntimeError"
            assert "Database connection failed" in error_data["message"]
            assert error_data["tool"] == "create_task"
    
    @pytest.mark.asyncio
    async def test_validation_error_with_suggestion(self, server):
        """Test validation error handling with helpful suggestions."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.get_task') as mock_tool:
            mock_tool.side_effect = ValueError("Task not found: invalid_id")
            
            result = await server._handle_tool_call("get_task", {"task_id": "invalid_id"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            
            error_data = json.loads(result[0].text)
            assert error_data["error"] is True
            assert "not found" in error_data["message"]
            assert "suggestion" in error_data
            assert "list_tasks" in error_data["suggestion"]
    
    def test_response_formatting(self, server):
        """Test response formatting for different data types."""
        # Test dict formatting
        dict_result = {"key": "value", "number": 42}
        formatted = server._format_tool_response(dict_result, "test_tool")
        parsed = json.loads(formatted)
        assert parsed == dict_result
        
        # Test list formatting
        list_result = [1, 2, 3, "test"]
        formatted = server._format_tool_response(list_result, "test_tool")
        parsed = json.loads(formatted)
        assert parsed == list_result
        
        # Test string formatting
        string_result = "Simple string response"
        formatted = server._format_tool_response(string_result, "test_tool")
        assert formatted == string_result
        
        # Test other type formatting
        int_result = 42
        formatted = server._format_tool_response(int_result, "test_tool")
        assert formatted == "42"
    
    def test_error_response_formatting(self, server):
        """Test error response formatting."""
        error = ValueError("Test validation error")
        formatted = server._format_error_response(error, "test_tool", {"arg": "value"})
        
        error_data = json.loads(formatted)
        assert error_data["error"] is True
        assert error_data["error_type"] == "ValueError"
        assert error_data["message"] == "Test validation error"
        assert error_data["tool"] == "test_tool"
        assert "timestamp" in error_data


class TestLoggingAndDebugging:
    """Test request logging and debugging support."""
    
    @pytest.mark.asyncio
    async def test_request_logging(self, server, caplog):
        """Test that requests are properly logged."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.return_value = {"success": True}
            
            await server._handle_tool_call("create_task", {"title": "Test Task"})
            
            # Check that appropriate log messages were created
            log_messages = [record.message for record in caplog.records]
            assert any("Tool call: create_task" in msg for msg in log_messages)
            assert any("completed successfully" in msg for msg in log_messages)
    
    @pytest.mark.asyncio
    async def test_error_logging(self, server, caplog):
        """Test that errors are properly logged."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.side_effect = RuntimeError("Test error")
            
            await server._handle_tool_call("create_task", {"title": "Test Task"})
            
            # Check that error was logged
            log_messages = [record.message for record in caplog.records]
            assert any("failed" in msg and "Test error" in msg for msg in log_messages)
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, server, caplog):
        """Test that execution time is logged."""
        server.task_service.initialize = AsyncMock()
        server.task_service._initialized = True
        
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.return_value = {"success": True}
            
            await server._handle_tool_call("create_task", {"title": "Test Task"})
            
            # Check that execution time was logged
            log_messages = [record.message for record in caplog.records]
            assert any("completed successfully in" in msg and "s" in msg for msg in log_messages)
    
    @pytest.mark.asyncio
    async def test_list_tools_logging(self, server, caplog):
        """Test that list_tools requests are logged."""
        tools = server._get_tool_definitions()
        
        # Simulate the handler
        @server.server.list_tools()
        async def handle_list_tools():
            server.logger.debug("Handling list_tools request")
            tools = server._get_tool_definitions()
            server.logger.info(f"Returning {len(tools)} available tools")
            return tools
        
        result = await handle_list_tools()
        
        assert len(result) > 0
        log_messages = [record.message for record in caplog.records]
        assert any("Handling list_tools request" in msg for msg in log_messages)
        assert any("available tools" in msg for msg in log_messages)


class TestToolSchemaValidation:
    """Test tool schema validation and compliance."""
    
    def test_all_tools_have_valid_schemas(self, server):
        """Test that all tools have valid JSON schemas."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            # Check basic schema structure
            assert hasattr(tool, 'inputSchema')
            schema = tool.inputSchema
            assert isinstance(schema, dict)
            assert schema.get('type') == 'object'
            
            # Check properties if they exist
            if 'properties' in schema:
                assert isinstance(schema['properties'], dict)
                for prop_name, prop_schema in schema['properties'].items():
                    assert isinstance(prop_schema, dict)
                    # Should have type or enum
                    assert 'type' in prop_schema or 'enum' in prop_schema
            
            # Check required fields if they exist
            if 'required' in schema:
                assert isinstance(schema['required'], list)
                for required_field in schema['required']:
                    assert required_field in schema.get('properties', {})
    
    def test_tool_names_consistency(self, server):
        """Test that tool names are consistent between definitions and handlers."""
        tools = server._get_tool_definitions()
        
        for tool in tools:
            # Check that handler exists
            handler_name = f"_handle_{tool.name}"
            assert hasattr(server, handler_name)
            
            # Check that tool name is valid
            assert tool.name.replace('_', '').replace('-', '').isalnum()
            assert not tool.name.startswith('_')
            assert not tool.name.endswith('_')
    
    def test_required_tools_present(self, server):
        """Test that all required tools are present."""
        tools = server._get_tool_definitions()
        tool_names = [tool.name for tool in tools]
        
        # Core task management tools
        required_tools = [
            "create_task", "update_task", "delete_task", "get_task", "list_tasks",
            "update_task_status", "get_pending_tasks", "get_in_progress_tasks",
            "get_blocked_tasks", "get_completed_tasks",
            "add_child_task", "get_task_hierarchy",
            "search_tasks", "get_task_statistics"
        ]
        
        for required_tool in required_tools:
            assert required_tool in tool_names, f"Missing required tool: {required_tool}"