import os
import re
import random
from io import BytesIO

import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
import numpy as np

from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch

from Opus import app
from config import YOUTUBE_IMG_URL


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()


def get_dominant_color(image):
    """Extract the dominant color from an image"""
    # Resize image to speed up processing
    img = image.copy()
    img.thumbnail((100, 100))
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Reshape the array to be 2D (all pixels in a single list)
    pixels = img_array.reshape(-1, 3)
    
    # Calculate the average color
    avg_color = np.mean(pixels, axis=0).astype(int)
    
    return tuple(avg_color)


def create_play_button(size, color=(255, 255, 255, 180)):
    """Create a play button icon"""
    play_button = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(play_button)
    
    # Draw a triangle for the play button
    width, height = size
    margin = width // 4
    points = [
        (margin, margin),
        (width - margin, height // 2),
        (margin, height - margin)
    ]
    draw.polygon(points, fill=color)
    
    return play_button


def create_duration_bar(width, height, duration_text, color=(255, 255, 255, 180)):
    """Create a duration bar with text"""
    bar = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bar)
    
    # Draw the progress bar background
    draw.rectangle([(0, 0), (width, height)], fill=(0, 0, 0, 100), outline=None)
    
    # Draw the progress (just for visual, not actual progress)
    progress_width = int(width * 0.7)  # 70% progress for visual effect
    draw.rectangle([(0, 0), (progress_width, height)], fill=(255, 255, 255, 100), outline=None)
    
    # Add duration text if provided
    if duration_text:
        # Try to load font, use default if not available
        try:
            font = ImageFont.truetype("arial.ttf", height - 4)
        except:
            font = ImageFont.load_default()
            
        # Position text at the right end
        text_width = draw.textlength(duration_text, font=font)
        draw.text((width - text_width - 10, 2), duration_text, fill=(255, 255, 255, 230), font=font)
    
    return bar


async def get_qthumb(videoid):
    try:
        url = f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg"
        return url
    except Exception:
        return YOUTUBE_IMG_URL


async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        title = "Unsupported Title"
        duration = "Unknown Mins"
        thumbnail = ""
        views = "Unknown Views"
        channel = "Unknown Channel"
        
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                pass
            try:
                duration = result["duration"]
            except:
                pass
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                pass
            try:
                channel = result["channel"]["name"]
            except:
                pass

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Load the original thumbnail
        youtube = Image.open(f"cache/thumb{videoid}.png")
        
        # Get the dominant color for styling
        dominant_color = get_dominant_color(youtube)
        
        # Create the base canvas (1280x720)
        final_image = Image.new('RGBA', (1280, 720), (0, 0, 0, 255))
        
        # Resize the original for background
        bg_image = changeImageSize(1400, 800, youtube)
        
        # Apply blur to background
        blurred_bg = bg_image.filter(ImageFilter.GaussianBlur(radius=15))
        
        # Darken the background
        enhancer = ImageEnhance.Brightness(blurred_bg)
        darkened_bg = enhancer.enhance(0.6)
        
        # Paste the blurred background
        final_image.paste(darkened_bg, (-60, -40))
        
        # Create a center rectangle for the clear image
        center_width, center_height = 800, 450
        center_x = (1280 - center_width) // 2
        center_y = (720 - center_height) // 2
        
        # Create a mask for rounded corners
        mask = Image.new('L', (center_width, center_height), 0)
        draw_mask = ImageDraw.Draw(mask)
        radius = 20  # Corner radius
        draw_mask.rounded_rectangle([(0, 0), (center_width, center_height)], radius, fill=255)
        
        # Create the center image container
        center_container = Image.new('RGBA', (center_width, center_height), (0, 0, 0, 0))
        
        # Resize the original image to fit the center container
        center_image = changeImageSize(center_width, center_height, youtube)
        
        # Apply the mask for rounded corners
        center_container.paste(center_image, (0, 0), mask)
        
        # Add a subtle border
        border_color = (*dominant_color, 150)  # Use dominant color with transparency
        border_width = 4
        draw = ImageDraw.Draw(final_image)
        draw.rounded_rectangle(
            [(center_x-border_width, center_y-border_width), 
             (center_x+center_width+border_width, center_y+center_height+border_width)],
            radius=radius+border_width,
            outline=border_color,
            width=border_width
        )
        
        # Paste the center container onto the final image
        final_image.paste(center_container, (center_x, center_y), mask)
        
        # Add play button in the center
        play_button_size = 100
        play_button = create_play_button((play_button_size, play_button_size))
        play_button_x = (1280 - play_button_size) // 2
        play_button_y = (720 - play_button_size) // 2
        final_image.paste(play_button, (play_button_x, play_button_y), play_button)
        
        # Add duration bar at the bottom of the center container
        duration_bar_height = 20
        duration_bar = create_duration_bar(center_width, duration_bar_height, duration)
        final_image.paste(duration_bar, (center_x, center_y + center_height - duration_bar_height), duration_bar)
        
        # Add title text
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            
        title_y = center_y + center_height + 20
        draw.text((center_x, title_y), clear(title), fill=(255, 255, 255, 230), font=font)
        
        # Add channel and views
        info_y = title_y + 30
        channel_views = f"{channel} • {views}"
        draw.text((center_x, info_y), channel_views, fill=(200, 200, 200, 200), font=font)
        
        # Convert to RGB for saving as PNG
        final_image = final_image.convert('RGB')
        
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        final_image.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL
