from django.db import models


class OLXAd(models.Model):
    id_advertisement = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=250)
    describe = models.TextField()
    images = models.TextField()
    date_published = models.CharField(max_length=50, null=True, blank=True)
    price = models.CharField(max_length=50)
    number_of_views = models.IntegerField(null=True, blank=True)
    tags = models.TextField()
    name_seller = models.CharField(max_length=50)
    rating = models.CharField(max_length=50)
    register_date_seller = models.CharField(max_length=100)
    last_online_seller = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    phone_number = models.TextField(null=True, blank=True, default="-")

    def __str__(self):
        return self.id_advertisement


