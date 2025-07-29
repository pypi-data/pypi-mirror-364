# Darshan MCP Server

The Darshan MCP server provides comprehensive analysis tools for Darshan I/O profiler trace files. It allows AI agents to explore, analyze, and extract insights from I/O performance data collected during HPC application runs.

## Features

- **Load and parse Darshan logs**: Extract metadata and basic information from .darshan files
- **Job-level analysis**: Get comprehensive job summaries with runtime and I/O statistics
- **File access pattern analysis**: Understand how applications access files (sequential vs random, read vs write)
- **I/O performance metrics**: Calculate bandwidth, IOPS, and request size statistics
- **POSIX and MPI-IO analysis**: Analyze system call patterns and MPI-IO operations
- **Bottleneck identification**: Automatically identify potential performance issues
- **Timeline analysis**: Understand I/O activity over time
- **Log comparison**: Compare multiple trace files to identify performance changes
- **Comprehensive reporting**: Generate detailed I/O analysis reports

## Installation

```bash
# Install the MCP server
uv pip install "git+https://github.com/iowarp/scientific-mcps.git@main#subdirectory=Darshan"

# Or install from local directory
cd Darshan
uv pip install -e .
```

## Running the Server

After installation, you can run the server using:

```bash
uv run darshan-mcp
```

Or if installed globally:

```bash
darshan-mcp
```

## Prerequisites

- **Darshan tools**: The server requires `darshan-parser` to be installed and available in PATH
- **Python libraries**: numpy, pandas, matplotlib for analysis and visualization
- **Darshan log files**: .darshan format trace files from instrumented applications

## Available Tools

### load_darshan_log
Load and parse a Darshan log file to extract basic information.
- **log_file_path**: Absolute path to the .darshan log file

```json
{
  "success": true,
  "log_file": "/path/to/trace.darshan",
  "job_info": {"job_id": "12345", "nprocs": 64},
  "modules": ["POSIX", "MPIIO", "STDIO"],
  "file_count": 42
}
```

### get_job_summary
Get comprehensive job-level summary including runtime and I/O statistics.
- **log_file_path**: Path to the Darshan log file

### analyze_file_access_patterns
Analyze how files were accessed during the job.
- **log_file_path**: Path to the Darshan log file
- **file_pattern** (optional): Filter files by pattern (e.g., '*.dat', '/scratch/*')

### get_io_performance_metrics
Extract detailed I/O performance metrics including bandwidth and IOPS.
- **log_file_path**: Path to the Darshan log file

### analyze_posix_operations
Analyze POSIX system call patterns (open, read, write, seek, etc.).
- **log_file_path**: Path to the Darshan log file

### analyze_mpiio_operations
Analyze MPI-IO operations including collective vs independent I/O.
- **log_file_path**: Path to the Darshan log file

### identify_io_bottlenecks
Automatically identify potential I/O performance bottlenecks.
- **log_file_path**: Path to the Darshan log file

### get_timeline_analysis
Generate timeline analysis of I/O activity over time.
- **log_file_path**: Path to the Darshan log file
- **time_resolution**: Time resolution for analysis (e.g., '1s', '100ms')

### compare_darshan_logs
Compare two Darshan log files to identify performance differences.
- **log_file_1**: Path to the first log file
- **log_file_2**: Path to the second log file
- **comparison_metrics**: List of metrics to compare ['bandwidth', 'iops', 'file_count']

### generate_io_summary_report
Generate a comprehensive I/O analysis report.
- **log_file_path**: Path to the Darshan log file
- **include_visualizations**: Whether to include visualization data

## Example Usage

```python
# Load a Darshan log file
result = await load_darshan_log("/path/to/application.darshan")

# Get job summary
summary = await get_job_summary("/path/to/application.darshan")
print(f"Job ran for {summary['runtime_seconds']} seconds")
print(f"Total I/O: {summary['total_io_volume']} bytes")

# Analyze file access patterns
patterns = await analyze_file_access_patterns("/path/to/application.darshan")
print(f"Found {patterns['read_only_files']} read-only files")
print(f"Found {patterns['sequential_access']} files with sequential access")

# Get performance metrics
metrics = await get_io_performance_metrics("/path/to/application.darshan")
print(f"Read bandwidth: {metrics['read_metrics']['bandwidth_mbps']} MB/s")
print(f"Write bandwidth: {metrics['write_metrics']['bandwidth_mbps']} MB/s")

# Identify bottlenecks
bottlenecks = await identify_io_bottlenecks("/path/to/application.darshan")
for issue in bottlenecks['identified_issues']:
    print(f"Issue: {issue['description']}")

# Compare two runs
comparison = await compare_darshan_logs(
    "/path/to/run1.darshan", 
    "/path/to/run2.darshan",
    ["bandwidth", "iops"]
)

# Generate comprehensive report
report = await generate_io_summary_report("/path/to/application.darshan")
```

## Understanding Darshan Data

Darshan logs contain rich information about I/O behavior:

- **Job metadata**: Process count, runtime, user information
- **File access data**: Which files were accessed, when, and how
- **I/O operations**: Read/write counts, sizes, and timing
- **Access patterns**: Sequential vs random, collective vs independent
- **Performance metrics**: Bandwidth, IOPS, request sizes

## Common Analysis Workflows

1. **Performance Assessment**: Load log → Get job summary → Analyze performance metrics
2. **Bottleneck Investigation**: Identify bottlenecks → Analyze access patterns → Review POSIX/MPI-IO operations
3. **Optimization Validation**: Compare logs before/after optimization
4. **Application Profiling**: Generate comprehensive report for detailed analysis

## Notes

- Requires Darshan-utils to be installed on the system
- Log files must be in .darshan format (not .darshan.gz)
- Large log files may take time to process
- Some analyses require specific modules to be present in the log
- Timeline analysis requires timestamp data which may not be available in all Darshan versions