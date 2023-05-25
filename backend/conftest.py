from datetime import date, timedelta

import pytest

from currency.models import CurrencyName, CurrencyDate, CurrencyValue


@pytest.fixture
def currency(db):
    currency_name = CurrencyName.objects.get(code="USD")
    currency_date = CurrencyDate.objects.create(date=date(2023, 5, 23))
    currency_value = CurrencyValue.objects.create(
        exchange_rate=0.1, currency_name=currency_name, currency_date=currency_date
    )
    return currency_date


@pytest.fixture
def currency_2(db):
    currency_name = CurrencyName.objects.get(code="USD")
    currency_date = CurrencyDate.objects.create(date=date(2023, 5, 22))
    currency_value = CurrencyValue.objects.create(
        exchange_rate=0.2, currency_name=currency_name, currency_date=currency_date
    )
    return currency_date


@pytest.fixture
def currency_date(db):
    return CurrencyDate.objects.create(date=date(2023, 5, 23))


@pytest.fixture
def currency_name(db):
    return CurrencyName.objects.get(code="USD")
