from django.contrib import admin
from .models import Person, Organization, Speech, Session, Link, Mandate
# Register your models here.

admin.site.register(Person)
admin.site.register(Organization)
admin.site.register(Speech)
admin.site.register(Session)
admin.site.register(Link)
admin.site.register(Mandate)