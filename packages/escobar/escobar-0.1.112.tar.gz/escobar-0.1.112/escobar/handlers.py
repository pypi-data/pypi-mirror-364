import json
import os
import re
import asyncio
import websockets
import ssl
import logging
import time
from urllib.parse import urlparse, urlunparse
from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.utils import url_path_join
import tornado
import tornado.web
import tornado.websocket
import aiohttp
from traitlets.config import LoggingConfigurable
import mimetypes
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# Default proxy port
DEFAULT_PROXY_PORT = 3000


class ProxyHandler(JupyterHandler):
    """
    Handler for /proxy endpoint.
    Proxies requests to http://localhost:<port>/<path>
    """
    async def _proxy_request(self, path_with_port, method='GET', body=None):
        # Extract port and path from the URL
        # Expected format: <port>/<path>
        match = re.match(r'^(\d+)(?:/(.*))?$', path_with_port)
        
        if match:
            port = match.group(1)
            path = match.group(2) or ''
            
            # Ensure port is an integer
            try:
                port = int(port)
            except (ValueError, TypeError):
                self.set_status(400)
                self.finish({"error": f"Invalid port: {port}"})
                return
        else:
            # If no port is specified in the URL, use the default port
            # and treat the entire path_with_port as the path
            port = DEFAULT_PROXY_PORT
            path = path_with_port
        
        # Log the port and path for debugging
        self.log.info(f"Proxying request to port {port}, path: {path}")
        
        # Construct the target URL with query parameters
        target_url = f"http://localhost:{port}/{path}"
        if self.request.query:
            target_url += f"?{self.request.query}"
        
        try:
            # Copy request headers
            headers = dict(self.request.headers)
            # Remove headers that might cause issues
            headers.pop('Host', None)
            headers.pop('Content-Length', None)
            
            # Make the request to the target URL with the same method
            async with aiohttp.ClientSession() as session:
                method_fn = getattr(session, method.lower())
                async with method_fn(target_url, headers=headers, data=body) as response:
                    # Log response details for debugging
                    self.log.info(f"Response status: {response.status}")
                    self.log.info(f"Response headers: {response.headers}")
                    
                    # Set the status code
                    self.set_status(response.status)
                    
                    # Get the content type
                    content_type = response.headers.get("Content-Type", "text/plain")
                    self.log.info(f"Content-Type: {content_type}")
                    
                    # Special handling for HTML content
                    if 'text/html' in content_type:
                        # For HTML content, we need to be extra careful
                        content = await response.text()
                        
                        # Clear any automatically added headers
                        self._headers = tornado.httputil.HTTPHeaders()
                        
                        # Set the content type explicitly
                        self.set_header("Content-Type", "text/html; charset=UTF-8")
                        
                        # Copy important headers from the original response
                        for header_name, header_value in response.headers.items():
                            if header_name.lower() in ('cache-control', 'etag', 'last-modified'):
                                self.set_header(header_name, header_value)
                        
                        # Write the content directly
                        self.write(content)
                        await self.finish()
                        return
                    
                    # For all other content types, copy all headers from the original response
                    for header_name, header_value in response.headers.items():
                        # Skip headers that would cause issues
                        if header_name.lower() not in ('content-length', 'transfer-encoding', 'content-encoding', 'connection'):
                            self.set_header(header_name, header_value)
                    
                    # Always set the Content-Type header explicitly
                    self.set_header("Content-Type", content_type)
                    
                    # Handle content based on content type
                    if 'application/json' in content_type:
                        # For JSON, parse and re-serialize to ensure proper formatting
                        data = await response.json()
                        self.write(json.dumps(data))
                    elif 'text/' in content_type or 'application/javascript' in content_type or 'application/xml' in content_type:
                        # For other text-based content
                        content = await response.text()
                        self.write(content)
                    else:
                        # For binary content
                        content = await response.read()
                        self.write(content)
                    
                    # Finish the response
                    await self.finish()
        except Exception as e:
            self.log.error(f"Proxy error: {str(e)}")
            self.set_status(500)
            self.finish({"error": str(e)})

    async def get(self, path_with_port):
        await self._proxy_request(path_with_port, 'GET')
    
    async def post(self, path_with_port):
        await self._proxy_request(path_with_port, 'POST', self.request.body)
    
    async def put(self, path_with_port):
        await self._proxy_request(path_with_port, 'PUT', self.request.body)
    
    async def delete(self, path_with_port):
        await self._proxy_request(path_with_port, 'DELETE')
    
    async def patch(self, path_with_port):
        await self._proxy_request(path_with_port, 'PATCH', self.request.body)
    
    async def head(self, path_with_port):
        await self._proxy_request(path_with_port, 'HEAD')
    
    async def options(self, path_with_port):
        await self._proxy_request(path_with_port, 'OPTIONS')


class OAuthCallbackHandler(JupyterHandler):
    """
    Handler for /static/escobar/oauth-callback.html endpoint.
    Serves the OAuth callback HTML file for Google authentication.
    """
    
    def _find_callback_file(self):
        """Find the OAuth callback HTML file in various possible locations"""
        import os
        import sys
        from pathlib import Path
        
        # List of possible locations to check
        possible_paths = []
        
        # 1. Development mode: static directory in project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        dev_path = os.path.join(project_root, 'static', 'oauth-callback.html')
        possible_paths.append(('Development', dev_path))
        
        # 2. Installed package: shared data directory
        # The file should be in share/jupyter/labextensions/escobar/static/
        try:
            import jupyter_core.paths
            data_dirs = jupyter_core.paths.jupyter_data_dir()
            if isinstance(data_dirs, str):
                data_dirs = [data_dirs]
            elif not isinstance(data_dirs, list):
                data_dirs = [data_dirs]
            
            for data_dir in data_dirs:
                shared_path = os.path.join(data_dir, 'labextensions', 'escobar', 'static', 'oauth-callback.html')
                possible_paths.append(('Jupyter shared data', shared_path))
        except Exception as e:
            self.log.debug(f"Could not get jupyter data dirs: {e}")
        
        # 3. Try to find via pkg_resources in the escobar package itself
        try:
            import pkg_resources
            # Try different possible resource paths
            resource_paths = [
                'static/oauth-callback.html',
                'labextension/static/oauth-callback.html'
            ]
            
            for resource_path in resource_paths:
                try:
                    if pkg_resources.resource_exists('escobar', resource_path):
                        # Return the content directly since pkg_resources handles the path
                        content = pkg_resources.resource_string('escobar', resource_path).decode('utf-8')
                        return ('Package resource', resource_path, content)
                except Exception as e:
                    self.log.debug(f"pkg_resources check failed for {resource_path}: {e}")
                    
        except ImportError:
            self.log.debug("pkg_resources not available")
        
        # 4. Check if file is bundled with the Python package
        try:
            escobar_module_path = os.path.dirname(os.path.abspath(__file__))
            bundled_path = os.path.join(escobar_module_path, 'static', 'oauth-callback.html')
            possible_paths.append(('Bundled with package', bundled_path))
        except Exception as e:
            self.log.debug(f"Could not determine escobar module path: {e}")
        
        # Check each possible file path
        for location_name, file_path in possible_paths:
            self.log.info(f"🔐 CALLBACK: Checking {location_name}: {file_path}")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return (location_name, file_path, content)
                except Exception as e:
                    self.log.warning(f"🔐 CALLBACK: Could not read {file_path}: {e}")
                    continue
        
        # If we get here, no file was found
        self.log.error(f"🔐 CALLBACK: OAuth callback file not found in any of these locations:")
        for location_name, file_path in possible_paths:
            self.log.error(f"🔐 CALLBACK:   - {location_name}: {file_path}")
        
        return None
    
    async def get(self):
        """Handle GET requests to serve the OAuth callback HTML"""
        try:
            # Find the callback file
            result = self._find_callback_file()
            
            if result is None:
                self.set_status(404)
                self.finish("OAuth callback file not found")
                return
            
            location_name, file_path, html_content = result
            
            self.log.info(f"🔐 CALLBACK: Serving OAuth callback from {location_name}: {file_path}")
            
            # Set proper headers
            self.set_header('Content-Type', 'text/html; charset=UTF-8')
            self.set_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.set_header('Pragma', 'no-cache')
            self.set_header('Expires', '0')
            
            # Write the HTML content
            self.write(html_content)
            self.log.info(f"🔐 CALLBACK: Successfully served OAuth callback HTML")
            
        except Exception as e:
            self.log.error(f"🔐 CALLBACK: Error serving OAuth callback: {e}")
            self.set_status(500)
            self.finish(f"Error serving OAuth callback: {str(e)}")


class WebSocketProxyHandler(tornado.websocket.WebSocketHandler):
    """
    WebSocket proxy handler that forwards connections from /ws to target server
    """
    
    def _resolve_target_url_for_docker(self, url):
        """
        Resolve target URL for Docker environment.
        Replace localhost/127.0.0.1 with Docker host IP when running in container.
        """
        # Enhanced Docker detection with multiple methods
        docker_indicators = []
        
        # Method 1: Check for /.dockerenv file
        dockerenv_exists = os.path.exists('/.dockerenv')
        docker_indicators.append(f"/.dockerenv exists: {dockerenv_exists}")
        
        # Method 2: Check environment variable
        docker_env = os.getenv('DOCKER_CONTAINER') == 'true'
        docker_indicators.append(f"DOCKER_CONTAINER env: {docker_env}")
        
        # Method 3: Check /proc/1/cgroup for docker
        cgroup_docker = False
        try:
            if os.path.exists('/proc/1/cgroup'):
                with open('/proc/1/cgroup', 'r') as f:
                    cgroup_content = f.read()
                    cgroup_docker = 'docker' in cgroup_content or 'containerd' in cgroup_content
                docker_indicators.append(f"/proc/1/cgroup contains docker/containerd: {cgroup_docker}")
        except Exception as e:
            docker_indicators.append(f"/proc/1/cgroup check failed: {e}")
        
        # Determine if we're in Docker
        is_docker = dockerenv_exists or docker_env or cgroup_docker
        
        if not is_docker:
            return url
        
        # Parse the URL to extract components
        parsed = urlparse(url)
        
        # Check if hostname is localhost or 127.0.0.1
        if parsed.hostname in ['localhost', '127.0.0.1']:
            # Replace with Docker host IP
            new_netloc = parsed.netloc.replace(parsed.hostname, '172.17.0.1')
            new_parsed = parsed._replace(netloc=new_netloc)
            new_url = urlunparse(new_parsed)
            
            return new_url
        
        return url
    
    def __init__(self, *args, **kwargs):
        print(f"[ESCOBAR-WS] WebSocketProxyHandler.__init__ called")
        super().__init__(*args, **kwargs)
        self.target_ws = None
        
        # Debug environment information
        print(f"[ESCOBAR-WS] Environment WEBSOCKET_PROXY_TARGET: {os.getenv('WEBSOCKET_PROXY_TARGET', 'NOT_SET')}")
        print(f"[ESCOBAR-WS] Running in container: {os.path.exists('/.dockerenv')}")
        try:
            print(f"[ESCOBAR-WS] Hostname: {os.uname().nodename}")
        except:
            print(f"[ESCOBAR-WS] Could not get hostname")
        
        # Store raw target URL from environment variable (resolve per-connection)
        self.raw_target_url = os.getenv('WEBSOCKET_PROXY_TARGET', 'ws://localhost:8777/ws')
        print(f"[ESCOBAR-WS] Raw target URL stored: {self.raw_target_url}")
        print(f"[ESCOBAR-WS] Docker resolution will be applied per-connection")
        
        # Debug all WebSocket-related environment variables
        websocket_env_vars = [(k, v) for k, v in os.environ.items() if 'WEBSOCKET' in k.upper()]
        print(f"[ESCOBAR-WS] All WEBSOCKET environment vars: {websocket_env_vars}")
        
        self.is_closing = False
    
    def _get_user_bonnie_url(self):
        """
        Get user-configured Bonnie URL from bonnie_url query parameter.
        This allows the frontend to override the environment variable.
        """
        try:
            # Get the bonnieUrl from query parameters
            bonnie_url = self.get_argument('bonnie_url', None)
            
            if bonnie_url and bonnie_url.strip():
                # Validate that it's a WebSocket URL
                if bonnie_url.startswith(('ws://', 'wss://')):
                    return bonnie_url.strip()
                else:
                    return None
            else:
                return None
                
        except Exception as e:
            print(f"[ESCOBAR-WS] Error reading bonnie_url query parameter: {e}")
            return None
    
    def _get_target_url(self):
        """
        Get the target URL with priority: User Setting > Environment Variable > Default
        """
        # Priority 1: User-configured Bonnie URL
        user_bonnie_url = self._get_user_bonnie_url()
        if user_bonnie_url:
            print(f"[ESCOBAR-WS] Using user-configured Bonnie URL: {user_bonnie_url}")
            return user_bonnie_url
        
        # Priority 2: Environment variable
        env_target_url = os.getenv('WEBSOCKET_PROXY_TARGET')
        if env_target_url:
            print(f"[ESCOBAR-WS] Using environment WEBSOCKET_PROXY_TARGET: {env_target_url}")
            return env_target_url
        
        # Priority 3: Default fallback
        default_url = 'ws://localhost:8777/ws'
        print(f"[ESCOBAR-WS] Using default target URL: {default_url}")
        return default_url
        
    def check_origin(self, origin):
        """Allow connections from any origin (adjust as needed for security)"""
        return True
    
    async def open(self):
        """Called when websocket connection is opened"""
        start_time = time.time()
        
        # Get target URL with priority: User Setting > Environment Variable > Default
        raw_target_url = self._get_target_url()
        
        # Apply Docker hostname resolution for this connection
        target_url = self._resolve_target_url_for_docker(raw_target_url)
        
        # Log which endpoint was accessed and path normalization
        request_path = self.request.path
        print(f"[ESCOBAR-WS] === CLIENT CONNECTION OPENED ===")
        print(f"[ESCOBAR-WS] Client connected via: {request_path}")
        print(f"[ESCOBAR-WS] Raw target URL: {raw_target_url}")
        print(f"[ESCOBAR-WS] Resolved target URL for this connection: {target_url}")
        if request_path != "/ws":
            print(f"[ESCOBAR-WS] Path normalization: {request_path} → /ws")
        
        print(f"[ESCOBAR-WS] Connection attempt started at {start_time}")
        print(f"[ESCOBAR-WS] Client origin: {self.request.headers.get('Origin', 'NO_ORIGIN')}")
        print(f"[ESCOBAR-WS] Client remote IP: {self.request.remote_ip}")
        print(f"[ESCOBAR-WS] Request headers: {dict(self.request.headers)}")
        print(f"[ESCOBAR-WS] Attempting to connect to target: {target_url}")
        
        try:
            # Establish connection to target websocket server
            # Copy relevant headers from the original request
            headers = {}
            
            # Forward authentication headers if present
            if 'Authorization' in self.request.headers:
                headers['Authorization'] = self.request.headers['Authorization']
                print(f"[ESCOBAR-WS] Forwarding Authorization header")
            if 'Cookie' in self.request.headers:
                headers['Cookie'] = self.request.headers['Cookie']
                print(f"[ESCOBAR-WS] Forwarding Cookie header")
            
            print(f"[ESCOBAR-WS] Headers to forward: {headers}")
            
            # Determine if we need SSL based on URL scheme
            use_ssl = target_url.startswith('wss://')
            ssl_context = ssl.create_default_context() if use_ssl else None
            print(f"[ESCOBAR-WS] Using SSL: {use_ssl}")
            
            print(f"[ESCOBAR-WS] Attempting websockets.connect() to {target_url}")
            
            # Connect to target websocket (works with both ws:// and wss://)
            self.target_ws = await websockets.connect(
                target_url,
                additional_headers=headers,
                ssl=ssl_context,
                ping_interval=45,
                ping_timeout=20,
                max_size=100 * 1024 * 1024 
            )
            
            end_time = time.time()
            print(f"[ESCOBAR-WS] Successfully connected to target server in {end_time - start_time:.2f} seconds")
            
            # Start listening for messages from target server
            print(f"[ESCOBAR-WS] Starting message forwarding task")
            asyncio.create_task(self._forward_from_target())
            
            print(f"[ESCOBAR-WS] === CONNECTION SETUP COMPLETE ===")
            
        except Exception as e:
            end_time = time.time()
            print(f"[ESCOBAR-WS] === CONNECTION FAILED ===")
            print(f"[ESCOBAR-WS] Connection failed after {end_time - start_time:.2f} seconds")
            print(f"[ESCOBAR-WS] Error: {str(e)}")
            print(f"[ESCOBAR-WS] Error type: {type(e).__name__}")
            print(f"[ESCOBAR-WS] Target URL: {target_url}")
            if hasattr(e, 'errno'):
                print(f"[ESCOBAR-WS] Errno: {e.errno}")
            if hasattr(e, 'strerror'):
                print(f"[ESCOBAR-WS] Strerror: {e.strerror}")
            print(f"[ESCOBAR-WS] === END CONNECTION FAILED ===")
            
            logging.error(f"Failed to connect to target websocket {target_url}: {str(e)}")
            self.close(code=1011, reason=f"Failed to connect to target server: {target_url}")
    
    async def on_message(self, message):
        """Called when a message is received from the client"""
        if self.target_ws and not self.is_closing:
            try:
                # Check for ping messages and handle silently
                try:
                    data = json.loads(message)
                    if data.get('method') == 'ping':
                        return  # Silent ping handling - no logging, no forwarding
                except (json.JSONDecodeError, TypeError):
                    pass  # Not JSON or not a dict, continue with normal processing
                
                # Forward message to target server
                await self.target_ws.send(message)
            except Exception as e:
                print(f"[ESCOBAR-WS] ERROR forwarding message to target:")
                print(f"[ESCOBAR-WS]   Error: {str(e)}")
                print(f"[ESCOBAR-WS]   Error type: {type(e).__name__}")
                logging.error(f"Error forwarding message to target: {str(e)}")
                self.close(code=1011, reason="Target connection error")
    
    async def _forward_from_target(self):
        """Forward messages from target server to client"""
        try:
            async for message in self.target_ws:
                if not self.is_closing:
                    # Forward message to client
                    self.write_message(message)
                else:
                    break
                
        except websockets.exceptions.ConnectionClosed as e:
            if not self.is_closing:
                self.close(code=1011, reason="Target server disconnected")
        except Exception as e:
            print(f"[ESCOBAR-WS] === TARGET MESSAGE FORWARDING ERROR ===")
            print(f"[ESCOBAR-WS] Error: {str(e)}")
            print(f"[ESCOBAR-WS] Error type: {type(e).__name__}")
            if hasattr(e, 'errno'):
                print(f"[ESCOBAR-WS] Errno: {e.errno}")
            if hasattr(e, 'strerror'):
                print(f"[ESCOBAR-WS] Strerror: {e.strerror}")
            print(f"[ESCOBAR-WS] === END TARGET MESSAGE FORWARDING ERROR ===")
            
            logging.error(f"Error receiving from target websocket: {str(e)}")
            if not self.is_closing:
                self.close(code=1011, reason="Target connection error")
    
    def on_close(self):
        """Called when websocket connection is closed"""
        self.is_closing = True
        
        # Close target connection if it exists
        if self.target_ws:
            asyncio.create_task(self._close_target_connection())
    
    async def _close_target_connection(self):
        """Safely close the target websocket connection"""
        try:
            if self.target_ws:
                # Check if connection is already closed using the correct websockets library API
                try:
                    is_closed = self.target_ws.state.name == 'CLOSED'
                except AttributeError:
                    # Fallback: just try to close it regardless of state
                    is_closed = False
                
                if not is_closed:
                    await self.target_ws.close()
        except Exception as e:
            print(f"[ESCOBAR-WS] ERROR closing target connection:")
            print(f"[ESCOBAR-WS]   Error: {str(e)}")
            print(f"[ESCOBAR-WS]   Error type: {type(e).__name__}")
            logging.error(f"Error closing target websocket: {str(e)}")


def _find_and_parse_env_file():
    """
    Find and parse .env file to extract GCP_CLIENT_ID.
    Returns tuple: (found_value, source_description)
    """
    print(f"[ESCOBAR-ENV] === SEARCHING FOR .ENV FILE ===")
    
    # List of possible .env file locations
    possible_env_paths = [
        ("/app/.env", "Docker mount location"),
        (".env", "Current working directory"),
        ("../.env", "Parent directory"),
        (os.path.expanduser("~/.env"), "Home directory")
    ]
    
    # Add current working directory info
    current_dir = os.getcwd()
    print(f"[ESCOBAR-ENV] Current working directory: {current_dir}")
    
    for env_path, description in possible_env_paths:
        print(f"[ESCOBAR-ENV] Checking {description}: {env_path}")
        
        try:
            # Check if file exists
            if not os.path.exists(env_path):
                print(f"[ESCOBAR-ENV]   ❌ File does not exist")
                continue
            
            # Check if file is readable
            if not os.access(env_path, os.R_OK):
                print(f"[ESCOBAR-ENV]   ❌ File exists but is not readable")
                continue
            
            print(f"[ESCOBAR-ENV]   ✅ File exists and is readable")
            
            # Read and parse the file
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"[ESCOBAR-ENV]   📄 File size: {len(content)} characters")
            
            # Parse each line looking for GCP_CLIENT_ID
            lines = content.splitlines()
            print(f"[ESCOBAR-ENV]   📄 File has {len(lines)} lines")
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Look for GCP_CLIENT_ID
                if line.startswith('GCP_CLIENT_ID='):
                    value = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    if value:
                        print(f"[ESCOBAR-ENV]   ✅ Found GCP_CLIENT_ID on line {line_num}")
                        print(f"[ESCOBAR-ENV]   🔑 Value: {value[:20]}...{value[-10:] if len(value) > 30 else value}")
                        return value, f"{description} ({env_path})"
                    else:
                        print(f"[ESCOBAR-ENV]   ⚠️  Found GCP_CLIENT_ID on line {line_num} but value is empty")
            
            print(f"[ESCOBAR-ENV]   ❌ GCP_CLIENT_ID not found in file")
            
        except Exception as e:
            print(f"[ESCOBAR-ENV]   ❌ Error reading file: {e}")
            continue
    
    print(f"[ESCOBAR-ENV] === .ENV FILE SEARCH COMPLETE - NOT FOUND ===")
    return None, None


def _get_gcp_client_id_from_environment():
    """
    Get GCP_CLIENT_ID from environment with comprehensive logging.
    Priority: .env file > system environment variable
    Returns tuple: (value, source_description)
    """
    print(f"[ESCOBAR-ENV] === SEARCHING FOR GCP_CLIENT_ID ===")
    
    # Step 1: Check .env file first
    env_file_value, env_file_source = _find_and_parse_env_file()
    if env_file_value:
        print(f"[ESCOBAR-ENV] ✅ Found GCP_CLIENT_ID in {env_file_source}")
        return env_file_value.strip(), env_file_source
    
    # Step 2: Check system environment variable
    print(f"[ESCOBAR-ENV] Checking system environment variable...")
    system_env_value = os.getenv('GCP_CLIENT_ID', '').strip()
    
    if system_env_value:
        print(f"[ESCOBAR-ENV] ✅ Found GCP_CLIENT_ID in system environment")
        print(f"[ESCOBAR-ENV] 🔑 Value: {system_env_value[:20]}...{system_env_value[-10:] if len(system_env_value) > 30 else system_env_value}")
        return system_env_value, "system environment variable"
    else:
        print(f"[ESCOBAR-ENV] ❌ GCP_CLIENT_ID not found in system environment")
    
    # Step 3: Show all environment variables for debugging
    print(f"[ESCOBAR-ENV] === DEBUGGING: ALL ENVIRONMENT VARIABLES ===")
    gcp_related_vars = [(k, v) for k, v in os.environ.items() 
                       if any(term in k.upper() for term in ['GCP', 'GOOGLE', 'CLIENT', 'OAUTH'])]
    
    if gcp_related_vars:
        print(f"[ESCOBAR-ENV] Found {len(gcp_related_vars)} potentially related environment variables:")
        for key, value in gcp_related_vars:
            masked_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else value
            print(f"[ESCOBAR-ENV]   {key}={masked_value}")
    else:
        print(f"[ESCOBAR-ENV] No GCP/Google/Client/OAuth related environment variables found")
    
    print(f"[ESCOBAR-ENV] === GCP_CLIENT_ID SEARCH COMPLETE - NOT FOUND ===")
    return None, None


async def auto_configure_google_client_id(settings_manager):
    """
    Safely auto-configure Google Client ID from GCP_CLIENT_ID environment variable.
    Only sets the value if user hasn't configured it in JupyterLab settings.
    Handles all error cases gracefully without crashing.
    """
    print(f"[ESCOBAR] === GOOGLE CLIENT ID AUTO-CONFIGURATION START ===")
    
    try:
        # Step 1: Always search for GCP_CLIENT_ID with comprehensive logging
        gcp_client_id, source = _get_gcp_client_id_from_environment()
        
        if not gcp_client_id:
            print(f"[ESCOBAR] ❌ No GCP_CLIENT_ID found in any source, skipping auto-configuration")
            print(f"[ESCOBAR] === GOOGLE CLIENT ID AUTO-CONFIGURATION END ===")
            return
        
        print(f"[ESCOBAR] ✅ Found GCP_CLIENT_ID from {source}")
        
        # Step 2: Check if settings manager is available
        if settings_manager is None:
            print(f"[ESCOBAR] ⚠️  Settings manager not available - cannot save to JupyterLab settings")
            print(f"[ESCOBAR] 💡 Google Client ID found but will need to be configured manually in JupyterLab")
            print(f"[ESCOBAR] 🔑 Value to configure: {gcp_client_id[:20]}...{gcp_client_id[-10:] if len(gcp_client_id) > 30 else gcp_client_id}")
            print(f"[ESCOBAR] === GOOGLE CLIENT ID AUTO-CONFIGURATION END ===")
            return
        
        print(f"[ESCOBAR] 🔍 Settings manager available, checking current user settings...")
        
        # Step 3: Check current user settings and save if needed
        try:
            plugin_settings = await settings_manager.get('escobar:plugin')
            current_settings = plugin_settings.get('composite', {})
            current_google_client_id = current_settings.get('googleClientId', '').strip()
            
            print(f"[ESCOBAR] 📋 Current user googleClientId: {'<empty>' if not current_google_client_id else '<configured>'}")
            
            # Step 4: Only set if user hasn't configured a value
            if not current_google_client_id:
                print(f"[ESCOBAR] 🔧 User has not configured googleClientId, setting from {source}")
                await settings_manager.set('escobar:plugin', 'googleClientId', gcp_client_id)
                print(f"[ESCOBAR] ✅ Successfully auto-configured Google Client ID from {source}")
                
                # Verify the setting was saved
                verification_settings = await settings_manager.get('escobar:plugin')
                verification_value = verification_settings.get('composite', {}).get('googleClientId', '')
                if verification_value == gcp_client_id:
                    print(f"[ESCOBAR] ✅ Verification: Setting was saved correctly")
                else:
                    print(f"[ESCOBAR] ⚠️  Verification: Setting may not have been saved correctly")
            else:
                print(f"[ESCOBAR] ℹ️  User has already configured googleClientId, respecting user choice")
                
        except Exception as settings_error:
            print(f"[ESCOBAR] ❌ Could not access or modify JupyterLab settings: {settings_error}")
            print(f"[ESCOBAR] ℹ️  This is non-fatal - Google Client ID can still be configured manually in JupyterLab settings")
            
    except Exception as e:
        print(f"[ESCOBAR] ❌ Error during Google Client ID auto-configuration: {e}")
        print(f"[ESCOBAR] ℹ️  This is non-fatal - Google Client ID can still be configured manually in JupyterLab settings")
    
    print(f"[ESCOBAR] === GOOGLE CLIENT ID AUTO-CONFIGURATION END ===")


def setup_handlers(web_app):
    print(f"[ESCOBAR-WS] === SETTING UP HANDLERS ===")
    
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    print(f"[ESCOBAR-WS] Host pattern: {host_pattern}")
    print(f"[ESCOBAR-WS] Base URL: {base_url}")
    
    # Debug web_app settings to find settings manager
    print(f"[ESCOBAR-WS] Web app settings keys: {list(web_app.settings.keys())}")
    
    # Try to find the settings manager
    settings_manager = None
    
    # Method 1: Check if it's directly in web_app.settings
    if 'settings_manager' in web_app.settings:
        settings_manager = web_app.settings['settings_manager']
        print(f"[ESCOBAR-WS] Found settings manager in web_app.settings")
    
    # Method 2: Check if there's a serverapp with settings manager
    elif hasattr(web_app, 'serverapp') and hasattr(web_app.serverapp, 'settings_manager'):
        settings_manager = web_app.serverapp.settings_manager
        print(f"[ESCOBAR-WS] Found settings manager in web_app.serverapp")
    
    # Method 3: Check if there's a parent app with settings manager
    elif hasattr(web_app, 'parent') and hasattr(web_app.parent, 'settings_manager'):
        settings_manager = web_app.parent.settings_manager
        print(f"[ESCOBAR-WS] Found settings manager in web_app.parent")
    
    # Method 4: Try to import and get the settings manager directly
    else:
        try:
            from jupyter_server.services.settings.manager import SettingsManager
            # Try to create a settings manager instance
            settings_manager = SettingsManager()
            print(f"[ESCOBAR-WS] Created new settings manager instance")
        except Exception as e:
            print(f"[ESCOBAR-WS] Could not create settings manager: {e}")
    
    print(f"[ESCOBAR-WS] Settings manager: {settings_manager}")
    print(f"[ESCOBAR-WS] Settings manager type: {type(settings_manager) if settings_manager else 'None'}")
    
    # Store the settings manager in web_app.settings for handlers to access
    if settings_manager:
        web_app.settings['settings_manager'] = settings_manager
        print(f"[ESCOBAR-WS] Stored settings manager in web_app.settings")
    else:
        print(f"[ESCOBAR-WS] WARNING: No settings manager available - user bonnieUrl will not work")
    
    # Always run Google Client ID auto-configuration (with or without settings manager)
    print(f"[ESCOBAR] About to schedule Google Client ID auto-configuration...")
    try:
        import asyncio
        print(f"[ESCOBAR] Asyncio imported successfully")
        loop = asyncio.get_event_loop()
        print(f"[ESCOBAR] Got event loop: {loop}")
        print(f"[ESCOBAR] Event loop is running: {loop.is_running()}")
        
        if loop.is_running():
            print(f"[ESCOBAR] Event loop is running, creating task...")
            task = asyncio.create_task(auto_configure_google_client_id(settings_manager))
            print(f"[ESCOBAR] Task created successfully: {task}")
        else:
            print(f"[ESCOBAR] Event loop not running, running until complete...")
            loop.run_until_complete(auto_configure_google_client_id(settings_manager))
            print(f"[ESCOBAR] Run until complete finished")
            
        print(f"[ESCOBAR] Google Client ID auto-configuration scheduled successfully")
        
    except Exception as e:
        print(f"[ESCOBAR] Could not schedule Google Client ID auto-configuration: {e}")
        print(f"[ESCOBAR] Exception type: {type(e).__name__}")
        import traceback
        print(f"[ESCOBAR] Traceback: {traceback.format_exc()}")
        print(f"[ESCOBAR] This is non-fatal - Google Client ID can still be configured manually")
    
    # Register the /proxy endpoint with a path parameter
    proxy_pattern = url_path_join(base_url, "proxy", "(.*)")
    print(f"[ESCOBAR-WS] Proxy pattern: {proxy_pattern}")
    
    # Register multiple WebSocket proxy endpoints that all route to the same backend
    ws_patterns = [
        url_path_join(base_url, "ws"),           # /ws
        url_path_join(base_url, "hub", "ws"),    # /hub/ws  
        url_path_join(base_url, "voitta", "ws")  # /voitta/ws
    ]
    
    print(f"[ESCOBAR-WS] WebSocket proxy patterns:")
    for pattern in ws_patterns:
        print(f"[ESCOBAR-WS]   - {pattern}")
    
    # Register OAuth callback endpoints with /static/escobar/ path
    oauth_patterns = [
        "/hub/static/escobar/oauth-callback.html",     # OAuth callback from Google (JupyterHub)
        "/static/escobar/oauth-callback.html"          # Direct access (standalone or root)
    ]
    
    print(f"[ESCOBAR-WS] OAuth callback patterns:")
    for pattern in oauth_patterns:
        print(f"[ESCOBAR-WS]   - {pattern}")
    
    # Build handlers list with OAuth callback and WebSocket patterns
    handlers = [
        (proxy_pattern, ProxyHandler),
        *[(pattern, OAuthCallbackHandler) for pattern in oauth_patterns],
        *[(pattern, WebSocketProxyHandler) for pattern in ws_patterns]
    ]
    
    print(f"[ESCOBAR-WS] Registering {len(handlers)} handlers")
    print(f"[ESCOBAR-WS] Handler patterns: {[h[0] for h in handlers]}")
    
    web_app.add_handlers(host_pattern, handlers)
    
    print(f"[ESCOBAR-WS] Handlers registered successfully")
    print(f"[ESCOBAR-WS] WebSocket proxy endpoints available:")
    for pattern in ws_patterns:
        print(f"[ESCOBAR-WS]   - {pattern} → ws://localhost:8777/ws")
    print(f"[ESCOBAR-WS] === END SETTING UP HANDLERS ===")
