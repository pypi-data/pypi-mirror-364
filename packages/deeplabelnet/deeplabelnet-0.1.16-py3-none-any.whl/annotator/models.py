from django.db import models
import os


class AnnotationProject(models.Model):
    """
    Model to store information about annotation projects
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ImageFile(models.Model):
    """
    Model to store information about uploaded image files
    """
    project = models.ForeignKey(AnnotationProject, on_delete=models.CASCADE, related_name='images')
    file = models.ImageField(upload_to='images/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

    @property
    def file_url(self):
        return self.file.url

    @property
    def filename_only(self):
        return os.path.basename(self.file.name)


class Annotation(models.Model):
    """
    Model to store annotation data for images
    """
    ANNOTATION_TYPES = (
        ('bbox', 'Bounding Box'),
        ('polygon', 'Polygon'),
        ('mask', 'Segmentation Mask'),
    )

    image = models.ForeignKey(ImageFile, on_delete=models.CASCADE, related_name='annotations')
    annotation_type = models.CharField(max_length=20, choices=ANNOTATION_TYPES)
    label = models.CharField(max_length=100)
    data = models.JSONField()  # Stores annotation coordinates and other data
    confidence = models.FloatField(default=1.0)  # For auto-generated annotations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.annotation_type}) on {self.image.filename}"


class TrainedModel(models.Model):
    """
    Model to store information about trained machine learning models
    """
    MODEL_TYPES = (
        ('faster_rcnn', 'Faster R-CNN'),
        ('mask_rcnn', 'Mask R-CNN'),
        ('yolo', 'YOLO'),
        ('detr', 'DETR'),
    )

    STATUS_CHOICES = (
        ('queued', 'Queued'),
        ('training', 'Training'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    project = models.ForeignKey(AnnotationProject, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    file_path = models.CharField(max_length=255, blank=True, null=True)  # Path to the saved model file
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    progress = models.IntegerField(default=0)  # Training progress (0-100%)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.model_type})"
from django.db import models

# Create your models here.
