import json
from datetime import datetime, timedelta

from django.views.generic import FormView
from urllib import request

from . import forms, models


def get_holidays(start_date, end_date):
    holidays_url = f"https://openholidaysapi.org/PublicHolidays?countryIsoCode=PL&languageIsoCode=PL&validFrom={start_date}&validTo={end_date}"
    with request.urlopen(holidays_url) as response:
        data = json.loads(response.read().decode())

    return [holiday["startDate"] for holiday in data]


def count_holidays_during_weekdays(start_date, end_date):
    holidays = get_holidays(start_date, end_date)

    count_weekday_holidays = 0

    for holiday in holidays:
        if datetime.strptime(holiday, "%Y-%m-%d").weekday() < 5:
            count_weekday_holidays += 1

    return count_weekday_holidays


def count_days_off(start_date, end_date):
    s_date = datetime.strptime(start_date, "%Y-%m-%d")
    e_date = datetime.strptime(end_date, "%Y-%m-%d")

    days_count = 0
    while s_date <= e_date:
        if s_date.weekday() >= 5:
            days_count += 1
        s_date += timedelta(days=1)

    return days_count


def count_days(start_date, end_date):
    return (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days


class CurrencyView(FormView):
    form_class = forms.CurrencyForm
    template_name = "currency/currency_view.html"
    success_url = "/"

    def form_valid(self, form):
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        currencies = form.cleaned_data.get("currency")

        dates = models.CurrencyDate.objects.filter(date__range=(start_date, end_date)).count()

        if dates >= count_days(start_date, end_date) - count_holidays_during_weekdays(
            start_date, end_date
        ) - count_days_off(start_date, end_date):
            # TODO: get data from db
            pass

        # TODO: get data from NBP API

        return super().form_valid(form)

    def get_form(self, form_class=None):
        currencies = models.CurrencyName.objects.all()
        form = super().get_form(form_class)

        form.fields["currency"].choices = [(currency.code, currency.name.capitalize()) for currency in currencies]

        return form
