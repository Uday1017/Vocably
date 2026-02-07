from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email


class Analysis(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analyses')
    video = models.FileField(upload_to='videos/')
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Results
    transcript = models.TextField(blank=True, null=True)
    grammar_score = models.FloatField(blank=True, null=True)
    fluency_score = models.FloatField(blank=True, null=True)
    politeness_score = models.FloatField(blank=True, null=True)
    body_language_score = models.FloatField(blank=True, null=True)
    overall_score = models.FloatField(blank=True, null=True)
    
    # Detailed feedback (JSON stored as text)
    detailed_feedback = models.JSONField(blank=True, null=True)
    video_stats = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Analyses'

    def __str__(self):
        return f"{self.user.email} - {self.filename} ({self.status})"
