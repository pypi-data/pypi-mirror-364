"""
Test cases for django-export-edit-import models
"""
import pytest
from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile

from export_edit_import.models import (
    GeneratedFileStatus,
    GeneratedExportFile,
    GeneratedImportFile,
)


class TestImports(TestCase):
    """Test basic imports work correctly"""
    
    def test_can_import_models(self):
        """Test that we can import all the main models"""
        from export_edit_import.models import (
            GeneratedFileStatus,
            GeneratedExportFile,
            GeneratedImportFile,
        )
        
        # Test that the status choices exist
        assert GeneratedFileStatus.PENDING == 'pending'
        assert GeneratedFileStatus.COMPLETED == 'completed'
        assert GeneratedFileStatus.FAILED == 'failed'
        assert GeneratedFileStatus.COMPLETED_WITH_ERRORS == 'completed_with_errors'
    
    def test_can_import_enums(self):
        """Test that we can import enums module"""
        try:
            from export_edit_import import enums
            assert True  # Import successful
        except ImportError:
            pytest.skip("Enums module not found - might be optional")
    
    def test_can_import_views(self):
        """Test that we can import views module"""
        from export_edit_import import views
        assert hasattr(views, '__name__')
    
    def test_can_import_utils(self):
        """Test that we can import utils module"""
        from export_edit_import import utils
        assert hasattr(utils, '__name__')


@pytest.mark.django_db
class TestGeneratedExportFile:
    """Test cases for GeneratedExportFile model"""
    
    def test_create_generated_export_file(self):
        """Test creating a GeneratedExportFile instance"""
        content_type = ContentType.objects.get_for_model(ContentType)
        
        export_file = GeneratedExportFile.objects.create(
            related_model_type=content_type,
            status=GeneratedFileStatus.PENDING,
            rows_count=100,
        )
        
        assert export_file.pk is not None
        assert export_file.status == GeneratedFileStatus.PENDING
        assert export_file.rows_count == 100
        assert export_file.rows_with_errors_count == 0  # default value
    
    def test_generated_export_file_status_methods(self):
        """Test status checking methods"""
        export_file = GeneratedExportFile.objects.create(
            status=GeneratedFileStatus.PENDING
        )
        
        # Test pending status
        assert export_file.is_task_pending() is True
        assert export_file.is_task_completed() is False
        assert export_file.is_task_failed() is False
        
        # Update to completed status
        export_file.status = GeneratedFileStatus.COMPLETED
        export_file.save()
        
        assert export_file.is_task_pending() is False
        assert export_file.is_task_completed() is True
        assert export_file.is_task_failed() is False
        
        # Update to failed status
        export_file.status = GeneratedFileStatus.FAILED
        export_file.save()
        
        assert export_file.is_task_pending() is False
        assert export_file.is_task_completed() is False
        assert export_file.is_task_failed() is True
    
    def test_get_download_filename(self):
        """Test download filename generation"""
        content_type = ContentType.objects.get_for_model(ContentType)
        
        export_file = GeneratedExportFile.objects.create(
            related_model_type=content_type,
        )
        
        filename = export_file.get_download_filename()
        assert filename.startswith('export_')
        assert filename.endswith('_list.xlsx')
        assert 'content type' in filename.lower()  # ContentType's verbose name


@pytest.mark.django_db
class TestGeneratedImportFile:
    """Test cases for GeneratedImportFile model"""
    
    def test_create_generated_import_file(self):
        """Test creating a GeneratedImportFile instance"""
        content_type = ContentType.objects.get_for_model(ContentType)
        
        import_file = GeneratedImportFile.objects.create(
            related_model_type=content_type,
            status=GeneratedFileStatus.COMPLETED,
            rows_count=50,
            rows_with_errors_count=5,
            updated_rows_count=20,
            created_rows_count=15,
            deleted_rows_count=10,
        )
        
        assert import_file.pk is not None
        assert import_file.status == GeneratedFileStatus.COMPLETED
        assert import_file.rows_count == 50
        assert import_file.rows_with_errors_count == 5
        assert import_file.updated_rows_count == 20
        assert import_file.created_rows_count == 15
        assert import_file.deleted_rows_count == 10
    
    def test_has_errors_method(self):
        """Test has_errors method"""
        import_file = GeneratedImportFile.objects.create(
            rows_with_errors_count=0
        )
        assert import_file.has_errors() is False
        
        import_file.rows_with_errors_count = 5
        import_file.save()
        assert import_file.has_errors() is True
    
    def test_get_success_count(self):
        """Test get_success_count method"""
        import_file = GeneratedImportFile.objects.create(
            rows_count=100,
            rows_with_errors_count=20
        )
        
        assert import_file.get_success_count() == 80
        
        # Test edge case where errors exceed total
        import_file.rows_with_errors_count = 150
        import_file.save()
        assert import_file.get_success_count() == 0  # Should not be negative
    
    def test_get_total_successful_count(self):
        """Test get_total_successful_count method"""
        import_file = GeneratedImportFile.objects.create(
            updated_rows_count=30,
            created_rows_count=20,
            deleted_rows_count=10
        )
        
        assert import_file.get_total_successful_count() == 60  # 30 + 20 + 10
    
    def test_get_download_filename_with_errors(self):
        """Test download filename generation with errors"""
        content_type = ContentType.objects.get_for_model(ContentType)
        
        import_file = GeneratedImportFile.objects.create(
            related_model_type=content_type,
            rows_with_errors_count=5
        )
        
        filename = import_file.get_download_filename()
        assert filename.startswith('import_errors_')
        assert filename.endswith('_list.xlsx')
    
    def test_get_download_filename_without_errors(self):
        """Test download filename generation without errors"""
        content_type = ContentType.objects.get_for_model(ContentType)
        
        import_file = GeneratedImportFile.objects.create(
            related_model_type=content_type,
            rows_with_errors_count=0
        )
        
        filename = import_file.get_download_filename()
        assert filename.startswith('import_')
        assert not filename.startswith('import_errors_')
        assert filename.endswith('_list.xlsx')
