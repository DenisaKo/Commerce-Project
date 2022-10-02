from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Category, Comment, Bid, AuctionListing, Watchlist


def index(request):
    return render(request, "auctions/index.html", {
        "items": AuctionListing.objects.filter(status='open')
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        starting_bid = request.POST['starting_bid']
        category = Category.objects.get(pk=int(request.POST['category']))
        image = request.POST['image']
        user = request.user
          
        #attempt to creat a new item
        try:
            new_item = AuctionListing(title=title, description=description, starting_bid=starting_bid, image=image, category=category, seller=user, price=starting_bid)
            new_item.save()
        except IntegrityError:
            return render(request, 'auctions/create.html', {
                'categories': Category.objects.all(),
                'message': "Something went wrong."
            })
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, 'auctions/create.html', {
            'categories': Category.objects.all()
        })


def listing(request, listing_id):
    item = AuctionListing.objects.get(pk=listing_id)
    comments = Comment.objects.filter(item__id=listing_id)

    message_sold = 'Item is active'
    # auction is open = no buyer jet
    buyer = None

    #message, if item is sold
    if item.status == 'close':
        message_sold = 'Item is SOLD!'
        # check if there are bids, if so, get him
        bids = Bid.objects.filter(item__id=listing_id)
        if bids != None:
            try:
                buyer = bids.last().buyer
            # close auction without buyer
            except:
                buyer = None
        
       
    return render(request, 'auctions/listing.html', {
        "item": item,
        'comments': comments,
        'message_sold': message_sold,
        'buyer': buyer
    })


@login_required
def watchlist_add(request, listing_id):
    current_item = AuctionListing.objects.get(pk=listing_id)
    user = request.user

    #check if the item already exists in current users W
    if Watchlist.objects.filter(user=user, items=current_item).exists():
        messages.add_message(request, messages.ERROR, "Item already in Watchlist")
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
  
    # Get the user watchlist or create it if it doesn't exists
    user_list, created = Watchlist.objects.get_or_create(user=user)

    # Add the item through the ManyToManyField (Watchlist => item)
    user_list.items.add(current_item)
    messages.add_message(request, messages.SUCCESS, "Item was added to your watchlist")
    return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required
def watchlist(request):
    list_current, created = Watchlist.objects.get_or_create(user=request.user)
    return render(request, 'auctions/watchlist.html', {
        'items': list_current.items.all()
    })


@login_required
def watchlist_remove(request, listing_id):
    if request.method == 'POST':
        item_id = request.POST['item_id']
        item = AuctionListing.objects.get(pk=item_id)
        user_list = Watchlist.objects.get(user=request.user)
        user_list.items.remove(item)
        messages.add_message(request, messages.SUCCESS, "Item was removed from your watchlist")
        return HttpResponseRedirect(reverse('watchlist'))
    else:
        current_item = AuctionListing.objects.get(pk=listing_id)
        user = request.user

        #check if the item already exists in current users W
        if not Watchlist.objects.filter(user=user, items=current_item).exists():
            messages.add_message(request, messages.ERROR, "Item is not in watchlist yet.")
            return HttpResponseRedirect(reverse('listing', args=(listing_id, )))
    
        # Get the user watchlist or create it if it doesn't exists
        user_list, created = Watchlist.objects.get_or_create(user=user)

        # Add the item through the ManyToManyField (Watchlist => item)
        user_list.items.remove(current_item)
        messages.add_message(request, messages.SUCCESS, "Item was removed from your watchlist")
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required
def categories(request):
    return render(request, 'auctions/categories.html', {
        'categories': Category.objects.all()
    })


@login_required
def category_listing(request, category_id):
    listing = AuctionListing.objects.filter(category__pk=category_id)
    return render(request, "auctions/index.html", {
        "items": listing,
        "greeting": Category.objects.get(pk=category_id).category_type
    })


@login_required
def comment(request, listing_id):
    if request.method == 'POST':
        item = AuctionListing.objects.get(pk=listing_id)
        Comment.objects.create(comment=request.POST['comment'], item=item)
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required
def bid_add(request, listing_id):
    if request.method == 'POST':
        item = AuctionListing.objects.get(pk=listing_id)
        # new bidding price
        bid_price = int(request.POST['bid'])
        # actual price
        price_actual = item.price
        starting_bid = item.starting_bid
        if bid_price > price_actual and bid_price >= starting_bid:
            AuctionListing.objects.filter(pk=listing_id).update(price=bid_price)
            Bid.objects.create(bid=bid_price, buyer=request.user, item=item)
            messages.add_message(request, messages.SUCCESS, "Your bid was successfully added.")
        else:
            messages.add_message(request, messages.ERROR, "Your bid needs to be greater than curret price.")
        return HttpResponseRedirect(reverse('listing', args=(listing_id, )))


@login_required
def my_items(request):
    return render(request, "auctions/index2.html", {
        "items": AuctionListing.objects.filter(seller=request.user)
    })
    

@login_required
def close(request, listing_id):
    if request.method == "POST":
        status = request.POST['status']
        AuctionListing.objects.filter(pk=listing_id).update(status=status)

        return HttpResponseRedirect(reverse('my_items'))