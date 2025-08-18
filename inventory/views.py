from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm, CategoryForm, UnitForm, WarehouseForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Unit, Warehouse, StockMovement
from django.contrib import messages
from .forms import ProductFilterForm, StockInForm, StockOutForm, CategoryFilterForm, StockMovementFilterForm
from datetime import datetime, time

def index(request):
    return render(request, "index.html")

def productDashboard(request):
    form = ProductFilterForm(request.GET or None)
    products = Product.objects.all()

    if form.is_valid():
        category = form.cleaned_data.get('category')
        ref_no = form.cleaned_data.get('ref_no')

        if category:
            products = products.filter(category=category)
        if ref_no:
            products = products.filter(ref_no__icontains=ref_no)

    return render(request, 'productdashboard.html', {
        'form': form,
        'products': products,
    })


def addProduct(request):
    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ürün Ekleme Başarılı")
            return redirect("addproduct")
    return render(request, 'addproduct.html', {"form":form})

def updateProduct(request, id):
    product = get_object_or_404(Product, id=id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        product = form.save(commit = False)
        product.save()
        messages.success(request, '{} Ürünü Güncellendi.'.format(product.name_tr))
        return redirect("productdashboard")
    return render(request, "updateproduct.html", {'form': form})

def deleteProduct(request, id):
        product = get_object_or_404(Product, id=id)
        product.delete()
        messages.info(request, "{} REFNO'lu {} Ürünü Silindi.".format(product.ref_no, product.name_tr))
        return redirect("productdashboard")


#---------------------Kategori İşlemleri---------------------

def addCategory(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    categories = Category.objects.all()
    if form.is_valid():
        category = form.save(commit = False)
        if Category.objects.filter(name=category):
            messages.warning(request,'{} Kategorisi Mevcut.'.format(category.name))
        else:
            category.save()
            messages.success(request, '{} Kategorisi Eklendi.'.format(category.name))
        return redirect("addcategory")
    return render(request, 'addcategory.html', {"form":form, 'categories':categories})

def updateCategory(request, id):
    category = get_object_or_404(Category, id=id)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if form.is_valid():
        category = form.save(commit = False)
        category.save()
        messages.success(request, '{} Güncellendi.'.format(category.name))
        return redirect("addcategory")
    return render(request, "updatecategory.html", {'form': form})

def deleteCategory(request, id):
        category = get_object_or_404(Category, id=id)
        category.delete()
        messages.info(request, "{} Kategorisi Silindi.".format(category.name))
        return redirect("addcategory")

#---------------------Birim İşlemleri---------------------

def addUnit(request):
    form = UnitForm(request.POST or None, request.FILES or None)
    units = Unit.objects.all()
    if form.is_valid():
        unit = form.save(commit = False)
        if Category.objects.filter(name=unit):
            messages.warning(request,'{} Birimi Mevcut.'.format(unit.name))
        else:
            unit.save()
            messages.success(request, '{} Birimi Eklendi.'.format(unit.name))
        return redirect("addunit")
    return render(request, 'addunit.html', {"form":form, 'units':units})

def updateUnit(request, id):
    unit = get_object_or_404(Unit, id=id)
    form = UnitForm(request.POST or None, request.FILES or None, instance=unit)
    if form.is_valid():
        unit = form.save(commit = False)
        unit.save()
        messages.success(request, '{} Güncellendi.'.format(unit.name))
        return redirect("addunit")
    return render(request, "updateunit.html", {'form': form})

def deleteUnit(request, id):
        unit = get_object_or_404(Unit, id=id)
        unit.delete()
        messages.info(request, "{} Birimi Silindi.".format(unit.name))
        return redirect("addunit")


#---------------------Depo İşlemleri---------------------

def addWarehouse(request):
    form = WarehouseForm(request.POST or None, request.FILES or None)
    warehouses = Warehouse.objects.all()
    if form.is_valid():
        warehouse = form.save(commit = False)
        if Category.objects.filter(name=warehouse):
            messages.warning(request,'{} Mevcut.'.format(warehouse.name))
        else:
            warehouse.save()
            messages.success(request, '{} Eklendi.'.format(warehouse.name))
        return redirect("addwarehouse")
    return render(request, 'addwarehouse.html', {"form":form, 'warehouses':warehouses})

def updateWarehouse(request, id):
    warehouse = get_object_or_404(Warehouse, id=id)
    form = WarehouseForm(request.POST or None, request.FILES or None, instance=warehouse)
    if form.is_valid():
        warehouse = form.save(commit = False)
        warehouse.save()
        messages.success(request, '{} Güncellendi.'.format(warehouse.name))
        return redirect("addwarehouse")
    return render(request, "updatewarehouse.html", {'form': form})

def deleteWarehouse(request, id):
        warehouse = get_object_or_404(Warehouse, id=id)
        warehouse.delete()
        messages.info(request, "{} Silindi.".format(warehouse.name))
        return redirect("addwarehouse")
    
#---------------------Ürüm Seçim İşlemleri---------------------
def index(request):
    return render(request, 'index.html')

def product_detail(request, product_slug):
    products = get_object_or_404(Product, slug=product_slug)
    return render(request, 'detail.html', {'products': products})

def category_list(request, category_slug):
    categories = get_object_or_404(Category, slug=category_slug)
    return render(request, 'inventorydefinitions.html', {'categories':categories})

def unit_list(request, unit_slug):
    units = get_object_or_404(Category, slug=unit_slug)
    return render(request, 'inventorydefinitions.html', {'units':units})

def warehouse_list(request, warehouse_slug):
    warehouses = get_object_or_404(Category, slug=warehouse_slug)
    return render(request, 'inventorydefinitions.html', {'warehouses':warehouses})


@login_required
def stock_movement_list(request):
    """
    Stok hareketlerini filtrelenmiş şekilde listeler.
    Sayfa ilk yüklendiğinde veri getirmez. Sadece filtre yapılırsa sonuç döner.
    """
    stock_movements = StockMovement.objects.none()  # Şu an listeyi boş başlatıyoruz
    filter_form = StockMovementFilterForm(request.GET or None)
    category_form = CategoryFilterForm(request.GET or None)
    filtered = False

    if filter_form.is_valid():
        start_date = filter_form.cleaned_data.get('start_date')
        end_date = filter_form.cleaned_data.get('end_date')
        movement_type = filter_form.cleaned_data.get('movement_type')
        category = category_form.cleaned_data.get('category')

        # En az bir filtre alanı doluysa filtreleme yap
        if start_date or end_date or movement_type:
            stock_movements = StockMovement.objects.all()
            
            if start_date:
                stock_movements = stock_movements.filter(movement_date__gte=start_date)

            if end_date:
                end_of_day = datetime.combine(end_date, time.max)
                stock_movements = stock_movements.filter(movement_date__lte=end_of_day)

            if movement_type:
                stock_movements = stock_movements.filter(movement_type=movement_type)
                
            if category:
                stock_movements = stock_movements.filter(product__category=category)  # ✅ ürün kategorisine göre filtrele

            stock_movements = stock_movements.order_by('-movement_date')
            filtered = True

    context = {
        'stock_movements': stock_movements,
        'filter_form': filter_form,
        'category_form': category_form,
        'title': 'Stok Hareketleri Listesi',
        'filtered': filtered,  # Eğer filtre uygulanmışsa True gönder
    }
    return render(request, 'stock_movement_list.html', context)

# --- Stok Giriş View'i ---
@login_required
def add_stock_in(request):
    company = getattr(request.user, 'company', None)
    if request.method == 'POST':
        form = StockInForm(request.POST, company=company)
        if form.is_valid():
            stock_movement = form.save(commit=False)
            stock_movement.movement_type = 'IN'
            stock_movement.user = request.user
            # Formun clean metodu zaten product'ı bulup ekledi
            stock_movement.product = form.cleaned_data['product']
            stock_movement.save()
            messages.success(request, 'Stok girişi başarıyla kaydedildi!')
            return redirect('add_stock_in')
        else:
            messages.error(request, 'Stok girişi kaydedilirken bir hata oluştu. Lütfen formu kontrol edin.')
            # Hata durumunda formun input alanlarını doldurmak için mevcut POST verileriyle formu tekrar oluştur
            context = {
                'form': form,
                'title': 'Yeni Stok Girişi',
            }
            return render(request, 'stock_in.html', context)
    else:
        form = StockInForm(company=company)

    context = {
        'form': form,
        'title': 'Yeni Stok Girişi',
    }
    return render(request, 'stock_in.html', context)

# --- Stok Çıkış View'i ---
@login_required
def add_stock_out(request):
    company = getattr(request.user, 'company', None)
    if request.method == 'POST':
        form = StockOutForm(request.POST, company=company)
        if form.is_valid():
            stock_movement = form.save(commit=False)
            stock_movement.movement_type = 'OUT'
            stock_movement.user = request.user
            # Formun clean metodu zaten product'ı bulup ekledi
            stock_movement.product = form.cleaned_data['product']
            stock_movement.save()
            messages.success(request, 'Stok çıkışı başarıyla kaydedildi!')
            return redirect('add_stock_out')
        else:
            messages.error(request, 'Stok çıkışı kaydedilirken bir hata oluştu. Lütfen formu kontrol edin.')
            # Hata durumunda formun input alanlarını doldurmak için mevcut POST verileriyle formu tekrar oluştur
            context = {
                'form': form,
                'title': 'Yeni Stok Çıkışı',
            }
            return render(request, 'stock_out.html', context)
    else:
        form = StockOutForm(company=company)

    context = {
        'form': form,
        'title': 'Yeni Stok Çıkışı',
    }
    return render(request, 'stock_out.html', context)

# --- AJAX için Ürün Bilgisi (Yeni View) ---
@login_required
def get_product_info_by_barcode_json(request):
    barcode = request.GET.get('barcode', '').strip()
    if not barcode:
        return JsonResponse({'found': False, 'message': 'Barkod girilmedi.'})

    try:
        product = Product.objects.get(barcode=barcode)
        data = {
            'found': True,
            'ref_no': product.ref_no,
            'name_tr': product.name_tr,
            'stock_quantity': product.stock_quantity,
            'barcode': product.barcode,
        }
    except Product.DoesNotExist:
        data = {'found': False, 'message': 'Ürün bulunamadı.'}
    return JsonResponse(data)

@login_required
def get_product_info_by_refno_json(request):
    ref_no = request.GET.get('ref_no', '').strip()
    if not ref_no:
        return JsonResponse({'found': False, 'message': 'Ref No girilmedi.'})

    try:
        product = Product.objects.get(ref_no=ref_no)
        data = {
            'found': True,
            'ref_no': product.ref_no,
            'name_tr': product.name_tr,
            'stock_quantity': product.stock_quantity,
            'barcode': product.barcode,
        }
    except Product.DoesNotExist:
        data = {'found': False, 'message': 'Ürün bulunamadı.'}
    return JsonResponse(data)

@login_required
def product_stock_summary(request):
    """
    Filtre uygulanmadıkça hiçbir ürün göstermez.
    Kullanıcı kategori filtresi yaptığında ürünler listelenir.
    """
    filter_form = CategoryFilterForm(request.GET or None)
    products_summary = Product.objects.none()  # Başlangıçta boş queryset
    filtered = False

    if filter_form.is_valid():
        selected_category = filter_form.cleaned_data.get('category')
        if selected_category:
            products_summary = Product.objects.filter(category=selected_category).order_by('ref_no')
            filtered = True

    context = {
        'products_summary': products_summary,
        'filter_form': filter_form,
        'title': 'Ürün Stok Özeti',
        'filtered': filtered,
    }
    return render(request, 'product_stock_summary.html', context)

