"""
Invoice system monitoring and error prevention middleware
"""

import logging
import time
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger(__name__)


class InvoiceErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle and log invoice-related errors
    """
    
    def process_exception(self, request, exception):
        """
        Handle exceptions that occur during invoice operations
        """
        # Only handle invoice-related requests
        if not request.path.startswith('/api/invoices/'):
            return None
        
        # Log the error with context
        logger.error(
            f"Invoice operation failed: {str(exception)}",
            extra={
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                'path': request.path,
                'method': request.method,
                'data': getattr(request, 'data', {}),
                'exception_type': type(exception).__name__,
            }
        )
        
        # Return a user-friendly error response
        if settings.DEBUG:
            # In debug mode, show detailed error
            return JsonResponse({
                'error': 'Invoice operation failed',
                'detail': str(exception),
                'type': type(exception).__name__
            }, status=500)
        else:
            # In production, show generic error
            return JsonResponse({
                'error': 'We encountered an issue processing your invoice. Please try again or contact support.'
            }, status=500)


class InvoicePerformanceMiddleware(MiddlewareMixin):
    """
    Middleware to monitor invoice operation performance
    """
    
    def process_request(self, request):
        """
        Start timing for invoice requests
        """
        if request.path.startswith('/api/invoices/'):
            request._invoice_start_time = time.time()
    
    def process_response(self, request, response):
        """
        Log performance metrics for invoice operations
        """
        if (hasattr(request, '_invoice_start_time') and 
            request.path.startswith('/api/invoices/')):
            
            duration = time.time() - request._invoice_start_time
            
            # Log slow operations
            if duration > 2.0:  # More than 2 seconds
                logger.warning(
                    f"Slow invoice operation: {request.path} took {duration:.2f}s",
                    extra={
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'path': request.path,
                        'method': request.method,
                        'duration': duration,
                        'status_code': response.status_code
                    }
                )
            else:
                logger.info(
                    f"Invoice operation: {request.path} completed in {duration:.2f}s",
                    extra={
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                        'path': request.path,
                        'method': request.method,
                        'duration': duration,
                        'status_code': response.status_code
                    }
                )
        
        return response
