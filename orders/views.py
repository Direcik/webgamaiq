from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from notifications.telegram import send_telegram_message

from .forms import OrderCompanyForm, OrderItemUpdateForm, OrderStatusForm, OrderFilterForm
from .models import Order, OrderItem, Product

from inventory.models import Product, StockMovement
from inventory.forms import CategoryFilterForm
from datetime import datetime, time, timedelta
from weasyprint import HTML



def generate_order_number():
    now = datetime.now()
    yy = now.strftime('%y')             # Yılın son iki hanesi, örn: '25'
    day_of_year = now.timetuple().tm_yday  # Yılın kaçıncı günü, örn: 191
    hour = now.strftime('%H')           # Saat, 24 saat formatı
    minute = now.strftime('%M')         # Dakika

    order_number = f"SIP{yy}{day_of_year:03d}{hour}{minute}"
    return order_number

@login_required
def order_create_view(request):
    order, created = Order.objects.get_or_create(created_by=request.user, status='pending')
    filter_form = CategoryFilterForm(request.GET or None)
    products = Product.objects.none()

    if filter_form.is_valid() and filter_form.cleaned_data.get('category'):
        products = Product.objects.filter(category=filter_form.cleaned_data['category'])

    order_form = OrderCompanyForm(instance=order)
    cart_product_ids = order.items.values_list('product_id', flat=True)

    return render(request, 'ordercreate.html', {
        'title': 'Firma ve Ürün Seçimi',
        'filter_form': filter_form,
        'order_form': order_form,
        'products': products,
        'cart_product_ids': list(cart_product_ids),
        'order': order,
    })


@require_POST
@login_required
def update_firma_ajax(request):
    order = get_object_or_404(Order, created_by=request.user, status='pending')
    form = OrderCompanyForm(request.POST, instance=order)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})


@require_POST
@login_required
def toggle_cart_product(request, product_id):
    order, _ = Order.objects.get_or_create(created_by=request.user, status='pending')
    product = get_object_or_404(Product, id=product_id)
    item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        item.delete()
        return JsonResponse({'added': False, 'message': 'Ürün sepetten çıkarıldı'})
    else:
        item.quantity = 1
        item.save()
        return JsonResponse({'added': True, 'message': 'Ürün sepete eklendi'})


@login_required
def load_products_by_category(request):
    category_id = request.GET.get('category')
    products = Product.objects.filter(category_id=category_id)
    order, _ = Order.objects.get_or_create(created_by=request.user, status='pending')
    cart_ids = order.items.values_list('product_id', flat=True)

    return render(request, 'partials/product_cards.html', {
        'products': products,
        'cart_product_ids': list(cart_ids)
    })

@login_required
def clear_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user, status='pending')

    # Ürünleri ve firma bilgisini sıfırla
    order.items.all().delete()
    order.customer_company = None
    order.save()

    messages.success(request, "Sipariş temizlendi.")
    return redirect('orders:ordercreate')

@login_required
def cart_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user, status='pending')
    return render(request, 'cart_detail.html', {'order': order})

@login_required
@require_POST
def cart_update_quantity(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__created_by=request.user, order__status='pending')
    try:
        qty = int(request.POST.get('quantity', 0))
        if qty < 1:
            raise ValueError()
        item.quantity = qty
        item.save()
        return JsonResponse({'success': True})
    except (ValueError, TypeError):
        return JsonResponse({'success': False})

@login_required
@require_POST
def cart_remove_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__created_by=request.user, order__status='pending')
    order = item.order
    item.delete()
    # Eğer sipariş kalemleri boşaldıysa, siparişi iptal et veya kullanıcıyı ürün seçimine yönlendir
    if not order.items.exists():
        # İstersen burda siparişi silebilirsin, biz sadece redirect flag yollayacağız
        return JsonResponse({'removed': True, 'item_id': item_id, 'redirect': True})
    return JsonResponse({'removed': True, 'item_id': item_id, 'redirect': False})

@login_required
@require_POST
def order_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user, status='pending')
    order.status = 'confirmed'
    # Sipariş numarası yoksa oluştur
    if not order.order_number:
        order.order_date = datetime.now()
        order.order_number = generate_order_number()  # Bu fonksiyonu kendi kodunda tanımlamalısın
        
    order.save()
    mesaj = (
            f"📦 <u><b>YENİ SİPARİŞ</b></u>\n"
            f"🧾 No: {order.order_number}\n"
            f"👤 Müşteri: {order.customer_company.name}\n"
            f"📅 Tarih: {order.order_date.strftime('%d/%m/%Y %H:%M:%S')}\n"
        )
    send_telegram_message(mesaj)
    messages.success(request, "Sipariş başarıyla kaydedildi.")
    return redirect('orders:ordercreate')  # Onay sonrası ürün seçme sayfasına yönlendirme

@login_required
@require_POST
def order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user, status='pending')
    order.status = 'cancelled'
    order.save()
    messages.info(request, "Sipariş iptal edildi.")
    # İstersen tüm kalemleri silebilirsin, ya da bırakabilirsin
    return redirect('orders:ordercreate')


@login_required
def order_list(request):
    form = OrderFilterForm(request.GET or None)
    filtered = False

    if form.is_valid():
        order_number = form.cleaned_data.get('order_number')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        status = form.cleaned_data.get('status')

        if order_number or start_date or end_date or status:
            orders = Order.objects.all()
            if order_number:
                orders = orders.filter(order_number=order_number)
            if start_date:
                orders = orders.filter(order_date__gte=start_date)
            if end_date:
                end_of_day = datetime.combine(end_date, time.max)
                orders = orders.filter(order_date__lte=end_of_day)
            if status:
                orders = orders.filter(status=status)

            orders = orders.order_by('-order_date')
            filtered = True
        else:
            # Filtre formu geçerli ama alanlar boş, o yüzden son 10 günü göster
            today = datetime.today()
            ten_days_ago = today - timedelta(days=10)
            orders = Order.objects.filter(order_date__gte=ten_days_ago).order_by('-order_date')
    else:
        # Form geçersizse hiçbir şey gösterme
        orders = Order.objects.none()

    return render(request, 'order_list.html', {
        'orders': orders,
        'filter_form': form,
        'title': 'Siparişlerim',
        'filtered': filtered,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, created_by=request.user)
    item_forms = []
    status_form = OrderStatusForm(request.POST or None, instance=order)

    if request.method == 'POST':
        is_valid = status_form.is_valid()

        for item in order.items.all():
            prefix = f'item_{item.id}'
            form = OrderItemUpdateForm(request.POST, prefix=prefix)
            if form.is_valid():
                new_delivery = form.cleaned_data['new_delivery']
                lot_no = form.cleaned_data['lot_no']

                if new_delivery > 0:
                    item.delivered_quantity += new_delivery
                    item.save()

                    # Stok hareketi oluştur
                    StockMovement.objects.create(
                        product=item.product,
                        quantity=new_delivery,
                        movement_type='OUT',
                        lot_no=lot_no,
                        company=order.customer_company,
                        user=request.user,
                        description=f"Sipariş No: {order.order_number}"
                    )
            else:
                is_valid = False

            kalan = item.quantity - item.delivered_quantity
            item_forms.append({
                'item': item,
                'form': OrderItemUpdateForm(prefix=prefix, initial={
                    'new_delivery': 0,
                    'lot_no': ''
                }),
                'kalan': kalan,
            })

        if is_valid:
            if status_form.has_changed():
                status_form.save()
            else:
                # Siparişteki toplam ve teslim edilen adetleri hesapla
                total_quantity = sum(i.quantity for i in order.items.all())
                total_delivered = sum(i.delivered_quantity for i in order.items.all())

                # Durumu otomatik güncelle
                # Hiç teslim edilmemişse durum 'onaylandı' (confirmed) kalsın
                if total_delivered == 0:
                    # Onaylandı durumunda kalmasını istediğiniz status değeri neyse onu yazın
                    order.status = 'confirmed'
                elif total_delivered < total_quantity:
                    order.status = 'partial'  # Kısmi teslimat durumu (durumunuzu buna göre ayarlayın)
                else:
                    order.status = 'delivered'  # Tam teslimat

            order.save()

            messages.success(request, "Sipariş güncellendi.")
            return redirect('orders:order_detail', order_id=order.id)

    else:
        for item in order.items.all():
            prefix = f'item_{item.id}'
            kalan = item.quantity - item.delivered_quantity
            item_forms.append({
                'item': item,
                'form': OrderItemUpdateForm(prefix=prefix, initial={
                    'new_delivery': 0,
                    'lot_no': ''
                }),
                'kalan': kalan,
            })

    return render(request, 'order_detail.html', {
        'order': order,
        'item_forms': item_forms,
        'status_form': status_form,
    })



def generate_order_html(order):
    # Word yerine HTML template oluştur
    return render_to_string('order_template.html', {'order': order})


def order_preview_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html_string = render_to_string('order_template.html', {
        'order': order,
        'items': order.items.all(),  # Bu satır önemli
    })
    
    # Mutlaka base_url verilmeli
    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))

    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="siparis_{order_id}.pdf"'
    return response
