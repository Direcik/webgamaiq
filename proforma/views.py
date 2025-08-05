from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from inventory.models import Product
from django.template.loader import render_to_string, get_template
from django.utils import timezone

from .forms import ProformaConfirmForm
from .models import ProformaDraft, ProformaDraftItem, ProformaInvoice, ProformaItem

from inventory.forms import CategoryFilterForm

from datetime import timedelta
from weasyprint import HTML

# 1. Ürün seçme ekranı
def product_selection_view(request):
    category_id = request.GET.get('category')
    products = Product.objects.none()  # başlangıçta boş gelsin

    filter_form = CategoryFilterForm(request.GET or None)

    if category_id:
        products = Product.objects.filter(category_id=category_id)

    draft_id = request.session.get("proforma_draft_id")
    if draft_id:
        draft, created = ProformaDraft.objects.get_or_create(id=draft_id)
    else:
        draft = ProformaDraft.objects.create()
        request.session["proforma_draft_id"] = draft.id

    selected_product_ids = draft.items.values_list("product_id", flat=True)

    context = {
        "products": products,
        "filter_form": filter_form,
        "selected_product_ids": list(selected_product_ids),
        "draft": draft,
    }
    return render(request, "product_selection.html", context)


# 2. Ürün sepete ekle/çıkar
@require_POST
def toggle_product_in_draft(request, product_id):
    draft_id = request.session.get("proforma_draft_id")
    draft = get_object_or_404(ProformaDraft, id=draft_id)
    product = get_object_or_404(Product, id=product_id)

    item, created = ProformaDraftItem.objects.get_or_create(draft=draft, product=product)
    if not created:
        item.delete()
        return JsonResponse({"removed": True, "product_id": product.id})
    return JsonResponse({"added": True, "product_id": product.id})


# 3. Miktar ve fiyat giriş ekranı
def draft_detail_view(request, draft_id):
    draft = get_object_or_404(ProformaDraft, id=draft_id)

    if request.method == "POST":
        # Firma adı ve para birimini al
        draft.company_name = request.POST.get("company_name")
        draft.currency = request.POST.get("currency", "TRY")
        draft.vat_rate = request.POST.get("vat_rate")
        draft.exchange_rate = request.POST.get("exchange_rate")
        draft.save()

        # Ürün bilgilerini al
        for item in draft.items.all():
            quantity = request.POST.get(f"quantity_{item.id}")
            unit_price = request.POST.get(f"unit_price_{item.id}")
            item.quantity = int(quantity or 0)
            item.unit_price = float(unit_price or 0)
            item.save()

        # Doğrudan onay ekranına gönderiyoruz
        return redirect("proforma:confirm_draft")

    return render(request, "draft_detail.html", {"draft": draft})
#Onay Ekranı
def confirm_draft_view(request):
    draft_id = request.session.get("proforma_draft_id")

    draft = get_object_or_404(ProformaDraft, id=draft_id)

    # Toplam hesapla
    total_amount = sum(item.total_price() for item in draft.items.all())
    total_with_vat = total_amount + (total_amount * draft.vat_rate / 100)
    total_tl = total_with_vat * draft.exchange_rate

    if request.method == 'POST':
        form = ProformaConfirmForm(request.POST)
        invoice = ProformaInvoice.objects.create(
                company_name=draft.company_name,
                currency=draft.currency,
                vat_rate=draft.vat_rate,
                exchange_rate=draft.exchange_rate
            )
        if form.is_valid():
            invoice = ProformaInvoice.objects.create(
                    company_name=draft.company_name,
                    currency=form.cleaned_data['currency'],
                    vat_rate=form.cleaned_data['vat_rate'],
                    exchange_rate=form.cleaned_data['exchange_rate'],  # 🔥 burada kaydediliyor
                    # diğer alanlar...
                )
        for item in draft.items.all():
            ProformaItem.objects.create(
                invoice=invoice,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
        draft.delete()
        return redirect("proforma:invoice_detail", invoice_id=invoice.id)
    else:
        form = ProformaConfirmForm(initial={
            'currency': draft.currency,
            'vat_rate': draft.vat_rate,
            'exchange_rate': draft.exchange_rate,
        })

    return render(request, "confirm_draft.html", {
        "draft": draft,
        "total_amount": total_amount,
        "total_with_vat": total_with_vat,
        "total_tl": total_tl,
        'form': form,
    })



def load_products_by_category(request):
    category_id = request.GET.get("category")
    products = Product.objects.all()
    if category_id:
        products = products.filter(category_id=category_id)

    draft_id = request.session.get("proforma_draft_id")
    draft = get_object_or_404(ProformaDraft, id=draft_id)
    selected_product_ids = draft.items.values_list("product_id", flat=True)

    html = render_to_string("partials/product_list.html", {
        "products": products,
        "selected_product_ids": list(selected_product_ids),
    })

    return HttpResponse(html)

def clear_proforma_draft(request, draft_id):
    draft = get_object_or_404(ProformaDraft, id=draft_id)
    draft.delete()
    if "proforma_draft_id" in request.session:
        del request.session["proforma_draft_id"]
    return redirect("proforma:product_selection")

#Detay Sayfası
def proforma_detail(request, invoice_id):
    invoice = get_object_or_404(ProformaInvoice, id=invoice_id)
    return render(request, "invoice_detail.html", {"invoice": invoice})

#PDF

def generate_proforma_pdf(request, invoice_id):
    invoice = get_object_or_404(ProformaInvoice, id=invoice_id)
    template = get_template("proforma_pdf.html")
    html_content = template.render({"invoice": invoice})

    # PDF'yi doğrudan bellek üzerinde oluştur
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Proforma_{invoice.id}.pdf"'
    return response


#proforma listesi
def invoice_list(request):
    today = timezone.now().date()
    default_start_date = today - timedelta(days=30)
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    try:
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else default_start_date
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else today
    except ValueError:
        start_date = default_start_date
        end_date = today

    invoices = ProformaInvoice.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).order_by("-created_at")

    context = {
        'invoices': invoices,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'invoice_list.html', context)


def invoice_pdf_view(request, pk):
    invoice = get_object_or_404(ProformaInvoice, pk=pk)
    html_string = render_to_string('invoice_detail.html', {'invoice': invoice})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    return html.write_pdf(stylesheets=[...])
