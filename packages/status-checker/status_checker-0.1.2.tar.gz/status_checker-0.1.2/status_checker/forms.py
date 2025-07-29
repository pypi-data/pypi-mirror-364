from django import forms

class URLForm(forms.Form):
    url = forms.URLField(label="Enter a website URL", widget=forms.URLInput(attrs={'placeholder': 'https://example.com'}))
