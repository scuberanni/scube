from django.db import models
from io import BytesIO
from PIL import Image, ImageOps  # ImageOps ഇമ്പോർട്ട് ചെയ്തു (റൊട്ടേഷൻ ശരിയാക്കാൻ)
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import datetime

# ==========================================
# CHOICES TUPLES
# ==========================================
status_choice = [ 
    ('SCUBE', 'SCUBE'),
    ('THIRUVALLA', 'THIRUVALLA'),
    ('GALLERY', 'GALLERY'),
    ('S-CUBE-DT', 'S-CUBE-DT'),
    ('ORDER', 'ORDER'),
    ('WORKSHOP', 'WORKSHOP') 
]

new_choice = [ 
    ('NEW', 'NEW'),
]

Catogory_choice = [ 
    ('CUPBOARD', 'CUPBOARD'),
    ('TABLE', 'TABLE'),
    ('BEDROOM-SET', 'BEDROOM-SET'),
    ('POOJA-STAND', 'POOJA-STAND'),
    ('TV-STAND', 'TV-STAND'),
    ('SOFA', 'SOFA'),
    ('OTHERS', 'OTHERS'),
    ('ORDER', 'ORDER'),
]

# ==========================================
# 1. CORE MODELS
# ==========================================
class Scube_ss(models.Model):
    code = models.CharField(max_length=50, null=True)
    Catogory = models.CharField(choices=Catogory_choice, max_length=50, null=True)
    name = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    prize = models.IntegerField(null=True, blank=True)
    material = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    pr_date = models.DateField(null=True)
    sl_date = models.DateField(null=True, blank=True)
    status = models.CharField(choices=status_choice, max_length=50, null=True)
    image = models.ImageField(upload_to='images/', blank=True)
    new_pr = models.CharField(choices=new_choice, max_length=50, null=True, blank=True)
    
    GALLERY_STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SHOW', 'SHOW'),
        ('UNSHOW', 'UNSHOW'),
    ]
    gallery_status = models.CharField(max_length=20, choices=GALLERY_STATUS_CHOICES, default='PENDING')
    sort_order = models.IntegerField(default=0)

    @property
    def encoded_prize(self):
        if not self.prize:
            return "SC00ST26"
            
        try:
            p = int(self.prize)
        except ValueError:
            return "SC00ST26"

        thousands = p // 1000
        hundreds = p % 1000
        letter_code = ""
        
        if 1 <= hundreds <= 100:
            letter_code = "A"
        elif 101 <= hundreds <= 200:
            letter_code = "B"
        elif 201 <= hundreds <= 300:
            letter_code = "C"
        elif 301 <= hundreds <= 400:
            letter_code = "D"
        elif 401 <= hundreds <= 500:
            letter_code = "E"
        elif 501 <= hundreds <= 600:
            letter_code = "EA"
        elif 601 <= hundreds <= 700:
            letter_code = "EB"
        elif 701 <= hundreds <= 800:
            letter_code = "EC"
        elif 801 <= hundreds <= 999:  
            letter_code = "ED"

        return f"SC{thousands}{letter_code}ST26"

    def __str__(self):
        return str(self.name)

class orders(models.Model):
    name = models.CharField(max_length=50, null=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='images/', blank=True)
    details = models.CharField(max_length=150, null=True, blank=True)    

    def __str__(self):
        return str(self.name)

# ==========================================
# 2. SOFA PRODUCTION & MASTERS
# ==========================================
class MaterialName(models.Model):
    name = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.name

class Material(models.Model):
    material = models.ForeignKey(MaterialName, on_delete=models.CASCADE, verbose_name="Material Name") 
    code = models.CharField(max_length=100, unique=True, verbose_name="Item Code")
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prize")

    def __str__(self):
        return f"{self.material.name} - {self.code}"

class SofaProductionRecord(models.Model):
    date = models.DateField()
    sofa_code = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='production_images/', null=True, blank=True)
    sofa_name = models.CharField(max_length=150, null=True, blank=True)
    sofa_size = models.CharField(max_length=100, null=True, blank=True)
    sofa_color = models.CharField(max_length=100, null=True, blank=True)
    
    other_desc = models.CharField(max_length=200, null=True, blank=True)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wood_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.sofa_code

class ProductionMaterialItem(models.Model):
    production = models.ForeignKey(SofaProductionRecord, on_delete=models.CASCADE, related_name='items')
    material_name = models.CharField(max_length=100) 
    material_code = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True) 
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.material_name} for {self.production.sofa_code}"

# ==========================================
# 3. BOARD (PB) PRODUCTION & MASTERS
# ==========================================
class BoardColor(models.Model):
    color = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.color

class BoardMaterial(models.Model):
    material = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.material

class ProductItem(models.Model):
    pb_category = models.CharField(choices=Catogory_choice, max_length=50, verbose_name="Category")
    pb_name = models.CharField(max_length=150, unique=True, verbose_name="Product Name")
    pb_size = models.CharField(max_length=100, null=True, blank=True, verbose_name="Size")
    pb_material = models.CharField(max_length=100, null=True, blank=True, verbose_name="Material")
    pb_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Wage")
    pb_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prize")
    pb_description = models.TextField(null=True, blank=True, verbose_name="Description")

    def __str__(self):
        return self.pb_name

class BoardProductionRecord(models.Model):
    cl_code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    cl_Catogory = models.CharField(max_length=50, null=True, blank=True)
    cl_name = models.CharField(max_length=150, null=True, blank=True)
    cl_size = models.CharField(max_length=100, null=True, blank=True)
    cl_prize = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cl_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cl_material = models.CharField(max_length=100, null=True, blank=True)
    cl_color = models.CharField(max_length=100, null=True, blank=True)
    cl_pr_date = models.DateField(null=True, blank=True)
    cl_status = models.CharField(max_length=50, default="SCUBE")
    cl_image = models.ImageField(upload_to='board_images/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.cl_code:
            last_record = BoardProductionRecord.objects.order_by('-id').first()
            if last_record and last_record.cl_code and last_record.cl_code.startswith('SCPB_'):
                try:
                    last_num = int(last_record.cl_code.split('_')[1])
                    self.cl_code = f"SCPB_{last_num + 1:02d}"
                except ValueError:
                    self.cl_code = "SCPB_01"
            else:
                self.cl_code = "SCPB_01"

        # 🟢 BoardProductionRecord Image Compression
        if self.cl_image and not getattr(self, '_image_compressed', False):
            img = Image.open(self.cl_image)
            
            # റൊട്ടേഷൻ പ്രശ്നം പരിഹരിക്കാൻ ImageOps ഉപയോഗിക്കുന്നു
            img = ImageOps.exif_transpose(img)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # ക്ലാരിറ്റി നിലനിർത്താൻ റെസല്യൂഷൻ കുറയ്ക്കുന്നു (max 1200px)
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            quality = 85
            
            # Optimize ഓപ്ഷൻ കൂടി നൽകി സേവ് ചെയ്യുന്നു
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # ക്ലാരിറ്റി വളരെ മോശമാകാതിരിക്കാൻ മിനിമം ക്വാളിറ്റി 50 ആയി നിലനിർത്തുന്നു
            while output.tell() > 180 * 1024 and quality > 50:
                output.seek(0)
                output.truncate()
                quality -= 5
                img.save(output, format='JPEG', quality=quality, optimize=True)

            output.seek(0)
            self.cl_image = InMemoryUploadedFile(
                output, 'ImageField', f"{self.cl_image.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )
            self._image_compressed = True

        super(BoardProductionRecord, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.cl_name)

# ==========================================
# 4. PAYMENT ENTRIES
# ==========================================
class PB_Paid_Entry(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('CASH', 'CASH'),
        ('GPAY', 'GPAY'),
    ]

    date = models.DateField(verbose_name="Date")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Description")
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, default='CASH', verbose_name="Payment Mode")

    def __str__(self):
        return f"{self.date} - {self.amount} ({self.payment_mode})"
    
class Sofa_Paid_Entry(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('CASH', 'CASH'),
        ('GPAY', 'GPAY'),
    ]

    date = models.DateField(verbose_name="Date")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Amount")
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name="Description")
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODE_CHOICES, default='CASH', verbose_name="Payment Mode")

    def __str__(self):
        return f"{self.date} - {self.amount} ({self.payment_mode})"
    
# ==========================================
# 5. INVOICE MODELS
# ==========================================
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return self.invoice_number

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    category = models.CharField(max_length=50, null=True, blank=True)
    product = models.ForeignKey(Scube_ss, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

# ==========================================
# 6. STOCK MANAGEMENT MODELS
# ==========================================
class StockMaterialCategory(models.Model):
    MATERIAL_TYPES = [
        ('SOFA', 'SOFA MATERIAL'),
        ('PB', 'PB MATERIAL'),
    ]
    
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPES, verbose_name="Material Type") 
    category_name = models.CharField(max_length=100, verbose_name="Category Name") 

    def __str__(self):
        return f"{self.get_material_type_display()} - {self.category_name}"

class StockItem(models.Model):
    material = models.ForeignKey(StockMaterialCategory, on_delete=models.CASCADE, related_name='stock_items', verbose_name="Select Material")
    
    name = models.CharField(max_length=150, verbose_name="Item Name")
    color = models.CharField(max_length=50, null=True, blank=True, verbose_name="Color")
    size = models.CharField(max_length=50, null=True, blank=True, verbose_name="Size")
    prize = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prize")
    stock = models.IntegerField(default=0, verbose_name="Stock Quantity")
    image = models.ImageField(upload_to='stock_images/', null=True, blank=True, verbose_name="Image")

    def save(self, *args, **kwargs):
        # 🟢 StockItem Image Compression
        if self.image and not getattr(self, '_image_compressed', False):
            img = Image.open(self.image)
            
            # റൊട്ടേഷൻ പ്രശ്നം പരിഹരിക്കാൻ ImageOps ഉപയോഗിക്കുന്നു
            img = ImageOps.exif_transpose(img)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            # ക്ലാരിറ്റി നിലനിർത്താൻ റെസല്യൂഷൻ കുറയ്ക്കുന്നു (max 1200px)
            img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            quality = 85
            
            # Optimize ഓപ്ഷൻ കൂടി നൽകി സേവ് ചെയ്യുന്നു
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            # ക്ലാരിറ്റി വളരെ മോശമാകാതിരിക്കാൻ മിനിമം ക്വാളിറ്റി 50 ആയി നിലനിർത്തുന്നു
            while output.tell() > 180 * 1024 and quality > 50:
                output.seek(0)
                output.truncate()
                quality -= 5
                img.save(output, format='JPEG', quality=quality, optimize=True)

            output.seek(0)
            self.image = InMemoryUploadedFile(
                output, 'ImageField', f"{self.image.name.split('.')[0]}.jpg",
                'image/jpeg', sys.getsizeof(output), None
            )
            self._image_compressed = True

        super(StockItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class StockAdjustment(models.Model):
    TYPE_CHOICES = [('IN', 'STOCK IN'), ('OUT', 'STOCK OUT')]
    
    item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='adjustments')
    date = models.DateField(default=datetime.date.today)
    adjustment_type = models.CharField(max_length=3, choices=TYPE_CHOICES)
    quantity = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        # Stock അപ്ഡേറ്റ് ചെയ്യുന്ന ലോജിക്
        if self.adjustment_type == 'IN':
            self.item.stock += self.quantity
        else:
            self.item.stock -= self.quantity
        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.adjustment_type} ({self.quantity})"
    
# ==========================================
# 7. DEMO PRINTING MODEL (Temporary)
# ==========================================
class DemoPrintJob(models.Model):
    dummy_text = models.TextField()
    is_printed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)