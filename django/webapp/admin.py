from django.contrib import admin

# Register your models here.
from webapp.models import Synagogue, Person

admin.site.register(Synagogue)
admin.site.register(Person)
