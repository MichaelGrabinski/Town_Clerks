from django import forms


class TransmittalEntryForm(forms.Form):
    """Simple clerk entry form for a transmittal report.

    This is intentionally lightweight and printable. We can adjust fields to match
    the exact official form once you confirm the required fields.
    """

    report_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Report Date",
    )
    prepared_by = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Prepared By",
        max_length=100,
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        label="Notes",
    )

    # A simple line-item table (up to 12 rows) using repeated fields.
    # We can expand or make it dynamic later.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 13):
            self.fields[f"item_{i}_description"] = forms.CharField(
                required=False,
                widget=forms.TextInput(attrs={"class": "form-control"}),
                label=f"Item {i} Description",
                max_length=200,
            )
            self.fields[f"item_{i}_amount"] = forms.DecimalField(
                required=False,
                widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
                label=f"Item {i} Amount",
                max_digits=12,
                decimal_places=2,
            )
