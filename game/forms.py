from django import forms

class GuessForm(forms.Form):
    guess = forms.CharField(
        label='4桁の数字（重複なし）',
        max_length=4,
        min_length=4,
        required=True
    )

    def clean_guess(self):
        guess = self.cleaned_data['guess']
        if not guess.isdigit():
            raise forms.ValidationError("数字のみで入力してください。")
        if len(set(guess)) != 4:
            raise forms.ValidationError("4桁すべて異なる数字で入力してください。")
        return guess
    
class NumberChoiceForm(forms.Form):
    number = forms.ChoiceField(choices=[(str(i), str(i)) for i in range(10)], label="強化する数字")