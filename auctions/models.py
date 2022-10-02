from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    pass


class Category(models.Model):
    category_type = models.CharField(max_length=64)   

    def __str__(self):
        return f'{self.id} {self.category_type}'


class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.PositiveIntegerField()
    image = models.URLField()
    date = models.DateField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=5, default='open')


    def __str__(self):
        return f"{self.title}"

class Bid(models.Model):
    bid = models.PositiveIntegerField()
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.item}: {self.bid}, {self.buyer}"


class Comment(models.Model):
    comment = models.TextField()
    item = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='items')
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.date}: {self.comment}"


class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(AuctionListing, blank=True, related_name='users')

    def __str__(self):
        return f"{self.user}'s Watchlist"