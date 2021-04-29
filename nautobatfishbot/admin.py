# admin.py
from django.contrib import admin

from .models import tests_to_run


@admin.register(tests_to_run)
class nautobatfishbotAdmin(admin.ModelAdmin):
    list_display = ('test_name', 'source_ip')