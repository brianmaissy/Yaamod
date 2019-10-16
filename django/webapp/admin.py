from django.contrib import admin

# Register your models here.
from webapp.models import Member, Synagogue

admin.site.register(Synagogue)
admin.site.register(Member)
