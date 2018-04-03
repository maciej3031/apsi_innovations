from django.contrib import admin

from innovations.models import Innovation, Grade, InnovationAttachment, InnovationUrl, Keyword


class InnovationAdmin(admin.ModelAdmin):
    pass


class GradeAdmin(admin.ModelAdmin):
    pass


class InnovationAttachmentAdmin(admin.ModelAdmin):
    pass


class InnovationUrlAdmin(admin.ModelAdmin):
    pass


class KeywordAdmin(admin.ModelAdmin):
    pass


admin.site.register(Innovation, InnovationAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(InnovationAttachment, InnovationAttachmentAdmin)
admin.site.register(InnovationUrl, InnovationUrlAdmin)
admin.site.register(Keyword, KeywordAdmin)
