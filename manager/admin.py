from django.contrib import admin
from .models import (
    Scube_ss, 
    orders, 
    MaterialName, 
    Material, 
    SofaProductionRecord, 
    ProductionMaterialItem, 
    BoardColor, 
    BoardMaterial, 
    ProductItem, 
    BoardProductionRecord,
    PB_Paid_Entry
)

# Register your models here.
admin.site.register(Scube_ss)
admin.site.register(orders)
admin.site.register(MaterialName)
admin.site.register(Material)
admin.site.register(SofaProductionRecord)
admin.site.register(ProductionMaterialItem)
admin.site.register(BoardColor)
admin.site.register(BoardMaterial)
admin.site.register(ProductItem)
admin.site.register(BoardProductionRecord)
admin.site.register(PB_Paid_Entry)