"""
MCP Protocol Compliance Tests.

This module tests compliance with the Model Context Protocol (MCP)
specification, including tool discovery, parameter validation,
and response formatting.
"""

import asyncio
import json
import pytest
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch

from src.todo_mcp.config import TodoConfig
from src.todo_mcp.server import TodoMCPServer


@pytest.fixture
def mcp_server():
    """Create MCP server for compliance testing."""
    config = TodoConfig(
        data_directory="test_data",
        log_level="DEBUG",
        performance_monitoring=True
    )
    server = TodoMCPServer(config)
    server.task_service.initialize = AsyncMock()
    server.task_service._initialized = True
    return server


class TestMCPToolDiscovery:
    """Test MCP tool discovery compliance."""
    
    def test_tool_definitions_structure(self, mcp_server):
        """Test that tool definitions follow MCP structure."""
        tools = mcp_server._get_tool_definitions()
        
        for tool in tools:
            # Required MCP tool fields
            assert hasattr(tool, 'name'), f"Tool missing name: {tool}"
            assert hasattr(tool, 'description'), f"Tool missing description: {tool.name}"
            assert hasattr(tool, 'inputSchema'), f"Tool missing inputSchema: {tool.name}"
            
            # Validate name format
            assert isinstance(tool.name, str), f"Tool name not string: {tool.name}"
            assert len(tool.name) > 0, f"Tool name empty: {tool.name}"
            assert tool.name.replace('_', '').replace('-', '').isalnum(), f"Invalid tool name: {tool.name}"
            
            # Validate description
            assert isinstance(tool.description, str), f"Tool description not string: {tool.name}"
            assert len(tool.description.strip()) > 0, f"Tool description empty: {tool.name}"
            
            # Validate schema
            assert isinstance(tool.inputSchema, dict), f"Tool schema not dict: {tool.name}"
    
    def test_json_schema_compliance(self, mcp_server):
        """Test that tool schemas are valid JSON Schema."""
        tools = mcp_server._get_tool_definitions()
        
        for tool in tools:
            schema = tool.inputSchema
            
            # Basic JSON Schema requirements
            assert schema.get('type') == 'object', f"Tool schema type not object: {tool.name}"
            
            # Properties validation
            if 'properties' in schema:
                properties = schema['properties']
                assert isinstance(properties, dict), f"Properties not dict: {tool.name}"
                
                for prop_name, prop_schema in properties.items():
                    assert isinstance(prop_schema, dict), f"Property schema not dict: {tool.name}.{prop_name}"
                    
                    # Each property should have type or enum
                    has_type = 'type' in prop_schema
                    has_enum = 'enum' in prop_schema
                    assert has_type or has_enum, f"Property missing type/enum: {tool.name}.{prop_name}"
                    
                    # Validate enum values
                    if has_enum:
                        enum_values = prop_schema['enum']
                        assert isinstance(enum_values, list), f"Enum not list: {tool.name}.{prop_name}"
                        assert len(enum_values) > 0, f"Empty enum: {tool.name}.{prop_name}"
            
            # Required fields validation
            if 'required' in schema:
                required = schema['required']
                assert isinstance(required, list), f"Required not list: {tool.name}"
                
                properties = schema.get('properties', {})
                for required_field in required:
                    assert required_field in properties, f"Required field not in properties: {tool.name}.{required_field}"
    
    def test_tool_name_uniqueness(self, mcp_server):
        """Test that all tool names are unique."""
        tools = mcp_server._get_tool_definitions()
        tool_names = [tool.name for tool in tools]
        
        assert len(tool_names) == len(set(tool_names)), "Duplicate tool names found"
    
    def test_required_tools_present(self, mcp_server):
        """Test that all required tools are present."""
        tools = mcp_server._get_tool_definitions()
        tool_names = [tool.name for tool in tools]
        
        # Core required tools based on requirements
        required_tools = [
            "create_task",
            "update_task", 
            "delete_task",
            "get_task",
            "list_tasks",
            "update_task_status",
            "get_pending_tasks",
            "get_in_progress_tasks",
            "get_completed_tasks",
            "get_blocked_tasks",
            "add_child_task",
            "remove_child_task",
            "get_task_hierarchy",
            "move_task",
            "search_tasks",
            "filter_tasks",
            "get_task_statistics",
            "get_task_context"
        ]
        
        for required_tool in required_tools:
            assert required_tool in tool_names, f"Missing required tool: {required_tool}"


class TestMCPToolExecution:
    """Test MCP tool execution compliance."""
    
    @pytest.mark.asyncio
    async def test_tool_call_response_format(self, mcp_server):
        """Test that tool calls return properly formatted responses."""
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.return_value = {"success": True, "task": {"id": "test_123"}}
            
            result = await mcp_server._handle_tool_call("create_task", {"title": "Test"})
            
            # Should return list of TextContent
            assert isinstance(result, list), "Tool call should return list"
            assert len(result) == 1, "Tool call should return single item"
            
            text_content = result[0]
            assert hasattr(text_content, 'type'), "Response missing type"
            assert hasattr(text_content, 'text'), "Response missing text"
            assert text_content.type == "text", "Response type should be text"
            
            # Text should be valid JSON
            response_data = json.loads(text_content.text)
            assert isinstance(response_data, dict), "Response should be JSON object"
    
    @pytest.mark.asyncio
    async def test_error_response_format(self, mcp_server):
        """Test that errors are properly formatted."""
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.side_effect = ValueError("Test error")
            
            result = await mcp_server._handle_tool_call("create_task", {"title": "Test"})
            
            assert len(result) == 1
            text_content = result[0]
            assert text_content.type == "text"
            
            # Should be valid JSON error response
            error_data = json.loads(text_content.text)
            assert isinstance(error_data, dict)
            
            # Check error structure
            if error_data.get("error") is True:
                assert "error_type" in error_data
                assert "message" in error_data
                assert "tool" in error_data
    
    @pytest.mark.asyncio
    async def test_unknown_tool_handling(self, mcp_server):
        """Test handling of unknown tool calls."""
        result = await mcp_server._handle_tool_call("unknown_tool", {})
        
        assert len(result) == 1
        text_content = result[0]
        assert text_content.type == "text"
        
        error_data = json.loads(text_content.text)
        assert error_data.get("error") is True
        assert "Unknown tool" in error_data["message"]
    
    @pytest.mark.asyncio
    async def test_all_tools_executable(self, mcp_server):
        """Test that all defined tools can be executed."""
        tools = mcp_server._get_tool_definitions()
        
        for tool in tools:
            # Check that handler exists
            handler_name = f"_handle_{tool.name}"
            assert hasattr(mcp_server, handler_name), f"Missing handler for {tool.name}"
            
            handler = getattr(mcp_server, handler_name)
            assert callable(handler), f"Handler not callable for {tool.name}"


class TestMCPParameterValidation:
    """Test MCP parameter validation."""
    
    @pytest.mark.asyncio
    async def test_required_parameter_validation(self, mcp_server):
        """Test validation of required parameters."""
        # Test create_task which requires 'title'
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.side_effect = ValueError("Missing required parameter: title")
            
            result = await mcp_server._handle_tool_call("create_task", {})
            
            error_data = json.loads(result[0].text)
            assert error_data.get("error") is True or "error" in str(error_data)
    
    @pytest.mark.asyncio
    async def test_parameter_type_validation(self, mcp_server):
        """Test parameter type validation."""
        # Test with invalid parameter types
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.side_effect = ValueError("Invalid parameter type")
            
            result = await mcp_server._handle_tool_call("create_task", {
                "title": 123  # Should be string
            })
            
            error_data = json.loads(result[0].text)
            assert error_data.get("error") is True or "error" in str(error_data)
    
    @pytest.mark.asyncio
    async def test_enum_parameter_validation(self, mcp_server):
        """Test enum parameter validation."""
        # Test with invalid enum value
        with patch('src.todo_mcp.tools.status_tools.update_task_status') as mock_tool:
            mock_tool.side_effect = ValueError("Invalid status value")
            
            result = await mcp_server._handle_tool_call("update_task_status", {
                "task_id": "test_123",
                "status": "invalid_status"  # Should be one of the enum values
            })
            
            error_data = json.loads(result[0].text)
            assert error_data.get("error") is True or "error" in str(error_data)


class TestMCPResponseConsistency:
    """Test MCP response consistency."""
    
    @pytest.mark.asyncio
    async def test_success_response_consistency(self, mcp_server):
        """Test that successful responses follow consistent format."""
        test_tools = [
            ("create_task", {"title": "Test"}, {"success": True, "task": {"id": "123"}}),
            ("list_tasks", {}, {"success": True, "tasks": []}),
            ("get_task_statistics", {}, {"success": True, "statistics": {}}),
        ]
        
        for tool_name, args, mock_response in test_tools:
            module_name = {
                "create_task": "task_tools",
                "list_tasks": "task_tools", 
                "get_task_statistics": "query_tools"
            }.get(tool_name, "task_tools")
            
            with patch(f'src.todo_mcp.tools.{module_name}.{tool_name}') as mock_tool:
                mock_tool.return_value = mock_response
                
                result = await mcp_server._handle_tool_call(tool_name, args)
                
                assert len(result) == 1
                assert result[0].type == "text"
                
                response_data = json.loads(result[0].text)
                assert isinstance(response_data, dict)
                assert response_data.get("success") is True
    
    @pytest.mark.asyncio
    async def test_error_response_consistency(self, mcp_server):
        """Test that error responses follow consistent format."""
        test_errors = [
            ("create_task", ValueError("Validation error")),
            ("get_task", RuntimeError("Database error")),
            ("update_task_status", KeyError("Task not found")),
        ]
        
        for tool_name, error in test_errors:
            module_name = {
                "create_task": "task_tools",
                "get_task": "task_tools",
                "update_task_status": "status_tools"
            }.get(tool_name, "task_tools")
            
            with patch(f'src.todo_mcp.tools.{module_name}.{tool_name}') as mock_tool:
                mock_tool.side_effect = error
                
                result = await mcp_server._handle_tool_call(tool_name, {})
                
                assert len(result) == 1
                assert result[0].type == "text"
                
                error_data = json.loads(result[0].text)
                assert isinstance(error_data, dict)
                
                # Check consistent error structure
                if error_data.get("error") is True:
                    assert "error_type" in error_data
                    assert "message" in error_data
                    assert "tool" in error_data
                    assert error_data["tool"] == tool_name


class TestMCPPerformanceCompliance:
    """Test MCP performance requirements."""
    
    @pytest.mark.asyncio
    async def test_response_time_logging(self, mcp_server, caplog):
        """Test that response times are logged for performance monitoring."""
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.return_value = {"success": True}
            
            await mcp_server._handle_tool_call("create_task", {"title": "Test"})
            
            # Check that execution time was logged
            log_messages = [record.message for record in caplog.records]
            assert any("completed successfully in" in msg for msg in log_messages)
    
    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, mcp_server):
        """Test that server can handle concurrent tool calls."""
        with patch('src.todo_mcp.tools.task_tools.create_task') as mock_tool:
            mock_tool.return_value = {"success": True, "task": {"id": "test"}}
            
            # Execute multiple tool calls concurrently
            tasks = [
                mcp_server._handle_tool_call("create_task", {"title": f"Task {i}"})
                for i in range(5)
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All should succeed
            assert len(results) == 5
            for result in results:
                assert len(result) == 1
                assert result[0].type == "text"
                data = json.loads(result[0].text)
                assert data["success"] is True