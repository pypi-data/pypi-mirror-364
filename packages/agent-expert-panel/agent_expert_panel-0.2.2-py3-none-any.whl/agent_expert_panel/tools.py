"""
Simple tools system for Agent Expert Panel.

This module provides an easy way to define tools as Python functions
and load them for use with agents, supporting both programmatic and YAML usage.
"""

import importlib.util
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Callable, Union


def load_tools_from_file(file_path: Union[str, Path]) -> Dict[str, Callable]:
    """
    Load all functions from a Python file that can be used as tools.

    Args:
        file_path: Path to the Python file containing tool functions

    Returns:
        Dictionary mapping function names to function objects
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Tools file not found: {file_path}")

    # Load the module
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Extract all callable functions (excluding private ones)
    tools = {}
    for name, obj in inspect.getmembers(module):
        if (
            inspect.isfunction(obj)
            and not name.startswith("_")
            and obj.__module__ == module.__name__
        ):
            tools[name] = obj

    return tools


def load_tools_from_directory(directory: Union[str, Path]) -> Dict[str, Callable]:
    """
    Load all tool functions from all Python files in a directory.

    Args:
        directory: Directory containing Python files with tool functions

    Returns:
        Dictionary mapping function names to function objects
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Tools directory not found: {directory}")

    all_tools = {}

    for py_file in directory.glob("*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            file_tools = load_tools_from_file(py_file)
            # Check for name conflicts
            for name, func in file_tools.items():
                if name in all_tools:
                    print(
                        f"Warning: Tool '{name}' defined in multiple files. Using version from {py_file}"
                    )
                all_tools[name] = func
        except Exception as e:
            print(f"Warning: Could not load tools from {py_file}: {e}")

    return all_tools


def import_function(import_path: str) -> Callable:
    """
    Import a function from a module path.

    Args:
        import_path: Path like "pandas.read_csv" or "json.loads"

    Returns:
        The imported function

    Raises:
        ImportError: If the module or function cannot be imported
        AttributeError: If the function doesn't exist in the module
    """
    if "." not in import_path:
        raise ValueError(
            "Import path must contain at least one dot (e.g., 'module.function')"
        )

    # Split into module path and function name
    parts = import_path.split(".")
    function_name = parts[-1]
    module_path = ".".join(parts[:-1])

    try:
        # Import the module
        module = importlib.import_module(module_path)

        # Get the function from the module
        if not hasattr(module, function_name):
            raise AttributeError(
                f"Module '{module_path}' has no attribute '{function_name}'"
            )

        func = getattr(module, function_name)

        if not callable(func):
            raise ValueError(f"'{import_path}' is not callable")

        return func

    except ImportError as e:
        raise ImportError(f"Could not import '{module_path}': {e}")


def create_library_tool(import_path: str, tool_name: str = None) -> Callable:
    """
    Create a tool from a library function with async wrapper if needed.

    Args:
        import_path: Path like "pandas.read_csv" or "json.loads"
        tool_name: Optional custom name for the tool (defaults to function name)

    Returns:
        Async wrapper function that can be used as a tool
    """
    func = import_function(import_path)
    name = tool_name or import_path.split(".")[-1]

    # Check if function is already async
    if inspect.iscoroutinefunction(func):
        # Already async, just return it
        func.__tool_name__ = name
        func.__import_path__ = import_path
        return func

    # Create async wrapper for sync function
    async def async_wrapper(*args, **kwargs):
        """Async wrapper for library function."""
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            return {"error": f"Tool '{name}' failed: {str(e)}"}

    # Copy metadata
    async_wrapper.__name__ = name
    async_wrapper.__doc__ = func.__doc__
    async_wrapper.__tool_name__ = name
    async_wrapper.__import_path__ = import_path
    async_wrapper.__wrapped__ = func

    return async_wrapper


def get_tools_by_names(
    tool_names: List[str], available_tools: Dict[str, Callable]
) -> List[Callable]:
    """
    Get tool functions by their names from a dictionary of available tools.
    Also supports importing functions directly from libraries using dot notation.

    Args:
        tool_names: List of tool names to retrieve. Can include:
                   - Built-in tool names: "web_search"
                   - Library imports: "pandas.read_csv", "json.loads"
                   - Custom tool names from available_tools
        available_tools: Dictionary of available tools

    Returns:
        List of tool functions

    Raises:
        ValueError: If a requested tool is not found
        ImportError: If a library import fails
    """
    tools = []
    for name in tool_names:
        if name in available_tools:
            # Found in available tools
            tools.append(available_tools[name])
        elif "." in name:
            # Looks like a library import path
            try:
                library_tool = create_library_tool(name)
                tools.append(library_tool)
            except (ImportError, AttributeError, ValueError) as e:
                raise ValueError(f"Could not import tool '{name}': {e}")
        else:
            # Not found anywhere
            available_names = list(available_tools.keys())
            raise ValueError(
                f"Tool '{name}' not found. Available tools: {available_names}. "
                f"For library functions, use dot notation like 'pandas.read_csv'"
            )

    return tools


# Built-in tools - simple functions that can be used directly
async def web_search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Search the web for information.

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        Dictionary with search results
    """
    # This is a mock implementation - replace with real search API
    results = [
        {
            "title": f"Search result {i + 1} for: {query}",
            "url": f"https://example.com/result-{i + 1}",
            "snippet": f"This is a sample search result snippet for query '{query}'",
        }
        for i in range(min(max_results, 3))
    ]

    return {"query": query, "results": results, "total_results": len(results)}


async def read_file(file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
    """
    Read contents from a file.

    Args:
        file_path: Path to the file to read
        encoding: File encoding

    Returns:
        Dictionary with file contents and metadata
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"error": f"File not found: {file_path}"}

        content = path.read_text(encoding=encoding)

        return {
            "file_path": str(path.absolute()),
            "content": content,
            "size": len(content),
            "encoding": encoding,
        }
    except Exception as e:
        return {"error": f"Failed to read file: {str(e)}"}


async def write_file(
    file_path: str, content: str, encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Write content to a file.

    Args:
        file_path: Path to the file to write
        content: Content to write
        encoding: File encoding

    Returns:
        Dictionary with write operation results
    """
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding=encoding)

        return {
            "file_path": str(path.absolute()),
            "bytes_written": len(content.encode(encoding)),
            "encoding": encoding,
        }
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}


async def calculate(expression: str) -> Dict[str, Any]:
    """
    Safely evaluate mathematical expressions.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Dictionary with calculation result
    """
    try:
        # Simple safe evaluation - only allow basic math operations
        allowed_chars = set("0123456789+-*/().,e ")
        if not all(c in allowed_chars for c in expression):
            return {"error": "Expression contains invalid characters"}

        # Use eval with restricted globals for safety
        result = eval(expression, {"__builtins__": {}}, {})

        return {
            "expression": expression,
            "result": result,
            "result_type": type(result).__name__,
        }
    except Exception as e:
        return {"error": f"Calculation failed: {str(e)}"}


def add_library_tools_to_dict(
    tools_dict: Dict[str, Callable], library_tools: Dict[str, str]
) -> None:
    """
    Add library tools to a tools dictionary.

    Args:
        tools_dict: Dictionary to add tools to
        library_tools: Dictionary mapping tool names to import paths
                      e.g., {"read_csv": "pandas.read_csv", "loads": "json.loads"}
    """
    for tool_name, import_path in library_tools.items():
        try:
            tools_dict[tool_name] = create_library_tool(import_path, tool_name)
        except (ImportError, AttributeError, ValueError) as e:
            print(
                f"Warning: Could not add library tool '{tool_name}' ({import_path}): {e}"
            )


# Built-in tools registry - simple dictionary
BUILTIN_TOOLS = {
    "web_search": web_search,
    "read_file": read_file,
    "write_file": write_file,
    "calculate": calculate,
}

# Add some common library tools that are likely to be useful
COMMON_LIBRARY_TOOLS = {
    "json_loads": "json.loads",
    "json_dumps": "json.dumps",
    "base64_encode": "base64.b64encode",
    "base64_decode": "base64.b64decode",
    "url_parse": "urllib.parse.urlparse",
    "datetime_now": "datetime.datetime.now",
}

# Try to add common library tools (will skip if libraries not available)
add_library_tools_to_dict(BUILTIN_TOOLS, COMMON_LIBRARY_TOOLS)
