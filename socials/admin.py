from django.contrib import admin

from socials.models import SocialPost, SocialPostAttachment, Comment


class SocialPostAdmin(admin.ModelAdmin):
    pass


class SocialPostAttachmentAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(SocialPost, SocialPostAdmin)
admin.site.register(SocialPostAttachment, SocialPostAttachmentAdmin)
admin.site.register(Comment, CommentAdmin)
