import io
import pytest
from PIL import Image
from blur_placeholder.utils import process_image_data

def test_image_processing():
    # Create test image
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    data_url = process_image_data(img_data)
    assert data_url.startswith("data:image/jpeg;base64,")

def test_invalid_image():
    with pytest.raises(Exception):
        process_image_data(b'invalid-image-data')

def test_different_formats():
    # Create test image
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    # Test PNG
    data_url = process_image_data(img_data, image_format="PNG")
    assert data_url.startswith("data:image/png;base64,")
    
    # Test WEBP
    data_url = process_image_data(img_data, image_format="WEBP")
    assert data_url.startswith("data:image/webp;base64,")