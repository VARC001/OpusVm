import os
import re
import random

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
    img = image.copy()
    img.thumbnail((100, 100))
    
    # Convert image to numpy array
    img_array = np.array(img)
    
    # Reshape the array to be 2D (all pixels in a single list)
    pixels = img_array.reshape(-1, 3)
    
    # Calculate the average color
    avg_color = np.mean(pixels, axis=0).astype(int)
    
    return tuple(avg_color)


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
        final_image = Image.new('RGB', (1280, 720), (0, 0, 0))
        
        # Create a heavily blurred background
        # First, resize the original image to be larger than the canvas
        bg_image = changeImageSize(1600, 900, youtube)
        
        # Apply strong blur to background (higher radius for more blur)
        blurred_bg = bg_image.filter(ImageFilter.GaussianBlur(radius=40))
        
        # Enhance the colors of the blurred background
        color_enhancer = ImageEnhance.Color(blurred_bg)
        blurred_bg = color_enhancer.enhance(1.4)  # Increase color saturation
        
        # Darken the background
        brightness_enhancer = ImageEnhance.Brightness(blurred_bg)
        darkened_bg = brightness_enhancer.enhance(0.6)  # Darken to 60% brightness
        
        # Paste the blurred background (centered)
        bg_x = (1280 - 1600) // 2
        bg_y = (720 - 900) // 2
        final_image.paste(darkened_bg, (bg_x, bg_y))
        
        # Create a square-edged box for the main content in the center
        box_width = 700
        box_height = 450
        box_x = (1280 - box_width) // 2  # Centered horizontally
        box_y = 80  # Position at the top with some margin
        
        # Create a mask for the box (square-edged, no rounded corners)
        box_image = youtube.copy()
        box_image = changeImageSize(box_width, box_height, box_image)
        
        # Enhance the clarity of the box image
        clarity_enhancer = ImageEnhance.Contrast(box_image)
        box_image = clarity_enhancer.enhance(1.2)  # Increase contrast
        
        # Paste the box image
        final_image.paste(box_image, (box_x, box_y))
        
        # Add a border to the box
        draw = ImageDraw.Draw(final_image)
        border_color = (255, 255, 255)  # White border
        border_width = 3
        draw.rectangle(
            [(box_x, box_y), (box_x + box_width, box_y + box_height)],
            outline=border_color,
            width=border_width
        )
        
        # Add duration in the corner of the video box
        if duration != "Unknown Mins":
            duration_x = box_x + 10
            duration_y = box_y + 10
            
            # Create a semi-transparent background for the duration
            duration_bg_width = 80
            duration_bg_height = 30
            duration_overlay = Image.new('RGBA', (duration_bg_width, duration_bg_height), (0, 0, 0, 200))
            duration_overlay = duration_overlay.convert('RGB')
            final_image.paste(duration_overlay, (duration_x, duration_y))
            
            # Add the duration text
            try:
                duration_font = ImageFont.truetype("arial.ttf", 20)
            except:
                duration_font = ImageFont.load_default()
                
            draw.text((duration_x + 10, duration_y + 5), duration, fill=(255, 255, 255), font=duration_font)
        
        # Create a semi-transparent overlay for the bottom text area
        overlay_height = 180
        overlay = Image.new('RGBA', (1280, overlay_height), (0, 0, 0, 180))
        overlay = overlay.convert('RGB')
        final_image.paste(overlay, (0, 720 - overlay_height))
        
        # Add title text at the bottom
        try:
            title_font = ImageFont.truetype("arial.ttf", 50)
            subtitle_font = ImageFont.truetype("arial.ttf", 30)
            views_font = ImageFont.truetype("arial.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = title_font
            views_font = title_font
        
        # Position for the title (bottom of the image)
        title_x = 40
        title_y = 720 - overlay_height + 20
        
        # Make title uppercase for impact
        title_text = clear(title).upper()
        
        # Draw the title with a shadow effect
        # First draw shadow
        shadow_offset = 2
        draw.text((title_x + shadow_offset, title_y + shadow_offset), title_text, 
                 fill=(0, 0, 0), font=title_font)
        # Then draw text
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=title_font)
        
        # Add view count on the right side
        if views != "Unknown Views":
            view_text = f"{views}"
            if "M" in views:  # If it's in millions
                view_text = f"{views.replace('M', '')} MILLION+"
            elif "K" in views:  # If it's in thousands
                view_text = f"{views.replace('K', '')} THOUSAND+"
            
            # Calculate position to align right
            view_width = draw.textlength(view_text, font=views_font)
            view_x = 1280 - view_width - 40  # Right aligned with margin
            view_y = 720 - overlay_height + 20
            
            # Draw views with shadow
            draw.text((view_x + shadow_offset, view_y + shadow_offset), view_text, 
                     fill=(0, 0, 0), font=views_font)
            draw.text((view_x, view_y), view_text, fill=(255, 255, 255), font=views_font)
            
            # Add "VIEWS" text below
            views_label = "VIEWS"
            views_label_width = draw.textlength(views_label, font=subtitle_font)
            views_label_x = 1280 - views_label_width - 40  # Right aligned
            
            draw.text((views_label_x + shadow_offset, view_y + 50 + shadow_offset), 
                     views_label, fill=(0, 0, 0), font=subtitle_font)
            draw.text((views_label_x, view_y + 50), 
                     views_label, fill=(255, 255, 255), font=subtitle_font)
        
        # Add channel name at the bottom
        channel_y = 720 - 50
        draw.text((title_x + shadow_offset, channel_y + shadow_offset), 
                 channel, fill=(0, 0, 0), font=subtitle_font)
        draw.text((title_x, channel_y), 
                 channel, fill=(200, 200, 200), font=subtitle_font)
        
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        final_image.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL
