from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Firma Adı")
    tax_number = models.CharField(max_length=20, unique=True, verbose_name="Vergi No")
    address = models.TextField(blank=True, null=True, verbose_name="Adres")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="E-mail")

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmalar"
        ordering = ['name']

    def __str__(self):
        return self.name