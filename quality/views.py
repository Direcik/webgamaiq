# quality/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.db.models import Q

from .models import QualityReport

from .forms import QualityReportForm, CategoryFilterForm, QualityReportSearchForm
from weasyprint import HTML

def create_quality_report(request):
    category_form = CategoryFilterForm(request.GET or None)
    selected_category = None

    if category_form.is_valid():
        selected_category = category_form.cleaned_data.get('category')

    form = QualityReportForm(request.POST or None, selected_category=selected_category)

    if request.method == 'POST' and form.is_valid():
        report = form.save(commit=False)  # Nesneyi al ama henüz veritabanına kaydetme
        report.save()  # Şimdi kaydet
        messages.success(request, f"{report.lot_number} numaralı kalite raporu başarıyla oluşturuldu.")
        return redirect('quality:create_report')

    return render(request, 'create_report.html', {
        'form': form,
        'category_form': category_form,
    })

def quality_report_list(request):
    form = QualityReportSearchForm(request.GET or None)
    reports = None  # Başlangıçta boş

    if form.is_valid():
        query = form.cleaned_data.get("q")
        if query:
            reports = QualityReport.objects.select_related("product").filter(
                Q(product__name_tr__icontains=query) | Q(lot_number__icontains=query)
            ).order_by("-created_at")

    return render(request, "report_list.html", {"reports": reports, "form": form})

def quality_report_pdf(request, pk):
    report = get_object_or_404(QualityReport, pk=pk)

    form = QualityReportForm()
    paper_translations = form.paper_translations
    film_translations = form.film_translations

    paper_en = paper_translations.get(report.paper, '')
    film_en = film_translations.get(report.film, '')

    context = {
        'report': report,
        'paper_en': paper_en,
        'film_en': film_en,
    }

    html_string = render_to_string("quality_report_pdf.html", context)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    # PDF'yi tarayıcıda aç, dosya ismini report_number ile ayarla
    filename = f"quality_report_{report.lot_number}_{report.report_number}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response