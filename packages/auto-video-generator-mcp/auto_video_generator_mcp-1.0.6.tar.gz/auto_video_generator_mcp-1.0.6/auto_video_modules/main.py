import sys
from mcp.server.fastmcp import FastMCP
from auto_video_modules.mcp_tools import (
    generate_auto_video_mcp,
    generate_auto_video_sync,
    generate_auto_video_async,
    get_task_status,
    list_all_tasks,
    cancel_task,
    get_system_status,
    get_available_voice_options,
    validate_input_parameters,
    get_generation_estimate,
    generate_srt_from_whisper_mcp,
    clip_video_by_srt_mcp
)
from auto_video_modules.ffmpeg_utils import check_gpu_acceleration
from auto_video_modules.motion_detection_utils import detect_video_motion, optimize_video_motion_params
from auto_video_modules.gpu_optimization_utils import get_system_performance_info, optimize_video_processing, benchmark_gpu_performance


def main():
    print("启动自动视频生成MCP服务器 v3.0...")
    print("服务器包含以下功能:")
    print("- 核心视频生成功能")
    print("- 配置获取工具")
    print("\n使用 get_all_available_tools 查看所有可用工具")
    print("服务器将以SSE方式运行")
    print("访问地址: http://localhost:8000/sse")
    mcp = FastMCP("auto-video-generator", log_level="INFO")
    # 注册MCP工具
    mcp.tool()(generate_auto_video_mcp)
    mcp.tool()(generate_auto_video_sync)
    mcp.tool()(generate_auto_video_async)
    mcp.tool()(get_task_status)
    mcp.tool()(list_all_tasks)
    mcp.tool()(cancel_task)
    mcp.tool()(check_gpu_acceleration)
    mcp.tool()(detect_video_motion)
    mcp.tool()(optimize_video_motion_params)
    mcp.tool()(get_system_performance_info)
    mcp.tool()(optimize_video_processing)
    mcp.tool()(benchmark_gpu_performance)
    mcp.tool()(generate_srt_from_whisper_mcp)
    mcp.tool()(clip_video_by_srt_mcp)
    mcp.run(transport='sse')

if __name__ == "__main__":
    main() 