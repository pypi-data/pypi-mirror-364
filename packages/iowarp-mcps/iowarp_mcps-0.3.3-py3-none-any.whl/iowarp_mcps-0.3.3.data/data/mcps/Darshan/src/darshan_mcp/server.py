#!/usr/bin/env python3
"""
Darshan MCP Server for analyzing I/O profiler trace files.
Provides tools to load, explore, and analyze Darshan log files to understand I/O patterns and performance.
"""
import os
import sys
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from darshan_mcp.capabilities import darshan_parser

# Initialize MCP server
mcp = FastMCP("DarshanMCP")

@mcp.tool(
    name="load_darshan_log",
    description="Load and parse a Darshan log file to extract I/O performance metrics and metadata. Returns basic information about the trace file including job details, file access patterns, and available modules."
)
async def load_darshan_log_tool(log_file_path: str) -> dict:
    """
    Load and parse a Darshan log file.
    
    Args:
        log_file_path: Absolute path to the Darshan log file (.darshan format)
        
    Returns:
        dict: Basic log information including job metadata, modules, and file summary
    """
    return await darshan_parser.load_darshan_log(log_file_path)

@mcp.tool(
    name="get_job_summary",
    description="Get comprehensive job-level summary from a loaded Darshan log including execution time, number of processes, total I/O volume, and performance metrics."
)
async def get_job_summary_tool(log_file_path: str) -> dict:
    """
    Get job-level summary information.
    
    Args:
        log_file_path: Path to the Darshan log file
        
    Returns:
        dict: Job summary with runtime, process count, I/O statistics, and performance metrics
    """
    return await darshan_parser.get_job_summary(log_file_path)

@mcp.tool(
    name="analyze_file_access_patterns",
    description="Analyze file access patterns from the trace including which files were accessed, access types (read/write), sequential vs random access patterns, and file size distributions."
)
async def analyze_file_access_patterns_tool(log_file_path: str, file_pattern: Optional[str] = None) -> dict:
    """
    Analyze file access patterns.
    
    Args:
        log_file_path: Path to the Darshan log file
        file_pattern: Optional pattern to filter files (e.g., '*.dat', '/path/to/files/*')
        
    Returns:
        dict: File access analysis including access types, patterns, and statistics
    """
    return await darshan_parser.analyze_file_access_patterns(log_file_path, file_pattern)

@mcp.tool(
    name="get_io_performance_metrics",
    description="Extract detailed I/O performance metrics including bandwidth, IOPS, average request sizes, and timing information for read and write operations."
)
async def get_io_performance_metrics_tool(log_file_path: str) -> dict:
    """
    Get I/O performance metrics.
    
    Args:
        log_file_path: Path to the Darshan log file
        
    Returns:
        dict: Detailed I/O performance metrics and statistics
    """
    return await darshan_parser.get_io_performance_metrics(log_file_path)

@mcp.tool(
    name="analyze_posix_operations",
    description="Analyze POSIX I/O operations from the trace including read/write system calls, file operations (open, close, seek), and their frequency and timing patterns."
)
async def analyze_posix_operations_tool(log_file_path: str) -> dict:
    """
    Analyze POSIX I/O operations.
    
    Args:
        log_file_path: Path to the Darshan log file
        
    Returns:
        dict: POSIX operations analysis with call counts, timing, and patterns
    """
    return await darshan_parser.analyze_posix_operations(log_file_path)

@mcp.tool(
    name="analyze_mpiio_operations",
    description="Analyze MPI-IO operations if present in the trace, including collective vs independent operations, file view usage, and MPI-IO specific performance metrics."
)
async def analyze_mpiio_operations_tool(log_file_path: str) -> dict:
    """
    Analyze MPI-IO operations.
    
    Args:
        log_file_path: Path to the Darshan log file
        
    Returns:
        dict: MPI-IO operations analysis including collective operations and performance
    """
    return await darshan_parser.analyze_mpiio_operations(log_file_path)

@mcp.tool(
    name="identify_io_bottlenecks",
    description="Identify potential I/O performance bottlenecks by analyzing access patterns, file system usage, small vs large I/O operations, and synchronization patterns."
)
async def identify_io_bottlenecks_tool(log_file_path: str) -> dict:
    """
    Identify I/O performance bottlenecks.
    
    Args:
        log_file_path: Path to the Darshan log file
        
    Returns:
        dict: Analysis of potential bottlenecks with recommendations
    """
    return await darshan_parser.identify_io_bottlenecks(log_file_path)

@mcp.tool(
    name="get_timeline_analysis",
    description="Generate timeline analysis showing I/O activity over time, including peak I/O periods, idle times, and temporal patterns in file access."
)
async def get_timeline_analysis_tool(log_file_path: str, time_resolution: str = "1s") -> dict:
    """
    Generate timeline analysis of I/O activity.
    
    Args:
        log_file_path: Path to the Darshan log file
        time_resolution: Time resolution for timeline (e.g., '1s', '100ms', '10ms')
        
    Returns:
        dict: Timeline analysis with I/O activity over time
    """
    return await darshan_parser.get_timeline_analysis(log_file_path, time_resolution)

@mcp.tool(
    name="compare_darshan_logs",
    description="Compare two Darshan log files to identify differences in I/O patterns, performance changes, and behavioral variations between different runs or configurations."
)
async def compare_darshan_logs_tool(log_file_1: str, log_file_2: str, comparison_metrics: List[str] = None) -> dict:
    """
    Compare two Darshan log files.
    
    Args:
        log_file_1: Path to the first Darshan log file
        log_file_2: Path to the second Darshan log file  
        comparison_metrics: List of metrics to compare (default: ['bandwidth', 'iops', 'file_count'])
        
    Returns:
        dict: Comparison analysis showing differences and similarities
    """
    if comparison_metrics is None:
        comparison_metrics = ['bandwidth', 'iops', 'file_count']
    return await darshan_parser.compare_darshan_logs(log_file_1, log_file_2, comparison_metrics)

@mcp.tool(
    name="generate_io_summary_report",
    description="Generate a comprehensive I/O summary report combining all analysis results into a human-readable format with key findings, performance insights, and recommendations."
)
async def generate_io_summary_report_tool(log_file_path: str, include_visualizations: bool = False) -> dict:
    """
    Generate comprehensive I/O summary report.
    
    Args:
        log_file_path: Path to the Darshan log file
        include_visualizations: Whether to include visualization data in the report
        
    Returns:
        dict: Comprehensive summary report with key findings and recommendations
    """
    return await darshan_parser.generate_io_summary_report(log_file_path, include_visualizations)

def main():
    """Main entry point for the server."""
    import asyncio
    
    # Run the FastMCP server
    asyncio.run(mcp.run())

if __name__ == "__main__":
    main()