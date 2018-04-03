from django.contrib import admin

from socials.models import SocialPost, SocialPostUrl, SocialPostAttachment, Comment


class SocialPostAdmin(admin.ModelAdmin):
    pass


class SocialPostAttachmentAdmin(admin.ModelAdmin):
    pass


class SocialPostUrlAdmin(admin.ModelAdmin):
    pass


class CommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(SocialPost, SocialPostAdmin)
admin.site.register(SocialPostAttachment, SocialPostAttachmentAdmin)
admin.site.register(SocialPostUrl, SocialPostUrlAdmin)
admin.site.register(Comment, CommentAdmin)
