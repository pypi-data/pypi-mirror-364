#!/usr/bin/env python3
"""Media Agent MCP Server - A Model Context Protocol server for media processing.

This server provides 9 tools for media processing:
1. TOS - Save content as URL
2. Video Concat - Concatenate two videos
3. Video Last Frame - Get the last frame from a video
4. Seedream - Creating images (AI model)
5. Seedance (lite & pro) - Creating videos (AI model)
6. Seededit - Maintain the main character (AI model)
7. Seed1.6 (VLM) - Do vision tasks in workflow (AI model)
8. Image Selector - Choose the best one from images
9. Video Selector - Choose the best video from videos
"""

import argparse
import logging
from typing import Optional, Dict, Any
import json

from mcp.server.fastmcp import FastMCP

# Import modules
from media_agent_mcp.storage import upload_to_tos
from media_agent_mcp.video import concat_videos, extract_last_frame
from media_agent_mcp.ai_models.seedream import generate_image
from media_agent_mcp.ai_models.seedance import generate_video
from media_agent_mcp.ai_models.seededit import seededit
from media_agent_mcp.media_selectors.image_selector import select_best_image
from media_agent_mcp.media_selectors.video_selector import select_best_video

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server (will be configured in main function)
mcp = FastMCP("Media Agent MCP")


@mcp.tool()
def video_concat_tool(video_urls: list[str]) -> str:
    """
    Concatenate multiple videos from URLs and upload to TOS.
    
    Args:
        video_urls: List of video URLs to concatenate in order
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = concat_videos(video_urls)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"url": result},
                    "message": "Videos concatenated successfully"
                })
    except Exception as e:
        logger.error(f"Error in video_concat_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def video_last_frame_tool(video_url: str) -> str:
    """
    Extract the last frame from a video file and upload to TOS.
    
    Args:
        video_url: URL or path to the video file
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        # Extract last frame and upload to TOS
        result = extract_last_frame(video_url)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"url": result},
                    "message": "Last frame extracted successfully"
                })
            
    except Exception as e:
        logger.error(f"Error in video_last_frame_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedream_generate_image_tool(prompt: str, size: str = "1024x1024") -> str:
    """
    Generate an image using Seedream AI model.
    
    Args:
        prompt: Text description of the image to generate
        size: Size of the image (e.g., "1024x1024")
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = generate_image(prompt, size=size)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image generated successfully"
                })
    except Exception as e:
        logger.error(f"Error in seedream_generate_image_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seedance_generate_video_tool(prompt: str, first_frame_image: str, 
                                last_frame_image: str = None, duration: int = 5, 
                                resolution: str = "720p") -> str:
    """
    Generate a video using Seedance AI model with first/last frame images.
    
    Args:
        prompt: Text description of the video to generate (optional for image-to-video)
        first_frame_image: URL or base64 of the first frame image
        last_frame_image: URL or base64 of the last frame image (optional)
        duration: Duration of the video in seconds (5 or 10)
        resolution: Video resolution (480p, 720p)
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        if not prompt and not first_frame_image:
            return json.dumps({
                "status": "error",
                "data": None,
                "message": "Error: Either prompt or first_frame_image must be provided"
            })
        
        result = generate_video(
            prompt=prompt,
            first_frame_image=first_frame_image,
            last_frame_image=last_frame_image,
            duration=duration,
            resolution=resolution
        )
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"url": result},
                    "message": "Video generated successfully"
                })
    except Exception as e:
        logger.error(f"Error in seedance_generate_video_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def seededit_tool(image_url: str, prompt: str, seed: int = -1, scale: float = 0.5, charactor_keep: bool = False) -> str:
    """
    Edit a image using Seededit model.
    
    Args:
        image_url: Input image URL for editing
        prompt: Text prompt for image editing
        seed: Random seed for reproducibility (-1 for random)
        scale: Influence degree of text description (0-1)
        charactor_keep: whether to keep the main charactor in this image, if you wanna change the main charactor, please keep False
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = seededit(
            image_url=image_url,
            prompt=prompt,
            charactor_keep=charactor_keep,
            return_url=True,
            scale=scale,
            seed=seed
        )
        
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"image_url": result},
                    "message": "Image editing completed successfully"
                })
    except Exception as e:
        logger.error(f"Error in seededit_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })

@mcp.tool()
def vlm_vision_task_tool(messages: list) -> str:
    """
    Perform vision-language tasks using VLM model.
    
    Args:
        messages: OpenAI-compatible messages format
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        from media_agent_mcp.ai_models.seed16 import process_vlm_task
        
        result = process_vlm_task(messages)
        if isinstance(result, dict):
            return json.dumps(result)
        else:
            # Handle legacy string returns
            if result.startswith("Error:"):
                return json.dumps({
                    "status": "error",
                    "data": None,
                    "message": result
                })
            else:
                return json.dumps({
                    "status": "success",
                    "data": {"result": result},
                    "message": "Vision task completed successfully"
                })
        
    except Exception as e:
        logger.error(f"Error in vlm_vision_task_tool: {str(e)}")
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Error: {str(e)}"
        })


@mcp.tool()
def image_selector_tool(image_paths: list[str], prompt: str) -> str:
    """
    Select the best image from multiple options using VLM model.
    
    Args:
        image_paths: List of paths to image files
        prompt: Selection criteria prompt
        
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = select_best_image(image_paths, prompt)
        return json.dumps({
            "status": "success",
            "data": result,
            "message": "Image selection completed successfully"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Image selection failed: {str(e)}"
        })


@mcp.tool()
def video_selector_tool(video_paths: list[str], prompt: str) -> str:
    """
    Select the best video from multiple options using VLM model.
    
    Args:
        video_paths: List of paths to videos to choose from
        prompt: Selection criteria prompt
    
    Returns:
        JSON string with status, data, and message
    """
    try:
        result = select_best_video(video_paths, prompt)
        return json.dumps({
            "status": "success",
            "data": result,
            "message": "Video selection completed successfully"
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "data": None,
            "message": f"Video selection failed: {str(e)}"
        })



def main():
    """Main entry point for the MCP server."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Media Agent MCP Server')
    parser.add_argument('--transport', type=str, choices=['sse', 'stdio'], default='stdio',
                        help='Transport method: sse or stdio (default: stdio)')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host for SSE transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port for SSE transport (default: 8000)')
    parser.add_argument('--version', action='store_true',
                        help='Show version information')
    
    args = parser.parse_args()
    
    if args.version:
        print("Media Agent MCP Server v0.1.0")
        return
    
    logger.info("Starting Media Agent MCP Server...")
    logger.info(f"Transport: {args.transport}")
    if args.transport == 'sse':
        logger.info(f"SSE Server will run on {args.host}:{args.port}")
    
    logger.info("Available tools:")
    logger.info("  1. video_last_frame_tool - Extract last frame from video and upload to TOS")
    logger.info("  2. video_concat_tool - Concatenate two videos")
    logger.info("  3. seedream_generate_image_tool - Generate images with AI (direct URL return)")
    logger.info("  4. seedance_generate_video_tool - Generate videos with AI (async with polling)")
    logger.info("  5. seededit_maintain_character_tool - Edit images while maintaining character")
    logger.info("  6. vlm_vision_task_tool - Perform vision tasks with OpenAI-compatible messages")
    logger.info("  7. image_selector_tool - Select best image using VLM model")
    logger.info("  8. video_selector_tool - Select best video using VLM model")
    logger.info("  9. tos_save_content_tool - Save content to TOS and return URL")
    
    # Start the server with specified transport
    if args.transport == 'sse':
        logger.info(f"Starting SSE server on {args.host}:{args.port}")
        mcp.settings.host = args.host
        mcp.settings.port = args.port

        mcp.run(transport="sse")
    else:
        # Default stdio transport
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()