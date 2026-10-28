import uuid
from django.db import models
from apps.accounts.models import Organization

class MediaAsset(models.Model):
    ASSET_TYPE_CHOICES = [
        ('VIDEO', 'Video Lecture'),
        ('DOCUMENT', 'Document/PDF'),
        ('IMAGE', 'Image Asset'),
    ]
    STATUS_CHOICES = [
        ('READY', 'Ready'),
        ('PROCESSING', 'Processing'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='media_assets')
    title = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES, default='VIDEO')
    storage_key = models.CharField(max_length=500, blank=True, default='')
    playback_url = models.URLField(blank=True, default='')
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='READY')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'media_assets'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.asset_type})"
