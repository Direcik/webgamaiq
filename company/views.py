from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CompanyForm, CompanyFilterForm
from .models import Company

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

