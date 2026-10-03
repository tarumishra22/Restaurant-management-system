from django.urls import path
from .views import ReserveTableView ,DailySalesReportView, LowStockAlertView, MenuView, AvailableTablesView, PlaceOrderView


urlpatterns = [
    path('menu/', MenuView.as_view(), name='menu'),
    path('tables/available/', AvailableTablesView.as_view(), name='available-tables'),
    path('orders/place/', PlaceOrderView.as_view(), name='place-order'),
    path('reservations/book/', ReserveTableView.as_view(), name='reserve-table'),
    path('reports/low-stock/', LowStockAlertView.as_view(), name='low-stock'),
    path('reports/daily-sales/', DailySalesReportView.as_view(), name='daily-sales'),
]