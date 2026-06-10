from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .decorators import admin_required, manager_or_admin_required
from .forms import LoginForm, OrderForm, ProductForm
from .models import AppUser, Order, OrderItem, Product, Role
from .utils import delete_product_image, process_product_image


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        return AppUser.objects.filter(pk=user_id).first()
    return None


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            user = AppUser.objects.filter(login=login, password=password).first()
            if user:
                request.session['user_id'] = user.id
                request.session['user_role'] = user.role
                request.session['user_name'] = user.full_name
                messages.success(request, f'Добро пожаловать, {user.full_name}!')
                return redirect('product_list')
            messages.error(
                request,
                'Неверный логин или пароль. Проверьте введённые данные и попробуйте снова.',
            )
    else:
        form = LoginForm()
    return render(request, 'shop/login.html', {
        'form': form,
        'page_title': 'Вход в систему',
    })


def logout_view(request):
    request.session.flush()
    messages.info(request, 'Вы вышли из системы.')
    return redirect('login')


def guest_products_view(request):
    products = Product.objects.select_related(
        'category', 'manufacturer', 'supplier',
    ).all()
    return render(request, 'shop/product_list.html', {
        'products': products,
        'can_filter': False,
        'can_edit': False,
        'page_title': 'Каталог товаров (Гость)',
        'current_user': None,
    })


def product_list_view(request):
    user = get_current_user(request)
    role = request.session.get('user_role')

    if not user:
        return redirect('guest_products')

    products = Product.objects.select_related(
        'category', 'manufacturer', 'supplier',
    ).all()

    can_filter = role in (Role.MANAGER, Role.ADMIN)
    can_edit = role == Role.ADMIN

    return render(request, 'shop/product_list.html', {
        'products': products,
        'can_filter': can_filter,
        'can_edit': can_edit,
        'page_title': 'Список товаров',
        'current_user': user,
    })


@admin_required
def product_add_view(request):
    if request.session.get('editing_product_id'):
        messages.warning(
            request,
            'Сначала завершите редактирование текущего товара. '
            'Нельзя открыть более одного окна редактирования.',
        )
        return redirect('product_edit', pk=request.session['editing_product_id'])

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            image_file = form.cleaned_data.get('image_file')
            if image_file:
                product.image = process_product_image(image_file)
            product.save()
            messages.success(request, f'Товар «{product.name}» успешно добавлен.')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'shop/product_form.html', {
        'form': form,
        'is_edit': False,
        'page_title': 'Добавление товара',
        'current_user': get_current_user(request),
    })


@admin_required
def product_edit_view(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.session.get('editing_product_id') and request.session['editing_product_id'] != pk:
        messages.warning(
            request,
            'Уже открыто окно редактирования другого товара. Завершите его перед открытием нового.',
        )
        return redirect('product_edit', pk=request.session['editing_product_id'])

    request.session['editing_product_id'] = pk

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            updated = form.save(commit=False)
            image_file = form.cleaned_data.get('image_file')
            if image_file:
                delete_product_image(product.image)
                updated.image = process_product_image(image_file)
            updated.save()
            request.session.pop('editing_product_id', None)
            messages.success(request, f'Товар «{updated.name}» успешно обновлён.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'shop/product_form.html', {
        'form': form,
        'product': product,
        'is_edit': True,
        'page_title': 'Редактирование товара',
        'current_user': get_current_user(request),
    })


@admin_required
@require_POST
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if OrderItem.objects.filter(product=product).exists():
        messages.error(
            request,
            f'Невозможно удалить товар «{product.name}»: он присутствует в заказах. '
            'Сначала удалите связанные заказы или измените их состав.',
        )
        return redirect('product_list')

    name = product.name
    delete_product_image(product.image)
    product.delete()
    request.session.pop('editing_product_id', None)
    messages.success(request, f'Товар «{name}» удалён.')
    return redirect('product_list')


@admin_required
def product_cancel_edit_view(request, pk):
    request.session.pop('editing_product_id', None)
    return redirect('product_list')


@manager_or_admin_required
def order_list_view(request):
    orders = Order.objects.select_related(
        'status', 'pickup_point', 'client',
    ).prefetch_related('items__product').all()
    role = request.session.get('user_role')
    return render(request, 'shop/order_list.html', {
        'orders': orders,
        'can_edit': role == Role.ADMIN,
        'page_title': 'Список заказов',
        'current_user': get_current_user(request),
    })


@admin_required
def order_add_view(request):
    if request.session.get('editing_order_id'):
        messages.warning(
            request,
            'Сначала завершите редактирование текущего заказа.',
        )
        return redirect('order_edit', pk=request.session['editing_order_id'])

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            last = Order.objects.order_by('-number').first()
            new_number = (last.number + 1) if last else 1
            order = form.save(commit=False)
            order.number = new_number
            order.client = form.cleaned_data.get('client')
            if not order.client:
                from .models import AppUser
                order.client = AppUser.objects.filter(role=Role.CLIENT).first()
            order.pickup_code = 900 + new_number
            order.save()
            for item in form.cleaned_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                )
            messages.success(request, f'Заказ №{order.number} успешно создан.')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'shop/order_form.html', {
        'form': form,
        'is_edit': False,
        'page_title': 'Добавление заказа',
        'current_user': get_current_user(request),
    })


@admin_required
def order_edit_view(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.session.get('editing_order_id') and request.session['editing_order_id'] != pk:
        messages.warning(request, 'Уже открыто окно редактирования другого заказа.')
        return redirect('order_edit', pk=request.session['editing_order_id'])

    request.session['editing_order_id'] = pk

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            updated = form.save()
            order.items.all().delete()
            for item in form.cleaned_items:
                OrderItem.objects.create(
                    order=updated,
                    product=item['product'],
                    quantity=item['quantity'],
                )
            request.session.pop('editing_order_id', None)
            messages.success(request, f'Заказ №{updated.number} успешно обновлён.')
            return redirect('order_list')
    else:
        form = OrderForm(instance=order)

    return render(request, 'shop/order_form.html', {
        'form': form,
        'order': order,
        'is_edit': True,
        'page_title': 'Редактирование заказа',
        'current_user': get_current_user(request),
    })


@admin_required
@require_POST
def order_delete_view(request, pk):
    order = get_object_or_404(Order, pk=pk)
    number = order.number
    order.delete()
    request.session.pop('editing_order_id', None)
    messages.success(request, f'Заказ №{number} удалён.')
    return redirect('order_list')
