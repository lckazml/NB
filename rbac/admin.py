from django.contrib import admin
from rbac import models
# Register your models here.
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['title','url','name']
    list_editable = ['url','name']

admin.site.register(models.Permission,PermissionAdmin)
admin.site.register(models.Menu)