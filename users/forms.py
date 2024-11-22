from django import forms
from .models import Answer

class AnswerForm(forms.ModelForm):
    content = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Answer here!',
            'rows': 4,
            'cols': 50
        })
    )

    class Meta:
        model = Answer
        fields = ['content']
