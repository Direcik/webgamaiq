from django.db import models
from inventory.models import Product



class QualityReport(models.Model):
    production_date = models.DateField()
    expiry_date = models.DateField(blank=True, null=True)
    lot_number = models.CharField(max_length=100)

    paper = models.CharField(max_length=50, choices=[
        ('Medikal Kraft Kağıt', 'Medikal Kraft Kağıt'),
        ('Tyvek', 'Tyvek')
    ])
    paper_en = models.CharField(max_length=100, blank=True)

    film = models.CharField(max_length=50, choices=[
        ('CPP+PET', 'CPP+PET'),
        ('PET+PE', 'PET+PE')
    ])
    film_en = models.CharField(max_length=100, blank=True)

    paper_weight = models.DecimalField(max_digits=6, decimal_places=2)
    film_weight = models.DecimalField(max_digits=6, decimal_places=2)
    paper_thickness = models.DecimalField(max_digits=6, decimal_places=2)
    film_thickness = models.DecimalField(max_digits=6, decimal_places=2)

    size_check = models.CharField(max_length=20, choices=[
        ('uygun', 'Uygun'),
        ('uygun_degil', 'Uygun Değil')
    ])
    size_check_en = models.CharField(max_length=50, blank=True)

    seal_strength_left = models.DecimalField(max_digits=6, decimal_places=2)
    seal_strength_right = models.DecimalField(max_digits=6, decimal_places=2)
    seal_strength_top = models.DecimalField(max_digits=6, decimal_places=2)

    leakage_test = models.CharField(max_length=20, choices=[
        ('uygun', 'Uygun'),
        ('uygun_degil', 'Uygun Değil')
    ])
    leakage_test_en = models.CharField(max_length=50, blank=True)

    peeling_direction = models.CharField(max_length=20, choices=[
        ('uygun', 'Uygun'),
        ('uygun_degil', 'Uygun Değil')
    ])
    peeling_direction_en = models.CharField(max_length=50, blank=True)

    indicator_1 = models.CharField(max_length=10, choices=[
        ('buhar', 'Buhar'),
        ('eo', 'EO'),
        ('plazma', 'Plazma')
    ])
    indicator_2 = models.CharField(max_length=10, choices=[
        ('buhar', 'Buhar'),
        ('eo', 'EO'),
        ('plazma', 'Plazma')
    ])

    indicator_1_en = models.CharField(max_length=50, blank=True)
    indicator_2_en = models.CharField(max_length=50, blank=True)

    indicator_1_color_change = models.CharField(max_length=20, choices=[
        ('yesilimsi siyah', 'Yeşilimsi Siyah'),
        ('sari', 'Sarı'),
        ('yesil', 'Yeşil'),
        ('kahverengi', 'Kahverengi'),
    ])
    indicator_1_color_change_en = models.CharField(max_length=20, blank=True)

    indicator_2_color_change = models.CharField(max_length=20, choices=[
        ('yesilimsi siyah', 'Yeşilimsi Siyah'),
        ('sari', 'Sarı'),
        ('yesil', 'Yeşil'),
        ('kahverengi', 'Kahverengi'),
    ])
    indicator_2_color_change_en = models.CharField(max_length=20, blank=True)

    report_number = models.CharField(max_length=20, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Otomatik İngilizce eşleştirme
        paper_map = {
            'Medikal Kraft Kağıt': 'Medical Craft Paper',
            'Tyvek': 'Tyvek'
        }
        film_map = {
            'CPP+PET': 'CPP+PET',
            'PET+PE': 'PET+PE'
        }
        suitability_map = {
            'uygun': 'Suitable',
            'uygun_degil': 'Not Suitable'
        }
        indicator_1_map = {
            'buhar': 'Steam',
            'eo' : 'EO',
            'plasma' : 'Plasma',
        }
        indicator_2_map = {
            'buhar': 'Steam',
            'eo' : 'EO',
            'plasma' : 'Plasma',
        }
        indicator_1_color_change_map = {
            'yesilimsi siyah': 'Greenish Black',
            'sari' : 'Yellow',
            'yesil' : 'Green',
            'kahverengi' : 'Brown',
        }
        indicator_2_color_change_map = {
            'yesilimsi siyah': 'Greenish Black',
            'sari' : 'Yellow',
            'yesil' : 'Green',
            'kahverengi' : 'Brown',
        }

        self.paper_en = paper_map.get(self.paper, '')
        self.film_en = film_map.get(self.film, '')
        self.size_check_en = suitability_map.get(self.size_check, '')
        self.leakage_test_en = suitability_map.get(self.leakage_test, '')
        self.peeling_direction_en = suitability_map.get(self.peeling_direction, '')
        self.indicator_1_en = indicator_1_map.get(self.indicator_1, '')
        self.indicator_2_en = indicator_2_map.get(self.indicator_2, '')
        self.indicator_1_color_change_en = indicator_1_color_change_map.get(self.indicator_1_color_change, '')
        self.indicator_2_color_change_en = indicator_2_color_change_map.get(self.indicator_2_color_change, '')

        # Benzersiz rapor numarası otomatik üretilebilir
        if not self.report_number:
            import uuid
            self.report_number = str(uuid.uuid4())[:18].replace('-', '').upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rapor: {self.report_number}"
