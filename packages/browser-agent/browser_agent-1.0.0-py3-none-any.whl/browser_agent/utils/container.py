import docker
import logging
import time
from typing import Dict, Optional, Any
from ..core.config import Config


class ContainerManager:
    """Manages Docker containers for secure browser automation"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.container = None
        
        if config.use_container:
            try:
                self.client = docker.from_env()
                self.logger.info("Docker client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Docker client: {e}")
                raise
    
    def start_container(self, browser: str = "chrome") -> Dict[str, Any]:
        """Start a browser container"""
        if not self.config.use_container:
            return {'success': False, 'error': 'Container mode not enabled'}
        
        try:
            # Select appropriate image based on browser
            images = {
                'chrome': 'selenium/standalone-chrome:latest',
                'firefox': 'selenium/standalone-firefox:latest',
                'edge': 'selenium/standalone-edge:latest'
            }
            
            image = images.get(browser.lower(), self.config.container_image)
            
            # Container configuration
            container_config = {
                'image': image,
                'ports': {'4444/tcp': 4444},
                'environment': {
                    'VNC_NO_PASSWORD': '1',
                    'SCREEN_WIDTH': str(self.config.window_width),
                    'SCREEN_HEIGHT': str(self.config.window_height)
                },
                'detach': True,
                'remove': True,  # Auto-remove when stopped
                'shm_size': '2g'  # Increase shared memory for stability
            }
            
            # Add headless configuration if needed
            if self.config.headless:
                container_config['environment']['START_XVFB'] = 'false'
            
            self.logger.info(f"Starting container with image: {image}")
            self.container = self.client.containers.run(**container_config)
            
            # Wait for container to be ready
            self._wait_for_container_ready()
            
            return {
                'success': True,
                'container_id': self.container.id,
                'selenium_url': 'http://localhost:4444/wd/hub',
                'vnc_url': 'http://localhost:4444/vnc' if not self.config.headless else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start container: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _wait_for_container_ready(self, timeout: int = 60):
        """Wait for container to be ready to accept connections"""
        import requests
        
        start_time = time.time()
        selenium_url = "http://localhost:4444/wd/hub/status"
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(selenium_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('value', {}).get('ready', False):
                        self.logger.info("Container is ready")
                        return
            except:
                pass
            
            time.sleep(2)
        
        raise TimeoutError("Container failed to become ready within timeout")
    
    def stop_container(self):
        """Stop the running container"""
        if self.container:
            try:
                self.container.stop()
                self.logger.info("Container stopped")
                self.container = None
            except Exception as e:
                self.logger.error(f"Error stopping container: {e}")
    
    def get_container_logs(self) -> str:
        """Get container logs for debugging"""
        if self.container:
            try:
                return self.container.logs().decode('utf-8')
            except Exception as e:
                return f"Error getting logs: {e}"
        return "No container running"
    
    def is_container_running(self) -> bool:
        """Check if container is running"""
        if not self.container:
            return False
        
        try:
            self.container.reload()
            return self.container.status == 'running'
        except:
            return False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_container()