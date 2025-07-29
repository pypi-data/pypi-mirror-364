"""
Excel Error File Generator for Import Operations

This module creates Excel files with highlighted errors for users to correct
and re-import. Errors are highlighted with colored backgrounds and comments.
"""

import os
import pandas as pd
import tempfile
from typing import Dict, List, Any, Tuple
from django.utils.translation import gettext as _
from collections import OrderedDict
from colegia_core.models import Accommodation, Activity
from export_edit_import.enums import (
    DELETE_FLAG_LABEL, 
    DATABASE_PROCESSOR_KEYS,
    PROCESSED_ROW_KEYS, 
    PROCESSED_ROWS_TYPES,
    OperationTypes,
    RESULTS_KEYS
)
from export_edit_import.formats import (
    ERROR_FORMAT, 
    WARNING_FORMAT, 
    NORMAL_FORMAT, 
    HEADER_FORMAT, 
    TITLE_FORMAT,
    TEXT_FORMAT,
    NUMBER_FORMAT
)


class ExcelErrorHighlighter:
    """
    Handles highlighting of errors in Excel files.
    """
    
    def get_error_format(self):
        return ERROR_FORMAT
    
    def get_warning_format(self):
        return WARNING_FORMAT
    
    def get_normal_format(self):
        return NORMAL_FORMAT
    
    def get_header_format(self):
        return HEADER_FORMAT
    
    def get_title_format(self):
        return TITLE_FORMAT
    
    def get_text_format(self):
        return TEXT_FORMAT
    
    def get_number_format(self):
        return NUMBER_FORMAT
    
    def create_error_summary_sheet(self, workbook, error_data: Dict[str, Any]):
        """
        Create a summary sheet with error statistics and instructions.
        
        Args:
            workbook: xlsxwriter workbook object
            error_data (dict): Error data with counts and details
        """
        # Create summary worksheet
        summary_sheet = workbook.add_worksheet('Resumen de Errores')
        
        # Define formats
        title_format = workbook.add_format(self.get_title_format())
        
        header_format = workbook.add_format(self.get_header_format())
        
        text_format = workbook.add_format(self.get_text_format())
        number_format = workbook.add_format(self.get_number_format())
        
        # Title
        summary_sheet.merge_range('A1:D1', 'RESUMEN DE ERRORES DE IMPORTACIÓN', title_format)
        
        # Statistics section
        row = 3
        summary_sheet.write(row, 0, 'Estadísticas:', header_format)
        summary_sheet.write(row, 1, 'Cantidad', header_format)
        row += 1
        
        stats = [
            ('Total de filas procesadas', error_data.get('total_rows', 0)),
            ('Filas con errores', error_data.get('error_count', 0)),
            ('Filas válidas', error_data.get('valid_count', 0)),
            ('Operaciones de creación', error_data.get('create_count', 0)),
            ('Operaciones de actualización', error_data.get('update_count', 0)),
            ('Operaciones de eliminación', error_data.get('delete_count', 0)),
        ]
        
        for label, value in stats:
            summary_sheet.write(row, 0, label, text_format)
            summary_sheet.write(row, 1, value, number_format)
            row += 1
        
        # Instructions section
        row += 2
        summary_sheet.write(row, 0, 'Instrucciones:', header_format)
        row += 1
        
        instructions = [
            '1. Las celdas con errores están resaltadas en rojo',
            '2. Las celdas con advertencias están resaltadas en naranja',
            '3. Corrija los errores en la hoja "Datos con Errores"',
            '4. Los comentarios en las celdas contienen detalles del error',
            '5. Una vez corregidos, puede reimportar el archivo',
            '6. Solo las filas con errores aparecen en este archivo',
        ]
        
        for instruction in instructions:
            summary_sheet.write(row, 0, instruction, text_format)
            row += 1
        
        # Set column widths
        summary_sheet.set_column(0, 0, 40)
        summary_sheet.set_column(1, 1, 15)
    
    def highlight_errors_in_worksheet(self, worksheet, workbook, error_rows: List[Dict], columns: List[str]):
        """
        Highlight errors in the main data worksheet.
        
        Args:
            worksheet: xlsxwriter worksheet object
            workbook: xlsxwriter workbook object
            error_rows (list): List of rows with errors
            columns (list): List of column names
        """
        # Define formats
        error_format = workbook.add_format(self.get_error_format())
        warning_format = workbook.add_format(self.get_warning_format())
        normal_format = workbook.add_format(self.get_normal_format())
        header_format = workbook.add_format(self.get_header_format())
        
        # Apply header formatting
        for col_idx, column in enumerate(columns):
            worksheet.write(0, col_idx, column, header_format)
        
        # Process each error row
        for data_row_idx, error_row in enumerate(error_rows):
            excel_row = data_row_idx + 1  # +1 for header
            raw_data = error_row.get('raw_data', {})
            errors = error_row.get('errors', [])
            
            # Create a set of fields that have errors for quick lookup
            error_fields = set()
            for error_msg in errors:
                # Try to extract field names from error messages
                # This is a simple approach - you might want to make it more sophisticated
                for col_name in columns:
                    if col_name.lower() in error_msg.lower():
                        error_fields.add(col_name)
            
            # Apply formatting to each cell in the row
            for col_idx, column in enumerate(columns):
                cell_value = raw_data.get(column, '')
                
                # Determine cell format based on whether it has errors
                if column in error_fields:
                    cell_format = error_format
                    # Add comment with error details
                    error_messages = [e for e in errors if column.lower() in e.lower()]
                    if error_messages:
                        comment_text = '\n'.join(error_messages)
                        worksheet.write_comment(excel_row, col_idx, comment_text)
                else:
                    cell_format = normal_format
                
                # Write cell value with appropriate formatting
                worksheet.write(excel_row, col_idx, cell_value, cell_format)


class BaseErrorFileGenerator:
    """
    Base class for generating Excel files with import errors highlighted.
    """
    
    def __init__(self, model_class, sheet_name='Datos con Errores', columns: List[str] = None):
        self.model_class = model_class
        self.columns = columns
        self.sheet_name = sheet_name
        self.highlighter = ExcelErrorHighlighter()
    
    def get_ordered_columns(self) -> List[str]:
        """
        Get the ordered list of columns for Excel output.
        Subclasses should override this method to define their specific column order.
        
        Returns:
            list: Ordered list of column labels
        """
        raise NotImplementedError("Subclasses must implement get_ordered_columns()")
    
    def get_column_width_config(self) -> Dict[str, int]:
        """
        Get column width configuration for specific columns.
        Subclasses can override this to customize column widths.
        
        Returns:
            dict: Mapping of column labels to widths
        """
        return {
            DELETE_FLAG_LABEL: 12,
        }
    
    def get_row_height_config(self) -> Dict[str, int]:
        """
        Get row height configuration for specific columns.
        Subclasses can override this to customize row heights.
        
        Returns:
            dict: Mapping of column labels to row heights
        """
        return {
        }
    
    def generate_error_file(self, import_results: Dict[str, Any]) -> Tuple[str, int]:
        """
        Generate Excel file with highlighted errors.
        
        Args:
            import_results (dict): Results from import processing
            
        Returns:
            tuple: (file_path, error_count)
        """
        # Extract error data
        error_rows = []
        
        # Collect all types of error rows
        if DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value in import_results:
            error_rows.extend(import_results[DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value])
        
        if DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value in import_results:
            error_rows.extend(import_results[DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value])
        
        if DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value in import_results:
            error_rows.extend(import_results[DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value])
        
        if DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value in import_results:
            error_rows.extend(import_results[DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value])
        
        # If no errors, return None
        if not error_rows:
            return None, 0
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        temp_file.close()
        
        try:
            # Prepare error data for Excel
            excel_data = self._prepare_error_data_for_excel(error_rows)
            
            # Create Excel file with errors
            with pd.ExcelWriter(temp_file.name, engine='xlsxwriter') as writer:
                # Create DataFrame with error data
                df = pd.DataFrame(excel_data['rows'])
                
                # Write to Excel
                df.to_excel(writer, sheet_name=self.sheet_name, index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets[self.sheet_name]
                
                # Apply error highlighting
                self.highlighter.highlight_errors_in_worksheet(
                    worksheet, workbook, error_rows, list(df.columns)
                )
                
                # Set column widths
                self._adjust_column_widths(worksheet, df)
                
                # Create error summary sheet
                summary_data = {
                    PROCESSED_ROWS_TYPES.TOTAL_ROWS.value: len(error_rows),
                    RESULTS_KEYS.ERROR_COUNT.value: len(error_rows),
                    RESULTS_KEYS.VALID_COUNT.value: 0,
                    RESULTS_KEYS.CREATE_COUNT.value: len([r for r in error_rows if r.get(PROCESSED_ROW_KEYS.OPERATION.value) == OperationTypes.CREATE.value]),
                    RESULTS_KEYS.UPDATE_COUNT.value: len([r for r in error_rows if r.get(PROCESSED_ROW_KEYS.OPERATION.value) == OperationTypes.UPDATE.value]),
                    RESULTS_KEYS.DELETE_COUNT.value: len([r for r in error_rows if r.get(PROCESSED_ROW_KEYS.OPERATION.value) == OperationTypes.DELETE.value]),
                }
                
                self.highlighter.create_error_summary_sheet(workbook, summary_data)
            
            return temp_file.name, len(error_rows)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise e
    
    def _prepare_error_data_for_excel(self, error_rows: List[Dict]) -> Dict[str, Any]:
        """
        Prepare error data for Excel output.
        
        Args:
            error_rows (list): List of rows with errors
            
        Returns:
            dict: Prepared data for Excel
        """
        # Get column order from subclass
        ordered_columns = self.get_ordered_columns()
        
        # Prepare rows for Excel
        excel_rows = []
        for error_row in error_rows:
            raw_data = error_row.get('raw_data', {})
            
            # Create ordered row data
            row_data = OrderedDict()
            for column in ordered_columns:
                row_data[column] = raw_data.get(column, '')
            
            excel_rows.append(row_data)
        
        return {
            'rows': excel_rows,
            'columns': ordered_columns
        }
    
    def _adjust_column_widths(self, worksheet, df: pd.DataFrame):
        """
        Adjust column widths for better readability.
        
        Args:
            worksheet: xlsxwriter worksheet object
            df (pd.DataFrame): DataFrame with data
        """
        width_config = self.get_column_width_config()
        height_config = self.get_row_height_config()
        
        for col_idx, column in enumerate(df.columns):
            # Calculate maximum width needed
            max_length = max(
                len(str(column)),  # Header length
                df[column].astype(str).map(len).max() if not df[column].empty else 0
            )
            
            # Check if column has custom width configuration
            if column in width_config:
                worksheet.set_column(col_idx, col_idx, width_config[column])
            else:
                # Standard width adjustment
                worksheet.set_column(col_idx, col_idx, min(max_length + 2, 50))
            
            # Set row heights for specific columns
            if column in height_config:
                for row_idx in range(1, len(df) + 1):
                                         worksheet.set_row(row_idx, height_config[column])



class ImportErrorFileProcessor:
    """
    Main processor for creating error files from import results.
    """
    
    def __init__(self, generator: BaseErrorFileGenerator):
        self.generator = generator()
    
    def create_error_file(self, import_results: Dict[str, Any]) -> Tuple[str, int]:
        """
        Create error file from import results.
        
        Args:
            import_results (dict): Results from import processing
            
        Returns:
            tuple: (file_path, error_count) or (None, 0) if no errors
        """
        return self.generator.generate_error_file(import_results)
    
    def get_error_summary(self, import_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get summary of errors from import results.
        
        Args:
            import_results (dict): Results from import processing
            
        Returns:
            dict: Error summary with counts and details
        """
        error_counts = {
            DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value: len(import_results.get(DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value, [])),
            DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value: len(import_results.get(DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value, [])),
            DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value: len(import_results.get(DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value, [])),
            DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value: len(import_results.get(DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value, [])),
            DATABASE_PROCESSOR_KEYS.DATABASE_ERRORS.value: len(import_results.get(DATABASE_PROCESSOR_KEYS.DATABASE_ERRORS.value, [])),
        }
        
        total_errors = sum(error_counts.values())
        
        # Categorize errors by type
        error_types = {
            DATABASE_PROCESSOR_KEYS.VALIDATION_ERRORS.value: error_counts[DATABASE_PROCESSOR_KEYS.EXCEL_ERRORS.value],
            DATABASE_PROCESSOR_KEYS.BUSINESS_RULE_ERRORS.value: error_counts[DATABASE_PROCESSOR_KEYS.CREATE_ERRORS.value] + 
            error_counts[DATABASE_PROCESSOR_KEYS.UPDATE_ERRORS.value] + 
            error_counts[DATABASE_PROCESSOR_KEYS.DELETE_ERRORS.value] + 
            error_counts[DATABASE_PROCESSOR_KEYS.DATABASE_ERRORS.value],
            DATABASE_PROCESSOR_KEYS.SYSTEM_ERRORS.value: error_counts[DATABASE_PROCESSOR_KEYS.DATABASE_ERRORS.value],
        }
        
        return {
            RESULTS_KEYS.TOTAL_ERRORS.value: total_errors,
            RESULTS_KEYS.ERROR_COUNTS.value: error_counts,
            RESULTS_KEYS.ERROR_TYPES.value: error_types,
            RESULTS_KEYS.HAS_ERRORS.value: total_errors > 0,
        } 