import tempfile
from django.shortcuts import render
from django.http import FileResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from .forms import BelgeOlusturForm
from inventory.models import Product
from django.templatetags.static import static


def belge_formu(request):
    form = BelgeOlusturForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        belge_tipi = request.POST.get("belge_tipi")
        data = form.cleaned_data

        context = {
            "firma": data["firma"],
            "tarih": data["tarih"],
            "alici": data["alici"],
            "ihale_no": data["ihale_no"],
            "urun": data["urun"],
            "product": data["product"],  # Sadece ürünlü belgede kullanılacak
        }

        if belge_tipi == "yetki":
            return render_pdf(request, "yetki_belgesi_template.html", context)

        elif belge_tipi == "urunlu_yetki":
            context["urun_detay"] = Product.objects.filter(id=data["product"].id).first()
            return render_pdf(request, "urunlu_yetki_belgesi_template.html", context)

        elif belge_tipi == "kapsam_disi":
            return render_pdf(request, "kapsam_disi_belgesi_template.html", context)

    return render(request, "belge_formu.html", {"form": form})


def render_pdf(request, template_name, context):
    html_string = render_to_string(template_name, context)
    
    # Statik dosyalar için mutlak yol gerekiyor (görsellerin görünmesi için)
    base_url = request.build_absolute_uri(static(""))

    html = HTML(string=html_string, base_url=base_url)

    result = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    html.write_pdf(result.name)

    result.seek(0)
    return FileResponse(result, content_type="application/pdf")
