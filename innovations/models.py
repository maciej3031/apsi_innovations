from django.contrib.auth.models import User
from django.db import models

from innovations.grades import calculate_innovation_grade


class Innovation(models.Model):
    class Status:
        ACCEPTED = 'accepted'
        BLOCKED = 'blocked'
        REJECTED = 'rejected'
        SUSPENDED = 'suspended'
        IN_REPLENISHMENT = 'in_replenishment'
        PENDING = 'pending'
        VOTING = 'voting'

    STATUS_CHOICES = (
        (Status.ACCEPTED, 'Accepted'),
        (Status.BLOCKED, 'Blocked'),
        (Status.REJECTED, 'Rejected'),
        (Status.SUSPENDED, 'Suspended'),
        (Status.IN_REPLENISHMENT, 'In Replenishment'),
        (Status.PENDING, 'Pending'),
        (Status.VOTING, 'Voting'),
    )

    subject = models.CharField(max_length=128)
    description = models.TextField(max_length=1024)
    assumptions = models.TextField(max_length=1024)
    benefits = models.CharField(max_length=1024)
    costs = models.CharField(max_length=1024)
    status = models.CharField(choices=STATUS_CHOICES, max_length=32, default=Status.PENDING)
    status_substantiation = models.CharField(max_length=1024, verbose_name='Status Substantiation', null=True)
    student_grade_weight = models.DecimalField(verbose_name="Student's Grade Weight", max_digits=3, decimal_places=2,
                                               default=1.0)
    employee_grade_weight = models.DecimalField(verbose_name="Employee's Grade Weight", max_digits=3, decimal_places=2,
                                                default=1.0)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Time Added')
    issuer = models.ForeignKey(User, related_name='innovations', on_delete=models.deletion.CASCADE)

    @property
    def grade(self):
        grades = Grade.objects.filter(innovation=self)
        return calculate_innovation_grade(grades)


class Keyword(models.Model):
    keyword = models.CharField(max_length=128)
    innovation = models.ForeignKey(Innovation, related_name='keywords', on_delete=models.deletion.CASCADE)


class Grade(models.Model):
    value = models.PositiveIntegerField(verbose_name='Grade')
    description = models.CharField(max_length=1024)
    innovation = models.ForeignKey(Innovation, related_name='grades', on_delete=models.deletion.CASCADE)
    user = models.ForeignKey(User, related_name='grades', on_delete=models.deletion.CASCADE)


class InnovationUrl(models.Model):
    class Meta:
        verbose_name = 'Innovation Url'
        verbose_name_plural = 'Innovation Urls'

    url = models.URLField()
    innovation = models.ForeignKey(Innovation, related_name='urls', on_delete=models.deletion.CASCADE)


class InnovationAttachment(models.Model):
    class Meta:
        verbose_name = 'Innovation Attachment'
        verbose_name_plural = 'Innovation Attachments'

    file = models.FileField(upload_to='attachments/', null=True)
    innovation = models.ForeignKey(Innovation, related_name='attachments', on_delete=models.deletion.CASCADE)


class ViolationReport(models.Model):
    substantiation = models.CharField(max_length=1024)
    creation_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField(default=None, null=True, blank=True)
    issuer = models.ForeignKey(User, related_name="violation_reports", on_delete=models.deletion.CASCADE)
    innovation = models.ForeignKey(Innovation, related_name='violation_reports', on_delete=models.deletion.CASCADE)
