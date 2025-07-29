import os
import pandas as pd
import tempfile
from django.utils.translation import gettext as _
from collections import OrderedDict
from copy import deepcopy
from export_edit_import.formats import HEADER_FORMAT, DELETE_COLUMN_FORMAT
from export_edit_import.enums import DELETE_FLAG_LABEL
from export_edit_import.utils import get_field_label_from_model_class


class ExcelExporter:
    
    
    def __init__(self, model_class, columns, sheet_name='', queryset=None):
        self.model_class = model_class
        self.columns = columns
        if queryset:
            self.queryset = queryset
        else:
            self.queryset = model_class.objects.all()
        if sheet_name:
            self.sheet_name = sheet_name
        else:
            self.sheet_name = model_class._meta.verbose_name_plural.title()
    
    def get_header_format(self):
        return HEADER_FORMAT
    
    def get_delete_column_format(self):
        return DELETE_COLUMN_FORMAT
        
    def get_field_value(self, instance, field_name):
        if field_method := getattr(self, f'get_{field_name}_cell_value', None):
            return field_method(instance)
        return getattr(instance, field_name, '')


    def get_field_label(self, field_name):
        get_field_label_method = getattr(self, f'get_{field_name}_label', None)
        if get_field_label_method:
            return get_field_label_method()
        label_from_columns = next((column.get('label', None) for column in self.columns if column.get('field_name') == field_name), None)
        if label_from_columns:
            return label_from_columns
        label = get_field_label_from_model_class(self.model_class, field_name)
        return str(label).title()

    def prepare_data(self):
        """
        Prepare data for accommodation export using model's column definitions.
        
        Args:
            queryset: QuerySet of accommodations to export
            
        Returns:
            list: List of dictionaries containing row data
        """
        data = []
        columns = deepcopy(self.columns)
        # columns.insert(0, {'field_name': 'delete_flag', 'label': 'ELIMINAR'})
        for instance in self.queryset:
            row_data = OrderedDict([
                (DELETE_FLAG_LABEL, ''),
            ])
            for column in columns:
                field_name = column['field_name']
                field_label = self.get_field_label(field_name)
                row_data[field_label] = self.get_field_value(instance, field_name)
            data.append(row_data)
            
        return data

    def create_excel(self):
        """
        Create Excel file for accommodation export.
        
        Args:
            queryset: QuerySet of accommodations to export
        
        Returns:
            tuple: (file_path, record_count)
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        temp_file.close()
        
        try:
            # Prepare data
            data = self.prepare_data()
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Save to Excel with formatting
            with pd.ExcelWriter(temp_file.name, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=self.sheet_name, index=False)
                
                # Get workbook and worksheet for formatting
                workbook = writer.book
                worksheet = writer.sheets[self.sheet_name]
                header_format = self.get_header_format()
                delete_column_format = self.get_delete_column_format()
                
                # Define formats
                header_format = workbook.add_format(header_format)
                delete_column_format = workbook.add_format(delete_column_format)
                
                # Apply header formatting
                for col_idx, column in enumerate(df.columns):
                    worksheet.write(0, col_idx, column, header_format)
                    
                    # Special formatting for ELIMINAR column
                    if column == DELETE_FLAG_LABEL:
                        for row_idx in range(1, len(df) + 1):
                            worksheet.write(row_idx, col_idx, '', delete_column_format)
                
                # Auto-adjust column widths and set row height for description
                for col_idx, column in enumerate(df.columns):
                    max_length = max(
                        len(str(column)),
                        df[column].astype(str).map(len).max() if not df[column].empty else 0
                    )
                    
                    if column_set_custom_method := getattr(self, f'set_column_{column}', None):
                        column_set_custom_method(worksheet, col_idx, df)
                    else:
                        worksheet.set_column(col_idx, col_idx, min(max_length + 2, 50))
                
                custom_format_methods_names = [
                    f"format_column_{column['field_name']}" for column in self.columns

                ]
                
                custom_format_methods = [
                    getattr(self, method_name, None) for method_name in custom_format_methods_names
                ]
                
                for method in custom_format_methods:
                    if method:
                        method(df, worksheet)
                
            return temp_file.name, len(data)
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
            raise e

