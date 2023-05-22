from django.db import models


class CurrencyName(models.Model):
    name = models.CharField(max_length=35)
    code = models.CharField(max_length=3)
    currency_values = models.ManyToManyField(
        "CurrencyValue", related_name="currency_values"
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Currency Name"
        verbose_name_plural = "Currency Names"


class CurrencyDate(models.Model):
    date = models.DateField(db_index=True)
    currency_names = models.ManyToManyField(
        "CurrencyName", related_name="currency_dates", null=True
    )

    def __str__(self):
        return str(self.date)

    class Meta:
        verbose_name = "Currency Date"
        verbose_name_plural = "Currency Dates"


class CurrencyValue(models.Model):
    exchange_rate = models.DecimalField(max_digits=10, decimal_places=8)

    def __str__(self):
        return str(self.exchange_rate)

    class Meta:
        verbose_name = "Currency Value"
        verbose_name_plural = "Currency Values"
