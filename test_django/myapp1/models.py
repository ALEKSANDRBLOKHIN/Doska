from django.db import models
from django.contrib.auth.models import User


class Categories(models.Model):
    title = models.CharField(max_length=64, blank=False)

    def __str__(self):
        return self.title


class Ads(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cat = models.ForeignKey(Categories, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=64, blank=False)
    text = models.TextField(blank=False)

    def __str__(self):
        return f"{self.title}: _ {self.text}"

class Replies(models.Model):
    ads = models.ForeignKey(Ads, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    text = models.CharField(max_length=256, blank=False)

    def __str__(self):
        return self.text