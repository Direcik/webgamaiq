from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from .models import PrintingOrder, PrintingRef, PrintingOrderMovement
from .forms import PrintingOrderForm, PrintingOrderMovementForm, PrintingRefForm
from datetime import datetime, timedelta, date

def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')

    # Tarih filtresi (isteğe bağlı)
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

    # Sipariş durumu hesaplama
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


def printing_order_create(request):
    if request.method == 'POST':
        form = PrintingOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('printing:printing_order_detail', pk=order.pk)
    else:
        form = PrintingOrderForm()
    return render(request, 'printing_order_form.html', {'form': form})


def printing_order_detail(request, pk):
    order = get_object_or_404(PrintingOrder, pk=pk)
    movements = order.movements.all().order_by('-date')
    return render(request, 'printing_order_detail.html', {
        'order': order,
        'movements': movements,
    })


def add_movement(request, pk, movement_type):
    order = get_object_or_404(PrintingOrder, pk=pk)
    
    if request.method == 'POST':
        form = PrintingOrderMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.order = order
            movement.movement_type = movement_type

            if movement_type == 'final_in':
                movement.product = order.paper  # inventory.product otomatik
            elif movement_type == 'semi_in':
                movement.product = order.ref_no  # PrintingRef otomatik
                # toplam yarı mamul KG güncelle
                order.ref_no.total_semi_kg += movement.weight_kg
                order.ref_no.save()

            movement.save()
            return redirect('printing:printing_order_detail', pk=order.pk)
    else:
        form = PrintingOrderMovementForm()
        if movement_type == 'final_in':
            form.fields['product'].initial = order.paper
        elif movement_type == 'semi_in':
            form.fields['product'].initial = order.ref_no

    title = "Mamul Ekle" if movement_type == 'final_in' else "Yarı Mamul Ekle"

    return render(request, 'printing_add_movement.html', {
        'form': form,
        'title': title,
        'order': order,
    })

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
