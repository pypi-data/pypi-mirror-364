"""
Content extraction orchestrator that coordinates multiple extraction strategies.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from ..extractors import (
    BaseExtractor, 
    LdJsonExtractor, 
    ReadabilityExtractor, 
    SelectorExtractor, 
    FullPageExtractor
)
from .config import ScrapingConfig

logger = logging.getLogger(__name__)


class ContentExtractor:
    """Orchestrates multiple content extraction strategies"""
    
    def __init__(self, config: ScrapingConfig):
        self.config = config
        self.extractors: List[BaseExtractor] = []
        self._initialize_extractors()
    
    def _initialize_extractors(self):
        """Initialize all extraction strategies in priority order"""
        self.extractors = [
            LdJsonExtractor(self.config),
            ReadabilityExtractor(self.config),
            SelectorExtractor(self.config),
            FullPageExtractor(self.config)
        ]
        
        # Sort by priority (higher number = higher priority, so reverse=True)
        self.extractors.sort(key=lambda x: x.get_extraction_priority(), reverse=True)
        
        logger.info(f"Initialized {len(self.extractors)} content extractors in order: {[e.__class__.__name__ for e in self.extractors]}")
    
    async def extract_content(self, url: str, html_content: str) -> Optional[Dict[str, Any]]:
        """
        Extract content using the best available strategy.
        
        Args:
            url: The URL being scraped
            html_content: Raw HTML content
            
        Returns:
            Dict with title, body, and extraction_method, or None if all fail
        """
        try:
            # Creating BeautifulSoup object once to pass to extractors if they need it
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Try each extractor in priority order
            for extractor in self.extractors:
                logger.debug(f"Trying {extractor.__class__.__name__} for {url}")
                try:
                    # Pass both html_content and soup, extractor can choose
                    result = await extractor.extract(html_content=html_content, url=url, soup=soup)
                    
                    if result and self._is_quality_content(result, url): # Pass URL for logging in quality check
                        logger.debug(f"Successfully extracted content using {extractor.__class__.__name__} for {url}")
                        # Ensure 'extraction_method' is present, if not add it from class name
                        if 'extraction_method' not in result or not result['extraction_method']:
                            result['extraction_method'] = extractor.__class__.__name__
                        return result
                    else:
                        logger.debug(f"{extractor.__class__.__name__} produced low-quality or no content for {url}")
                except Exception as e_inner:
                    logger.warning(f"Extractor {extractor.__class__.__name__} failed for {url}: {e_inner}", exc_info=True)
            
            logger.warning(f"All extractors failed to produce quality content for {url}")
            return None
            
        except Exception as e_outer:
            logger.error(f"Content extraction orchestrator failed for {url}: {e_outer}", exc_info=True)
            return None
    
    def _is_quality_content(self, content: Dict[str, Any], url: str) -> bool: 
        """
        Evaluate if extracted content meets quality thresholds
        
        Args:
            content: Extracted content dict
            url: The URL being scraped (for logging)
            
        Returns:
            True if content meets quality standards
        """
        if not content or not isinstance(content, dict):
            logger.debug(f"Content is None or not a dict for {url}")
            return False
        
        title = content.get('title', '').strip()
        body = content.get('body', '')
        
        if isinstance(body, str):
            body = body.strip()
        elif body is None:
            body = ""

        # Check minimum length requirements
        if not body:
            logger.debug(f"Body is empty for {url}. Title: '{title[:50]}...'")
            return False
        
        min_body_length = getattr(self.config, 'min_body_length', 50)  # More lenient default
        if len(body) < min_body_length:
            logger.debug(f"Body too short for {url}: {len(body)} < {min_body_length}. Title: '{title[:50]}...'")
            return False
        
        # Title is good to have, but not strictly required if body is substantial
        min_title_length = getattr(self.config, 'min_title_length', 5)
        if title and len(title) < min_title_length:
            logger.debug(f"Title present but too short for {url}: {len(title)} < {min_title_length}. Body length: {len(body)}")
            # Allow it to pass if body is substantial
        
        # Check for suspicious patterns (only if body is string)
        if isinstance(body, str):
            suspicious_patterns = getattr(self.config, 'suspicious_patterns', [
                'javascript required',
                'enable javascript',
                'cookie policy',
                'privacy policy',
                'terms of service'
            ])
            
            body_lower = body.lower()
            for pattern in suspicious_patterns:
                if pattern in body_lower and len(body) < (min_body_length + 200):
                    logger.debug(f"Suspicious pattern '{pattern}' detected in relatively short body for {url}")
                    return False
        
        # Title/body ratio check (only if both are strings and body is not empty)
        if isinstance(title, str) and isinstance(body, str) and body:
            ratio_threshold = getattr(self.config, 'title_body_ratio_threshold', 0.5)
            if len(body) > 0:
                title_body_ratio = len(title) / len(body)
                if title_body_ratio > ratio_threshold and len(title) > 20:
                    logger.debug(f"Poor title/body ratio for {url}: {title_body_ratio} > {ratio_threshold}. Title: '{title[:50]}...', Body len: {len(body)}")
                    return False
        
        logger.debug(f"Content deemed quality for {url}. Method: {content.get('extraction_method', 'N/A')}, Title: '{title[:50]}...', Body len: {len(body) if body else 0}")
        return True
    
    def get_extractor_info(self) -> List[Dict[str, Any]]: # Changed type hint for Any
        """Get information about available extractors"""
        return [
            {
                'name': extractor.__class__.__name__,
                'priority': extractor.get_extraction_priority(), # Use method
                'description': extractor.__doc__ or 'No description'
            }
            for extractor in self.extractors
        ]