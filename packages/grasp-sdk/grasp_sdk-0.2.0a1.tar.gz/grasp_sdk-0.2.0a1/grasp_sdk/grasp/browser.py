"""GraspBrowser class for browser interface."""

import aiohttp
from typing import Optional, Dict, Any

from ..services.browser import CDPConnection


class GraspBrowser:
    """Browser interface for Grasp session."""
    
    def __init__(self, connection: CDPConnection):
        """Initialize GraspBrowser.
        
        Args:
            connection: CDP connection instance
        """
        self.connection = connection
    
    def get_endpoint(self) -> str:
        """Get browser WebSocket endpoint URL.
        
        Returns:
            WebSocket URL for browser connection
        """
        return self.connection.ws_url
    
    async def get_current_page_target_info(self) -> Optional[Dict[str, Any]]:
        """Get current page target information.
        
        Warning:
            This method is experimental and may change or be removed in future versions.
            Use with caution in production environments.
        
        Returns:
            Dictionary containing target info and last screenshot, or None if failed
        """
        host = self.connection.http_url
        api = f"{host}/api/page/info"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api) as response:
                    if not response.ok:
                        return None
                    
                    data = await response.json()
                    page_info = data.get('pageInfo', {})
                    last_screenshot = page_info.get('lastScreenshot')
                    session_id = page_info.get('sessionId')
                    targets = page_info.get('targets', {})
                    
                    if session_id and session_id in targets:
                        target_info = targets[session_id].copy()
                        target_info['lastScreenshot'] = last_screenshot
                        return target_info
                    
                    return None
        except Exception:
            return None
    
    def get_liveview_url(self) -> Optional[str]:
        """Get liveview URL (TODO: implementation pending).
        
        Returns:
            Liveview URL or None
        """
        # TODO: Implement liveview URL generation
        return None