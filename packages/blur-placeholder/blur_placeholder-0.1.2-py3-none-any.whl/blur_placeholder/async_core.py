import asyncio
import hashlib


DEFAULT_BLUR_WIDTH = 20
DEFAULT_BLUR_RADIUS = 2
DEFAULT_QUALITY = 30
DEFAULT_TIMEOUT = 60 * 60 * 24  # 24 hours

async def generate_blur_placeholder_async(
    image_source,
    blur_width=DEFAULT_BLUR_WIDTH,
    blur_radius=DEFAULT_BLUR_RADIUS,
    quality=DEFAULT_QUALITY,
    cache=None,
    timeout=DEFAULT_TIMEOUT,
    image_format="JPEG"
):
    
    import aiohttp  # lazy import
    from .utils import process_image_data
    from .cache import BaseAsyncCache, get_default_async_cache
    from .exceptions import BlurPlaceholderException, InvalidImageSource
    
    
    
    """Asynchronously generate blurred placeholder"""
    cache = cache or get_default_async_cache()
    
    # Generate cache key
    if isinstance(image_source, bytes):
        cache_key = f"blur_async_{hashlib.sha256(image_source).hexdigest()}"
    else:
        cache_key = f"blur_async_{hashlib.md5(image_source.encode()).hexdigest()}"

    # Check cache
    if cached := await cache.aget(cache_key):
        return cached

    try:
        # Handle different input types
        if isinstance(image_source, bytes):
            image_data = image_source
        elif image_source.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(image_source) as response:
                    if response.status != 200:
                        return None
                    image_data = await response.read()
        elif isinstance(image_source, str):  # Local file path
            with open(image_source, "rb") as f:
                image_data = f.read()
        else:
            raise InvalidImageSource("Unsupported image source type")
        
        # Process image in thread pool
        loop = asyncio.get_running_loop()
        data_url = await loop.run_in_executor(
            None, 
            lambda: process_image_data(
                image_data,
                blur_width,
                blur_radius,
                quality,
                image_format
            )
        )
        
        # Cache result
        await cache.aset(cache_key, data_url, timeout)
        return data_url
        
    except Exception as e:
        raise BlurPlaceholderException(f"Async error: {str(e)}") from e