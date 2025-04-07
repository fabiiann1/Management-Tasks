from django.contrib import admin
from .models import Task, Log
# Register your models here.
admin.site.register(Task)

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'created_date', 'formatted_data')
    list_filter = ('created_date', 'user')

    def formatted_data(self, obj):
        return obj.data 
    formatted_data.short_description = 'Datos del log'
