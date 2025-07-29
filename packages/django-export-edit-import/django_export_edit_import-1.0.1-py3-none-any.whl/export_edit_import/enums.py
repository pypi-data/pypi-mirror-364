from enum import Enum


DELETE_FLAG_LABEL = 'ELIMINAR'
DELETE_FLAG_FIELD_NAME = 'delete_flag'


class OperationTypes(Enum):
    EXPORT = 'export'
    IMPORT = 'import'
    ERROR = 'error'
    DELETE = 'delete'
    CREATE = 'create'
    UPDATE = 'update'
    VALIDATE = 'validate'
    TRANSACTION = 'transaction'
    
    
    
class PROCESSED_ROWS_TYPES(Enum):
    CREATE_ROWS = 'create_rows'
    UPDATE_ROWS = 'update_rows'
    DELETE_ROWS = 'delete_rows'
    ERROR_ROWS = 'error_rows'
    TOTAL_ROWS = 'total_rows'
    VALID_ROWS = 'valid_rows'
    DUPLICATE_CHECK = 'duplicate_check'


class PROCESSED_ROW_KEYS(Enum):
    ROW_NUMBER = 'row_number'
    RAW_DATA = 'raw_data'
    PROCESSED_DATA = 'processed_data'
    OPERATION = 'operation'
    HAS_ERRORS = 'has_errors'
    ERRORS = 'errors'
    
    
class RESULTS_KEYS(Enum):
    SUCCESS = 'success'
    PROCESSED_DATA = 'processed_data'
    CREATE_COUNT = 'create_count'
    UPDATE_COUNT = 'update_count'
    DELETE_COUNT = 'delete_count'
    ERROR_COUNT = 'error_count'
    VALID_COUNT = 'valid_count'
    TOTAL_ERRORS = 'total_errors'
    ERROR_COUNTS = 'error_counts'
    ERROR_TYPES = 'error_types'
    HAS_ERRORS = 'has_errors'
    
    
    
class DATABASE_PROCESSOR_KEYS(Enum):
    CREATE_READY = 'create_ready'
    UPDATE_READY = 'update_ready'
    DELETE_READY = 'delete_ready'
    CREATE_ERRORS = 'create_errors'
    UPDATE_ERRORS = 'update_errors'
    DELETE_ERRORS = 'delete_errors'
    DATABASE_ERRORS = 'database_errors'
    FINAL_DATA = 'final_data'
    EXCEL_ERRORS = 'excel_errors'
    EXISTING_INSTANCE = 'existing_instance'
    CREATED_COUNT = 'created_count'
    UPDATED_COUNT = 'updated_count'
    DELETED_COUNT = 'deleted_count'
    CREATED_ITEMS = 'created_items'
    UPDATED_ITEMS = 'updated_items'
    DELETED_ITEMS = 'deleted_items'
    OPERATION_ERRORS = 'operation_errors'
    VALIDATION_ERRORS = 'validation_errors'
    BUSINESS_RULE_ERRORS = 'business_rule_errors'
    SYSTEM_ERRORS = 'system_errors'
    
    
    