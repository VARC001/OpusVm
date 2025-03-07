import os
import re
import random

import aiofiles
import aiohttp

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps, ImageFilter

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
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        image1 = changeImageSize(1280, 720, youtube)
        bg_bright = ImageEnhance.Brightness(image1)
        bg_logo = bg_bright.enhance(1.1)
        bg_contra = ImageEnhance.Contrast(bg_logo)
        bg_logo = bg_contra.enhance(1.1)
        background = changeImageSize(1280, 720, bg_logo)

        # Apply a slight blur to the background
        background = background.filter(ImageFilter.GaussianBlur(1))

        # Create a gradient overlay
        gradient = Image.new('RGBA', (1280, 720), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        for i in range(720):
            alpha = int(255 * (i / 720))
            draw.rectangle((0, i, 1280, i + 1), fill=(0, 0, 0, alpha))

        # Composite the gradient over the background
        background = Image.alpha_composite(background.convert('RGBA'), gradient)

        # Add text with shadow
        draw = ImageDraw.Draw(background)
        title_font = ImageFont.truetype("arial.ttf", 60)
        info_font = ImageFont.truetype("arial.ttf", 40)

        # Draw title with shadow
        title_text = clear(title)
        shadow_color = (0, 0, 0, 128)
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            draw.text((50 + offset[0], 50 + offset[1]), title_text, fill=shadow_color, font=title_font)
        draw.text((50, 50), title_text, fill="white", font=title_font)

        # Draw channel, views, and duration with shadow
        info_text = f"{channel} | {views} | {duration}"
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            draw.text((50 + offset[0], 150 + offset[1]), info_text, fill=shadow_color, font=info_font)
        draw.text((50, 150), info_text, fill="white", font=info_font)

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
