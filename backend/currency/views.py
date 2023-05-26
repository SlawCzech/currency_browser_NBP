from django.views.generic import FormView

from currency.forms import CurrencyForm


class CurrencyView(FormView):
    form_class = CurrencyForm
    template_name = "currency/currency_view.html"
    success_url = "/"
