# Lmod MCP Server

The Lmod MCP server provides tools for managing environment modules using the Lmod system. It allows AI agents to search, load, unload, and inspect modules on HPC systems.

## Features

- **List loaded modules**: See which modules are currently active
- **Search available modules**: Find modules by name or pattern
- **Show module details**: Get comprehensive information about any module
- **Load/unload modules**: Manage your environment by loading or unloading modules
- **Swap modules**: Atomically replace one module with another
- **Spider search**: Deep search through the entire module hierarchy
- **Save/restore collections**: Save and restore sets of modules

## Installation

```bash
# Install the MCP server
uv pip install "git+https://github.com/iowarp/scientific-mcps.git@main#subdirectory=lmod"

# Or install from local directory
cd lmod
uv pip install -e .
```

## Running the Server

After installation, you can run the server using:

```bash
uv run lmod-mcp
```

Or if installed globally:

```bash
lmod-mcp
```

## Available Tools

### module_list
List all currently loaded environment modules.
```json
{
  "success": true,
  "modules": ["gcc/11.2.0", "python/3.9.0"],
  "count": 2
}
```

### module_avail
Search for available modules that can be loaded.
- **pattern** (optional): Search pattern with wildcards (e.g., 'python*', 'gcc/*')

### module_show
Display detailed information about a specific module.
- **module_name**: Name of the module (e.g., 'python/3.9.0')

### module_load
Load one or more environment modules.
- **modules**: List of module names to load

### module_unload
Unload one or more currently loaded modules.
- **modules**: List of module names to unload

### module_swap
Swap one module for another atomically.
- **old_module**: Module to unload
- **new_module**: Module to load in its place

### module_spider
Search the entire module tree comprehensively.
- **pattern** (optional): Search pattern

### module_save
Save the current set of loaded modules as a named collection.
- **collection_name**: Name for the saved collection

### module_restore
Restore a previously saved module collection.
- **collection_name**: Name of the collection to restore

### module_savelist
List all saved module collections.

## Example Usage

```python
# List loaded modules
result = await module_list()

# Search for Python modules
result = await module_avail(pattern="python*")

# Load specific modules
result = await module_load(modules=["gcc/11.2.0", "python/3.9.0"])

# Show module details
result = await module_show(module_name="python/3.9.0")

# Save current configuration
result = await module_save(collection_name="my_env")

# Restore saved configuration
result = await module_restore(collection_name="my_env")
```

## Requirements

- Python >= 3.10
- Lmod installed and available in PATH
- Access to a system with environment modules

## Notes

- The server requires Lmod to be installed on the system
- Module commands are executed in the server's environment
- Some operations may require appropriate permissions
- Module changes affect the server process environment