from django import forms


class CurrencyForm(forms.Form):
    start_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.TextInput(attrs={"type": "date"}))
    currency = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)
