import pytest
import os
from blur_placeholder import generate_blur_placeholder

def test_url_placeholder():
    data_url = generate_blur_placeholder("https://picsum.photos/200/300")
    assert data_url.startswith("data:image/jpeg;base64,")
    assert len(data_url) > 100

def test_local_file():
    # Create a test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img.save('test_image.jpg')
    
    data_url = generate_blur_placeholder('test_image.jpg')
    assert data_url.startswith("data:image/jpeg;base64,")
    os.remove('test_image.jpg')

def test_bytes_input():
    # Create a test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img.save('test_image.jpg')
    with open('test_image.jpg', 'rb') as f:
        data = f.read()
    data_url = generate_blur_placeholder(data)
    assert data_url.startswith("data:image/jpeg;base64,")
    os.remove('test_image.jpg')

def test_invalid_url():
    with pytest.raises(Exception):
        generate_blur_placeholder("https://invalid.url/does-not-exist.jpg")

def test_invalid_file():
    with pytest.raises(FileNotFoundError):
        generate_blur_placeholder("non_existent_file.jpg")