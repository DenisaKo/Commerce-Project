from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create', views.create, name='create'),
    path('categories', views.categories, name='categories'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('<int:listing_id>', views.listing, name='listing'),
    path('<int:listing_id>/watchlist', views.watchlist_add, name='watchlist_add'),
    path('<int:category_id>/category', views.category_listing, name='category_listing'),
    path('<int:listing_id>watchlist_remove', views.watchlist_remove, name='watchlist_remove'),
    path('<int:listing_id>/comment', views.comment, name='comment'),
    path('<int:listing_id>/bid', views.bid_add, name='bid_add'),
    path('my_items', views.my_items, name='my_items'),
    path('<int:listing_id>/close', views.close, name='close'),
]
