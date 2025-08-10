from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_GET
import os
from .forms import CompanyForm, CompanyFilterForm
from .models import Company
from zeep import Client

def index(request):
    return render(request, "index.html")


@login_required
def companyDashboard(request):
    form = CompanyFilterForm(request.GET or None)
    companies = Company.objects.all()

    if form.is_valid():
        name = form.cleaned_data.get('name')

        if name:
            companies = companies.filter(name__icontains=name)

    return render(request, 'companydashboard.html', {
        'form': form,
        'companies': companies,
    })


def addCompany(request):
    form = CompanyForm()
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Firma Ekleme Başarılı")
            return redirect("addcompany")
    return render(request, 'addcompany.html', {"form":form})

def updateCompany(request, id):
    company = get_object_or_404(Company, id=id)
    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    if form.is_valid():
        company = form.save(commit = False)
        company.save()
        messages.success(request, '{} Firması Güncellendi.'.format(company.name))
        return redirect("companydashboard")
    return render(request, "updatecompany.html", {'form': form})

def deleteCompany(request, id):
        company = get_object_or_404(Company, id=id)
        company.delete()
        messages.info(request, "{} Firması Silindi.".format(company.name))
        return redirect("companydashboard")


@login_required
@require_GET
def get_company_from_izibiz(request):
    tax_number = request.GET.get('tax_number')
    if not tax_number:
        return JsonResponse({"error": "Vergi numarası gerekli"}, status=400)

    try:
        wsdl_url = os.environ.get("IZIBIZ_URL")
        username = os.environ.get("IZIBIZ_USERNAME")
        password = os.environ.get("IZIBIZ_PASSWORD")

        client = Client(wsdl_url)

        # getGibUserList çağrısı
        result = client.service.getGibUserList(
            VKN_TCKN=tax_number,
            role="PK",
            username=username,
            password=password
        )

        if not result or len(result) == 0:
            return JsonResponse({"error": "Firma bulunamadı"}, status=404)

        # İzibiz dönüş yapısını çözümleme
        user_info = result[0]
        company_data = {
            "name": getattr(user_info, "title", ""),
            "address": getattr(user_info, "address", ""),
            "email": getattr(user_info, "email", ""),
            "phone": getattr(user_info, "phone", "")
        }
        return JsonResponse(company_data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

