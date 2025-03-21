from django import forms

class QuestionCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select CSV file")
