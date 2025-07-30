import hashlib
import requests
from .utils import process_image_data
from .cache import BaseCache, get_default_cache
from .exceptions import BlurPlaceholderException, InvalidImageSource

DEFAULT_BLUR_WIDTH = 20
DEFAULT_BLUR_RADIUS = 2
DEFAULT_QUALITY = 30
DEFAULT_TIMEOUT = 60 * 60 * 24  # 24 hours

def generate_blur_placeholder(
    image_source,
    blur_width=DEFAULT_BLUR_WIDTH,
    blur_radius=DEFAULT_BLUR_RADIUS,
    quality=DEFAULT_QUALITY,
    cache=None,
    timeout=DEFAULT_TIMEOUT,
    image_format="JPEG"
):
    """Generate blurred placeholder synchronously"""
    cache = cache or get_default_cache()
    
    # Generate cache key
    if isinstance(image_source, bytes):
        cache_key = f"blur_{hashlib.sha256(image_source).hexdigest()}"
    else:
        cache_key = f"blur_{hashlib.md5(image_source.encode()).hexdigest()}"
    
    # Check cache
    if cached := cache.get(cache_key):
        return cached
    
    try:
        # Handle byte input
        if isinstance(image_source, bytes):
            image_data = image_source
        # Handle URL
        elif image_source.startswith(("http://", "https://")):
            response = requests.get(image_source, timeout=5)
            response.raise_for_status()
            image_data = response.content
        # Handle local file path
        elif isinstance(image_source, str):
            with open(image_source, "rb") as f:
                image_data = f.read()
        else:
            raise InvalidImageSource("Unsupported image source type")
            
        data_url = process_image_data(
            image_data,
            blur_width,
            blur_radius,
            quality,
            image_format
        )
        
        # Cache result
        cache.set(cache_key, data_url, timeout)
        return data_url
            
    except Exception as e:
        raise BlurPlaceholderException(f"Error generating placeholder: {str(e)}") from e