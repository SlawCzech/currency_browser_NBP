import json
from datetime import datetime, timedelta

from django.views.generic import FormView
from urllib import request

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import forms, models
from .serializers import CurrencyRateSerializer


def get_holidays(start_date, end_date):
    start_date = datetime.strftime(start_date, "%Y-%m-%d")
    end_date = datetime.strftime(end_date, "%Y-%m-%d")
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

    def get_form(self, form_class=None):
        currencies = models.CurrencyName.objects.all()
        form = super().get_form(form_class)

        form.fields["currency"].choices = [(currency.code, currency.name.capitalize()) for currency in currencies]

        return form


class CurrencyAPI(APIView):
    def post(self, request, format=None):
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        if start_date is not None and end_date is not None:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

            currencies = models.CurrencyName.objects.all()

            dates = models.CurrencyDate.objects.filter(date__range=(start_date, end_date))

            if dates.count() < count_days(start_date, end_date) - count_holidays_during_weekdays(
                start_date, end_date
            ) - count_days_off(start_date, end_date):
                get_currency_data_from_nbp_API(start_date, end_date)

            currency_data = models.CurrencyValue.objects.filter(
                currency_date__date__range=(start_date, end_date)
            ).select_related("currency_name")

            data = {
                "labels": [date.date.strftime("%Y-%m-%d") for date in dates],
                "datasets": [
                    {
                        "label": currency.code,
                        "data": [
                            float(value.exchange_rate)
                            for value in currency_data
                            if value.currency_name.code == currency.code
                        ],
                    }
                    for currency in currencies
                ],
            }

        else:
            return Response("Start date and end date are required.", status=status.HTTP_400_BAD_REQUEST)

        # serializer = CurrencyRateSerializer(data, many=True)

        return Response(data, status=status.HTTP_200_OK)
