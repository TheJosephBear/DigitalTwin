"""
Logger Service - Centralized logging configuration for Flask application
"""
import logging
import sys
import os


class LoggerService:
    """
    Centralized logging service that configures loggers based on environment.
    Handles both Gunicorn (production) and development/Vercel environments.
    """

    _logger = None
    _app = None

    @classmethod
    def configure_app_logger(cls, app):
        """
        Configure Flask app logger based on runtime environment.

        Args:
            app: Flask application instance

        Returns:
            Configured logger instance
        """
        cls._app = app

        # Always configure stdout logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )

        if __name__ != '__main__' and not os.getenv('VERCEL'):
            # Production: Running under Gunicorn (Docker)
            gunicorn_logger = logging.getLogger('gunicorn.error')
            app.logger.handlers = gunicorn_logger.handlers
            app.logger.setLevel(gunicorn_logger.level)
        else:
            # Development or Vercel: Use stdout directly
            app.logger.setLevel(logging.INFO)

        cls._logger = app.logger
        return app.logger

    @classmethod
    def log_startup_info(cls):
        """
        Log application startup information including environment variables.
        """
        cls.info("Logger initialized.")
        cls.info(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
        cls.info(f"VERCEL: {os.getenv('VERCEL')}")
        cls.info(f"Python version: {sys.version}")

    @classmethod
    def info(cls, message):
        """Log info level message"""
        if cls._logger:
            cls._logger.info(message)

    @classmethod
    def debug(cls, message):
        """Log debug level message"""
        if cls._logger:
            cls._logger.debug(message)

    @classmethod
    def warning(cls, message):
        """Log warning level message"""
        if cls._logger:
            cls._logger.warning(message)

    @classmethod
    def error(cls, message):
        """Log error level message"""
        if cls._logger:
            cls._logger.error(message)

    @classmethod
    def critical(cls, message):
        """Log critical level message"""
        if cls._logger:
            cls._logger.critical(message)

    @classmethod
    def create_request_logger(cls):
        """
        Create before_request handler for logging incoming requests.

        Returns:
            Decorated function for Flask's before_request
        """
        def log_request():
            """Log incoming requests for debugging"""
            if cls._app:
                from flask import request
                cls.info(f'{request.method} {request.path} - {request.remote_addr}')

        return log_request

    @classmethod
    def create_response_logger(cls):
        """
        Create after_request handler for logging response status.

        Returns:
            Decorated function for Flask's after_request
        """
        def log_response(response):
            """Log response status"""
            if cls._app:
                from flask import request
                cls.info(f'{request.method} {request.path} - {response.status_code}')
            return response

        return log_response
