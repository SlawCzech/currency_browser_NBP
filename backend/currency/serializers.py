from rest_framework import serializers

from currency.models import CurrencyValue


class DataSetSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.FloatField())


class CurrencyRateSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.DateField(format="%Y-%m-%d"))
    datasets = DataSetSerializer(many=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        dates = [value.currency_date.date for value in CurrencyValue.objects.all().order_by("currency_date__date")]
        currencies = [[value.currency_name.code for value in CurrencyValue.objects.all()]]

        data["labels"] = [date.strftime("%Y-%m-%d") for date in dates]
        data["datasets"] = [
            {
                "label": currency,
                "data": [
                    float(value.exchange_rate) for value in CurrencyValue.objects.filter(currency_name__code=currency)
                ],
            }
            for currency in currencies
        ]

        return data
