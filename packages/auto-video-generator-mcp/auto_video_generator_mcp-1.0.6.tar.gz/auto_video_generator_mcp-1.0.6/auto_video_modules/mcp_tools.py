"""
MCP工具模块
负责整合所有模块功能，提供完整的视频生成服务
"""

import os
import asyncio
from mcp.server.fastmcp import FastMCP
import json
import subprocess
from typing import Any, Dict, Optional
import uuid
from datetime import datetime
import cv2
import numpy as np

# 导入各个模块
from .ffmpeg_utils import setup_ffmpeg, get_mcp_instance as get_ffmpeg_mcp
from .voice_utils import get_voice_by_index, get_mcp_instance as get_voice_mcp
from .audio_utils import synthesize_and_get_durations, get_mcp_instance as get_audio_mcp
from .subtitle_utils import split_text, create_subtitle_image, get_mcp_instance as get_subtitle_mcp
from .video_utils import create_video_with_subtitles, get_mcp_instance as get_video_mcp

# 创建主MCP实例
mcp = FastMCP("auto-video-generator", log_level="ERROR")

# 任务状态管理
task_status = {}

class VideoGenerationTask:
    """视频生成任务类"""
    def __init__(self, task_id: str, params: Dict):
        self.task_id = task_id
        self.params = params
        self.status = "pending"  # pending, running, completed, failed
        self.progress = 0
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.created_at = datetime.now()

def cleanup_temp_files(temp_files):
    """清理临时文件
    
    Args:
        temp_files: 临时文件路径列表
    """
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"清理临时文件: {file_path}")
        except Exception as e:
            print(f"清理临时文件失败 {file_path}: {e}")

async def generate_video_with_subtitles(text, video_path, voice_index=0, output_path="output_video.mp4"):
    """生成带字幕的视频
    
    Args:
        text: 要转换的文本
        video_path: 视频文件路径
        voice_index: 语音音色索引
        output_path: 输出视频路径
        
    Returns:
        bool: 是否成功
    """
    try:
        # 设置FFmpeg
        setup_ffmpeg()
        
        # 获取语音音色
        voice = get_voice_by_index(voice_index)
        
        # 检查文本是否包含时间标记
        import re
        time_pattern = r'\{(\d+(?:\.\d+)?)(s|ms)\}'
        has_timing = bool(re.search(time_pattern, text))
        
        if has_timing:
            # 包含时间标记，使用split_timings处理
            from .subtitle_utils import split_timings
            # 创建初始timing结构
            initial_timing = [{"text": text, "duration": 0}]
            # 使用split_timings进行智能分割，包含时间标记解析
            timing = split_timings(initial_timing, max_chars=20)
        else:
            # 不包含时间标记，使用原有的split_text
            text_segments = split_text(text)
            timing = [{"text": seg} for seg in text_segments]
        
        # 生成音频和获取时长
        from .audio_utils import synthesize_and_get_durations
        tts_result = await synthesize_and_get_durations(timing, voice)
        audio_path = tts_result["audio_path"]
        segments = tts_result["segments"]
        
        # 创建字幕图片
        subtitle_images = []
        for i, segment in enumerate(timing):
            image_path = f"temp_subtitle_{i}.png"
            from .video_utils import create_subtitle_image_pil
            image_path = create_subtitle_image_pil(
                segment["text"], 
                fontsize=40, 
                color='white', 
                font_path=r"C:\Windows\Fonts\msyh.ttc",  # 使用微软雅黑
                size=(1920, 1080),
                bg_color=(0,0,0,0),
                subtitle_height=100
            )
            subtitle_images.append(image_path)
        
        # 创建带字幕的视频
        # 生成 (text, start, end) 三元组列表
        subtitle_tuples = []
        cur_time = 0.0
        for seg in segments:
            text = seg["text"]
            duration = seg.get("duration", 0)
            start = cur_time
            end = cur_time + duration
            subtitle_tuples.append((text, start, end))
            cur_time = end
        success = create_video_with_subtitles(video_path, audio_path, subtitle_tuples, output_path)
        
        # 清理临时文件
        temp_files = [audio_path] + subtitle_images
        cleanup_temp_files(temp_files)
        
        return success
        
    except Exception as e:
        print(f"生成视频失败: {e}")
        return False

@mcp.tool()
async def generate_auto_video(
    video_path: str, 
    text: str = "", 
    voice_index: int = 0, 
    output_path: str = "output_video.mp4",
    segments_mode: str = "keep",
    segments: str = "",
    subtitle_style: str = "",
    auto_split_config: str = "",
    quality_preset: str = "720p",
    enable_motion_clip: bool = False,
    motion_clip_params: Optional[dict] = None,
    enable_gpu_acceleration: bool = False,
    gpu_type: str = "auto"
) -> str:
    """
    新增：enable_motion_clip, motion_clip_params
    """
    try:
        import json
        # 运动检测逻辑
        if enable_motion_clip:
            print("[自动检测] 启用帧间运动量自动剪辑...")
            from .motion_detection_utils import detect_static_segments_by_motion, to_timestamp, load_motion_config
            
            # 加载配置参数
            if motion_clip_params:
                # 使用传入的参数
                params = motion_clip_params
            else:
                # 使用配置文件中的参数
                config = load_motion_config()
                params = {
                    "motion_threshold": config.motion_threshold,
                    "min_static_duration": config.min_static_duration,
                    "sample_step": config.sample_step
                }
            
            static_segments = await detect_static_segments_by_motion(
                video_path,
                motion_threshold=params.get("motion_threshold", 0.1),
                min_static_duration=params.get("min_static_duration", 2.0),
                sample_step=params.get("sample_step", 1)
            )
            print(f"[自动检测] 检测到静止片段 {len(static_segments)} 个")
            segments_list = [seg.to_dict() for seg in static_segments]
            segments = json.dumps([{ "start": to_timestamp(s["start"]), "end": to_timestamp(s["end"])} for s in segments_list])
            segments_mode = "cut"
        
        # 验证输入参数
        if not os.path.exists(video_path):
            return f"错误：视频文件不存在: {video_path}"
        
        if voice_index < 0 or voice_index > 4:
            return "错误：语音音色索引无效，有效范围为 0-4"
        
        # 验证画质预设
        valid_qualities = ["240p", "360p", "480p", "720p", "1080p"]
        if quality_preset.lower() not in [q.lower() for q in valid_qualities]:
            return f"错误：不支持的画质预设: {quality_preset}，支持: {valid_qualities}"
        
        print(f"使用画质预设: {quality_preset}")
        
        # 解析segments_mode
        if segments_mode not in ["keep", "cut", "audio"]:
            return "错误：segments_mode 参数无效，支持 'keep'、'cut' 或 'audio'"
        
        # 解析segments配置
        segments_list = []
        if segments:
            try:
                segments_list = json.loads(segments)
                if not isinstance(segments_list, list):
                    return "错误：segments 参数格式错误，应为JSON数组"
            except json.JSONDecodeError:
                return "错误：segments 参数JSON格式错误"
        
        # 解析subtitle_style配置
        from .subtitle_utils import normalize_subtitle_style
        subtitle_config = normalize_subtitle_style(subtitle_style)
        
        # 解析auto_split_config配置
        split_config = {}
        if auto_split_config:
            try:
                split_config = json.loads(auto_split_config)
                if not isinstance(split_config, dict):
                    return "错误：auto_split_config 参数格式错误，应为JSON对象"
            except json.JSONDecodeError:
                return "错误：auto_split_config 参数JSON格式错误"
        else:
            # 默认开启智能分割
            from .config import get_config
            config = get_config()
            auto_split_default = config.get_auto_split_config()
            split_config = {
                "enabled": True,
                "maxLength": auto_split_default.max_length,
                "minLength": auto_split_default.min_length,
                "splitChars": auto_split_default.split_chars,
                "preservePunctuation": auto_split_default.preserve_punctuation
            }
        
        # 设置FFmpeg
        setup_ffmpeg()
        
        # 获取视频信息
        from .video_utils import get_video_info
        video_info = get_video_info(video_path)
        
        # 处理视频片段剪辑
        clipped_video_path = video_path  # 默认使用原视频
        if segments_mode == "audio":
            from .video_utils import detect_audio_active_segments
            print("[音频剪辑] 启用音频活动检测模式...")
            segments_list = detect_audio_active_segments(video_path)
            print(f"[音频剪辑] 有音频区间: {segments_list}")
            if not segments_list:
                print("[音频剪辑] 未检测到有音频的区间，输出空视频。")
                # 可选：生成空白视频或直接返回
                return "未检测到有音频的区间，未生成输出。"
        if segments_list:
            from .video_utils import parse_video_segments, clip_video_segments
            video_duration = video_info.get('duration', 0)
            keep_intervals = parse_video_segments(segments_list, video_duration, segments_mode)
            # 执行视频剪辑
            try:
                print(f"开始视频片段剪辑 - 模式: {segments_mode}, 片段数: {len(segments_list)}")
                final_clip = clip_video_segments(video_path, keep_intervals)
                # 保存剪辑后的视频到临时文件
                clipped_video_path = "temp_clipped_video.mp4"
                final_clip.write_videofile(clipped_video_path, codec='libx264', fps=24, audio=True)
                final_clip.close()
                print(f"视频剪辑完成，保存到: {clipped_video_path}")
                # 更新视频信息
                from .video_utils import get_video_info
                video_info = get_video_info(clipped_video_path)
            except Exception as e:
                print(f"视频剪辑失败，使用原视频: {e}")
                clipped_video_path = video_path
        else:
            print("未指定视频片段，使用全部视频内容")
        
        # 检查是否有文本需要处理
        has_text = text and text.strip()
        
        if has_text:
            # 有文本时，进行文本转语音和字幕处理
            print("检测到文本内容，开始文本转语音处理...")
            
            # 获取语音音色
            voice = get_voice_by_index(voice_index)
            
            # 智能分割文本
            if split_config.get("enabled", True):
                from .subtitle_utils import split_timings
                # 创建初始timing结构
                initial_timing = [{"text": text, "duration": 0}]
                timing = split_timings(
                    initial_timing,
                    max_chars=split_config.get("maxLength", 50),
                    min_chars=split_config.get("minLength", 5)
                )
                print(f"智能分割完成，共生成 {len(timing)} 个片段")
            else:
                # 不分割，整个文本作为一个片段
                timing = [{"text": text, "duration": 0}]
                print("智能分割已关闭，使用完整文本")
            
            # 生成音频和获取时长
            from .audio_utils import synthesize_and_get_durations
            tts_result = await synthesize_and_get_durations(timing, voice)
            audio_path = tts_result["audio_path"]
            segments_with_duration = tts_result["segments"]
            
            # 创建字幕图片
            subtitle_images = []
            
            # 获取默认字幕配置和画质配置
            from .config import get_config
            config = get_config()
            subtitle_config_default = config.get_subtitle_config()
            video_config = config.get_video_config()
            
            # 获取目标分辨率
            target_width, target_height = video_config.get_resolution_by_quality(quality_preset)
            print(f"目标分辨率: {target_width}x{target_height}")
            
            # 使用配置中的默认值，如果用户提供了自定义配置则覆盖
            font_path = subtitle_config.get('fontPath', subtitle_config_default.font_path)
            font_size = subtitle_config.get('fontSize', subtitle_config_default.font_size)
            color = subtitle_config.get('color', subtitle_config_default.font_color)
            bg_color = tuple(subtitle_config.get('bgColor', subtitle_config_default.bg_color))
            margin_x = subtitle_config.get('marginX', subtitle_config_default.margin_x)
            margin_bottom = subtitle_config.get('marginBottom', subtitle_config_default.margin_bottom)
            subtitle_height = subtitle_config.get('height', 100)
            
            # 使用segments_with_duration生成字幕图片，确保与音频同步
            for i, segment in enumerate(segments_with_duration):
                # 跳过空白静默片段，不生成字幕图片
                if not segment["text"].strip():
                    subtitle_images.append(None)  # 标记为静默片段
                    continue
                    
                # 使用create_subtitle_image_pil生成numpy数组
                from .video_utils import create_subtitle_image_pil
                img_array = create_subtitle_image_pil(
                    segment["text"], 
                    fontsize=font_size, 
                    color=color, 
                    font_path=font_path,
                    size=(target_width, target_height),
                    bg_color=bg_color,
                    subtitle_height=subtitle_height
                )
                subtitle_images.append(img_array)
            
            # 创建带字幕的视频
            # 生成 (text, start, end) 三元组列表
            subtitle_tuples = []
            cur_time = 0.0
            for seg in segments_with_duration:
                text = seg["text"]
                duration = seg.get("duration", 0)
                start = cur_time
                end = cur_time + duration
                subtitle_tuples.append((text, start, end))
                cur_time = end
            
            # 创建视频（传递画质配置）
            success = create_video_with_subtitles(clipped_video_path, audio_path, subtitle_tuples, output_path, subtitle_config, subtitle_images, quality_preset)
            
            # 清理临时文件
            temp_files = [audio_path]
            if clipped_video_path != video_path and os.path.exists(clipped_video_path):
                temp_files.append(clipped_video_path)
            cleanup_temp_files(temp_files)
            
        else:
            # 没有文本时，只进行视频处理（剪辑、画质调整等）
            # 【修正】无字幕时，始终保留原视频音频，不做任何去除或替换
            print("未检测到文本内容，仅进行视频处理，保留原视频音频...")
            
            # 获取画质配置
            from .config import get_config
            config = get_config()
            video_config = config.get_video_config()
            
            # 如果指定了画质预设，则应用画质配置
            if quality_preset:
                video_config.set_quality(quality_preset)
                print(f"应用画质配置: {quality_preset}")
            
            # 获取目标分辨率和比特率
            target_width, target_height = video_config.get_resolution_by_quality()
            target_bitrate = video_config.get_bitrate_by_quality()
            
            print(f"目标分辨率: {target_width}x{target_height}")
            print(f"目标比特率: {target_bitrate}")
            
            # 使用ffmpeg直接处理视频，保留原音频
            from .ffmpeg_utils import check_ffmpeg, get_gpu_encoder
            ffmpeg_path, _ = check_ffmpeg()
            
            try:
                if enable_gpu_acceleration:
                    gpu_encoder = get_gpu_encoder(quality_preset, gpu_type)
                    if gpu_encoder:
                        video_codec = gpu_encoder
                        print(f"[GPU加速] 使用编码器: {gpu_encoder}")
                    else:
                        video_codec = "libx264"
                        print("[GPU加速] 未检测到可用GPU编码器，使用CPU编码器: libx264")
                else:
                    video_codec = "libx264"
                    print("使用CPU编码器: libx264")
                
                cmd = [
                    ffmpeg_path, "-y",
                    "-i", clipped_video_path,
                    "-c:v", video_codec,
                    "-b:v", target_bitrate,
                    "-s", f"{target_width}x{target_height}",
                    "-c:a", "copy",  # 保持原音频
                    output_path
                ]
                import subprocess
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"视频处理完成: {output_path}")
                success = True
            except Exception as e:
                print(f"[视频处理] 失败: {e}")
                success = False
        
        if success:
            # 获取输出视频信息
            output_info = get_video_info(output_path)
            absolute_output_path = os.path.abspath(output_path)
            
            # 构建结果信息
            result = {
                "status": "success",
                "message": "视频生成成功",
                "video_info": video_info,
                "output_info": output_info,
                "absolute_output_path": absolute_output_path,
                "config_used": {
                    "segments_mode": segments_mode,
                    "segments_count": len(segments_list),
                    "subtitle_style": subtitle_config,
                    "auto_split_config": split_config,
                    "quality_preset": quality_preset,
                    "has_text": has_text
                }
            }
            
            # 如果有文本处理，添加文本相关信息
            if has_text:
                result["input_text_length"] = len(text)
                result["text_segments"] = len(timing) if 'timing' in locals() else 1
                result["audio_segments"] = len(segments_with_duration) if 'segments_with_duration' in locals() else 0
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return "错误：视频生成失败"
        
    except Exception as e:
        return f"错误：生成视频时发生异常 - {str(e)}"

@mcp.tool()
async def get_system_status() -> str:
    """获取系统状态信息
    
    Returns:
        系统状态信息
    """
    try:
        # 检查FFmpeg
        try:
            setup_ffmpeg()
            ffmpeg_status = "FFmpeg: 正常"
        except Exception as e:
            ffmpeg_status = f"FFmpeg: 异常 - {str(e)}"
        
        # 检查语音音色
        voice_status = f"语音音色: 可用 {len(get_voice_by_index(0))} 种"
        
        # 检查输出目录
        output_dir = os.getcwd()
        output_status = f"输出目录: {output_dir}"
        
        return f"""系统状态检查:

{ffmpeg_status}
{voice_status}
{output_status}

模块状态:
- FFmpeg工具: 正常
- 语音工具: 正常
- 音频工具: 正常
- 字幕工具: 正常
- 视频工具: 正常

系统准备就绪，可以开始生成视频！"""
        
    except Exception as e:
        return f"系统状态检查失败: {str(e)}"

@mcp.tool()
async def get_available_voice_options() -> str:
    """获取可用的语音选项
    
    Returns:
        可用的语音选项信息
    """
    try:
        voices = []
        for i in range(5):
            voice_name = get_voice_by_index(i)
            gender = "女声" if i in [0, 2, 3] else "男声"
            voices.append(f"{i}: {voice_name} ({gender})")
        
        return f"""可用的语音音色选项:

{chr(10).join(voices)}

使用说明:
- 0: 女声小晓 (推荐)
- 1: 男声云扬
- 2: 女声小艺
- 3: 女声云希
- 4: 男声云健

选择建议:
- 正式内容推荐使用女声 (0, 2, 3)
- 新闻播报推荐使用男声 (1, 4)
- 默认推荐使用索引 0"""
        
    except Exception as e:
        return f"获取语音选项失败: {str(e)}"

@mcp.tool()
async def validate_input_parameters(text: str, video_path: str, voice_index: int = 0) -> str:
    """验证输入参数
    
    Args:
        text: 要转换的文本
        video_path: 视频文件路径
        voice_index: 语音音色索引
        
    Returns:
        验证结果
    """
    try:
        errors = []
        warnings = []
        
        # 验证文本
        if not text or not text.strip():
            errors.append("文本内容不能为空")
        elif len(text) > 1000:
            warnings.append("文本内容较长，处理时间可能较长")
        
        # 验证视频文件
        if not os.path.exists(video_path):
            errors.append(f"视频文件不存在: {video_path}")
        else:
            file_size = os.path.getsize(video_path)
            if file_size > 100 * 1024 * 1024:  # 100MB
                warnings.append("视频文件较大，处理时间可能较长")
        
        # 验证语音音色
        if voice_index < 0 or voice_index > 4:
            errors.append("语音音色索引无效，有效范围为 0-4")
        
        # 生成结果
        if errors:
            return f"验证失败:\n" + "\n".join([f"- {error}" for error in errors])
        
        result = "验证通过！"
        if warnings:
            result += "\n\n警告:\n" + "\n".join([f"- {warning}" for warning in warnings])
        
        return result
        
    except Exception as e:
        return f"参数验证出错: {str(e)}"

@mcp.tool()
async def get_generation_estimate(text: str, video_path: str) -> str:
    """获取生成时间估算
    
    Args:
        text: 要转换的文本
        video_path: 视频文件路径
        
    Returns:
        时间估算信息
    """
    try:
        # 文本长度估算
        text_length = len(text)
        from .subtitle_utils import split_text
        text_segments = len(split_text(text))
        
        # 视频时长估算
        video_duration = 0.0
        if os.path.exists(video_path):
            try:
                from .video_utils import get_video_info
                info = get_video_info(video_path)
                if "error" not in info and isinstance(info.get('duration'), (int, float)):
                    video_duration = float(info['duration'])
            except:
                pass
        
        # 时间估算
        tts_time = text_length * 0.1  # 每字符0.1秒
        video_time = video_duration * 0.5  # 视频处理时间
        total_time = tts_time + video_time + 30  # 额外30秒缓冲
        
        return f"""生成时间估算:

输入信息:
- 文本长度: {text_length} 字符
- 文本片段: {text_segments} 个
- 视频时长: {video_duration:.1f} 秒

时间估算:
- 文本转语音: {tts_time:.1f} 秒
- 视频处理: {video_time:.1f} 秒
- 总估算时间: {total_time:.1f} 秒 ({total_time/60:.1f} 分钟)

注意事项:
- 实际时间可能因系统性能而异
- 大文件处理时间可能更长
- 建议在生成期间不要关闭程序"""
        
    except Exception as e:
        return f"时间估算失败: {str(e)}"

def get_mcp_instance():
    """获取MCP实例
    
    Returns:
        FastMCP: MCP实例
    """
    return mcp

def get_all_mcp_instances():
    """获取所有模块的MCP实例
    
    Returns:
        dict: 所有MCP实例
    """
    return {
        "main": mcp,
        "ffmpeg": get_ffmpeg_mcp(),
        "voice": get_voice_mcp(),
        "audio": get_audio_mcp(),
        "subtitle": get_subtitle_mcp(),
        "video": get_video_mcp()
    }

@mcp.tool()
async def generate_auto_video_mcp(
    video_path: Any, 
    text: Any = "", 
    voice_index: Any = 0, 
    output_path: Any = "output_video.mp4",
    segments_mode: Any = "keep",
    segments: Any = "",
    subtitle_style: Any = "",
    auto_split_config: Any = "",
    quality_preset: Any = "720p",
    enable_motion_clip: Any = False,
    motion_clip_params: Any = None
) -> str:
    import json
    if not isinstance(segments, str):
        segments = json.dumps(segments, ensure_ascii=False)
    if not isinstance(subtitle_style, str):
        subtitle_style = json.dumps(subtitle_style, ensure_ascii=False)
    if not isinstance(auto_split_config, str):
        auto_split_config = json.dumps(auto_split_config, ensure_ascii=False)
    return await create_video_generation_task(
        video_path, text, voice_index, output_path,
        segments_mode, segments, subtitle_style, auto_split_config, quality_preset,
        enable_motion_clip, motion_clip_params
    )

async def create_video_generation_task(
    video_path: str, 
    text: str = "", 
    voice_index: int = 0, 
    output_path: str = "output_video.mp4",
    segments_mode: str = "keep",
    segments: str = "",
    subtitle_style: str = "",
    auto_split_config: str = "",
    quality_preset: str = "720p",
    enable_motion_clip: bool = False,
    motion_clip_params: Optional[dict] = None
) -> str:
    """创建视频生成任务（异步）"""
    task_id = str(uuid.uuid4())
    
    task = VideoGenerationTask(task_id, {
        "video_path": video_path,
        "text": text,
        "voice_index": voice_index,
        "output_path": output_path,
        "segments_mode": segments_mode,
        "segments": segments,
        "subtitle_style": subtitle_style,
        "auto_split_config": auto_split_config,
        "quality_preset": quality_preset,
        "enable_motion_clip": enable_motion_clip,
        "motion_clip_params": motion_clip_params
    })
    
    task_status[task_id] = task
    
    # 启动异步任务
    asyncio.create_task(run_video_generation_task(task))
    
    return json.dumps({
        "task_id": task_id,
        "status": "created",
        "message": "视频生成任务已创建，请使用 get_task_status 查询进度"
    }, ensure_ascii=False)

async def run_video_generation_task(task: VideoGenerationTask):
    """运行视频生成任务"""
    try:
        task.status = "running"
        task.start_time = datetime.now()
        task.progress = 10
        
        # 执行视频生成
        result = await generate_auto_video(
            task.params["video_path"],
            task.params["text"],
            task.params["voice_index"],
            task.params["output_path"],
            task.params["segments_mode"],
            task.params["segments"],
            task.params["subtitle_style"],
            task.params["auto_split_config"],
            task.params["quality_preset"],
            task.params["enable_motion_clip"],
            task.params["motion_clip_params"]
        )
        
        task.progress = 100
        task.status = "completed"
        task.result = result
        task.end_time = datetime.now()
        
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.end_time = datetime.now()

@mcp.tool()
async def generate_auto_video_async(
    video_path: Any, 
    text: Any = "", 
    voice_index: Any = 0, 
    output_path: Any = "output_video.mp4",
    segments_mode: Any = "keep",
    segments: Any = "",
    subtitle_style: Any = "",
    auto_split_config: Any = "",
    quality_preset: Any = "720p",
    enable_motion_clip: Any = False,
    motion_clip_params: Any = None
) -> str:
    import json
    if not isinstance(segments, str):
        segments = json.dumps(segments, ensure_ascii=False)
    if not isinstance(subtitle_style, str):
        subtitle_style = json.dumps(subtitle_style, ensure_ascii=False)
    if not isinstance(auto_split_config, str):
        auto_split_config = json.dumps(auto_split_config, ensure_ascii=False)
    return await create_video_generation_task(
        video_path, text, voice_index, output_path,
        segments_mode, segments, subtitle_style, auto_split_config, quality_preset,
        enable_motion_clip, motion_clip_params
    )

@mcp.tool()
async def get_task_status(task_id: str) -> str:
    """获取任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
    """
    if task_id not in task_status:
        return json.dumps({
            "error": "任务不存在",
            "task_id": task_id
        }, ensure_ascii=False)
    
    task = task_status[task_id]
    
    result = {
        "task_id": task_id,
        "status": task.status,
        "progress": task.progress,
        "created_at": task.created_at.isoformat(),
        "start_time": task.start_time.isoformat() if task.start_time else None,
        "end_time": task.end_time.isoformat() if task.end_time else None
    }
    
    if task.status == "completed":
        result["result"] = task.result
    elif task.status == "failed":
        result["error"] = task.error
    
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
async def list_all_tasks() -> str:
    """列出所有任务
    
    Returns:
        所有任务列表
    """
    tasks = []
    for task_id, task in task_status.items():
        tasks.append({
            "task_id": task_id,
            "status": task.status,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "video_path": task.params.get("video_path", ""),
            "text_length": len(task.params.get("text", ""))
        })
    
    return json.dumps({
        "total_tasks": len(tasks),
        "tasks": tasks
    }, ensure_ascii=False, indent=2)

@mcp.tool()
async def cancel_task(task_id: str) -> str:
    """取消任务
    
    Args:
        task_id: 任务ID
        
    Returns:
        取消结果
    """
    if task_id not in task_status:
        return json.dumps({
            "error": "任务不存在",
            "task_id": task_id
        }, ensure_ascii=False)
    
    task = task_status[task_id]
    if task.status in ["completed", "failed"]:
        return json.dumps({
            "error": "任务已完成或失败，无法取消",
            "task_id": task_id,
            "status": task.status
        }, ensure_ascii=False)
    
    task.status = "cancelled"
    task.end_time = datetime.now()
    
    return json.dumps({
        "message": "任务已取消",
        "task_id": task_id
    }, ensure_ascii=False)

@mcp.tool()
async def generate_auto_video_sync(
    video_path: Any, 
    text: Any = "", 
    voice_index: Any = 0, 
    output_path: Any = "output_video.mp4",
    segments_mode: Any = "keep",
    segments: Any = "",
    subtitle_style: Any = "",
    auto_split_config: Any = "",
    quality_preset: Any = "720p",
    enable_motion_clip: Any = False,
    motion_clip_params: Any = None
) -> str:
    import json
    if not isinstance(segments, str):
        segments = json.dumps(segments, ensure_ascii=False)
    if not isinstance(subtitle_style, str):
        subtitle_style = json.dumps(subtitle_style, ensure_ascii=False)
    if not isinstance(auto_split_config, str):
        auto_split_config = json.dumps(auto_split_config, ensure_ascii=False)
    return await generate_auto_video(
        video_path, text, voice_index, output_path,
        segments_mode, segments, subtitle_style, auto_split_config, quality_preset,
        enable_motion_clip, motion_clip_params
    ) 

@mcp.tool()
async def generate_subtitles_from_audio(
    video_path: str,
    threshold: float = 0.01,
    min_duration: float = 1.0,
    step: float = 0.5
) -> str:
    """
    根据视频中的音频活动区间自动生成字幕list。
    Args:
        video_path: 视频文件路径
        threshold: 音量阈值（RMS），低于此值视为无音频
        min_duration: 最小保留区间（秒）
        step: 检测步长（秒）
    Returns:
        JSON字符串，格式为list[{text, start, end}]
    """
    from .video_utils import detect_audio_active_segments
    segments = detect_audio_active_segments(video_path, threshold, min_duration, step)
    # 生成字幕list，每个区间一条字幕，内容可自定义
    subtitle_list = [
        {"text": "（有音频）", "start": seg["start"], "end": seg["end"]}
        for seg in segments
    ]
    import json
    return json.dumps(subtitle_list, ensure_ascii=False, indent=2) 

@mcp.tool()
async def generate_subtitle_list_from_asr(
    video_path: str,
    language: str = "zh-CN"
) -> str:
    """
    对视频中的音频进行ASR识别，输出带时间戳的字幕list。
    Args:
        video_path: 视频文件路径
        language: 语音识别语言（默认中文）
    Returns:
        JSON字符串，格式为list[{text, start, end}]
    """
    import os
    import tempfile
    import json
    from moviepy.editor import VideoFileClip
    import azure.cognitiveservices.speech as speechsdk

    # 1. 提取音频到临时文件
    video = VideoFileClip(video_path)
    temp_audio = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    video.audio.write_audiofile(temp_audio.name, fps=16000, codec='pcm_s16le')
    video.close()

    # 2. 配置Azure语音服务
    speech_key = os.environ.get("AZURE_SPEECH_KEY")
    service_region = os.environ.get("AZURE_SPEECH_REGION")
    if not speech_key or not service_region:
        return json.dumps({"error": "请配置AZURE_SPEECH_KEY和AZURE_SPEECH_REGION环境变量"}, ensure_ascii=False)
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=temp_audio.name)
    speech_config.speech_recognition_language = language

    # 3. 使用ConversationTranscriber获取带时间戳的识别结果
    transcriber = speechsdk.transcription.ConversationTranscriber(speech_config, audio_config)
    results = []
    done = False
    def result_callback(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            offset = evt.result.offset / 10_000_000  # ticks to seconds
            duration = evt.result.duration.total_seconds() if evt.result.duration else 0
            text = evt.result.text
            results.append({
                "text": text,
                "start": offset,
                "end": offset + duration
            })
    def stop_callback(evt):
        nonlocal done
        done = True
    transcriber.recognized.connect(result_callback)
    transcriber.session_stopped.connect(stop_callback)
    transcriber.canceled.connect(stop_callback)
    transcriber.start_transcribing_async()
    import time
    while not done:
        time.sleep(0.5)
    transcriber.stop_transcribing_async()
    os.unlink(temp_audio.name)
    return json.dumps(results, ensure_ascii=False, indent=2) 

@mcp.tool()
async def generate_subtitle_list_from_whisper(
    video_path: str,
    model_size: str = "base",
    language: str = "zh"
) -> str:
    """
    使用openai-whisper对视频音频进行识别，输出带时间戳的字幕list。
    Args:
        video_path: 视频文件路径
        model_size: whisper模型大小（tiny/base/small/medium/large）
        language: 语音识别语言（如zh、en等）
    Returns:
        JSON字符串，格式为list[{text, start, end}]
    """
    import whisper
    import json
    model = whisper.load_model(model_size)
    result = model.transcribe(video_path, language=language)
    subtitle_list = [
        {"text": seg["text"], "start": seg["start"], "end": seg["end"]}
        for seg in result.get("segments", [])
    ]
    return json.dumps(subtitle_list, ensure_ascii=False, indent=2)

@mcp.tool()
async def generate_srt_from_whisper_mcp(
    video_path: Any,
    output_path: Any = None,
    model_size: Any = "base",
    language: Any = "zh"
) -> str:
    """
    使用openai-whisper对视频音频进行识别，直接生成srt字幕文件。
    每个时间段都输出，无声音区间输出空字幕，保证时间段连续完整，便于后续视频剪辑。
    Args:
        video_path: 视频文件路径
        output_path: srt输出路径（可选，默认与视频同名）
        model_size: whisper模型大小
        language: 语音识别语言
    Returns:
        srt文件路径
    """
    import os
    import json
    from moviepy.editor import VideoFileClip
    
    try:
        # 1. 获取字幕list
        subtitle_json = await generate_subtitle_list_from_whisper(video_path, model_size=model_size, language=language)
        subtitle_list = json.loads(subtitle_json)
        
        # 2. 生成srt内容（只输出有内容的字幕）
        def format_time(seconds):
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        
        srt_lines = []
        idx = 1
        for seg in subtitle_list:
            text = seg["text"].strip()
            if not text:
                continue  # 跳过空白
            start = float(seg["start"])
            end = float(seg["end"])
            srt_lines.append(str(idx))
            srt_lines.append(f"{format_time(start)} --> {format_time(end)}")
            srt_lines.append(text)
            srt_lines.append("")
            idx += 1
        
        srt_content = "\n".join(srt_lines)
        
        # 3. 写入文件
        if not output_path:
            output_path = os.path.splitext(video_path)[0] + ".srt"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(srt_content)
        
        print(f"[Whisper SRT] 生成完成: {output_path}")
        return output_path
        
    except Exception as e:
        error_msg = f"生成SRT文件失败: {str(e)}"
        print(f"[错误] {error_msg}")
        return error_msg

@mcp.tool()
async def clip_video_by_srt_mcp(
    video_path: Any,
    srt_path: Any,
    output_path: Any
) -> str:
    """
    根据srt字幕文件剪辑视频，只保留有字幕的区间，输出新视频。
    Args:
        video_path: 原视频路径
        srt_path: 字幕文件路径（SRT）
        output_path: 输出视频路径
    Returns:
        输出视频路径
    """
    try:
        from .video_utils import clip_video_by_srt
        clip_video_by_srt(video_path, srt_path, output_path)
        print(f"[SRT剪辑] 剪辑完成: {output_path}")
        return output_path
    except Exception as e:
        error_msg = f"SRT剪辑失败: {str(e)}"
        print(f"[错误] {error_msg}")
        return error_msg 