from django.contrib import admin
from .models import (
    # Core
    Scube_ss, 
    orders,
    # Material Masters
    MaterialName, 
    Material, 
    BoardColor, 
    BoardMaterial, 
    ProductItem, 
    # Production
    SofaProductionRecord, 
    ProductionMaterialItem, 
    BoardProductionRecord,
    # Payments
    PB_Paid_Entry,
    Sofa_Paid_Entry,
    # Stock Management
    StockMaterialCategory,
    StockItem,
    # Invoicing
    Invoice,
    InvoiceItem
)

# ==========================================
# 1. CORE & ORDERS
# ==========================================
admin.site.register(Scube_ss)
admin.site.register(orders)

# ==========================================
# 2. MASTER DATA (MATERIALS & PRODUCTS)
# ==========================================
admin.site.register(MaterialName)
admin.site.register(Material)
admin.site.register(BoardColor)
admin.site.register(BoardMaterial)
admin.site.register(ProductItem)

# ==========================================
# 3. PRODUCTION RECORDS
# ==========================================
admin.site.register(SofaProductionRecord)
admin.site.register(ProductionMaterialItem)
admin.site.register(BoardProductionRecord)

# ==========================================
# 4. PAYMENT ENTRIES
# ==========================================
admin.site.register(PB_Paid_Entry)
admin.site.register(Sofa_Paid_Entry)

# ==========================================
# 5. STOCK MANAGEMENT
# ==========================================
admin.site.register(StockMaterialCategory)
admin.site.register(StockItem)

# ==========================================
# 6. INVOICING
# ==========================================
admin.site.register(Invoice)
admin.site.register(InvoiceItem)