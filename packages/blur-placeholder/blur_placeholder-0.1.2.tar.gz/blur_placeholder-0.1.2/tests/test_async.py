import pytest
import asyncio
from blur_placeholder import generate_blur_placeholder_async

@pytest.mark.asyncio
async def test_async_url_placeholder():
    data_url = await generate_blur_placeholder_async("https://picsum.photos/200/300")
    assert data_url.startswith("data:image/jpeg;base64,")

@pytest.mark.asyncio
async def test_async_local_file():
    # Create a test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save('test_async_image.jpg')
    
    data_url = await generate_blur_placeholder_async('test_async_image.jpg')
    assert data_url.startswith("data:image/jpeg;base64,")
    import os
    os.remove('test_async_image.jpg')

@pytest.mark.asyncio
async def test_async_bytes_input():
    # Create a test image
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='blue')
    img.save('test_async_image.jpg')
    with open('test_async_image.jpg', 'rb') as f:
        data = f.read()
    data_url = await generate_blur_placeholder_async(data)
    assert data_url.startswith("data:image/jpeg;base64,")
    import os
    os.remove('test_async_image.jpg')