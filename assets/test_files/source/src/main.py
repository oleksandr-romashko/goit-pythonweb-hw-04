from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import mimetypes
from pathlib import Path
import urllib.parse

from jinja2 import Environment, FileSystemLoader, select_autoescape

from decorators.handle_server_errors import handle_server_errors
from storage.storage import MessageStorage
from utils.constants import (
    TIMESTAMP_STORAGE_FORMAT,
    SUPPORTED_ASSET_PATHS,
    NEW_STATUS_DURATION_SEC,
)
from utils.validations import validate_form_data, validate_is_safe_path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    _storage_file_path = (
        Path(__file__).parent / "storage" / "data" / "data.json"
    ).resolve()

    _web_base_dir_path = (Path(__file__).parent / "web").resolve()

    _static_dir_path = (_web_base_dir_path / "static").resolve()
    _template_dir_path = (_web_base_dir_path / "templates").resolve()

    _jinja_env = Environment(
        loader=FileSystemLoader(_template_dir_path),
        autoescape=select_autoescape(["html", "xml"]),
    )

    _message_storage = MessageStorage(_storage_file_path)

    def do_GET(self) -> None:
        """Handles all GET requests to the server."""
        logging.info("Handling %s request for path: %s", self.command, self.path)

        # Define request path
        url_path = urllib.parse.urlparse(self.path)
        req_path = url_path.path

        # Redirect direct *.html access to its clean equivalent
        # * e.g. localhost/message.htm -> localhost/message
        if req_path.endswith(".html"):
            pretty_path = req_path.removesuffix(".html")
            self.redirect_to(location=pretty_path or "/", status_code=301)
            return

        # Main route dispatcher for GET methods
        match req_path:
            case "/":
                self.send_html_page("index.html")
            case "/message":
                self.send_html_page("message.html")
            case "/read":
                self.send_rendered_read_page()
            case _:
                suffix = Path(req_path).suffix
                if suffix in SUPPORTED_ASSET_PATHS:
                    # Serve static asset
                    filename = Path(req_path).name
                    self.send_asset_file(filename, suffix)
                    return

                # Handle unknown resource
                self.send_rendered_error_page(
                    error_message=(
                        "Page not found. "
                        "The page you're looking for doesn't exist or might have been moved."
                    ),
                    error_code=404,
                )

    @handle_server_errors()
    def do_POST(self):
        """Handles all POST requests to the server."""
        logging.info("Handling %s request for path: %s", self.command, self.path)

        # Retrieve request data
        content_length = self.headers.get("Content-Length")
        if content_length is None:
            self.send_response(411)  # Length Required
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"411 Length Required: Missing Content-Length header.")
            return
        data_raw = self.rfile.read(int(content_length))
        data_parsed = urllib.parse.unquote_plus(data_raw.decode("utf-8"))
        form_data_dict = dict(urllib.parse.parse_qsl(data_parsed))

        # Basic form validation for empty form
        try:
            message_data = validate_form_data(form_data_dict)
        except ValueError as exc:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"400 Bad request. Reason: {exc}".encode("utf-8"))
            return

        # Save message data to storage
        self._message_storage.save_message(message_data)

        # Response with redirect
        self.redirect_to(location="/read", status_code=302)

    @handle_server_errors()
    def send_html_page(self, filename: str, status: int = 200):
        """Send static html page"""
        # Define page paths
        base_dir_path = (self._static_dir_path / "pages").resolve()
        file_path = (base_dir_path / filename).resolve()

        # Improve static file serving security (prevent Path Traversal)
        if not validate_is_safe_path(base_dir_path, file_path):
            self.send_forbidden()
            return

        # Try read file content
        try:
            with open(file_path, "rb") as fh:
                content = fh.read()
        except FileNotFoundError:
            self.send_rendered_error_page(
                error_message=(
                    "Page not found. "
                    "The page you're looking for doesn't exist or might have been moved."
                ),
                error_code=404,
            )
            return

        # Send response only after ensuring we have content
        self.send_response(status)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_asset_file(self, filename, suffix):
        """Send static asset file"""
        # Define asset paths
        base_dir_name = SUPPORTED_ASSET_PATHS[suffix]
        base_dir_path = (self._static_dir_path / base_dir_name).resolve()
        file_path = (base_dir_path / filename).resolve()

        # Improve static file serving security (prevent Path Traversal)
        if not validate_is_safe_path(base_dir_path, file_path):
            self.send_forbidden()
            return

        # Try read file content
        try:
            with open(file_path, "rb") as fh:
                content = fh.read()
        except FileNotFoundError:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404 File not found")
            return
        except (PermissionError, OSError):
            logging.error(
                "%s. File: %s. %s.",
                "Error while reading asset file",
                file_path,
                "PermissionError or OSError was raised",
            )
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"500 Internal server error.")
            return

        # Define asset mime type (e.g. image/png)
        mime_type = mimetypes.guess_type(file_path)[0] or "text/plain"

        # Send response only after ensuring we have content
        self.send_response(200)
        self.send_header("Content-Type", mime_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    @handle_server_errors()
    def send_rendered_read_page(self):
        """Send rendered page with all messages"""
        # Get all messages from storage
        messages_data = {}
        messages_data = self._message_storage.get_all()

        # Form list of messages
        messages_list = []
        for timestamp_str, msg in messages_data.items():
            datetime_obj = datetime.strptime(timestamp_str, TIMESTAMP_STORAGE_FORMAT)
            datetime_obj = datetime_obj.replace(tzinfo=timezone.utc)
            formatted_timestamp_str = datetime_obj.isoformat()

            username = msg.get("username") or "Anonymous user"
            message = msg.get("message") or "No message"

            time_diff = datetime.now(timezone.utc) - datetime_obj
            is_new = time_diff.total_seconds() < NEW_STATUS_DURATION_SEC

            messages_list.append(
                {
                    "sort_key": datetime_obj,
                    "timestamp": formatted_timestamp_str,
                    "username": username,
                    "message": message,
                    "is_new": is_new,
                }
            )

        # Sort by latest message on top
        messages_list.sort(key=lambda x: x["sort_key"], reverse=True)

        # Clean-up to ensure serialization
        for message in messages_list:
            del message["sort_key"]

        # Render page based on template using messages
        rendered_page = self.render_template("read.html", messages=messages_list)

        # Form response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(rendered_page.encode("utf-8"))

    def send_rendered_error_page(
        self, error_message: str = "Unknown error", error_code: int = 500
    ):
        """Renders error page with error code and error message"""
        # Render error page based on page template
        rendered_page = self.render_template(
            "error.html",
            error_code=error_code,
            error_message=error_message,
        )

        # Form response with rendered page
        self.send_response(error_code)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(rendered_page.encode("utf-8"))

    def render_template(self, template_name, **render_data):
        """Render page base on template and provided data"""
        # Load template file
        template = self._jinja_env.get_template(template_name)

        # Return rendered page
        return template.render(**render_data)

    def redirect_to(self, location: str, status_code: int = 302) -> None:
        """Redirects client to other location"""
        self.send_response(status_code)
        self.send_header("Location", location)
        self.end_headers()

    def send_forbidden(self):
        """Send forbidden response"""
        self.send_response(403)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"403 Forbidden")


def run():
    """Run server"""
    host = "0.0.0.0"
    port = 3000
    server_address = (host, port)
    httpd = HTTPServer(server_address, HTTPRequestHandler)

    try:
        logging.info("Starting server at http://localhost:%s", port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        logging.info("Server is stopped.")


if __name__ == "__main__":
    run()
