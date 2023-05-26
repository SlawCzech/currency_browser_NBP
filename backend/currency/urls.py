from django.urls import path

from . import views

app_name = "currency"

urlpatterns = [path("", views.CurrencyView.as_view(), name="currency_form")]
