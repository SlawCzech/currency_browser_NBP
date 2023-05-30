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
    days_count = 0
    while start_date <= end_date:
        if start_date.weekday() >= 5:
            days_count += 1
        start_date += timedelta(days=1)

    return days_count


def count_days(start_date, end_date):
    return (end_date - start_date).days


def get_currency_data_from_nbp_API(start_date, end_date):
    currency_nbp_url = f"http://api.nbp.pl/api/exchangerates/tables/a/{start_date}/{end_date}/"

    with request.urlopen(currency_nbp_url) as response:
        data = json.loads(response.read().decode())

    currency_names = models.CurrencyName.objects.all()

    for day in data:
        if not models.CurrencyDate.objects.filter(date=datetime.strptime(day["effectiveDate"], "%Y-%m-%d")):
            currency_date = models.CurrencyDate.objects.create(date=datetime.strptime(day["effectiveDate"], "%Y-%m-%d"))

            currency_values = [
                models.CurrencyValue(
                    exchange_rate=rate["mid"],
                    currency_date=currency_date,
                    currency_name=currency_names.get(code=rate["code"]),
                )
                for rate in day["rates"]
            ]

            models.CurrencyValue.objects.bulk_create(currency_values)


class CurrencyView(FormView):
    form_class = forms.CurrencyForm
    template_name = "currency/currency_view.html"
    success_url = "/"

    def form_valid(self, form):
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        currencies = form.cleaned_data.get("currency")

        dates = models.CurrencyDate.objects.filter(date__range=(start_date, end_date))

        if dates.count() < count_days(start_date, end_date) - count_holidays_during_weekdays(
            start_date, end_date
        ) - count_days_off(start_date, end_date):
            get_currency_data_from_nbp_API(start_date, end_date)

        currency_data = models.CurrencyValue.objects.filter(
            currency_date__date__range=(start_date, end_date), currency_name__code__in=currencies
        ).select_related("currency_name")

        data = {
            "labels": [x.code for x in models.CurrencyName.objects.all()],
            "datasets": [
                {"label": day.currency_name.code, "data": [z for z in currency_data]
                 # float(day.exchange_rate)} for day in currency_data
            ],
        }

        context = self.get_context_data()
        context.update({"dates": currency_data})
        context.update({"data": data})

        return self.render_to_response(context)

    def get_form(self, form_class=None):
        currencies = models.CurrencyName.objects.all()
        form = super().get_form(form_class)

        form.fields["currency"].choices = [(currency.code, currency.name.capitalize()) for currency in currencies]

        return form
