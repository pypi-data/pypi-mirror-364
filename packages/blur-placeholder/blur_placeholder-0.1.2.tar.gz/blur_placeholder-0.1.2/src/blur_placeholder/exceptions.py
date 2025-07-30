class BlurPlaceholderException(Exception):
    """Base exception for the package"""
    
class InvalidImageSource(BlurPlaceholderException):
    """Invalid image source provided"""
    
class ImageProcessingError(BlurPlaceholderException):
    """Error during image processing"""
    
class CacheError(BlurPlaceholderException):
    """Cache-related error"""