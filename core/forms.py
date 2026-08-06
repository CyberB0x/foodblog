from django import forms

from recipes.models import Profile


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = [
            'avatar',
            'bio',
            'github',
            'linkedin',
            'instagram',
            'youtube',
            'favorite_cuisine',
        ]

        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-3 rounded-xl border'
            }),

            'github': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'linkedin': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'instagram': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'youtube': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'favorite_cuisine': forms.Select(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'hidden',
                'accept': 'image/png,image/jpeg,image/webp',
            }),

            'bio': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full p-3 rounded-xl border'
            }),

            'github': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'linkedin': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'instagram': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'youtube': forms.URLInput(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),

            'favorite_cuisine': forms.Select(attrs={
                'class': 'w-full p-3 rounded-xl border'
            }),
        }


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-xl border-gray-300 focus:ring-orange-500 focus:border-orange-500",
            "placeholder": "Your name"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full rounded-xl border-gray-300 focus:ring-orange-500 focus:border-orange-500",
            "placeholder": "Your email"
        })
    )
    subject = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-xl border-gray-300 focus:ring-orange-500 focus:border-orange-500",
            "placeholder": "Subject"
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            "rows": 6,
            "class": "w-full rounded-xl border-gray-300 focus:ring-orange-500 focus:border-orange-500",
            "placeholder": "Your message"
        })
    )