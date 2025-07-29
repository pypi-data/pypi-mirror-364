"""
Choice Field Mappings for Import Processing

This module handles mapping between user-facing text (Spanish translations)
and model choice field values for import operations.
"""

class BaseChoiceMappings:
    """
    Basic choice field mappings for import operations.
    Maps Spanish translations to actual model choice values.
    """

    
    # Boolean field mappings
    BOOLEAN_MAPPINGS = {
        # Spanish variations
        'sí': True,
        'Si': True,  # Without accent
        'no': False,
        
        # English variations
        'yes': True,
        'no': False,
        
        # Numeric/symbol variations
        '1': True,
        '0': False,
        'X': True,
        '': False,
        
        # Common variations
        'true': True,
        'false': False,
    }
    
    @classmethod
    def get_boolean_value(cls, text_value):
        """
        Get boolean value from text input.
        
        Args:
            text_value (str): User input text (e.g., "Sí", "No")
            
        Returns:
            bool or None: Boolean value or None if not found
        """
        if text_value is None:
            return None
            
        text_value = str(text_value).strip()
        
        # Try exact match first
        if text_value in cls.BOOLEAN_MAPPINGS:
            return cls.BOOLEAN_MAPPINGS[text_value]
        
        # Try case-insensitive match
        for key, value in cls.BOOLEAN_MAPPINGS.items():
            if key.lower() == text_value.lower():
                return value
                
        return None
    
    
    @classmethod
    def validate_eliminate_column(cls, text_value):
        """
        Validate ELIMINATE column value.
        
        Args:
            text_value (str): User input text
            
        Returns:
            bool: True if record should be deleted, False otherwise
        """
        if not text_value:
            return False
        
        text_value = str(text_value).strip().upper()
        return text_value == 'X'
