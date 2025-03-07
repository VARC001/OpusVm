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
        thumbnail = ""
        
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                pass
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # Load the original thumbnail
        youtube = Image.open(f"cache/thumb{videoid}.png")
        
        # Create the base canvas (1280x720)
        final_image = Image.new('RGB', (1280, 720), (0, 0, 0))
        
        # Create a heavily blurred background
        # First, resize the original image to be larger than the canvas
        bg_image = changeImageSize(1600, 900, youtube)
        
        # Apply strong blur to background (higher radius for more blur)
        blurred_bg = bg_image.filter(ImageFilter.GaussianBlur(radius=30))
        
        # Enhance the colors of the blurred background
        color_enhancer = ImageEnhance.Color(blurred_bg)
        blurred_bg = color_enhancer.enhance(1.2)  # Slightly increase color saturation
        
        # Darken the background
        brightness_enhancer = ImageEnhance.Brightness(blurred_bg)
        darkened_bg = brightness_enhancer.enhance(0.7)  # Darken to 70% brightness
        
        # Paste the blurred background (centered)
        bg_x = (1280 - 1600) // 2
        bg_y = (720 - 900) // 2
        final_image.paste(darkened_bg, (bg_x, bg_y))
        
        # Create a square-edged box for the main content
        # Center the box
        box_width = 600
        box_height = 600
        box_x = (1280 - box_width) // 2  # Centered horizontally
        box_y = (720 - box_height) // 2  # Centered vertically
        
        # Create a mask for the box (square-edged, no rounded corners)
        box_image = youtube.copy()
        box_image = changeImageSize(box_width, box_height, box_image)
        
        # Enhance the clarity of the box image
        clarity_enhancer = ImageEnhance.Contrast(box_image)
        box_image = clarity_enhancer.enhance(1.1)  # Slightly increase contrast
        
        # Add a music disc behind the box
        disc_size = 700
        disc_image = Image.new('RGBA', (disc_size, disc_size), (0, 0, 0, 0))
        draw_disc = ImageDraw.Draw(disc_image)
        draw_disc.ellipse((0, 0, disc_size, disc_size), fill=(50, 50, 50, 200))
        disc_x = (1280 - disc_size) // 2
        disc_y = (720 - disc_size) // 2
        final_image.paste(disc_image, (disc_x, disc_y), disc_image)
        
        # Paste the box image
        final_image.paste(box_image, (box_x, box_y))
        
        # Add a border to the box
        draw = ImageDraw.Draw(final_image)
        border_color = (255, 255, 255)  # White border
        border_width = 2
        draw.rectangle(
            [(box_x, box_y), (box_x + box_width, box_y + box_height)],
            outline=border_color,
            width=border_width
        )
        
        # Add title text at the bottom
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
        except:
            title_font = ImageFont.load_default()
        
        # Position for the title (bottom of the image)
        title_text = clear(title).upper()
        title_width, title_height = title_font.getsize(title_text)
        title_x = (1280 - title_width) // 2
        title_y = 720 - 100
        
        # Draw the title with a shadow effect
        # First draw shadow
        shadow_offset = 3
        draw.text((title_x + shadow_offset, title_y + shadow_offset), title_text, 
                 fill=(0, 0, 0), font=title_font)
        # Then draw text
        draw.text((title_x, title_y), title_text, fill=(255, 255, 255), font=title_font)
        
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        final_image.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return YOUTUBE_IMG_URL
