# Understanding Python .pth Files

## What is a .pth file?

A `.pth` (path configuration) file is a special file that Python uses to add additional directories to `sys.path` - the list of directories Python searches when importing modules.

## Key Characteristics

1. **Location**: Must be placed in a site-packages directory
2. **Format**: Simple text file with one directory path per line
3. **Extension**: Must end with `.pth`
4. **Processing**: Python reads these files at startup automatically

## How it works

When Python starts, it:
1. Scans site-packages directories for `.pth` files
2. Reads each `.pth` file
3. Adds valid directory paths to `sys.path`
4. Ignores comments (lines starting with #) and blank lines

## Example

If you have a file `/usr/lib/python3.11/site-packages/myproject.pth` containing:
```
/home/user/my_project/src
/home/user/another_project
```

Python will add both directories to `sys.path`, allowing you to import modules from those locations.

## Common Uses

1. **Editable Installs**: When you run `uv pip install -e .` (or `pip install -e .`), it creates a `.pth` file pointing to your development directory
2. **Virtual Environments**: Tools use `.pth` files to include additional packages
3. **Development**: Manually add development paths without modifying PYTHONPATH

## In Your Case

When you ran `uv pip install -e .` in your project, uv created the file `_mcp_logger_utils.pth` in your virtual environment's site-packages directory. However, this file was empty (0 bytes), which is why imports failed. 

It should have contained:
```
/home/graham/workspace/experiments/mcp-logger-utils/src
```

This tells Python: "When looking for the mcp_logger_utils package, also check this directory."

This appears to be a bug in the build system where the `.pth` file was created but not properly populated with the source directory path.

## Advantages over PYTHONPATH

- Persistent: Survives shell restarts
- Scoped: Only affects the specific Python environment
- Automatic: No need to set environment variables
- Package-specific: Each package can have its own `.pth` file

## Important Notes

- Only works for directories listed in `sys.path` (like site-packages)
- Processed in alphabetical order
- Can include Python code (lines starting with `import`), but this is discouraged
- Empty `.pth` files do nothing (which was your issue)