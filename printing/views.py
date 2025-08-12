from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import PrintingOrder
from .forms import PrintingOrderForm, PrintingOrderMovementForm

import qrcode
from io import BytesIO
import base64

def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')
    return render(request, 'printing_order_list.html', {'orders': orders})

def printing_order_create(request):
    if request.method == 'POST':
        form = PrintingOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            return redirect('printing_order_detail', pk=order.pk)
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
            return redirect('printing_order_detail', pk=pk)
    else:
        form = PrintingOrderMovementForm()

    # QR kod dinamik oluşturma
    url = request.build_absolute_uri(reverse('printing_order_detail', args=[order.pk]))
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
