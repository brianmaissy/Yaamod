from django.contrib import admin

# Register your models here.
from webapp.models import Synagogue, Person, Member, MaleMember

admin.site.register(Synagogue)
admin.site.register(Person)
admin.site.register(Member)
admin.site.register(MaleMember)
