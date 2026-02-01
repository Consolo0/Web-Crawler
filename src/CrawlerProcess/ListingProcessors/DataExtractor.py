"""
DataExtractor: Utility class for extracting and parsing product data.

This class consolidates common extraction methods used across all listing processors,
following the Single Responsibility Principle and DRY (Don't Repeat Yourself).
"""

from typing import Optional, Dict
import re
import json
from bs4 import BeautifulSoup


class DataExtractor:
    """
    Centralized utility for extracting and parsing data from HTML content.
    
    Provides methods for:
    - Extracting JSON-LD structured data
    - Parsing price values
    - Parsing rating values
    - Parsing vote counts
    """
    
    @staticmethod
    def extract_json_ld(soup: BeautifulSoup) -> Optional[Dict]:
        """
        Extract JSON-LD structured data from script tags.
        
        JSON-LD is a standardized format for embedding structured data in HTML.
        This method searches for script tags with type="application/ld+json"
        and returns the first one that contains a 'name' field.
        
        Args:
            soup: BeautifulSoup object of the HTML content
            
        Returns:
            Dictionary containing the JSON-LD data, or None if not found
        """
        try:
            script_tags = soup.find_all("script", type="application/ld+json")
            for script in script_tags:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if isinstance(data, dict) and "name" in data:
                            return data
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass
        return None
    
    @staticmethod
    def extract_price_value(text: str) -> Optional[float]:
        """
        Extract numeric price from text.
        
        Handles various formats like:
        - "$45,990.50"
        - "45990,50 CLP"
        - "$ 45.990,00"
        
        Args:
            text: Text containing price information
            
        Returns:
            Float value of the price, or None if extraction fails
        """
        if not text:
            return None
        try:
            # Remove common currency symbols and spaces
            clean = re.sub(r'[^\d.,]', '', text).strip()
            if clean:
                # Replace comma with dot for decimal
                clean = clean.replace(',', '.')
                return float(clean)
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def extract_rating_value(text: str) -> Optional[float]:
        """
        Extract rating value from text.
        
        Expects a numeric value between 0-5.
        Handles formats like:
        - "4.5 stars"
        - "Rating: 4.88"
        - "4,88 de 5"
        
        Args:
            text: Text containing rating information
            
        Returns:
            Float value (0-5), or None if not found or out of range
        """
        if not text:
            return None
        try:
            # Extract first number that looks like a rating (0-5)
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
        except (ValueError, AttributeError):
            pass
        return None
    
    @staticmethod
    def extract_votes_value(text: str) -> Optional[int]:
        """
        Extract number of votes/reviews from text.
        
        Handles formats like:
        - "188 reviews"
        - "5 opiniones"
        - "(123)"
        
        Args:
            text: Text containing vote count information
            
        Returns:
            Integer count of votes, or None if extraction fails
        """
        if not text:
            return None
        try:
            # Extract the number
            match = re.search(r'(\d+)', text)
            if match:
                return int(match.group(1))
        except (ValueError, AttributeError):
            pass
        return None
