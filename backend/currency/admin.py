from django.contrib import admin

from .models import CurrencyDate, CurrencyName, CurrencyValue

admin.site.register(CurrencyDate)
admin.site.register(CurrencyName)
admin.site.register(CurrencyValue)
