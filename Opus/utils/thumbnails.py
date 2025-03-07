import random
import logging
import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from youtubesearchpython.__future__ import VideosSearch

logging.basicConfig(level=logging.INFO)

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1, text2]

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_gradient(width, height, start_color, end_color):
    base = Image.new('RGBA', (width, height), start_color)
    top = Image.new('RGBA', (width, height), end_color)
    mask = Image.new('L', (width, height))
    mask_data = []
    for y in range(height):
        mask_data.extend([int(60 * (y / height))] * width)
    mask.putdata(mask_data)
    base.paste(top, (0, 0), mask)
    return base

def add_border(image, border_width, border_color):
    width, height = image.size
    new_width = width + 2 * border_width
    new_height = height + 2 * border_width
    new_image = Image.new("RGBA", (new_width, new_height), border_color)
    new_image.paste(image, (border_width, border_width))
    return new_image

def draw_text_with_shadow(background, draw, position, text, font, fill, shadow_offset=(3, 3), shadow_blur=5):
    shadow = Image.new('RGBA', background.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.text(position, text, font=font, fill="black")
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur))
    background.paste(shadow, shadow_offset, shadow)
    draw.text(position, text, font=font, fill=fill)

async def get_thumb(videoid: str):
    try:
        if os.path.isfile(f"cache/{videoid}_v4.png"):
            return f"cache/{videoid}_v4.png"

        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = result.get("title")
            if title:
                title = re.sub("\W+", " ", title).title()
            else:
                title = "Unsupported Title"
            duration = result.get("duration")
            if not duration:
                duration = "Live"
            thumbnail_data = result.get("thumbnails")
            if thumbnail_data:
                thumbnail = thumbnail_data[0]["url"].split("?")[0]
            else:
                thumbnail = None
            views_data = result.get("viewCount")
            if views_data:
                views = views_data.get("short")
                if not views:
                    views = "Unknown Views"
            else:
                views = "Unknown Views"
            channel_data = result.get("channel")
            if channel_data:
                channel = channel_data.get("name")
                if not channel:
                    channel = "Unknown Channel"
            else:
                channel = "Unknown Channel"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                content = await resp.read()
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        extension = 'jpg'
                    elif 'png' in content_type:
                        extension = 'png'
                    else:
                        logging.error(f"Unexpected content type: {content_type}")
                        return None

                    filepath = f"cache/thumb{videoid}.png"
                    f = await aiofiles.open(filepath, mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                    
        image_path = f"cache/thumb{videoid}.png"
        youtube = Image.open(image_path)
        image1 = changeImageSize(1280, 720, youtube)
        
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(20))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)

        start_gradient_color = random_color()
        end_gradient_color = random_color()
        gradient_image = generate_gradient(1280, 720, start_gradient_color, end_gradient_color)
        background = Image.blend(background, gradient_image, alpha=0.2)
        
        draw = ImageDraw.Draw(background)
        arial = ImageFont.truetype("Opus/assets/font2.ttf", 30)
        font = ImageFont.truetype("Opus/assets/font.ttf", 30)
        title_font = ImageFont.truetype("Opus/assets/font3.ttf", 45)

        # Create a box for the thumbnail
        box_size = (400, 400)
        box_position = (440, 50)
        box = Image.new("RGBA", box_size, (0, 0, 0, 128))
        background.paste(box, box_position, box)

        # Paste the thumbnail inside the box
        thumbnail_resized = image1.resize((380, 380))
        background.paste(thumbnail_resized, (box_position[0] + 10, box_position[1] + 10))

        # Add title and other information
        title1 = truncate(title)
        draw_text_with_shadow(background, draw, (50, 500), title1[0], title_font, (255, 255, 255))
        draw_text_with_shadow(background, draw, (50, 550), title1[1], title_font, (255, 255, 255))
        draw_text_with_shadow(background, draw, (50, 600), f"{channel}  |  {views[:23]}", arial, (255, 255, 255))

        # Add play icons
        play_icons = Image.open("Opus/assets/play_icons.png")
        play_icons = play_icons.resize((1180, 62))
        background.paste(play_icons, (50, 700), play_icons)

        os.remove(f"cache/thumb{videoid}.png")

        background_path = f"cache/{videoid}_v4.png"
        background.save(background_path)
        
        return background_path

    except Exception as e:
        logging.error(f"Error generating thumbnail for video {videoid}: {e}")
        traceback.print_exc()
        return None
