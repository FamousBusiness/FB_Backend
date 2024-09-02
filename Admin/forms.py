from django import forms


class AdminExcelUploadForm(forms.Form):
    excel_file = forms.FileField()
    