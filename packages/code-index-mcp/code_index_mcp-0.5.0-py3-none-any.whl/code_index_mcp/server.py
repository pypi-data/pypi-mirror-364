"""
Code Index MCP Server

This MCP server allows LLMs to index, search, and analyze code from a project directory.
It provides tools for file discovery, content retrieval, and code analysis.
"""
# Standard library imports
import fnmatch
import json
import os
import sys
import tempfile
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Dict, List, Optional, Tuple, Any

# Third-party imports
from mcp import types
from mcp.server.fastmcp import FastMCP, Context

# Local imports
from .analyzers.analyzer_factory import AnalyzerFactory
from .constants import SETTINGS_DIR
from .project_settings import ProjectSettings

# MCP server will be created after lifespan manager is defined

# In-memory references (will be loaded from persistent storage)
file_index = {}
code_content_cache = {}
supported_extensions = [
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rb', '.php', '.swift', '.kt', '.rs', '.scala', '.sh',
    '.bash', '.html', '.css', '.scss', '.md', '.json', '.xml', '.yml', '.yaml', '.zig',
    # Frontend frameworks
    '.vue', '.svelte', '.mjs', '.cjs',
    # Style languages
    '.less', '.sass', '.stylus', '.styl',
    # Template engines
    '.hbs', '.handlebars', '.ejs', '.pug',
    # Modern frontend
    '.astro', '.mdx',
    # Objective-C
    '.m', '.mm',
    # Database and SQL
    '.sql', '.ddl', '.dml', '.mysql', '.postgresql', '.psql', '.sqlite',
    '.mssql', '.oracle', '.ora', '.db2',
    # Database objects
    '.proc', '.procedure', '.func', '.function', '.view', '.trigger', '.index',
    # Database frameworks and tools
    '.migration', '.seed', '.fixture', '.schema',
    # NoSQL and modern databases
    '.cql', '.cypher', '.sparql', '.gql',
    # Database migration tools
    '.liquibase', '.flyway'
]

@dataclass
class CodeIndexerContext:
    """Context for the Code Indexer MCP server."""
    base_path: str
    settings: ProjectSettings
    file_count: int = 0

@asynccontextmanager
async def indexer_lifespan(server: FastMCP) -> AsyncIterator[CodeIndexerContext]:
    """Manage the lifecycle of the Code Indexer MCP server."""
    # Don't set a default path, user must explicitly set project path
    base_path = ""  # Empty string to indicate no path is set

    print("Initializing Code Indexer MCP server...")

    # Initialize settings manager with skip_load=True to skip loading files
    settings = ProjectSettings(base_path, skip_load=True)

    # Initialize context
    context = CodeIndexerContext(
        base_path=base_path,
        settings=settings
    )

    # Initialize global variables
    global file_index, code_content_cache

    try:
        print("Server ready. Waiting for user to set project path...")
        # Provide context to the server
        yield context
    finally:
        # Only save index and cache if project path has been set
        if context.base_path and file_index:
            print(f"Saving index for project: {context.base_path}")
            settings.save_index(file_index)

        if context.base_path and code_content_cache:
            print(f"Saving cache for project: {context.base_path}")
            settings.save_cache(code_content_cache)

# Create the MCP server with lifespan manager
mcp = FastMCP("CodeIndexer", lifespan=indexer_lifespan, dependencies=["pathlib"])

# ----- RESOURCES -----

@mcp.resource("config://code-indexer")
def get_config() -> str:
    """Get the current configuration of the Code Indexer."""
    ctx = mcp.get_context()

    # Get the base path from context
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return json.dumps({
            "status": "not_configured",
            "message": "Project path not set. Please use set_project_path to set a project directory first.",
            "supported_extensions": supported_extensions
        }, indent=2)

    # Get file count
    file_count = ctx.request_context.lifespan_context.file_count

    # Get settings stats
    settings = ctx.request_context.lifespan_context.settings
    settings_stats = settings.get_stats()

    config = {
        "base_path": base_path,
        "supported_extensions": supported_extensions,
        "file_count": file_count,
        "settings_directory": settings.settings_path,
        "settings_stats": settings_stats
    }

    return json.dumps(config, indent=2)

@mcp.resource("files://{file_path}")
def get_file_content(file_path: str) -> str:
    """Get the content of a specific file."""
    ctx = mcp.get_context()

    # Get the base path from context
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return "Error: Project path not set. Please use set_project_path to set a project directory first."

    # Handle absolute paths (especially Windows paths starting with drive letters)
    if os.path.isabs(file_path) or (len(file_path) > 1 and file_path[1] == ':'):
        # Absolute paths are not allowed via this endpoint
        return f"Error: Absolute file paths like '{file_path}' are not allowed. Please use paths relative to the project root."

    # Normalize the file path
    norm_path = os.path.normpath(file_path)

    # Check for path traversal attempts
    if "..\\" in norm_path or "../" in norm_path or norm_path.startswith(".."):
        return f"Error: Invalid file path: {file_path} (directory traversal not allowed)"

    # Construct the full path and verify it's within the project bounds
    full_path = os.path.join(base_path, norm_path)
    real_full_path = os.path.realpath(full_path)
    real_base_path = os.path.realpath(base_path)

    if not real_full_path.startswith(real_base_path):
        return f"Error: Access denied. File path must be within project directory."

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Cache the content for faster retrieval later
        code_content_cache[norm_path] = content

        return content
    except UnicodeDecodeError:
        return f"Error: File {file_path} appears to be a binary file or uses unsupported encoding."
    except (FileNotFoundError, PermissionError, OSError) as e:
        return f"Error reading file: {e}"

@mcp.resource("structure://project")
def get_project_structure() -> str:
    """Get the structure of the project as a JSON tree."""
    ctx = mcp.get_context()

    # Get the base path from context
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return json.dumps({
            "status": "not_configured",
            "message": "Project path not set. Please use set_project_path to set a project directory first."
        }, indent=2)

    # Check if we need to refresh the index
    if not file_index:
        _index_project(base_path)
        # Update file count in context
        ctx.request_context.lifespan_context.file_count = _count_files(file_index)
        # Save updated index
        ctx.request_context.lifespan_context.settings.save_index(file_index)

    return json.dumps(file_index, indent=2)

@mcp.resource("settings://stats")
def get_settings_stats() -> str:
    """Get statistics about the settings directory and files."""
    ctx = mcp.get_context()

    # Get settings manager from context
    settings = ctx.request_context.lifespan_context.settings

    # Get settings stats
    stats = settings.get_stats()

    return json.dumps(stats, indent=2)

# ----- AUTO-REFRESH HELPERS -----

REFRESH_RATE_LIMIT_SECONDS = 30

# Memory cache for refresh time (loaded once per server session)
_cached_last_refresh_time = None

def _get_last_refresh_time(ctx: Context) -> float:
    """Get last refresh time, with memory cache for performance."""
    global _cached_last_refresh_time
    
    # Load from config only once per server session
    if _cached_last_refresh_time is None:
        config = ctx.request_context.lifespan_context.settings.load_config()
        _cached_last_refresh_time = config.get('last_auto_refresh_time', 0.0)
    
    return _cached_last_refresh_time

def _should_auto_refresh(ctx: Context) -> bool:
    """Check if auto-refresh is allowed based on 30-second rate limit."""
    last_refresh_time = _get_last_refresh_time(ctx)
    current_time = time.time()
    return (current_time - last_refresh_time) >= REFRESH_RATE_LIMIT_SECONDS

def _update_last_refresh_time(ctx: Context) -> None:
    """Update refresh time in both memory cache and persistent config."""
    global _cached_last_refresh_time
    current_time = time.time()
    
    # Update memory cache immediately for performance
    _cached_last_refresh_time = current_time
    
    # Persist to config for stateless client support
    config = ctx.request_context.lifespan_context.settings.load_config()
    config['last_auto_refresh_time'] = current_time
    ctx.request_context.lifespan_context.settings.save_config(config)

def _get_remaining_refresh_time(ctx: Context) -> int:
    """Get remaining seconds until next refresh is allowed."""
    last_refresh_time = _get_last_refresh_time(ctx)
    current_time = time.time()
    elapsed = current_time - last_refresh_time
    remaining = max(0, REFRESH_RATE_LIMIT_SECONDS - elapsed)
    return int(remaining)

# ----- TOOLS -----

@mcp.tool()
def set_project_path(path: str, ctx: Context) -> str:
    """Set the base project path for indexing."""
    # Validate and normalize path
    try:
        norm_path = os.path.normpath(path)
        abs_path = os.path.abspath(norm_path)

        if not os.path.exists(abs_path):
            return f"Error: Path does not exist: {abs_path}"

        if not os.path.isdir(abs_path):
            return f"Error: Path is not a directory: {abs_path}"

        # Clear existing in-memory index and cache
        global file_index, code_content_cache
        file_index.clear()
        code_content_cache.clear()

        # Update the base path in context
        ctx.request_context.lifespan_context.base_path = abs_path

        # Create a new settings manager for the new path (don't skip loading files)
        ctx.request_context.lifespan_context.settings = ProjectSettings(abs_path, skip_load=False)

        # Print the settings path for debugging
        settings_path = ctx.request_context.lifespan_context.settings.settings_path
        print(f"Project settings path: {settings_path}")

        # Try to load existing index and cache
        print(f"Project path set to: {abs_path}")
        print(f"Attempting to load existing index and cache...")

        # Try to load index
        loaded_index = None
        try:
            loaded_index = ctx.request_context.lifespan_context.settings.load_index()
        except Exception as e:
            print(f"Could not load existing index, it might be an old format. A new index will be created. Error: {e}")

        if loaded_index:
            print(f"Existing index found and loaded successfully")
            file_index = loaded_index
            file_count = _count_files(file_index)
            ctx.request_context.lifespan_context.file_count = file_count

            # Try to load cache
            loaded_cache = ctx.request_context.lifespan_context.settings.load_cache()
            if loaded_cache:
                print(f"Existing cache found and loaded successfully")
                code_content_cache.update(loaded_cache)

            # Get search capabilities info
            search_tool = ctx.request_context.lifespan_context.settings.get_preferred_search_tool()
            
            if search_tool is None:
                search_info = " Basic search available."
            else:
                search_info = f" Advanced search enabled ({search_tool.name})."
            
            return f"Project path set to: {abs_path}. Loaded existing index with {file_count} files.{search_info}"
        else:
            print(f"No existing index found, creating new index...")

        # If no existing index, create a new one
        file_count = _index_project(abs_path)
        ctx.request_context.lifespan_context.file_count = file_count

        # Save the new index
        ctx.request_context.lifespan_context.settings.save_index(file_index)

        # Save project config
        config = {
            "base_path": abs_path,
            "supported_extensions": supported_extensions,
            "last_indexed": ctx.request_context.lifespan_context.settings.load_config().get('last_indexed', None)
        }
        ctx.request_context.lifespan_context.settings.save_config(config)

        # Get search capabilities info (this will trigger lazy detection)
        search_tool = ctx.request_context.lifespan_context.settings.get_preferred_search_tool()
        
        if search_tool is None:
            search_info = " Basic search available."
        else:
            search_info = f" Advanced search enabled ({search_tool.name})."

        return f"Project path set to: {abs_path}. Indexed {file_count} files.{search_info}"
    except (OSError, ValueError, RuntimeError) as e:
        return f"Error setting project path: {e}"

@mcp.tool()
def search_code_advanced(
    pattern: str, 
    ctx: Context,
    case_sensitive: bool = True,
    context_lines: int = 0,
    file_pattern: Optional[str] = None,
    fuzzy: bool = False,
    regex: bool = False
) -> Dict[str, Any]:
    """
    Search for a code pattern in the project using an advanced, fast tool.
    
    This tool automatically selects the best available command-line search tool 
    (like ugrep, ripgrep, ag, or grep) for maximum performance.
    
    Args:
        pattern: The search pattern. Can be literal text or regex (see regex parameter).
        case_sensitive: Whether the search should be case-sensitive.
        context_lines: Number of lines to show before and after the match.
        file_pattern: A glob pattern to filter files to search in (e.g., "*.py", "*.js", "test_*.py").
                     All search tools now handle glob patterns consistently:
                     - ugrep: Uses glob patterns (*.py, *.{js,ts}) 
                     - ripgrep: Uses glob patterns (*.py, *.{js,ts})
                     - ag (Silver Searcher): Automatically converts globs to regex patterns
                     - grep: Basic glob pattern matching
                     All common glob patterns like "*.py", "test_*.js", "src/*.ts" are supported.
        fuzzy: If True, enables fuzzy/partial matching behavior varies by search tool:
               - ugrep: Native fuzzy search with --fuzzy flag (true edit-distance fuzzy search)
               - ripgrep, ag, grep, basic: Word boundary pattern matching (not true fuzzy search)
               IMPORTANT: Only ugrep provides true fuzzy search. Other tools use word boundary 
               matching which allows partial matches at word boundaries.
               For exact literal matches, set fuzzy=False (default and recommended).
        regex: If True, enables regex pattern matching. Use this for patterns like "ERROR|WARN".
               The pattern will be validated for safety to prevent ReDoS attacks.
               If False (default), uses literal string search.
               
    Returns:
        A dictionary containing the search results or an error message.
        
    """
    base_path = ctx.request_context.lifespan_context.base_path
    if not base_path:
        return {"error": "Project path not set. Please use set_project_path first."}

    settings = ctx.request_context.lifespan_context.settings
    strategy = settings.get_preferred_search_tool()

    if not strategy:
        return {"error": "No search strategies available. This is unexpected."}

    print(f"Using search strategy: {strategy.name}")

    try:
        results = strategy.search(
            pattern=pattern,
            base_path=base_path,
            case_sensitive=case_sensitive,
            context_lines=context_lines,
            file_pattern=file_pattern,
            fuzzy=fuzzy,
            regex=regex
        )
        return {"results": results}
    except Exception as e:
        return {"error": f"Search failed using '{strategy.name}': {e}"}

@mcp.tool()
def find_files(pattern: str, ctx: Context) -> Dict[str, Any]:
    """
    Find files matching a glob pattern. Auto-refreshes index if no results found.
    
    Use when:
    - Looking for files by pattern (e.g., "*.py", "test_*.js", "src/**/*.ts")
    - Checking if specific files exist in the project
    - Getting file lists for further analysis
    
    Auto-refresh behavior:
    - If no files found, automatically refreshes index once and retries
    - Rate limited to once every 30 seconds to avoid excessive refreshes
    - Manual refresh_index tool is always available without rate limits
    
    Args:
        pattern: Glob pattern to match files (e.g., "*.py", "test_*.js")
        
    Returns:
        Dictionary with files list and status information
    """
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return {
            "error": "Project path not set. Please use set_project_path to set a project directory first.",
            "files": []
        }

    # Check if we need to index the project initially
    if not file_index:
        _index_project(base_path)
        ctx.request_context.lifespan_context.file_count = _count_files(file_index)
        ctx.request_context.lifespan_context.settings.save_index(file_index)

    # First search attempt
    matching_files = []
    for file_path, _ in _get_all_files(file_index):
        if fnmatch.fnmatch(file_path, pattern):
            matching_files.append(file_path)

    # If no results found, try auto-refresh once (with rate limiting)
    if not matching_files:
        if _should_auto_refresh(ctx):
            # Perform full re-index
            file_index.clear()
            _index_project(base_path)
            ctx.request_context.lifespan_context.file_count = _count_files(file_index)
            ctx.request_context.lifespan_context.settings.save_index(file_index)
            
            # Update last refresh time
            _update_last_refresh_time(ctx)
            
            # Search again after refresh
            for file_path, _ in _get_all_files(file_index):
                if fnmatch.fnmatch(file_path, pattern):
                    matching_files.append(file_path)
            
            if matching_files:
                return {
                    "files": matching_files,
                    "status": f"✅ Found {len(matching_files)} files after refresh"
                }
            else:
                return {
                    "files": [],
                    "status": "⚠️ No files found even after refresh"
                }
        else:
            # Rate limited
            remaining_time = _get_remaining_refresh_time(ctx)
            return {
                "files": [],
                "status": f"⚠️ No files found - Rate limited. Try again in {remaining_time} seconds"
            }

    # Return successful results
    return {
        "files": matching_files,
        "status": f"✅ Found {len(matching_files)} files"
    }

@mcp.tool()
def get_file_summary(file_path: str, ctx: Context) -> Dict[str, Any]:
    """
    Get a summary of a specific file, including:
    - Line count
    - Function/class definitions (for supported languages)
    - Import statements
    - Basic complexity metrics
    """
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return {"error": "Project path not set. Please use set_project_path to set a project directory first."}

    # Normalize the file path
    norm_path = os.path.normpath(file_path)
    if norm_path.startswith('..'):
        return {"error": f"Invalid file path: {file_path}"}

    full_path = os.path.join(base_path, norm_path)

    try:
        # Get file content
        if norm_path in code_content_cache:
            content = code_content_cache[norm_path]
        else:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            code_content_cache[norm_path] = content
            # Save the updated cache
            ctx.request_context.lifespan_context.settings.save_cache(code_content_cache)

        # Basic file info
        lines = content.splitlines()
        line_count = len(lines)

        # File extension for language-specific analysis
        _, ext = os.path.splitext(norm_path)

        summary = {
            "file_path": norm_path,
            "line_count": line_count,
            "size_bytes": os.path.getsize(full_path),
            "extension": ext,
        }

        # Use the new analyzer framework for language-specific analysis
        try:
            analyzer = AnalyzerFactory.get_analyzer(ext)
            if analyzer is None:
                summary["error"] = "No analyzer available for this file type"
                summary["basic_info"] = True
                return summary
                
            analysis_result = analyzer.analyze(content, norm_path, full_path)
            
            # Convert to dict for backwards compatibility
            return analysis_result.to_dict()
        except Exception as e:
            # Fallback to basic summary if analyzer fails
            summary["error"] = f"Analysis failed: {str(e)}"
            summary["basic_info"] = True
            return summary
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return {"error": f"Error analyzing file: {e}"}

@mcp.tool()
def refresh_index(ctx: Context) -> str:
    """
    Manually refresh the project index when files have been added/removed/moved.
    
    Use when:
    - Files were added, deleted, or moved outside the editor
    - After git operations (checkout, merge, pull) that change files
    - When find_files results seem incomplete or outdated
    - For immediate refresh without waiting for auto-refresh rate limits
    
    Important notes for LLMs:
    - This tool bypasses the 30-second rate limit that applies to auto-refresh
    - Always available for immediate use when you know files have changed
    - Performs full project re-indexing for complete accuracy
    - Use when you suspect the index is stale after file system changes
    
    Returns:
        Success message with total file count
    """
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        return "Error: Project path not set. Please use set_project_path to set a project directory first."

    # Clear existing index
    global file_index
    file_index.clear()

    # Re-index the project
    file_count = _index_project(base_path)
    ctx.request_context.lifespan_context.file_count = file_count

    # Save the updated index
    ctx.request_context.lifespan_context.settings.save_index(file_index)

    # Update the last indexed timestamp in config
    config = ctx.request_context.lifespan_context.settings.load_config()
    ctx.request_context.lifespan_context.settings.save_config({
        **config,
        'last_indexed': ctx.request_context.lifespan_context.settings._get_timestamp()
    })
    
    # Update auto-refresh timer to prevent immediate auto-refresh after manual refresh
    _update_last_refresh_time(ctx)

    return f"Project re-indexed. Found {file_count} files."

@mcp.tool()
def get_settings_info(ctx: Context) -> Dict[str, Any]:
    """Get information about the project settings."""
    base_path = ctx.request_context.lifespan_context.base_path

    # Check if base_path is set
    if not base_path:
        # Even if base_path is not set, we can still show the temp directory
        temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)
        return {
            "status": "not_configured",
            "message": "Project path not set. Please use set_project_path to set a project directory first.",
            "temp_directory": temp_dir,
            "temp_directory_exists": os.path.exists(temp_dir)
        }

    settings = ctx.request_context.lifespan_context.settings

    # Get config
    config = settings.load_config()

    # Get stats
    stats = settings.get_stats()

    # Get temp directory
    temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)

    return {
        "settings_directory": settings.settings_path,
        "temp_directory": temp_dir,
        "temp_directory_exists": os.path.exists(temp_dir),
        "config": config,
        "stats": stats,
        "exists": os.path.exists(settings.settings_path)
    }

@mcp.tool()
def create_temp_directory() -> Dict[str, Any]:
    """Create the temporary directory used for storing index data."""
    temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)

    result = {
        "temp_directory": temp_dir,
        "existed_before": os.path.exists(temp_dir),
    }

    try:
        # Use ProjectSettings to handle directory creation consistently
        temp_settings = ProjectSettings("", skip_load=True)
        
        result["created"] = not result["existed_before"]
        result["exists_now"] = os.path.exists(temp_dir)
        result["is_directory"] = os.path.isdir(temp_dir)
    except Exception as e:
        result["error"] = str(e)

    return result

@mcp.tool()
def check_temp_directory() -> Dict[str, Any]:
    """Check the temporary directory used for storing index data."""
    temp_dir = os.path.join(tempfile.gettempdir(), SETTINGS_DIR)

    result = {
        "temp_directory": temp_dir,
        "exists": os.path.exists(temp_dir),
        "is_directory": os.path.isdir(temp_dir) if os.path.exists(temp_dir) else False,
        "temp_root": tempfile.gettempdir(),
    }

    # If the directory exists, list its contents
    if result["exists"] and result["is_directory"]:
        try:
            contents = os.listdir(temp_dir)
            result["contents"] = contents
            result["subdirectories"] = []

            # Check each subdirectory
            for item in contents:
                item_path = os.path.join(temp_dir, item)
                if os.path.isdir(item_path):
                    subdir_info = {
                        "name": item,
                        "path": item_path,
                        "contents": os.listdir(item_path) if os.path.exists(item_path) else []
                    }
                    result["subdirectories"].append(subdir_info)
        except (OSError, PermissionError) as e:
            result["error"] = str(e)

    return result

@mcp.tool()
def clear_settings(ctx: Context) -> str:
    """Clear all settings and cached data."""
    settings = ctx.request_context.lifespan_context.settings
    settings.clear()
    return "Project settings, index, and cache have been cleared."

@mcp.tool()
def refresh_search_tools(ctx: Context) -> str:
    """
    Manually re-detect the available command-line search tools on the system.
    This is useful if you have installed a new tool (like ripgrep) after starting the server.
    """
    settings = ctx.request_context.lifespan_context.settings
    settings.refresh_available_strategies()
    
    config = settings.get_search_tools_config()
    
    return f"Search tools refreshed. Available: {config['available_tools']}. Preferred: {config['preferred_tool']}."


# ----- PROMPTS -----

@mcp.prompt()
def analyze_code(file_path: str = "", query: str = "") -> list[types.PromptMessage]:
    """Prompt for analyzing code in the project."""
    messages = [
        types.PromptMessage(role="user", content=types.TextContent(type="text", text=f"""I need you to analyze some code from my project.

{f'Please analyze the file: {file_path}' if file_path else ''}
{f'I want to understand: {query}' if query else ''}

First, let me give you some context about the project structure. Then, I'll provide the code to analyze.
""")),
        types.PromptMessage(role="assistant", content=types.TextContent(type="text", text="I'll help you analyze the code. Let me first examine the project structure to get a better understanding of the codebase."))
    ]
    return messages

@mcp.prompt()
def code_search(query: str = "") -> types.TextContent:
    """Prompt for searching code in the project."""
    search_text = f"\"query\"" if not query else f"\"{query}\""
    return types.TextContent(type="text", text=f"""I need to search through my codebase for {search_text}.

Please help me find all occurrences of this query and explain what each match means in its context.
Focus on the most relevant files and provide a brief explanation of how each match is used in the code.

If there are too many results, prioritize the most important ones and summarize the patterns you see.""")

@mcp.prompt()
def set_project() -> list[types.PromptMessage]:
    """Prompt for setting the project path."""
    messages = [
        types.PromptMessage(role="user", content=types.TextContent(type="text", text="""
        I need to analyze code from a project, but I haven't set the project path yet. Please help me set up the project path and index the code.

        First, I need to specify which project directory to analyze.
        """)),
        types.PromptMessage(role="assistant", content=types.TextContent(type="text", text="""
        Before I can help you analyze any code, we need to set up the project path. This is a required first step.

        Please provide the full path to your project folder. For example:
        - Windows: "C:/Users/username/projects/my-project"
        - macOS/Linux: "/home/username/projects/my-project"

        Once you provide the path, I'll use the `set_project_path` tool to configure the code analyzer to work with your project.
        """))
    ]
    return messages

# ----- HELPER FUNCTIONS -----

def _index_project(base_path: str) -> int:
    """
    Create an index of the project files.
    Returns the number of files indexed.
    """
    file_count = 0
    file_index.clear()

    for root, dirs, files in os.walk(base_path):
        # Skip hidden directories and common build/dependency directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and
                 d not in ['node_modules', 'venv', '__pycache__', 'build', 'dist']]

        # Create relative path from base_path
        rel_path = os.path.relpath(root, base_path)
        current_dir = file_index

        # Skip the '.' directory (base_path itself)
        if rel_path != '.':
            # Split the path and navigate/create the tree
            path_parts = rel_path.replace('\\', '/').split('/')
            for part in path_parts:
                if part not in current_dir:
                    current_dir[part] = {"type": "directory", "children": {}}
                current_dir = current_dir[part]["children"]

        # Add files to current directory
        for file in files:
            # Skip hidden files and files with unsupported extensions
            _, ext = os.path.splitext(file)
            if file.startswith('.') or ext not in supported_extensions:
                continue

            # Store file information
            file_path = os.path.join(rel_path, file).replace('\\', '/')
            if rel_path == '.':
                file_path = file

            current_dir[file] = {
                "type": "file",
                "path": file_path,
                "ext": ext
            }
            file_count += 1

    return file_count

def _count_files(directory: Dict) -> int:
    """
    Count the number of files in the index.
    """
    count = 0
    for name, value in directory.items():
        if isinstance(value, dict):
            if value.get("type") == "file":
                count += 1
            elif value.get("type") == "directory":
                count += _count_files(value.get("children", {}))
    return count

def _get_all_files(directory: Dict, prefix: str = "") -> List[Tuple[str, Dict]]:
    """Recursively get all files from the index."""
    all_files = []
    for name, item in directory.items():
        current_path = os.path.join(prefix, name).replace('\\', '/')
        if item.get('type') == 'file':
            all_files.append((current_path, item))
        elif item.get('type') == 'directory':
            all_files.extend(_get_all_files(item.get('children', {}), current_path))
    return all_files


def main():
    """Main function to run the MCP server."""
    # Run the server. Tools are discovered automatically via decorators.
    mcp.run()

if __name__ == '__main__':
    # Set path to project root
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
