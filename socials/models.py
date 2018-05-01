from django.contrib.auth.models import User
from django.db import models


class SocialPost(models.Model):
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    text = models.CharField(max_length=1024)
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Time Added')
    issuer = models.ForeignKey(User, related_name='social_posts', on_delete=models.deletion.CASCADE)


class SocialPostUrl(models.Model):
    class Meta:
        verbose_name = "Post Url"
        verbose_name_plural = "Post Urls"

    url = models.URLField()
    post = models.ForeignKey(SocialPost, related_name='urls', on_delete=models.deletion.CASCADE)


class SocialPostAttachment(models.Model):
    class Meta:
        verbose_name = "Post Attachment"
        verbose_name_plural = "Post Attachments"

    file = models.FileField(upload_to='attachments/', null=True)
    post = models.ForeignKey(SocialPost, related_name='attachments', on_delete=models.deletion.CASCADE)


class Comment(models.Model):
    text = models.CharField(max_length=1024)
    issuer = models.ForeignKey(User, related_name='comments', on_delete=models.deletion.CASCADE)
    social_post = models.ForeignKey(SocialPost, related_name='comments', verbose_name='Post',
                                    on_delete=models.deletion.CASCADE)
