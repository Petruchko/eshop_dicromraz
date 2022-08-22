import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, Address
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import CheckOutForm, CategoryForm
from django.db.models import Count
from allauth.account.decorators import login_required


class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 5

    def get_queryset(self):
        category = self.request.GET.get('category')
        if category:
            return Item.objects.filter(category=category)
        else:
            return Item.objects.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['categories'] = self.get_unique_categories()
        return context

    @staticmethod
    def get_unique_categories():
        items = Item.objects.all()
        categories = []
        for item in items:
            if item.category not in categories:
                categories.append((item.category, item.get_category_display))
        return categories

    # TODO сделать категории фильтр
    # TODO настроить систему оплаты


class OrderSummaryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'objects': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "У вас нету активного заказа")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'payment.html')


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckOutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckOutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                print(form.cleaned_data)
                street_address = form.cleaned_data.get('street_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                payment_option = form.cleaned_data.get('payment_option')
                address = Address.objects.create(
                    user=self.request.user,
                    street_address=street_address,
                    countries=country,
                    zip=zip
                )
                order.address = address
                order.save()
                if payment_option == 'N':
                    messages.info(self.request, 'Ваш заказ был создан. Ждите звонка от оператора')
                    return redirect('/')
                # TODO настроить Юкассу
                if payment_option == 'B':
                    messages.warning(self.request, 'Выберите другой метод оплаты')
                    return redirect('core:checkout')
            messages.warning(self.request, 'Ошибка оплаты')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "У вас нету активного заказа")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Если товар есть в заказе - добавляем еще один экземпляр
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Количество товара в корзине было обновлено")
        # Если товара не было - просто добавляем его
        else:
            messages.info(request, "Товар был добавлен в корзину")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Товар был добавлен в корзину")
    return redirect("core:product", slug=slug)


def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "Товар был удален из корзины")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "Товара не было в корзине")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "Вам нужно создать заказ")
        return redirect("core:product", slug=slug)


def add_quantity(request, slug):
    item = OrderItem.objects.get(user=request.user, item__slug=slug)
    item.quantity += 1
    item.save()
    return redirect("core:order-summary")


def minus_quantity(request, slug):
    item = OrderItem.objects.get(user=request.user, item__slug=slug)
    item.quantity -= 1
    item.save()
    return redirect("core:order-summary")


def delete_from_order(request, slug):
    order_item = OrderItem.objects.get(user=request.user, item__slug=slug)
    order = Order.objects.get(user=request.user, ordered=False)
    order.items.remove(order_item)
    return redirect("core:order-summary")


