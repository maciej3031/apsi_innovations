from enum import Enum

from django.contrib.auth.models import User
from django.db import models


class Innovation(models.Model):
    class Status(Enum):
        ACCEPTED = 'accepted'
        BLOCKED = 'blocked'
        REJECTED = 'rejected'
        SUSPENDED = 'suspended'
        VOTING = 'voting'
        IN_REPLENISHMENT = 'in_replenishment'
        PENDING = 'pending'

    STATUS_CHOICES = (
        (Status.ACCEPTED, 'Accepted'),
        (Status.BLOCKED, 'Blocked'),
        (Status.REJECTED, 'Rejected'),
        (Status.SUSPENDED, 'Suspended'),
        (Status.IN_REPLENISHMENT, 'In Replenishment'),
        (Status.PENDING, 'Pending'),
    )

    subject = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    assumptions = models.CharField(max_length=1024)
    benefits = models.CharField(max_length=1024)
    costs = models.CharField(max_length=1024)
    status = models.CharField(choices=STATUS_CHOICES, max_length=32, default=Status.PENDING)
    status_substantiation = models.CharField(max_length=1024, verbose_name='Status Substantiation')
    student_grade_weight = models.PositiveIntegerField(verbose_name="Student's Grade Weight")
    employee_grade_weight = models.PositiveIntegerField(verbose_name="Employee's Grade Weight")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Time Added')
    issuer = models.ForeignKey(User, related_name='innovations', on_delete=models.deletion.CASCADE)


class Keyword(models.Model):
    keyword = models.CharField(max_length=128)
    innovation = models.ForeignKey(Innovation, related_name='keywords', on_delete=models.deletion.CASCADE)


class Grade(models.Model):
    value = models.PositiveIntegerField(verbose_name='Grade')
    description = models.CharField(max_length=1024)
    innovation = models.ForeignKey(Innovation, related_name='grades', on_delete=models.deletion.CASCADE)
    user = models.ForeignKey(User, related_name='grades', on_delete=models.deletion.CASCADE)


class BaseUrl(models.Model):
    url = models.URLField()
    description = models.CharField(max_length=1024)


class BaseAttachment(models.Model):
    name = models.CharField(max_length=128)
    file = models.FileField(upload_to='attachments/')
    description = models.CharField(max_length=1024)


class InnovationUrl(BaseUrl):
    class Meta:
        verbose_name = 'Innovation Url'
        verbose_name_plural = 'Innovation Urls'

    innovation = models.ForeignKey(Innovation, related_name='urls', on_delete=models.deletion.CASCADE)


class InnovationAttachment(BaseAttachment):
    class Meta:
        verbose_name = 'Innovation Attachment'
        verbose_name_plural = 'Innovation Attachments'

    innovation = models.ForeignKey(Innovation, related_name='attachments', on_delete=models.deletion.CASCADE)
