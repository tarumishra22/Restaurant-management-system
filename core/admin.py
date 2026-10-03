from django.contrib import admin
from .models import Reservation, RestaurantTable, MenuItem, InventoryItem, Order, OrderItem 


admin.site.register(RestaurantTable)
admin.site.register(MenuItem)
admin.site.register(InventoryItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reservation)


# Register your models here.
