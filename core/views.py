from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import MenuItem, RestaurantTable, InventoryItem, Order, OrderItem
from .serializers import MenuItemSerializer, RestaurantTableSerializer, OrderSerializer
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F
from django.utils import timezone
from .models import Reservation
from .serializers import ReservationSerializer


# 1. API to view the Menu
class MenuView(APIView):
    def get(self, request):
        items = MenuItem.objects.filter(is_available=True)
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)


# 2. API to view available tables
class AvailableTablesView(APIView):
    def get(self, request):
        tables = RestaurantTable.objects.filter(is_occupied=False)
        serializer = RestaurantTableSerializer(tables, many=True)
        return Response(serializer.data)


# 3. API to place an order, occupy table, and auto-deduct inventory
class PlaceOrderView(APIView):
    @transaction.atomic
    def post(self, request):
        table_id = request.data.get('table_id')
        items_data = request.data.get('items', [])

        if not table_id or not items_data:
            return Response(
                {"error": "Please provide table_id and items list."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Check if table exists
        try:
            table = RestaurantTable.objects.get(id=table_id)
        except RestaurantTable.DoesNotExist:
            return Response({"error": "Table not found."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Mark table as occupied
        table.is_occupied = True
        table.save()

        # 3. Create the Order
        order = Order.objects.create(table=table)

        # 4. Process items and auto-update inventory
        for entry in items_data:
            menu_item_id = entry.get('menu_item_id')
            qty = entry.get('quantity', 1)

            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
            except MenuItem.DoesNotExist:
                return Response(
                    {"error": f"MenuItem with id {menu_item_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check matching inventory stock
            inventory_item = InventoryItem.objects.filter(name__iexact=menu_item.name).first()
            if inventory_item:
                if inventory_item.stock_quantity < qty:
                    # Rollback transaction automatically if stock is insufficient
                    transaction.set_rollback(True)
                    return Response(
                        {"error": f"Not enough stock for {menu_item.name}. Available: {inventory_item.stock_quantity}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Deduct stock
                inventory_item.stock_quantity -= qty
                inventory_item.save()

            # Record order item
            OrderItem.objects.create(order=order, menu_item=menu_item, quantity=qty)

        return Response(
            {"message": "Order placed successfully!", "order_id": order.id},
            status=status.HTTP_201_CREATED
        )


# 4. API to Reserve a Table
class ReserveTableView(APIView):
    def post(self, request):
        customer_name = request.data.get('customer_name')
        customer_phone = request.data.get('customer_phone')
        guests = request.data.get('number_of_guests')
        res_time_str = request.data.get('reservation_time')

        if not all([customer_name, customer_phone, guests, res_time_str]):
            return Response(
                {"error": "Please provide customer_name, customer_phone, number_of_guests, and reservation_time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        res_time = parse_datetime(res_time_str)
        if not res_time:
            return Response(
                {"error": "Invalid date format. Use ISO format (e.g., 2026-10-04T19:00:00Z)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find tables with sufficient capacity
        eligible_tables = RestaurantTable.objects.filter(capacity__gte=int(guests))

        # Check for time conflicts (+/- 2-hour window)
        time_buffer = timedelta(hours=2)
        assigned_table = None

        for table in eligible_tables:
            conflict = Reservation.objects.filter(
                table=table,
                reservation_time__range=(res_time - time_buffer, res_time + time_buffer)
            ).exists()
            if not conflict:
                assigned_table = table
                break

        if not assigned_table:
            return Response(
                {"error": "No available table found for this guest count and time slot."},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation = Reservation.objects.create(
            table=assigned_table,
            customer_name=customer_name,
            customer_phone=customer_phone,
            reservation_time=res_time,
            number_of_guests=int(guests)
        )

        return Response(
            {
                "message": "Reservation confirmed!",
                "table_number": assigned_table.table_number,
                "reservation_id": reservation.id
            },
            status=status.HTTP_201_CREATED
        )


# 5. Optional Reporting Feature: Stock Alerts
class LowStockAlertView(APIView):
    def get(self, request):
        # Items with stock lower than 5 units
        low_stock = InventoryItem.objects.filter(stock_quantity__lte=5)
        serializer = InventoryItemSerializer(low_stock, many=True)
        return Response({
            "alert": "These items require restocking!",
            "low_stock_items": serializer.data
        })


# 6. Optional Reporting Feature: Daily Sales Summary
class DailySalesReportView(APIView):
    def get(self, request):
        today = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today)
        
        # Calculate total revenue
        total_sales = OrderItem.objects.filter(
            order__in=today_orders
        ).aggregate(
            revenue=Sum(F('quantity') * F('menu_item__price'))
        )['revenue'] or 0.0

        return Response({
            "date": str(today),
            "total_orders": today_orders.count(),
            "total_revenue": float(total_sales)
        })