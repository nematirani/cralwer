from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=300, null=True)
    price = models.CharField(max_length=300, null=False)
    created = models.DateTimeField(auto_now_add=True)

# Create your models here.
