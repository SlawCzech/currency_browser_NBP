from django import forms


class CurrencyForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    currency = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple
    )
