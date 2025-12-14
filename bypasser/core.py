import logging
import re
import asyncio
from urllib.parse import urlparse, parse_qs
from typing import Dict, Optional
from config import Config
from .cloudflare import CloudflareBypasser
from .advanced import advanced_bypasser
from .sites import gdtot, sharerw, universal

logger = logging.getLogger(__name__)

class LinkBypasser:
    """Main link bypasser class"""
    
    def __init__(self):
        self.cf_bypasser = CloudflareBypasser()
        self.supported_sites = {
            # GDToT and variants
            'gdtot': ['gdtot', 'gdflix', 'gd.com'],
            'sharerw': ['sharer.pw', 'filepress'],
            'uptobox': ['uptobox.com'],
            'terabox': ['terabox.com', '1024tera.com', 'teraboxapp.com'],
            'anonfiles': ['anonfiles.com', 'bayfiles.com'],
            'linkvertise': ['linkvertise.com', 'link-to.net', 'up-to-down.net'],
            'adfly': ['adf.ly', 'ay.gy', 'j.gs'],
            'gplinks': ['gplinks.co', 'gplinks.in'],
            'ouo': ['ouo.io', 'ouo.press'],
            'shortingly': ['shortingly.in', 'bit.ly'],
            'droplink': ['droplink.co', 'droplink.org'],
            'linkbox': ['linkbox.to'],
            'wetransfer': ['wetransfer.com'],
            # Add more sites as needed
        }
    
    async def bypass(self, url: str) -> Dict:
        """Main bypass method"""
        try:
            logger.info(f"Starting bypass for: {url}")
            
            # Identify site type
            site_type = self._identify_site(url)
            
            if not site_type:
                return {
                    "success": False,
                    "error": "Unsupported site or unable to identify link type"
                }
            
            logger.info(f"Identified site type: {site_type}")
            
            # Route to appropriate bypasser
            if site_type == 'gdtot':
                result = await self._bypass_gdtot(url)
            elif site_type == 'sharerw':
                result = await self._bypass_sharerw(url)
            elif site_type == 'uptobox':
                result = await self._bypass_uptobox(url)
            elif site_type == 'terabox':
                result = await self._bypass_terabox(url)
            elif site_type in ['linkvertise', 'adfly', 'gplinks', 'ouo', 'shortingly', 'droplink']:
                result = await self._bypass_shortener(url, site_type)
            else:
                # Try universal bypasser
                result = await self._bypass_universal(url)
            
            return result
            
        except Exception as e:
            logger.error(f"Error bypassing {url}: {str(e)}")
            return {
                "success": False,
                "error": f"Bypass failed: {str(e)}"
            }
    
    def _identify_site(self, url: str) -> Optional[str]:
        """Identify the type of site from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            domain = domain.replace('www.', '')
            
            # Check against supported sites
            for site_type, domains in self.supported_sites.items():
                for supported_domain in domains:
                    if supported_domain in domain:
                        return site_type
            
            return None
            
        except Exception as e:
            logger.error(f"Error identifying site: {str(e)}")
            return None
    
    async def _bypass_gdtot(self, url: str) -> Dict:
        """Bypass GDToT links"""
        try:
            if not Config.GDTOT_CRYPT:
                return await universal.bypass_gdtot_alternative(url)
            
            result = await gdtot.bypass(url, Config.GDTOT_CRYPT)
            return result
            
        except Exception as e:
            logger.error(f"GDToT bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _bypass_sharerw(self, url: str) -> Dict:
        """Bypass Sharer.pw links"""
        try:
            if not Config.XSRF_TOKEN or not Config.LARAVEL_SESSION:
                return await universal.bypass_sharerw_alternative(url)
            
            result = await sharerw.bypass(url, Config.XSRF_TOKEN, Config.LARAVEL_SESSION)
            return result
            
        except Exception as e:
            logger.error(f"Sharer.pw bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _bypass_uptobox(self, url: str) -> Dict:
        """Bypass Uptobox links"""
        try:
            return await universal.bypass_uptobox(url, Config.UPTOBOX_TOKEN)
        except Exception as e:
            logger.error(f"Uptobox bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _bypass_terabox(self, url: str) -> Dict:
        """Bypass Terabox links"""
        try:
            return await universal.bypass_terabox(url, Config.TERA_COOKIE)
        except Exception as e:
            logger.error(f"Terabox bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _bypass_shortener(self, url: str, site_type: str) -> Dict:
        """Bypass various URL shorteners"""
        try:
            return await universal.bypass_shortener(url, site_type)
        except Exception as e:
            logger.error(f"Shortener bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _bypass_universal(self, url: str) -> Dict:
        """Universal bypass method for unknown sites"""
        try:
            # Try multiple strategies in order
            
            # 1. Try direct extraction with all methods (HTML, CSS, JS, etc.)
            logger.info("Trying direct extraction with multiple methods...")
            result = await universal.extract_direct_link(url)
            if result["success"]:
                return result
            
            # 2. Try Cloudflare bypass
            if Config.CLOUDFLARE_COOKIE:
                logger.info("Trying Cloudflare bypass...")
                result = await self.cf_bypasser.bypass(url)
                if result["success"]:
                    return result
            
            # 3. Try generic bypass methods
            logger.info("Trying generic bypass...")
            result = await universal.generic_bypass(url)
            if result["success"]:
                return result
            
            # 4. Try advanced browser automation (for complex JS sites)
            logger.info("Trying advanced browser automation...")
            result = await advanced_bypasser.bypass_with_browser(url)
            if result["success"]:
                return result
            
            return {
                "success": False,
                "error": "All bypass methods failed. Site may not be supported yet."
            }
            
        except Exception as e:
            logger.error(f"Universal bypass error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_supported_sites(self) -> list:
        """Get list of all supported sites"""
        sites = []
        for site_type, domains in self.supported_sites.items():
            sites.extend(domains)
        return sorted(set(sites))
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is from a supported site"""
        return self._identify_site(url) is not None
