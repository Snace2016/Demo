from django.db import models


class Role(models.TextChoices):
    CLIENT = 'client', 'Авторизированный клиент'
    MANAGER = 'manager', 'Менеджер'
    ADMIN = 'admin', 'Администратор'


class AppUser(models.Model):
    role = models.CharField('Роль', max_length=20, choices=Role.choices)
    full_name = models.CharField('ФИО', max_length=200)
    login = models.EmailField('Логин', unique=True)
    password = models.CharField('Пароль', max_length=100)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.full_name


class Category(models.Model):
    name = models.CharField('Категория', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField('Производитель', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Производитель'
        verbose_name_plural = 'Производители'

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField('Поставщик', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'

    def __str__(self):
        return self.name


class Product(models.Model):
    article = models.CharField('Артикул', max_length=20, unique=True)
    name = models.CharField('Наименование', max_length=300)
    unit = models.CharField('Единица измерения', max_length=20)
    price = models.DecimalField('Цена', max_digits=12, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name='Категория',
    )
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.PROTECT, verbose_name='Производитель',
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.PROTECT, verbose_name='Поставщик',
    )
    discount = models.DecimalField(
        'Действующая скидка', max_digits=5, decimal_places=2, default=0,
    )
    quantity = models.PositiveIntegerField('Количество на складе', default=0)
    description = models.TextField('Описание', blank=True)
    image = models.CharField('Путь к изображению', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['id']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        if self.discount > 0:
            return round(self.price * (100 - self.discount) / 100, 2)
        return self.price

    @property
    def has_discount(self):
        return self.discount > 0

    @property
    def is_out_of_stock(self):
        return self.quantity == 0

    @property
    def high_discount(self):
        return self.discount > 15


class PickupPoint(models.Model):
    address = models.CharField('Адрес', max_length=300)

    class Meta:
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'

    def __str__(self):
        return self.address


class OrderStatus(models.Model):
    name = models.CharField('Статус', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Статус заказа'
        verbose_name_plural = 'Статусы заказов'

    def __str__(self):
        return self.name


class Order(models.Model):
    number = models.PositiveIntegerField('Номер заказа', unique=True)
    status = models.ForeignKey(
        OrderStatus, on_delete=models.PROTECT, verbose_name='Статус',
    )
    pickup_point = models.ForeignKey(
        PickupPoint, on_delete=models.PROTECT, verbose_name='Пункт выдачи',
    )
    order_date = models.DateField('Дата заказа')
    delivery_date = models.DateField('Дата выдачи')
    client = models.ForeignKey(
        AppUser, on_delete=models.PROTECT,
        verbose_name='Клиент', limit_choices_to={'role': Role.CLIENT},
    )
    pickup_code = models.PositiveIntegerField('Код для получения')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['number']

    def __str__(self):
        return f'Заказ №{self.number}'

    @property
    def articles_display(self):
        items = self.items.select_related('product').all()
        parts = []
        for item in items:
            parts.append(f'{item.product.article}, {item.quantity}')
        return ', '.join(parts)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, verbose_name='Товар',
    )
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказов'

    def __str__(self):
        return f'{self.product.article} x{self.quantity}'
