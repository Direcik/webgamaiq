from .models import Company


def companies(request):
    return {'companies': Company.objects.all()}