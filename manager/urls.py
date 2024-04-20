
from django.urls import path
from . import views


urlpatterns = [

    path('',views.home,name='home'),
    path('create/',views.create,name='create'),
    path('reports/',views.reports,name='reports'),   
    path('list/',views.list,name='list'),
    path('Pr_Approvel',views.Pr_Approvel,name='Pr_Approvel'),
    path('pr_img',views.pr_img,name='pr_img'),
    path('admin/',views.admin,name='admin'),
    path('all_products/',views.all_products,name='all_products'),
    path('edit/<pk>',views.edit,name='edit'),
    path('edit2/<pk>',views.edit2,name='edit2'),
    path('del_cnf/<pk>',views.del_cnf,name='del_cnf'),
    path('viewimage/<pk>',views.viewimage,name='viewimage'),
    path('details/<pk>',views.details,name='details'),
    path('order_delcnf/<pk>',views.order_delcnf,name='order_delcnf'),
    path('reports/',views.reports,name='reports'),
    path('sales_reports/',views.sales_reports,name='sales_reports'),
    path('show_cupboard/',views.show_cupboard,name='show_cupboard'),
    path('show_table/',views.show_table,name='show_table'),
    path('show_tv_stand/',views.show_tv_stand,name='show_tv_stand'),
    path('show_sofa/',views.show_sofa,name='show_sofa'),
    path('bedroom_set/',views.bedroom_set,name='bedroom_set'),
    path('pooja_stand/',views.pooja_stand,name='pooja_stand'),
    path('order/',views.order,name='order'),
    path('orders_det/',views.orders_det,name='orders_det'),
    path('order_det/',views.order_det,name='order_det'),
    path('others/',views.others,name='others'),
  
    path('show_cupboard2/',views.show_cupboard2,name='show_cupboard2'),
    path('show_table2/',views.show_table2,name='show_table2'),
    path('show_tv_stand2/',views.show_tv_stand2,name='show_tv_stand2'),
    path('show_sofa2/',views.show_sofa2,name='show_sofa2'),
    path('bedroom_set2/',views.bedroom_set2,name='bedroom_set2'),
    path('pooja_stand2/',views.pooja_stand2,name='pooja_stand2'),
    path('order2/',views.order2,name='order2'),
    path('others2/',views.others2,name='others2'),
    


]