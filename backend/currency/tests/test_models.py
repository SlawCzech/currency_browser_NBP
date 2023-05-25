from _decimal import Decimal
from datetime import date

from currency.models import CurrencyValue, CurrencyDate


def test_add_one_currency_data(currency):
    currency_value = CurrencyValue.objects.filter(currency_dates=currency).first()

    assert currency_value.currency_names.first().code == "USD"
    assert currency_value.currency_names.first().name == "dolar amerykański"
    assert currency_value.currency_dates.first().date == currency.date


def test_get_values_by_date_range(currency, currency_2):
    dates = CurrencyDate.objects.filter(
        date__range=(date(2023, 5, 20), date(2023, 5, 23))
    )
    values = dates.filter(currency_values__currency_names__code="USD")

    assert len(values) == 2
    assert values.first().currency_values.first().exchange_rate == Decimal("0.1")
