from django.contrib import admin
from django.contrib.auth.models import Group

from theater.models import (
    Actor,
    TheaterHall,
    Performance,
    Reservation,
    Ticket,
    Genre,
    Play,
)

admin.site.unregister(Group)

admin.site.register(Actor)
admin.site.register(Genre)
admin.site.register(Play)
admin.site.register(TheaterHall)
admin.site.register(Performance)
admin.site.register(Reservation)
admin.site.register(Ticket)
