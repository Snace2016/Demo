from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Category, Manufacturer, Order, OrderStatus, PickupPoint, Product, Supplier,
)


class LoginForm(forms.Form):
    login = forms.EmailField(
        label='Логин',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите логин (email)', 'class': 'input',
        }),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль', 'class': 'input',
        }),
    )


class ProductForm(forms.ModelForm):
    image_file = forms.ImageField(
        label='Фото товара', required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'}),
    )

    class Meta:
        model = Product
        fields = [
            'article', 'name', 'category', 'description', 'manufacturer',
            'supplier', 'price', 'unit', 'quantity', 'discount',
        ]
        widgets = {
            'article': forms.TextInput(attrs={'class': 'input'}),
            'name': forms.TextInput(attrs={'class': 'input'}),
            'unit': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'input'}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'input'}),
            'quantity': forms.NumberInput(attrs={'min': '0', 'class': 'input'}),
            'discount': forms.NumberInput(attrs={
                'step': '0.01', 'min': '0', 'max': '100', 'class': 'input',
            }),
            'category': forms.Select(attrs={'class': 'select'}),
            'manufacturer': forms.Select(attrs={'class': 'select'}),
            'supplier': forms.Select(attrs={'class': 'select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.order_by('name')
        self.fields['manufacturer'].queryset = Manufacturer.objects.order_by('name')
        self.fields['supplier'].queryset = Supplier.objects.order_by('name')

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise ValidationError('Стоимость товара не может быть отрицательной.')
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 0:
            raise ValidationError('Количество не может быть отрицательным.')
        return quantity


class OrderForm(forms.ModelForm):
    articles = forms.CharField(
        label='Артикул',
        help_text='Формат: артикул, количество, артикул, количество (например: А112Т4, 2, G843H5, 2)',
        widget=forms.TextInput(attrs={
            'placeholder': 'А112Т4, 2, G843H5, 2', 'class': 'input',
        }),
    )

    class Meta:
        model = Order
        fields = [
            'status', 'pickup_point', 'order_date', 'delivery_date',
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'select'}),
            'pickup_point': forms.Select(attrs={'class': 'select'}),
            'order_date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].queryset = OrderStatus.objects.order_by('name')
        self.fields['pickup_point'].queryset = PickupPoint.objects.order_by('id')
        if self.instance.pk:
            self.fields['articles'].initial = self.instance.articles_display

    def clean_articles(self):
        raw = self.cleaned_data['articles']
        parts = [p.strip() for p in raw.split(',') if p.strip()]
        if len(parts) < 2 or len(parts) % 2 != 0:
            raise ValidationError(
                'Неверный формат артикулов. Укажите пары «артикул, количество» через запятую.',
            )
        items = []
        for i in range(0, len(parts), 2):
            article = parts[i]
            try:
                qty = int(parts[i + 1])
            except ValueError as exc:
                raise ValidationError(
                    f'Количество для артикула «{article}» должно быть целым числом.',
                ) from exc
            if qty <= 0:
                raise ValidationError(
                    f'Количество для артикула «{article}» должно быть больше нуля.',
                )
            try:
                product = Product.objects.get(article=article)
            except Product.DoesNotExist as exc:
                raise ValidationError(
                    f'Товар с артикулом «{article}» не найден в каталоге.',
                ) from exc
            items.append({'product': product, 'quantity': qty})
        self.cleaned_items = items
        return raw
