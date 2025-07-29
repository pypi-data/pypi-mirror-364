"""
Business rule validation for import operations.

This module handles business rule validation for import operations,
including validation rules for import operations.
"""

from typing import Dict, List, Any
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from colegia_core.models import Accommodation
from django.core.validators import validate_email
import logging
import re

logger = logging.getLogger(__name__)


class BusinessValidator:
    """
    Handles business rule validation for import operations.
    """
    
    @classmethod
    def _validate_url_field(cls, value: str, field_name: str) -> List[str]:
        """
        Validate URL format.
        """
        errors = []
        if value and not bool(re.fullmatch(r'(http|www\.).+', value, flags=re.IGNORECASE)):
            errors.append(_("Invalid URL format for field {field_name}").format(field_name=field_name))
        return errors
    
    @classmethod
    def _validate_required_field(cls, value: str, field_name: str) -> List[str]:
        """
        Validate required field.
        
        Args:
            name (str): Name to validate
            is_required (bool): Whether name is required
            
        Returns:
            list: Validation errors
        """
        errors = []
        value = value.strip() if value else ''
        
        if not value:
            errors.append(_("Value is required for field {field_name}").format(field_name=field_name))
        
        return errors
    
    @classmethod
    def _validate_max_length_field(cls, value: str, field_name: str, max_length: int) -> List[str]:
        """
        Validate max length field.
        """
        errors = []
        value = value.strip() if value else ''
        
        if len(value) > max_length:
            errors.append(
                _(
                    "Value is too long (maximum {max_length} characters) for field {field_name}").format(
                        max_length=max_length, 
                        field_name=field_name
                    )
                )
        
        return errors
    
    @classmethod
    def _validate_email_field(cls, email: str, field_name: str) -> List[str]:
        """
        Validate email format.
        
        Args:
            email (str): Email to validate
            
        Returns:
            list: Validation errors
        """
        errors = []
        email = email.strip() if email else ''
        
        if email:
            try:
                validate_email(email)
            except ValidationError:
                errors.append(
                    _(
                        "Invalid email format for field {field_name}").format(
                            field_name=field_name
                        )
                    )
        
        return errors
    
    @classmethod
    def _validate_positive_numeric_field(cls, value: float, field_name: str) -> List[str]:
        """
        Validate positive numeric field.
        
        Args:
            data (dict): Data containing numeric fields
            
        Returns:
            list: Validation errors
        """
        errors = []
        if value is not None and value < 0:
            errors.append(
                _(
                    "Value must be positive for field {field_name}").format(
                        field_name=field_name
                    )
                )
            
        return errors
    
    
    @classmethod
    def _validate_instance_exists(cls, instance_id: int, model_class: Any) -> List[str]:
        """
        Validate if instance can be deleted.
        
        Args:
            instance_id (int): ID of instance to delete
            model_class (Any): Model class of instance
            
        Returns:
            list: List of validation errors
        """
        errors = []
        model_class_name = model_class.__name__
        # Add debugging
        logger.info(f"Business validation INSTANCE EXISTS for ID: {instance_id} (type: {model_class_name})")
        
        # Check if accommodation exists
        try:
            instance = model_class.objects.get(id=instance_id)
            logger.info(f"Found instance: {instance.name} (ID: {instance.id})")
        except model_class.DoesNotExist:
            logger.info(f"Instance lookup failed for ID: {instance_id}")
            errors.append(_("Instance with ID {id} does not exist").format(id=instance_id))
            return errors
        
        logger.info(f"Business validation INSTANCE EXISTS complete for ID {instance_id}: {len(errors)} errors")
        return errors
    
    
    def validate_create(self, data: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("validate_create not implemented")
    
    def validate_update(self, instance_id: int, data: Dict[str, Any]) -> List[str]:
        raise NotImplementedError("validate_update not implemented")
    
    def validate_delete(self, instance_id: int) -> List[str]:
        raise NotImplementedError("validate_delete not implemented")

