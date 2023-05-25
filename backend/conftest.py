from datetime import date, timedelta

import pytest

from currency.models import CurrencyName, CurrencyDate, CurrencyValue


@pytest.fixture
def currency(db):
    currency_name = CurrencyName.objects.get(code="USD")
    currency_date = CurrencyDate.objects.create(date=date.today())
    currency_value = CurrencyValue.objects.create(exchange_rate=0.1)
    currency_value.currency_names.add(currency_name)
    currency_value.currency_dates.add(currency_date)
    return currency_date


@pytest.fixture
def currency_2(db):
    currency_name = CurrencyName.objects.get(code="USD")
    currency_date = CurrencyDate.objects.create(date=date.today() - timedelta(days=2))
    currency_value = CurrencyValue.objects.create(exchange_rate=0.2)
    currency_value.currency_names.add(currency_name)
    currency_value.currency_dates.add(currency_date)
    return currency_date
