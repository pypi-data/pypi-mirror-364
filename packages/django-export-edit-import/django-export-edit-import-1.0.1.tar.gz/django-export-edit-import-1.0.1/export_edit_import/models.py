from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

EXAMPLE_RELATED_MODELS_MAP = {
    'model_class_name': 'model_class_name',
    'display_name': 'display_name',
    'app_label': 'app_name',
}
    
    
class GeneratedFileStatus(models.TextChoices):
    PENDING = 'pending', _('Pending')
    COMPLETED = 'completed', _('Completed')
    FAILED = 'failed', _('Failed')
    COMPLETED_WITH_ERRORS = 'completed_with_errors', _('Completed with errors')


class GeneratedFile(TimeStampedModel):
    
    file = models.FileField(upload_to='generated_files/%Y/%m/%d', blank=True, null=True)
    related_model_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    status = models.CharField(
        max_length=255, 
        choices=GeneratedFileStatus.choices,
        default=GeneratedFileStatus.PENDING
    )
    rows_count = models.IntegerField(default=0)
    rows_with_errors_count = models.IntegerField(default=0)
    
    # Task tracking fields
    task_id = models.CharField(max_length=255, blank=True, null=True, help_text="Celery task ID")
    error_message = models.TextField(blank=True, null=True, help_text="Error message if task failed")
        
    class Meta:
        abstract = True
        ordering = ['-created', '-modified']
        
        
    def get_related_model(self):
        if self.related_model_type:
            return self.related_model_type.model_class()
        return None
    
    def is_task_completed(self):
        """Check if the task is completed (successfully or with errors)"""
        return self.status in [GeneratedFileStatus.COMPLETED, GeneratedFileStatus.COMPLETED_WITH_ERRORS]
    
    def is_task_failed(self):
        """Check if the task failed"""
        return self.status == GeneratedFileStatus.FAILED
    
    def is_task_pending(self):
        """Check if the task is still pending"""
        return self.status == GeneratedFileStatus.PENDING
    
        
class GeneratedExportFile(GeneratedFile):
    
    def is_file_up_to_date(self):
        """Check if the export file is up to date by comparing record counts"""
        if self.status == GeneratedFileStatus.COMPLETED:
            related_model = self.get_related_model()
            if related_model:
                return related_model.objects.count() == self.rows_count
        return False
    
    def get_download_filename(self):
        """Generate a user-friendly filename for download"""
        if related_model := self.get_related_model():
            model_name = related_model._meta.verbose_name
        else:
            model_name = 'unknown'
        timestamp = self.created.strftime('%Y%m%d_%H%M%S')
        return f"export_{model_name}_{timestamp}_list.xlsx"
    
    def can_reuse_file(self):
        """Check if this export file can be reused (up to date and completed)"""
        return self.is_task_completed() and self.is_file_up_to_date()


class GeneratedImportFile(GeneratedFile):
    file_with_errors = models.FileField(upload_to='generated_files/%Y/%m/%d', blank=True, null=True)
    updated_rows_count = models.IntegerField(default=0)
    created_rows_count = models.IntegerField(default=0)
    deleted_rows_count = models.IntegerField(default=0)
    
    def get_download_filename(self):
        """Generate a user-friendly filename for download"""
        model_name = self.get_related_model()._meta.verbose_name
        timestamp = self.created.strftime('%Y%m%d_%H%M%S')
        if self.rows_with_errors_count > 0:
            return f"import_errors_{model_name}_{timestamp}_list.xlsx"
        else:
            return f"import_{model_name}_{timestamp}_list.xlsx"
    
    def has_errors(self):
        """Check if this import has errors"""
        return self.rows_with_errors_count > 0
    
    def get_success_count(self):
        """Get the number of successfully imported rows"""
        return max(0, self.rows_count - self.rows_with_errors_count)
    
    def get_total_successful_count(self):
        """Get the number of successfully imported rows"""
        return self.updated_rows_count + self.created_rows_count + self.deleted_rows_count
