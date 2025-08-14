from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from django.template.loader import render_to_string
from .models import PrintingOrder, PrintingRef, PrintingOrderMovement
from .forms import PrintingOrderForm, PrintingOrderMovementForm, PrintingRefForm
from datetime import datetime, timedelta, date
from inventory.models import Product, StockMovement
from weasyprint import HTML
from django.http import HttpResponse
from django.urls import reverse
import qrcode
from io import BytesIO
import base64


# ---------------------------
# LISTELEME & FİLTRELEME
# ---------------------------
def printing_order_list(request):
    orders = PrintingOrder.objects.all().order_by('-date')

    # Tarih filtresi
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

    context = {
        'orders': orders,
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
    order_url = request.build_absolute_uri(order.get_absolute_url())
    qr_code_base64 = order.generate_qr_code_base64(order_url)
    movements = order.movements.all().order_by('-date')

    # Toplam KG hesaplama
    total_final = movements.filter(movement_type='final_in').aggregate(total=Sum('weight_kg'))['total'] or 0
    total_semi = movements.filter(movement_type='semi_in').aggregate(total=Sum('weight_kg'))['total'] or 0

    return render(request, 'printing_order_detail.html', {
        'order': order,
        'movements': movements,
        'total_final': total_final,
        'total_semi': total_semi,
        'qr_code': qr_code_base64
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
                movement.product = order.paper
                movement.save()

                # Mamül stoktan düş
                movement.product.stock_quantity = float(movement.product.stock_quantity) - float(movement.weight_kg)
                movement.product.save()

                StockMovement.objects.create(
                    product=movement.product,
                    movement_type='OUT',
                    quantity=float(movement.weight_kg),
                    description=f"Mamul üretimi: {order.order_no}"
)

            elif movement_type == 'semi_in':
                movement.product = order.paper  # dummy Product
                movement.semi_ref = order.ref_no
                movement.save()

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



def printing_order_complete(request, pk):
    order = get_object_or_404(PrintingOrder, pk=pk)

    if order.status != "Üretimde":
        messages.warning(request, "Sipariş zaten tamamlanmış veya henüz başlatılmamış.")
        return redirect('printing:printing_order_detail', pk=order.pk)

    # Siparişi manuel tamamla
    order.status_override = "Tamamlandı"
    order.save()

    messages.success(request, f"Sipariş {order.order_no} başarıyla tamamlandı.")
    return redirect('printing:printing_order_detail', pk=order.pk)

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

# ---------------------------
# BASKI PDF 
# ---------------------------
def printing_order_pdf(request, pk):
    order = get_object_or_404(PrintingOrder, pk=pk)
    
    order_url = request.build_absolute_uri(reverse('printing:printing_order_detail', args=[order.pk]))
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=6,
        border=2,
    )
    qr.add_data(order_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()  # <-- base64 string

    context = {
        'order': order,
        'qr_code_base64': qr_code_base64,  # template bunu direkt kullanacak
    }

    html_string = render(request, 'printing_order_pdf.html', context).content.decode('utf-8')
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'filename="siparis_{order.order_no}.pdf"'
    return response



def printing_order_movements_pdf(request, pk):
    order = get_object_or_404(PrintingOrder, pk=pk)
    movements = order.movements.all()

    # QR kod
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=3,
        border=2,
    )
    qr.add_data(request.build_absolute_uri())
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()

    html_string = render_to_string("printing_order_movements_pdf.html", {
        "order": order,
        "movements": movements,
        "total_final": sum(m.weight_kg for m in movements if m.movement_type == "final_in"),
        "total_semi": sum(m.weight_kg for m in movements if m.movement_type != "final_in"),
        "qr_code_base64": qr_code_base64,
    })

    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type="application/pdf")
    response['Content-Disposition'] = f'filename="siparis_{order.order_no}_hareketler.pdf"'
    return response