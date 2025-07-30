# Blur Placeholder

[![PyPI version](https://badge.fury.io/py/blur-placeholder.svg)](https://badge.fury.io/py/blur-placeholder)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/blur-placeholder.svg)](https://pypi.org/project/blur-placeholder)

A simple, fast, and lightweight Python library to generate base64-encoded blurred image placeholders for lazy loading. This helps improve user experience by showing a low-quality version of an image while the full-quality version is loading.

## Key Features

- **Multiple Image Sources:** Generate placeholders from URLs, local file paths, or raw image bytes.
- **Asynchronous Support:** Built-in async support using `aiohttp` for non-blocking operations.
- **Caching:** In-memory caching to avoid regenerating placeholders for the same image.
- **Customizable:** Control the blur intensity, quality, and image format.
- **Lightweight:** Minimal dependencies (`Pillow` and `requests`).

## Installation

Install the basic version with synchronous support:

```bash
pip install blur-placeholder
```

For asynchronous support, install the `async` extra:

```bash
pip install blur-placeholder[async]
```

## Usage

### Synchronous

The synchronous `generate_blur_placeholder` function is ideal for simple scripts and applications where blocking operations are acceptable.

```python
from blur_placeholder import generate_blur_placeholder

# From a URL
data_url = generate_blur_placeholder("https://picsum.photos/seed/picsum/800/600")
print(data_url)

# From a local file
# with open("my_image.jpg", "wb") as f:
#     f.write(requests.get("https://picsum.photos/seed/picsum/800/600").content)
# data_url = generate_blur_placeholder("my_image.jpg")
# print(data_url)

# From image bytes
# with open("my_image.jpg", "rb") as f:
#     image_bytes = f.read()
# data_url = generate_blur_placeholder(image_bytes)
# print(data_url)
```

### Asynchronous

The asynchronous `generate_blur_placeholder_async` function is perfect for high-performance applications using `asyncio`.

```python
import asyncio
from blur_placeholder import generate_blur_placeholder_async

async def main():
    # From a URL
    data_url = await generate_blur_placeholder_async("https://picsum.photos/seed/picsum/800/600")
    print(data_url)

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

You can customize the placeholder generation with several optional parameters:

```python
data_url = generate_blur_placeholder(
    "https://picsum.photos/seed/picsum/800/600",
    blur_width=25,      # Width of the blurred image (default: 20)
    blur_radius=5,      # Blur radius (default: 2)
    quality=40,         # JPEG quality (default: 30)
    image_format="WEBP" # Output format (default: "JPEG")
)
```

## API Reference

### `generate_blur_placeholder(image_source, **kwargs)`

- `image_source` (str | bytes): The source of the image. Can be a URL, a local file path, or image data in bytes.
- `blur_width` (int, optional): The width to resize the image to before blurring. Defaults to `20`.
- `blur_radius` (int, optional): The radius for the Gaussian blur. Defaults to `2`.
- `quality` (int, optional): The quality of the output JPEG image (1-100). Defaults to `30`.
- `cache` (BaseCache, optional): A custom cache object. Defaults to a built-in in-memory cache.
- `timeout` (int, optional): The cache timeout in seconds. Defaults to `86400` (24 hours).
- `image_format` (str, optional): The output image format (e.g., "JPEG", "WEBP", "PNG"). Defaults to `"JPEG"`.

### `generate_blur_placeholder_async(image_source, **kwargs)`

This function has the same parameters as the synchronous version but is an `async` function.

## Caching

By default, `blur-placeholder` caches results in memory to speed up repeated requests for the same image. You can provide your own cache implementation by creating a class that inherits from `BaseCache` (for sync) or `BaseAsyncCache` (for async) and passing an instance to the `cache` parameter.

## Contributing

Contributions are welcome! To get started:

1.  Fork the repository.
2.  Clone your fork: `git clone https://github.com/your-username/blur-placeholder.git`
3.  Install the development dependencies: `pip install -e ".[dev]"`
4.  Run the tests: `pytest`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.