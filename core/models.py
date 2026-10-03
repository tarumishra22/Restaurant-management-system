from django.db import models

class RestaurantTable(models.Model):
    table_number = models.IntegerField(unique =True)
    capacity = models.IntegerField(help_text="number of seats ")
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.table_number} {self.capacity} seats"


class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - Rs.{self.price}"


class InventoryItem(models.Model):
    name = models.CharField(max_length=100)
    stock_quantity= models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.stock_quantity} in stock"


class Order(models.Model):
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid =models.BooleanField(default=False)

    def __str__(self):
        return f"order {self.id} for Table {self.table.table_number}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"



class Reservation(models.Model):
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    reservation_time = models.DateTimeField()
    number_of_guests = models.PositiveIntegerField()

    def __str__(self):
        return f"Reservation for {self.customer_name} at Table {self.table.table_number}"