from django.contrib import admin
from .models import Task, Log, State, Priority
# Register your models here.
admin.site.register(State)
admin.site.register(Priority)

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'created_date', 'formatted_data')
    list_filter = ('created_date', 'user')

    def formatted_data(self, obj):
        return obj.data 
    formatted_data.short_description = 'Datos del log'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'priority', 'due_date', 'assigned_user')
    list_filter = ('state', 'priority', 'due_date', 'assigned_user')
    search_fields = ('name', 'description', 'comment')

   