from django.contrib import admin
from django.contrib.auth.models import *

admin.site.unregister(User)
admin.site.unregister(Group)