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

    @staticmethod
    def _describe_log_level(level):
        """Convert a numeric log level to its name when possible."""
        for level_name, level_value in logging.getLevelNamesMapping().items():
            if level_value == level:
                return level_name

        return str(level)

    @staticmethod
    def _resolve_log_level():
        """Resolve the configured log level from the environment."""
        level_name = os.getenv("LOG_LEVEL", "INFO").strip().upper()

        if level_name.isdigit():
            return int(level_name)

        return getattr(logging, level_name, logging.INFO)

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

        log_level = cls._resolve_log_level()

        # Always configure stdout logging first
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )

        if __name__ != '__main__' and not os.getenv('VERCEL'):
            # Production: Running under Gunicorn (Docker)
            gunicorn_logger = logging.getLogger('gunicorn.error')
            app.logger.handlers = gunicorn_logger.handlers
        else:
            # Development or Vercel: Use stdout directly
            pass

        app.logger.setLevel(log_level)

        cls._logger = app.logger
        cls.info(f"Log level set to {cls._describe_log_level(app.logger.level)}")
        return app.logger

    @classmethod
    def log_startup_info(cls):
        """
        Log application startup information including environment variables.
        """
        cls.info("Logger initialized.")
        cls.info(f"FLASK_ENV: {os.getenv('FLASK_ENV')}")
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
