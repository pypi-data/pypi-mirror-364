import io
import base64
from PIL import Image, ImageFilter
from .exceptions import ImageProcessingError

def process_image_data(
    image_data,
    blur_width=20,
    blur_radius=2,
    quality=30,
    image_format="JPEG"
):
    """Process image data to create blurred placeholder"""
    try:
        img = Image.open(io.BytesIO(image_data))
        if img.mode != 'RGB':
            img = img.convert("RGB")
            
        img.thumbnail((blur_width, blur_width))
        img = img.filter(ImageFilter.GaussianBlur(blur_radius))
        
        output = io.BytesIO()
        img.save(output, format=image_format, quality=quality)
        b64 = base64.b64encode(output.getvalue()).decode()
        
        # Handle MIME types
        if image_format.lower() in ["jpg", "jpeg"]:
            mime_type = "image/jpeg"
        elif image_format.lower() == "png":
            mime_type = "image/png"
        elif image_format.lower() == "webp":
            mime_type = "image/webp"
        else:
            mime_type = f"image/{image_format.lower()}"
            
        return f"data:{mime_type};base64,{b64}"
    except Exception as e:
        raise ImageProcessingError(f"Image processing failed: {str(e)}")