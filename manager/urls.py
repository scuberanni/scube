
from django.urls import path
from . import views


urlpatterns = [

    path('',views.home,name='home'),
    path('others-menu/', views.others_menu, name='others_menu'),
    path('image-categories/', views.image_categories, name='image_categories'),
    path('gallery/<str:category>/', views.image_gallery, name='image_gallery'),
    path('master-data/', views.master_data_page, name='master_data'),
    path('edit-material/<int:item_id>/', views.edit_material, name='edit_material'),
    path('production-entry/', views.production_entry, name='production_entry'),

    path('production-summary/', views.production_summary, name='production_summary'),
    path('production-bill/<int:record_id>/', views.production_bill, name='production_bill'),
    path('approve-production/<int:record_id>/', views.approve_production, name='approve_production'),
    path('delete-production/<int:record_id>/', views.delete_production, name='delete_production'),
    path('edit-production/<int:record_id>/', views.edit_production, name='edit_production'),
    path('sofa-wage-paid-report/', views.sofa_wage_paid_report, name='sofa_wage_report_current'),
    path('sofa-wage-paid-report/<int:year>/<int:month>/', views.sofa_wage_paid_report, name='sofa_wage_report'),
    path('edit-sofa-payment/<int:payment_id>/', views.edit_sofa_payment, name='edit_sofa_payment'),
    path('delete-sofa-payment/<int:payment_id>/', views.delete_sofa_payment, name='delete_sofa_payment'),

    # Product Master URLs
    path('product-master/', views.product_master, name='product_master'),
    path('edit-product/<int:item_id>/', views.edit_product, name='edit_product'),
    path('board-production-entry/', views.board_production_entry, name='board_production_entry'),
    path('ajax/add-product/', views.ajax_add_product, name='ajax_add_product'),
    path('board-production-summary/', views.board_production_summary, name='board_production_summary'),
    path('delete-board-production/<int:record_id>/', views.delete_board_production, name='delete_board_production'),
    path('edit-board-production/<int:record_id>/', views.edit_board_production, name='edit_board_production'),
    path('approve-board-production/<int:record_id>/', views.approve_board_production, name='approve_board_production'),
    path('reports/wage-paid-report/', views.wage_paid_report, name='wage_report_current'), # current month automatically
    path('reports/wage-paid-report/<int:year>/<int:month>/', views.wage_paid_report, name='wage_report'), # specific month navigation poakumbol
    path('edit-payment/<int:payment_id>/', views.edit_payment, name='edit_payment'),
    path('delete-payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('bulk-approve-board-production/', views.bulk_approve_board_production, name='bulk_approve_board_production'),

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
    path('reports_s2s/',views.reports_s2s,name='reports_s2s'),
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
  
    path('pr_img/show_cupboard/',views.show_cupboard2,name='show_cupboard2'),
    path('pr_img/show_table/',views.show_table2,name='show_table2'),
    path('pr_img/show_tv_stand/',views.show_tv_stand2,name='show_tv_stand2'),
    path('pr_img/show_sofa/',views.show_sofa2,name='show_sofa2'),
    path('pr_img/bedroom_set/',views.bedroom_set2,name='bedroom_set2'),
    path('pr_img/pooja_stand/',views.pooja_stand2,name='pooja_stand2'),
    path('pr_img/order/',views.order2,name='order2'),
    path('pr_img/others/',views.others2,name='others2'),
    path('all_img/',views.all_img,name='all_img'),
    


]