from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import PrintingOrder, PrintingRef
from .forms import PrintingOrderForm, PrintingOrderMovementForm, PrintingRefForm
from datetime import date, timedelta
import qrcode
from io import BytesIO
import base64




def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')

    # Tarih filtresi için default değerler: son 1 ay
    today = date.today()
    one_month_ago = today - timedelta(days=30)

    start_date = request.GET.get('start_date', one_month_ago)
    end_date = request.GET.get('end_date', today)

    # Filtreleme (GET parametreleri varsa uygula)
    if start_date:
        try:
            start_date_obj = date.fromisoformat(str(start_date))
            orders = orders.filter(date__gte=start_date_obj)
        except ValueError:
            pass

    if end_date:
        try:
            end_date_obj = date.fromisoformat(str(end_date))
            orders = orders.filter(date__lte=end_date_obj)
        except ValueError:
            pass

    context = {
        'orders': orders,
        'start_date': start_date,
        'end_date': end_date,
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

    if request.method == 'POST':
        form = PrintingOrderMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.order = order
            movement.save()
            return redirect('printing:printing_order_detail', pk=pk)
    else:
        form = PrintingOrderMovementForm()

    # QR kod dinamik oluşturma
    url = request.build_absolute_uri(reverse('printing:printing_order_detail', args=[order.pk]))
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'printing_order_detail.html', {
        'order': order,
        'movements': movements,
        'form': form,
        'qr_code': qr_code_base64,
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
