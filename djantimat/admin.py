# -*- coding: utf-8 -*-

from .models import Slang
from django.contrib import admin

@admin.register(Slang)
class SlangAdmin(admin.ModelAdmin):
    pass
