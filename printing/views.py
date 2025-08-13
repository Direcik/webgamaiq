from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from .models import PrintingOrder, PrintingRef
from .forms import PrintingOrderForm, PrintingOrderMovementForm, PrintingRefForm
from datetime import datetime, timedelta, date
import qrcode
from io import BytesIO
import base64




def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')

    # Bugün ve 1 ay öncesi
    today = date.today()
    one_month_ago = today - timedelta(days=30)

    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Tarihleri datetime.date objesine çevir
    start_date = one_month_ago
    end_date = today
    date_format = "%Y-%m-%d"

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, date_format).date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, date_format).date()
    except ValueError:
        # Hatalı tarih gelirse default olarak son 1 ay kullan
        start_date = one_month_ago
        end_date = today

    orders = orders.filter(date__range=[start_date, end_date])

    context = {
        'orders': orders,
        'start_date': start_date.strftime(date_format),
        'end_date': end_date.strftime(date_format),
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
