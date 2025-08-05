from .models import Order

def cart_item_count(request):
    if request.user.is_authenticated:
        order = Order.objects.filter(created_by=request.user, status='pending').first()
        if order:
            # Toplam kalem sayısı (adet değil)
            item_count = order.items.count()
            return {'cart_item_count': item_count}
    return {'cart_item_count': 0}