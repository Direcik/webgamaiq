from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import PrintingOrder, PrintingRef, PrintingOrderMovement
from .forms import PrintingOrderForm, PrintingOrderMovementForm, PrintingRefForm
from datetime import datetime, timedelta, date
from inventory.models import Product, StockMovement
from decimal import Decimal
# ---------------------------
# LISTELEME & FİLTRELEME
# ---------------------------
def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    today = date.today()
    one_month_ago = today - timedelta(days=30)

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else one_month_ago
    except ValueError:
        start_date = one_month_ago

    try:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today
    except ValueError:
        end_date = today

    orders = orders.filter(date__range=[start_date, end_date])

    # Sipariş durumu
    orders_with_status = []
    for order in orders:
        semi_in_total = order.movements.filter(movement_type='semi_in').aggregate(total=Sum('weight_kg'))['total'] or 0
        if order.movements.count() == 0:
            status = "Sipariş Oluşturuldu"
        elif semi_in_total >= order.weight:
            status = "Tamamlandı"
        else:
            status = "Üretimde"
        orders_with_status.append((order, status))

    context = {
        'orders_with_status': orders_with_status,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'printing_order_list.html', context)


# ---------------------------
# SİPARİŞ OLUŞTUR
# ---------------------------
def printing_order_create(request):
    if request.method == 'POST':
        form = PrintingOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('printing:printing_order_detail', pk=order.pk)
    else:
        form = PrintingOrderForm()
    return render(request, 'printing_order_form.html', {'form': form})


# ---------------------------
# SİPARİŞ DETAY & HAREKETLER
# ---------------------------
def printing_order_detail(request, pk):
    order = get_object_or_404(PrintingOrder, pk=pk)
    movements = order.movements.all().order_by('-date')

    # Toplam KG hesaplama
    total_final = movements.filter(movement_type='final_in').aggregate(total=Sum('weight_kg'))['total'] or 0
    total_semi = movements.filter(movement_type='semi_in').aggregate(total=Sum('weight_kg'))['total'] or 0

    return render(request, 'printing_order_detail.html', {
        'order': order,
        'movements': movements,
        'total_final': total_final,
        'total_semi': total_semi,
    })

# ---------------------------
# HAREKET EKLEME
# ---------------------------
def add_movement(request, pk, movement_type):
    order = get_object_or_404(PrintingOrder, pk=pk)

    if request.method == 'POST':
        form = PrintingOrderMovementForm(request.POST, movement_type=movement_type, order=order)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.order = order
            movement.movement_type = movement_type

            if movement_type == 'final_in':
                # Mamul: Kağıt otomatik
                movement.product = order.paper
                movement.save()

                # Mamül stoktan düşme
                movement_quantity = Decimal(movement.weight_kg)
                movement.product.stock_quantity = Decimal(movement.product.stock_quantity) - movement_quantity
                movement.product.save()

                # StockMovement kaydı oluştur
                StockMovement.objects.create(
                    product=movement.product,
                    movement_type='OUT',
                    quantity=float(movement_quantity),
                    description=f"Mamul üretimi: {order.order_no}"
                )

            elif movement_type == 'semi_in':
                # Yarı mamul: PrintingRef ile ilişkilendir
                movement.product = order.paper  # dummy product
                movement.semi_ref = order.ref_no
                movement.save()

                # PrintingRef toplam yarı mamul KG güncelle
                total_semi = order.movements.filter(
                    movement_type='semi_in',
                    semi_ref=order.ref_no
                ).aggregate(total=Sum('weight_kg'))['total'] or 0
                order.ref_no.total_semi_kg = total_semi
                order.ref_no.save()

            return redirect('printing:printing_order_detail', pk=order.pk)

    else:
        form = PrintingOrderMovementForm(movement_type=movement_type, order=order)
        if movement_type == 'final_in':
            form.fields['product'].initial = order.paper

    title = "Mamul Ekle" if movement_type == 'final_in' else "Yarı Mamul Ekle"

    return render(request, 'printing_add_movement.html', {
        'form': form,
        'title': title,
        'order': order,
    })

# ---------------------------
# BASKI REF
# ---------------------------
def printing_ref_list(request):
    refs = PrintingRef.objects.all()
    return render(request, 'printing_ref_list.html', {'refs': refs})


def printing_ref_add(request):
    if request.method == 'POST':
        form = PrintingRefForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Baskı ref numarası eklendi.')
            return redirect('printing:printing_ref_list')
    else:
        form = PrintingRefForm()
    return render(request, 'printing_ref_form.html', {'form': form})


def printing_ref_edit(request, pk):
    ref = get_object_or_404(PrintingRef, pk=pk)
    if request.method == 'POST':
        form = PrintingRefForm(request.POST, instance=ref)
        if form.is_valid():
            form.save()
            messages.success(request, 'Baskı ref numarası güncellendi.')
            return redirect('printing:printing_ref_list')
    else:
        form = PrintingRefForm(instance=ref)
    return render(request, 'printing_ref_form.html', {'form': form})


def printing_ref_delete(request, pk):
    ref = get_object_or_404(PrintingRef, pk=pk)
    ref.delete()
    messages.success(request, 'Baskı ref numarası silindi.')
    return redirect('printing:printing_ref_list')
