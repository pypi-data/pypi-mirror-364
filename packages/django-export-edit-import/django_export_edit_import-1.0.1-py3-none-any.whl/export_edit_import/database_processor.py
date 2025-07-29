
from typing import Dict, List, Any, Optional, Tuple
from django.db import transaction
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from export_edit_import.enums import OperationTypes
from export_edit_import.business_validator import BusinessValidator
import pandas as pd
import re
import html
import logging
from export_edit_import.enums import DATABASE_PROCESSOR_KEYS, RESULTS_KEYS, PROCESSED_ROW_KEYS, PROCESSED_ROWS_TYPES

logger = logging.getLogger(__name__)


class DatabaseProcessor:
    """
    Handles database operations for imports.
    """
    
    required_fields = []
    
    def __init__(self, columns: List[Dict], validator: BusinessValidator, instance_class: Any):
        self.columns = columns
        self.validator = validator()
        self.instance_class = instance_class
    
    def process_import_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process accommodation import data with database operations.
        
        Args:
            processed_data (dict): Data from Excel processor
            
        Returns:
            dict: Updated processing results with database validation
        """
        results = {
            DATABASE_PROCESSOR_KEYS.CREATE_READY.value: [],
            DATABASE_PROCESSOR_KEYS.UPDATE_READY.value: [],
            DATABASE_PROCESSOR_KEYS.DELETE_READY.value: [],
            DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value: [],
            DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value: [],
            DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value: [],
            DATABASE_PROCESSOR_KEYS.DATABASE_ERRORS.value: []
        }
        
        # Process each operation type
        results[DATABASE_PROCESSOR_KEYS.CREATE_READY.value], results[DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value] = self._process_create_operations(
            processed_data.get(PROCESSED_ROWS_TYPES.CREATE_ROWS.value, [])
        )
        
        results[DATABASE_PROCESSOR_KEYS.UPDATE_READY.value], results[DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value] = self._process_update_operations(
            processed_data.get(PROCESSED_ROWS_TYPES.UPDATE_ROWS.value, [])
        )
        
        results[DATABASE_PROCESSOR_KEYS.DELETE_READY.value], results[DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value] = self._process_delete_operations(
            processed_data.get(PROCESSED_ROWS_TYPES.DELETE_ROWS.value, [])
        )
        
        # Add existing error rows
        results[DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value] = processed_data.get(PROCESSED_ROWS_TYPES.ERROR_ROWS.value, [])
        
        return results
    
    def _process_create_operations(self, create_rows: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Process CREATE operations with database validation.
        
        Args:
            create_rows (list): Rows for creating new accommodations
            
        Returns:
            tuple: (ready_for_creation, error_rows)
        """
        ready_rows = []
        error_rows = []
        
        for row in create_rows:
            try:
                # Validate business rules
                validation_errors = self.validator.validate_create(row[RESULTS_KEYS.PROCESSED_DATA.value])
                
                if validation_errors:
                    # Add validation errors to row
                    row[PROCESSED_ROW_KEYS.ERRORS.value].extend(validation_errors)
                    row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                    error_rows.append(row)
                else:
                    row[DATABASE_PROCESSOR_KEYS.FINAL_DATA.value] = self._prepare_data(row[RESULTS_KEYS.PROCESSED_DATA.value])
                    ready_rows.append(row)
                    
            except Exception as e:
                logger.error(f"CREATE processing error for row {row.get(PROCESSED_ROW_KEYS.ROW_NUMBER.value, 'unknown')}: {type(e).__name__}: {str(e)}")
                row.setdefault(PROCESSED_ROW_KEYS.ERRORS.value, [])
                row[PROCESSED_ROW_KEYS.ERRORS.value].append(f"Database validation error: {type(e).__name__}: {str(e)}")
                row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                error_rows.append(row)
        
        return ready_rows, error_rows
    
    def get_field_label(self, field_name: str) -> str:
        """
        Get the label of the field.
        """
        return next(column.get('label') for column in self.columns if column.get('field_name') == field_name)
    
    def get_id_label(self) -> str:
        """
        Get the label of the ID column.
        """
        return self.get_field_label('id')
    
    def _process_update_operations(self, update_rows: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Process UPDATE operations with database validation.
        
        Args:
            update_rows (list): Rows for updating existing instances
            
        Returns:
            tuple: (ready_for_update, error_rows)
        """
        ready_rows = []
        error_rows = []
        id_label = self.get_id_label()
        
        for row in update_rows:
            try:
                instance_id = row[RESULTS_KEYS.PROCESSED_DATA.value][id_label]
                
                # Validate business rules
                validation_errors = self.validator.validate_update(
                    instance_id, row[RESULTS_KEYS.PROCESSED_DATA.value]
                )
                
                if validation_errors:
                    row.setdefault(PROCESSED_ROW_KEYS.ERRORS.value, [])
                    row[PROCESSED_ROW_KEYS.ERRORS.value].extend(validation_errors)
                    row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                    error_rows.append(row)
                else:
                    # Get existing accommodation for update
                    try:
                        existing_instance = self.instance_class.objects.get(id=instance_id)
                        row[DATABASE_PROCESSOR_KEYS.EXISTING_INSTANCE.value] = existing_instance
                        row[DATABASE_PROCESSOR_KEYS.FINAL_DATA.value] = self._prepare_data(row[RESULTS_KEYS.PROCESSED_DATA.value])
                        ready_rows.append(row)

                    except self.instance_class.DoesNotExist:
                        row.setdefault(PROCESSED_ROW_KEYS.ERRORS.value, [])
                        row[PROCESSED_ROW_KEYS.ERRORS.value].append(_("Instance with ID {id} not found").format(id=instance_id))
                        row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                        error_rows.append(row)
                    
            except Exception as e:
                logger.error(f"UPDATE processing error for row {row.get(PROCESSED_ROW_KEYS.ROW_NUMBER.value, 'unknown')}: {type(e).__name__}: {str(e)}")
                # Add the actual exception details to the row
                row.setdefault(PROCESSED_ROW_KEYS.ERRORS.value, [])
                row[PROCESSED_ROW_KEYS.ERRORS.value].append(f"Database validation error: {type(e).__name__}: {str(e)}")
                row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                error_rows.append(row)
        
        return ready_rows, error_rows
    
    def _process_delete_operations(self, delete_rows: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Process DELETE operations with database validation.
        
        Args:
            delete_rows (list): Rows for deleting accommodations
            
        Returns:
            tuple: (ready_for_deletion, error_rows)
        """
        ready_rows = []
        error_rows = []
        id_label = self.get_id_label()
        for row in delete_rows:
            try:
                instance_id = row[RESULTS_KEYS.PROCESSED_DATA.value][id_label]
                
                # Validate business rules
                validation_errors = self.validator.validate_delete(instance_id)
                
                if validation_errors:
                    row[PROCESSED_ROW_KEYS.ERRORS.value].extend(validation_errors)
                    row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                    error_rows.append(row)
                else:
                    # Get existing accommodation for deletion
                    try:
                        existing_instance = self.instance_class.objects.get(id=instance_id)
                        row[DATABASE_PROCESSOR_KEYS.EXISTING_INSTANCE.value] = existing_instance
                        ready_rows.append(row)
                        
                    except self.instance_class.DoesNotExist:
                        row[PROCESSED_ROW_KEYS.ERRORS.value].append(_("Instance with ID {id} not found").format(id=instance_id))
                        row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                        error_rows.append(row)
                        
            except Exception as e:
                logger.error(f"DELETE processing error for row {row.get(PROCESSED_ROW_KEYS.ROW_NUMBER.value, 'unknown')}: {type(e).__name__}: {str(e)}")
                row.setdefault(PROCESSED_ROW_KEYS.ERRORS.value, [])
                row[PROCESSED_ROW_KEYS.ERRORS.value].append(f"Database validation error: {type(e).__name__}: {str(e)}")
                row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                error_rows.append(row)
        
        return ready_rows, error_rows
    
    
    def add_additional_data_in_row(self, final_row_data: Dict[str, Any], processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add additional data to final data.
        """
        return final_row_data
    
    
    def _prepare_data(self, data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        """
        Prepare final data for database operations.
        
        Args:
            data (dict): Processed data
            *args: Additional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            dict: Final data ready for database insertion/update
        """
        final_data = {}
        
        # Map Excel columns to model fields using .value attribute
        columns = [column for column in self.columns if column.get('field_name') != 'id']
        
        # Copy data using column definitions
        for column in columns:
            if column.get('label') in data:
                value = data[column.get('label')]
                
                if field_method := getattr(self, f"configure_final_data_of_{column.get('field_name')}", None):
                    final_data = field_method(final_data, column, value)
                
                else:
                    if value is not None or column.get('field_name') in self.required_fields:
                        final_data[column.get('field_name')] = value
                        
        final_data = self.add_additional_data_in_row(final_data, data)
        
        return final_data
    
    def execute_database_operations(self, ready_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database operations for accommodations.
        
        Args:
            ready_data (dict): Data ready for database operations
            
        Returns:
            dict: Execution results with counts and errors
        """
        results = {
            DATABASE_PROCESSOR_KEYS.CREATED_COUNT.value: 0,
            DATABASE_PROCESSOR_KEYS.UPDATED_COUNT.value: 0,
            DATABASE_PROCESSOR_KEYS.DELETED_COUNT.value: 0,
            DATABASE_PROCESSOR_KEYS.CREATED_ITEMS.value: [],
            DATABASE_PROCESSOR_KEYS.UPDATED_ITEMS.value: [],
            DATABASE_PROCESSOR_KEYS.DELETED_ITEMS.value: [],
            DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value: []
        }
        
        # Log what we're about to execute
        logger.info(f"Starting database operations:")
        logger.info(f"- Create operations: {len(ready_data.get(DATABASE_PROCESSOR_KEYS.CREATE_READY.value, []))}")
        logger.info(f"- Update operations: {len(ready_data.get(DATABASE_PROCESSOR_KEYS.UPDATE_READY.value, []))}")
        logger.info(f"- Delete operations: {len(ready_data.get(DATABASE_PROCESSOR_KEYS.DELETE_READY.value, []))}")
        
        try:
            with transaction.atomic():
                # Execute CREATE operations
                create_ready = ready_data.get(DATABASE_PROCESSOR_KEYS.CREATE_READY.value, [])
                logger.info(f"Executing {len(create_ready)} create operations...")
                for row in create_ready:
                    try:
                        instance = self.instance_class.objects.create(**row[DATABASE_PROCESSOR_KEYS.FINAL_DATA.value])
                        results[DATABASE_PROCESSOR_KEYS.CREATED_ITEMS.value].append({
                            'id': instance.id,
                            'name': str(instance),
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]
                        })
                        results[DATABASE_PROCESSOR_KEYS.CREATED_COUNT.value] += 1
                        logger.info(f"Created instance ID {instance.id}: {instance}")
                    except Exception as e:
                        logger.error(f"Error creating instance at row {row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]}: {str(e)}")
                        results[DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value].append({
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value],
                            PROCESSED_ROW_KEYS.OPERATION.value: OperationTypes.CREATE.value,
                            PROCESSED_ROW_KEYS.ERRORS.value: str(e)
                        })
                
                # Execute UPDATE operations
                update_ready = ready_data.get(DATABASE_PROCESSOR_KEYS.UPDATE_READY.value, [])
                logger.info(f"Executing {len(update_ready)} update operations...")
                for row in update_ready:
                    try:
                        instance = row[DATABASE_PROCESSOR_KEYS.EXISTING_INSTANCE.value]
                        original_name = str(instance)
                        for field, value in row[DATABASE_PROCESSOR_KEYS.FINAL_DATA.value].items():
                            setattr(instance, field, value)
                        instance.save()
                        
                        results[DATABASE_PROCESSOR_KEYS.UPDATED_ITEMS.value].append({
                            'id': instance.id,
                            'name': str(instance),
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]
                        })
                        results[DATABASE_PROCESSOR_KEYS.UPDATED_COUNT.value] += 1
                        logger.info(f"Updated instance ID {instance.id}: {original_name} -> {str(instance)}")
                    except Exception as e:
                        logger.error(f"Error updating instance at row {row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]}: {str(e)}")
                        results[DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value].append({
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value],
                            PROCESSED_ROW_KEYS.OPERATION.value: OperationTypes.UPDATE.value,
                            PROCESSED_ROW_KEYS.ERRORS.value: str(e)
                        })
                
                # Execute DELETE operations
                delete_ready = ready_data.get(DATABASE_PROCESSOR_KEYS.DELETE_READY.value, [])
                logger.info(f"Executing {len(delete_ready)} delete operations...")
                for row in delete_ready:
                    try:
                        instance = row[DATABASE_PROCESSOR_KEYS.EXISTING_INSTANCE.value]
                        deleted_info = {
                            'id': instance.id,
                            'name': str(instance),
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]
                        }
                        instance.delete()
                        
                        results[DATABASE_PROCESSOR_KEYS.DELETED_ITEMS.value].append(deleted_info)
                        results[DATABASE_PROCESSOR_KEYS.DELETED_COUNT.value] += 1
                        logger.info(f"Deleted instance ID {deleted_info['id']}: {deleted_info['name']}")
                    except Exception as e:
                        logger.error(f"Error deleting instance at row {row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]}: {str(e)}")
                        results[DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value].append({
                            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row[PROCESSED_ROW_KEYS.ROW_NUMBER.value],
                            PROCESSED_ROW_KEYS.OPERATION.value: OperationTypes.DELETE.value,
                            PROCESSED_ROW_KEYS.ERRORS.value: str(e)
                        })
                        
        except Exception as e:
            # If transaction fails, all operations are rolled back
            logger.error(f"Transaction failed: {str(e)}")
            results[DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value].append({
                PROCESSED_ROW_KEYS.ERRORS.value: _("Transaction failed: {error}").format(error=str(e)),
                PROCESSED_ROW_KEYS.OPERATION.value: OperationTypes.TRANSACTION.value
            })
        
        logger.info(f"Database operations completed:")
        logger.info(f"- Created: {results[DATABASE_PROCESSOR_KEYS.CREATED_COUNT.value]}")
        logger.info(f"- Updated: {results[DATABASE_PROCESSOR_KEYS.UPDATED_COUNT.value]}")
        logger.info(f"- Deleted: {results[DATABASE_PROCESSOR_KEYS.DELETED_COUNT.value]}")
        logger.info(f"- Errors: {len(results[DATABASE_PROCESSOR_KEYS.OPERATION_ERRORS.value])}")
        
        return results 