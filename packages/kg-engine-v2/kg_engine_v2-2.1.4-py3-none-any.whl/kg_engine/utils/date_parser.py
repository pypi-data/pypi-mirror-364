"""
Date parsing utilities for Knowledge Graph Engine v2
Uses dateparser library for robust natural language date parsing
"""
import re
from datetime import datetime
from typing import Optional, Tuple
import dateparser


class DateParser:
    """Enhanced date parser using dateparser library for natural language support"""
    
    def __init__(self):
        # Configure dateparser settings
        self.parser_settings = {
            'PREFER_DAY_OF_MONTH': 'first',  # When day is ambiguous, prefer first of month
            'PREFER_DATES_FROM': 'past',     # When year is ambiguous, prefer past dates
            'RETURN_AS_TIMEZONE_AWARE': False,  # Return naive datetime objects
            'DATE_ORDER': 'MDY',             # Default to US date order
            'STRICT_PARSING': False,         # Allow fuzzy parsing
        }
        
        # Extended list of temporal indicators for text extraction
        self.temporal_indicators = [
            # Specific dates
            r'\b(?:on\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
            r'\b(?:on\s+)?\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            r'\b(?:on\s+)?\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            
            # Relative dates
            r'\b(?:since|from|until|before|after|during)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
            r'\b(?:since|from|until|before|after)\s+\d{4}\b',
            r'\b(?:in|during)\s+(?:the\s+)?(?:early|mid|late)\s+\d{4}s?\b',
            r'\b(?:in|during)\s+\d{4}\b',
            
            # Common relative expressions
            r'\b(?:yesterday|today|tomorrow|last\s+week|next\s+week|last\s+month|next\s+month|last\s+year|next\s+year)\b',
            r'\b(?:a\s+few\s+(?:days|weeks|months|years)\s+ago)\b',
            r'\b(?:recently|lately|now|currently)\b',
            
            # Period expressions
            r'\b(?:between|from)\s+\d{4}\s+(?:and|to)\s+\d{4}\b',
            r'\b(?:from|since)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\s+(?:to|until)\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b',
        ]
    
    def parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse various date formats using dateparser library"""
        if not date_str:
            return None
        
        try:
            # Use dateparser library for robust parsing
            parsed_date = dateparser.parse(
                date_str.strip(), 
                settings=self.parser_settings
            )
            return parsed_date
        except Exception as e:
            print(f"Warning: Could not parse date '{date_str}': {e}")
            return None
    
    def extract_date_from_text(self, text: str) -> Tuple[Optional[datetime], str]:
        """Extract temporal information from text using advanced pattern matching"""
        if not text:
            return None, text
        
        original_text = text
        extracted_date = None
        
        # Try each temporal pattern
        for pattern in self.temporal_indicators:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                date_text = match.group(0)
                
                # Clean the date text by removing prepositions
                clean_date_text = re.sub(
                    r'^\b(?:on|in|since|from|until|before|after|during|the)\s+',
                    '', 
                    date_text, 
                    flags=re.IGNORECASE
                ).strip()
                
                # Try to parse the cleaned date
                parsed_date = self.parse_date(clean_date_text)
                
                if parsed_date:
                    # Remove the date expression from text
                    text = text.replace(date_text, '').strip()
                    # Clean up multiple spaces
                    text = re.sub(r'\s+', ' ', text)
                    extracted_date = parsed_date
                    break
            
            if extracted_date:
                break
        
        return extracted_date, text if text.strip() else original_text
    
    def parse_date_range(self, text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract date ranges from text (e.g., 'from 2020 to 2023', 'between Jan 2021 and Dec 2022')"""
        if not text:
            return None, None
        
        # Pattern for "from X to Y" or "between X and Y"
        range_patterns = [
            r'\b(?:from|between)\s+([^,\s]+(?:\s+\d{1,2}(?:st|nd|rd|th)?)?,?\s+\d{4})\s+(?:to|and|until)\s+([^,\s]+(?:\s+\d{1,2}(?:st|nd|rd|th)?)?,?\s+\d{4})\b',
            r'\b(?:from|between)\s+(\d{4})\s+(?:to|and|until)\s+(\d{4})\b',
        ]
        
        for pattern in range_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start_str, end_str = match.groups()
                start_date = self.parse_date(start_str)
                end_date = self.parse_date(end_str)
                
                if start_date and end_date:
                    return start_date, end_date
        
        return None, None
    
    def is_temporal_expression(self, text: str) -> bool:
        """Check if text contains temporal expressions"""
        if not text:
            return False
        
        for pattern in self.temporal_indicators:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def normalize_relative_date(self, date_str: str) -> Optional[str]:
        """Convert relative dates to absolute dates for better consistency"""
        if not date_str:
            return None
        
        # Let dateparser handle the relative date conversion
        parsed = self.parse_date(date_str)
        if parsed:
            return parsed.strftime("%Y-%m-%d")
        
        return None