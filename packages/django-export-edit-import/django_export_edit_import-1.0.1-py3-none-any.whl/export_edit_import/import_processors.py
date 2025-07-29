"""
Excel Processing Engine for Import Operations

This module handles reading, validating, and processing Excel files
for accommodation and activity imports.
"""

import pandas as pd
from typing import Dict, List, Tuple, Any
from django.utils.translation import gettext as _
from export_edit_import.enums import (
    DELETE_FLAG_LABEL, 
    OperationTypes,
    PROCESSED_ROWS_TYPES,
    PROCESSED_ROW_KEYS,
    RESULTS_KEYS
)
from django.contrib.contenttypes.models import ContentType
from export_edit_import.base_choice_mapping import BaseChoiceMappings
import logging

logger = logging.getLogger(__name__)


DEFAULT_FIELD_PROCESSORS_NAMES = [
    'process_id_field',
    'process_text_field',
    'process_boolean_field',
    'process_decimal_field',
    'process_email_field',
    'process_url_field',
]


class ExcelStructureValidator:
    """
    Validates Excel file structure and required columns.
    """
    
    @staticmethod
    def validate_structure(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate that Excel file has required columns for import.
        
        Args:
            df (pd.DataFrame): DataFrame from Excel file
            model_type (str): Type of model being imported
            
        Returns:
            tuple: (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append(_("The Excel file is empty"))
        
        is_valid = len(errors) == 0
        return is_valid, errors


class ExcelDataProcessor:
    """
    Processes Excel data into structured format for import operations.
    """
    
    def __init__(
        self, 
        model_type: ContentType, 
        columns: List[Dict[str, Any]], 
        choice_mappings_class: BaseChoiceMappings,
    ):
        self.model_type = model_type
        self.model_class = self._get_model_class()
        self.columns = columns
        self.choice_mappings = choice_mappings_class()

    def _get_model_class(self):
        if self.model_type:
            return self.model_type.model_class()
        
        raise ValueError(f"Model type is required")
    
    def _get_id_label(self):
        return next(column['label'] for column in self.columns if column['field_name'] == 'id')
    
    def read_excel_file(self, file_path: str) -> Tuple[bool, pd.DataFrame, List[str]]:
        """
        Read Excel file and return DataFrame.
        
        Args:
            file_path (str): Path to Excel file
            
        Returns:
            tuple: (success, dataframe, errors)
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Convert all column names to strings and strip whitespace
            df.columns = [str(col).strip() for col in df.columns]
            
            # Replace NaN values with empty strings for better processing
            df = df.fillna('')
            
            return True, df, []
            
        except Exception as e:
            error_msg = f"{_('Error reading Excel file:')} {str(e)}"
            return False, pd.DataFrame(), [error_msg]
    
    def process_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Process DataFrame into structured import data.
        
        Args:
            df (pd.DataFrame): DataFrame from Excel file
            
        Returns:
            dict: Processed data with categorized rows and errors
        """
        result = {
            PROCESSED_ROWS_TYPES.CREATE_ROWS.value: [],
            PROCESSED_ROWS_TYPES.UPDATE_ROWS.value: [],
            PROCESSED_ROWS_TYPES.DELETE_ROWS.value: [],
            PROCESSED_ROWS_TYPES.ERROR_ROWS.value: [],
            PROCESSED_ROWS_TYPES.TOTAL_ROWS.value: len(df),
            PROCESSED_ROWS_TYPES.DUPLICATE_CHECK.value: {}
        }
        
        for index, row in df.iterrows():
            try:
                processed_row = self._process_single_row(row, index + 2)  # +2 for Excel row number (header + 0-index)
                if processed_row[PROCESSED_ROW_KEYS.HAS_ERRORS.value]:
                    result[PROCESSED_ROWS_TYPES.ERROR_ROWS.value].append(processed_row)
                elif processed_row[PROCESSED_ROW_KEYS.OPERATION.value] == OperationTypes.DELETE.value:
                    result[PROCESSED_ROWS_TYPES.DELETE_ROWS.value].append(processed_row)
                elif processed_row[PROCESSED_ROW_KEYS.OPERATION.value] == OperationTypes.CREATE.value:
                    result[PROCESSED_ROWS_TYPES.CREATE_ROWS.value].append(processed_row)
                elif processed_row[PROCESSED_ROW_KEYS.OPERATION.value] == OperationTypes.UPDATE.value:
                    result[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value].append(processed_row)
                else:
                    # This might be the issue - unknown operation types
                    logger.warning(f"Row {index + 2} has unknown operation type: '{processed_row[PROCESSED_ROW_KEYS.OPERATION.value]}'")
                    logger.warning(f"Expected types: CREATE={OperationTypes.CREATE.value}, UPDATE={OperationTypes.UPDATE.value}, DELETE={OperationTypes.DELETE.value}")
                    
            except Exception as e:
                logger.error(f"Exception processing row {index + 2}: {str(e)}")
                # Handle unexpected errors in row processing
                error_row = {
                    PROCESSED_ROW_KEYS.ROW_NUMBER.value: index + 2,
                    PROCESSED_ROW_KEYS.RAW_DATA.value: row.to_dict(),
                    PROCESSED_ROW_KEYS.PROCESSED_DATA.value: {},
                    PROCESSED_ROW_KEYS.OPERATION.value: OperationTypes.ERROR.value,
                    PROCESSED_ROW_KEYS.HAS_ERRORS.value: True,
                    PROCESSED_ROW_KEYS.ERRORS.value: [f"{_('Error processing row:')} {str(e)}"]
                }
                result[PROCESSED_ROWS_TYPES.ERROR_ROWS.value].append(error_row)
        
        # Check for duplicates
        result = self._check_duplicates(result)
        return result
    
    def _process_single_row(self, row: pd.Series, row_number: int) -> Dict[str, Any]:
        """
        Process a single row from the Excel file.
        
        Args:
            row (pd.Series): Single row from DataFrame
            row_number (int): Row number in Excel (for error reporting)
            
        Returns:
            dict: Processed row data
        """
        errors = []
        raw_data = row.to_dict()
        processed_data = {}
        id_label = self._get_id_label()
        
        # Step 1: Check ELIMINATE column
        eliminate_value = str(row.get(DELETE_FLAG_LABEL, '')).strip()
        should_delete = self.choice_mappings.validate_eliminate_column(eliminate_value)
        
        if should_delete:
            # DELETE operation - must have valid ID
            id_value = self._process_id_field(row)
            if id_value is None or id_value == '':
                errors.append(f"{_('Para eliminar un registro, debe proporcionar un ID válido')}")
                operation = OperationTypes.ERROR.value
            else:
                processed_data[id_label] = id_value
                operation = OperationTypes.DELETE.value
        else:
            # CREATE or UPDATE operation
            id_value = self._process_id_field(row)
            
            if id_value is None or id_value == '':
                # CREATE operation - new record
                operation = OperationTypes.CREATE.value
            else:
                # UPDATE operation - existing record
                operation = OperationTypes.UPDATE.value
            
            # Process all other fields for CREATE/UPDATE
            processed_data, field_errors = self._process_all_fields(row)
            errors.extend(field_errors)
            
            # Add ID field for UPDATE operations (after processing other fields)
            if operation == OperationTypes.UPDATE.value:
                processed_data[id_label] = id_value
        
        result = {
            PROCESSED_ROW_KEYS.ROW_NUMBER.value: row_number,
            PROCESSED_ROW_KEYS.RAW_DATA.value: raw_data,
            PROCESSED_ROW_KEYS.PROCESSED_DATA.value: processed_data,
            PROCESSED_ROW_KEYS.OPERATION.value: operation,
            PROCESSED_ROW_KEYS.HAS_ERRORS.value: len(errors) > 0,
            PROCESSED_ROW_KEYS.ERRORS.value: errors
        }
        return result
    
    def _process_id_field(self, row: pd.Series) -> Any:
        """
        Process ID field from row.
        
        Args:
            row (pd.Series): Row data
            
        Returns:
            int or None: Processed ID value
        """
        id_label = self._get_id_label()
        id_value = row.get(id_label, '')
        
        if pd.isna(id_value) or str(id_value).strip() == '':
            return None
        
        try:
            return int(float(str(id_value)))  # Handle Excel's numeric formatting
        except (ValueError, TypeError):
            return None
    
    def _process_all_fields(self, row: pd.Series) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process all fields in a row for CREATE/UPDATE operations.
        
        Args:
            row (pd.Series): Row data
            
        Returns:
            tuple: (processed_data, errors)
        """
        errors = []
        processed_data = {}
        
        # Process each column
        field_processors = self._get_field_processors()
        
        for label, processor in field_processors.items():
            if label in row:
                try:
                    value, field_error = processor(row[label], label)
                    if field_error:
                        errors.append(field_error)
                    else:
                        processed_data[label] = value
                except Exception as e:
                    errors.append(f"{_('Error processing field')} {label}: {str(e)}")
            else:
                logger.error(f"Field not found: {label}")
        logger.info(f"Errors: {errors}")
        return processed_data, errors
    
    def _get_field_processors(self) -> Dict[str, callable]:
        """
        Get field processors based on model type.
        
        Returns:
            dict: Mapping of field names to processor functions
        """
        field_processors = {}
        for column in self.columns:
            label = column.get('label', None)
            processor_name = column.get('processor', None)
            if processor_name:
                processor = getattr(self, f'_{processor_name}', None)
                if processor:
                    field_processors[label] = processor
            else:
                field_processors[label] = self._process_text_field
        return field_processors
    
  
    #     elif self.model_type == 'activity':
    #         return {
    #             self.columns.NAME.label: self._process_text_field,
    #             self.columns.DESTINATION.label: self._process_text_field,  # Foreign key as text
    #             self.columns.SUPPLIER.label: self._process_text_field,  # Foreign key as text
    #             self.columns.IS_ACTIVE.label: self._process_boolean_field,
    #             self.columns.PRIORITY.label: self._process_boolean_field,
    #             self.columns.TYPEOF.label: self._process_text_field,  # Foreign key as text
    #             self.columns.DESCRIPTION.label: self._process_description_field,
    #             self.columns.TEACHER_NOTES.label: self._process_description_field,
    #             self.columns.REGISTERED_NOTES.label: self._process_description_field,
    #             self.columns.NOTES.label: self._process_description_field,
    #             self.columns.PHONE.label: self._process_text_field,
    #             self.columns.EMAIL.label: self._process_email_field,
    #             self.columns.WEB.label: self._process_url_field,
    #             self.columns.LOCATION_LINK_NAME.label: self._process_text_field,
    #             self.columns.LOCATION_LINK_URL.label: self._process_url_field,
    #         }
    #     else:
    #         raise ValueError(f"Unsupported model type: {self.model_type}")
    
    def _process_text_field(self, value: Any, field_name: str) -> Tuple[Any, str]:
        """Process text field."""
        if pd.isna(value) or str(value).strip() == '':
            return '', ''
        return str(value).strip(), ''
    
    
    def _process_boolean_field(self, value: Any, field_name: str) -> Tuple[Any, str]:
        """Process boolean field."""
        if pd.isna(value) or str(value).strip() == '':
            return False, ''  # Default to False for empty boolean fields
        
        text_value = str(value).strip().lower()  # Convert to lowercase for mapping
        bool_value = self.choice_mappings.get_boolean_value(text_value)
        
        if bool_value is not None:
            return bool_value, ''
        else:
            return False, f"{_('Invalid boolean value for')} {field_name}: '{value}'"
    
    def _process_decimal_field(self, value: Any, field_name: str) -> Tuple[Any, str]:
        """Process decimal field."""
        if pd.isna(value) or str(value).strip() == '':
            return None, ''
        
        try:
            return float(str(value)), ''
        except (ValueError, TypeError):
            return None, f"Valor numérico inválido para {field_name}: '{value}'"
    
    def _process_email_field(self, value: Any, field_name: str) -> Tuple[Any, str]:
        """Process email field with basic validation."""
        if pd.isna(value) or str(value).strip() == '':
            return '', ''
        
        email = str(value).strip()
        # Basic email validation
        if '@' in email and '.' in email:
            return email, ''
        else:
            return email, f"Email inválido: '{email}'"
    
    def _process_url_field(self, value: Any, field_name: str) -> Tuple[Any, str]:
        """Process URL field."""
        if pd.isna(value) or str(value).strip() == '':
            return '', ''
        
        url = str(value).strip()
        # Basic URL validation
        if url.startswith(('http://', 'https://')):
            return url, ''
        else:
            # Add https:// if not present
            return f"https://{url}", ''
    
    def _check_duplicates(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for duplicate records in the import data.
        
        Args:
            result (dict): Processed import data
            
        Returns:
            dict: Updated result with duplicate errors
        """
        seen_ids = set()
        # Check all non-error rows
        all_rows = result[PROCESSED_ROWS_TYPES.CREATE_ROWS.value] + \
            result[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value] + \
            result[PROCESSED_ROWS_TYPES.DELETE_ROWS.value]
        id_label = self._get_id_label()
        
        for row in all_rows:
            row_data = row[PROCESSED_ROW_KEYS.PROCESSED_DATA.value]
            row_number = row[PROCESSED_ROW_KEYS.ROW_NUMBER.value]
            
            # Check ID duplicates (for update/delete operations)
            if id_label in row_data:
                id_value = row_data[id_label]
                if id_value in seen_ids:
                    # Move to error rows
                    row[PROCESSED_ROW_KEYS.HAS_ERRORS.value] = True
                    row[PROCESSED_ROW_KEYS.ERRORS.value].append(f"{_('ID duplicated in the file')}: {id_value}")
                    result[PROCESSED_ROWS_TYPES.ERROR_ROWS.value].append(row)
                else:
                    seen_ids.add(id_value)
        
        # Remove duplicates from their original lists
        result[PROCESSED_ROWS_TYPES.CREATE_ROWS.value] = [
            row for row in result[PROCESSED_ROWS_TYPES.CREATE_ROWS.value] if not row[PROCESSED_ROW_KEYS.HAS_ERRORS.value]
            ]
        result[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value] = [
            row for row in result[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value] if not row[PROCESSED_ROW_KEYS.HAS_ERRORS.value]
            ]
        result[PROCESSED_ROWS_TYPES.DELETE_ROWS.value] = [
            row for row in result[PROCESSED_ROWS_TYPES.DELETE_ROWS.value] if not row[PROCESSED_ROW_KEYS.HAS_ERRORS.value]
            ]
        return result


class ExcelImportProcessor:
    """
    Main processor for Excel import operations.
    """
    
    def __init__(
        self, 
        data_processor: ExcelDataProcessor,
    ):
        self.data_processor = data_processor()
    
    def process_excel_import(self, file_path: str) -> Dict[str, Any]:
        """
        Complete processing of Excel file for import.
        
        Args:
            file_path (str): Path to Excel file
            
        Returns:
            dict: Complete processing result
        """
        # Step 1: Read Excel file
        success, df, read_errors = self.data_processor.read_excel_file(file_path)
        if not success:
            return {
                RESULTS_KEYS.SUCCESS.value: False,
                PROCESSED_ROW_KEYS.ERRORS.value: read_errors,
                PROCESSED_ROWS_TYPES.TOTAL_ROWS.value: 0,
                PROCESSED_ROWS_TYPES.VALID_ROWS.value: 0,
                PROCESSED_ROWS_TYPES.ERROR_ROWS.value: 0
            }
        
        # Step 2: Validate structure
        is_valid, structure_errors = ExcelStructureValidator.validate_structure(df)
        if not is_valid:
            return {
                RESULTS_KEYS.SUCCESS.value: False,
                PROCESSED_ROW_KEYS.ERRORS.value: structure_errors,
                PROCESSED_ROWS_TYPES.TOTAL_ROWS.value: len(df),
                PROCESSED_ROWS_TYPES.VALID_ROWS.value: 0,
                PROCESSED_ROWS_TYPES.ERROR_ROWS.value: len(df)
            }
        
        # Step 3: Process data
        processed_data = self.data_processor.process_data(df)
        
        # Step 4: Calculate summary
        total_valid = (len(processed_data[PROCESSED_ROWS_TYPES.CREATE_ROWS.value]) + 
                      len(processed_data[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value]) + 
                      len(processed_data[PROCESSED_ROWS_TYPES.DELETE_ROWS.value]))
        
        return {
            RESULTS_KEYS.SUCCESS.value: True,
            RESULTS_KEYS.PROCESSED_DATA.value: processed_data,
            PROCESSED_ROWS_TYPES.TOTAL_ROWS.value: processed_data[PROCESSED_ROWS_TYPES.TOTAL_ROWS.value],
            PROCESSED_ROWS_TYPES.VALID_ROWS.value: total_valid,
            PROCESSED_ROWS_TYPES.ERROR_ROWS.value: len(processed_data[PROCESSED_ROWS_TYPES.ERROR_ROWS.value]),
            RESULTS_KEYS.CREATE_COUNT.value: len(processed_data[PROCESSED_ROWS_TYPES.CREATE_ROWS.value]),
            RESULTS_KEYS.UPDATE_COUNT.value: len(processed_data[PROCESSED_ROWS_TYPES.UPDATE_ROWS.value]),
            RESULTS_KEYS.DELETE_COUNT.value: len(processed_data[PROCESSED_ROWS_TYPES.DELETE_ROWS.value]),
            PROCESSED_ROW_KEYS.ERRORS.value: []
        }
