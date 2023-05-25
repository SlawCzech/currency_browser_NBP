from _decimal import Decimal
from datetime import date

import pytest
from django.db import IntegrityError

from currency.models import CurrencyValue, CurrencyDate


def test_add_one_currency_data(currency):
    currency_value = CurrencyValue.objects.filter(currency_date=currency).first()

    assert currency_value.currency_name.code == "USD"
    assert currency_value.currency_name.name == "dolar amerykański"
    assert currency_value.currency_date.date == currency.date


def test_get_values_by_date_range(currency, currency_2):
    dates = CurrencyDate.objects.filter(
        date__range=(date(2023, 5, 20), date(2023, 5, 23))
    )
    values = dates.filter(currency_values__currency_name__code="USD")

    assert len(values) == 2
    assert values.first().currency_values.first().exchange_rate == Decimal("0.1")


def test_add_two_values_for_date_for_one_currency(currency_date, currency_name):
    CurrencyValue.objects.create(
        exchange_rate=Decimal("1.0"),
        currency_date=currency_date,
        currency_name=currency_name,
    )

    with pytest.raises(IntegrityError) as excinfo:
        CurrencyValue.objects.create(
            exchange_rate=Decimal("2.0"),
            currency_date=currency_date,
            currency_name=currency_name,
        )
    assert "UNIQUE constraint failed" in str(excinfo)
