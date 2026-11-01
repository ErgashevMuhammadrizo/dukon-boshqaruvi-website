from django.contrib import admin
from .models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Aloqa ma’lumotlari', {'fields': ['telegram_url','phone','email','contact_title','contact_text']}),
        ('DEALS kompaniyasi', {'fields': ['deals_url']}),
        ('Windows yuklamasi', {'fields': ['windows_file','windows_url','windows_version']}),
        ('Android', {'fields': ['android_version']}),
    ]
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteSettings.objects.exists()
    def has_delete_permission(self, request, obj=None): return False

admin.site.site_header = 'e-dukon · DEALS'
admin.site.site_title = 'e-dukon boshqaruvi'
admin.site.index_title = 'Sayt boshqaruvi'
