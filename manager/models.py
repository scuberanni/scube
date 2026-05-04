
from django.db import models
from django.shortcuts import render


# Create your models here.

status_choice= [ 
    ('SCUBE', 'SCUBE'),
    ('THIRUVALLA', 'THIRUVALLA'),
    ('SALE', 'SALE'),
    ('S-CUBE-DT', 'S-CUBE-DT'),
    ('ORDER','ORDER')

]
new_choice= [ 
    ('NEW', 'NEW'),
]


Catogory_choice= [ 
    ('CUPBOARD', 'CUPBOARD'),
    ('TABLE', 'TABLE'),
    ('BEDROOM-SET', 'BEDROOM-SET'),
    ('POOJA-STAND','POOJA-STAND'),
    ('TV-STAND','TV-STAND'),
    ('SOFA','SOFA'),
    ('OTHERS','OTHERS'),
    ('ORDER','ORDER'),
    
]



class Scube_ss(models.Model):
    code=models.CharField(max_length=50 ,null=True)
    Catogory= models.CharField(choices=Catogory_choice , max_length=50 ,null=True )
    name=models.CharField(max_length=50 ,null=True)
    size=models.CharField(max_length=50 ,null=True,blank=True)
    prize=models.IntegerField(null=True,blank=True)
    material=models.CharField(max_length=50 ,null=True)
    color=models.CharField(max_length=50 ,null=True,blank=True)
    pr_date=models.DateField(null=True)
    sl_date=models.DateField(null=True, blank=True)
    status= models.CharField(choices=status_choice , max_length=50 ,null=True )
    image=models.ImageField(upload_to='images/',blank=True)
    new_pr= models.CharField(choices=new_choice , max_length=50 ,null=True,blank=True )

    def __str__(self):
        return self.name

class orders(models.Model):
    name=models.CharField(max_length=50 ,null=True,)
    size=models.CharField(max_length=50 ,null=True,blank=True)
    color=models.CharField(max_length=50 ,null=True,blank=True)
    image=models.ImageField(upload_to='images/',blank=True)
    details=models.CharField(max_length=150 ,null=True, blank=True)    

    def __str__(self):
        return self.name
    

class MaterialName(models.Model):
    name = models.CharField(max_length=100, unique=True) 

    def __str__(self):
        return self.name

# 2. Ningal paranja Main Table
class Material(models.Model):
    # 1- MATERIAL (Mugalile MaterialName table-ilekk link cheythirikkunnu)
    material = models.ForeignKey(MaterialName, on_delete=models.CASCADE, verbose_name="Material Name") 
    
    # 2- CODE (Unique - Oru code orikkal mathrame add cheyyan pattu)
    code = models.CharField(max_length=100, unique=True, verbose_name="Item Code")
    
    # 3- DESCRIPTION (Not compulsory - null=True, blank=True koduthal athu nirbandham alla ennartham)
    description = models.TextField(null=True, blank=True)
    
    # 4- PRIZE (Decimal field aanu paisakk ettavum nallathu)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prize")

    def __str__(self):
        return f"{self.material.name} - {self.code}"
    

# models.py-il avasanamayi add cheyyuka

# Sofa Production Main Details (Date, Sofa Code, Grand Total)
class SofaProductionRecord(models.Model):
    date = models.DateField()
    sofa_code = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='production_images/', null=True, blank=True)
    sofa_name = models.CharField(max_length=150, null=True, blank=True)
    sofa_size = models.CharField(max_length=100, null=True, blank=True)
    sofa_color = models.CharField(max_length=100, null=True, blank=True)
    
    # Fixed Costs
    other_desc = models.CharField(max_length=200, null=True, blank=True)
    other_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wood_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    profit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Grand Total & Status
    grand_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # PUTHIYATHAYI ADD CHEYYENDA FIELD
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.sofa_code

# Materials Used for a specific Sofa
class ProductionMaterialItem(models.Model):
    production = models.ForeignKey(SofaProductionRecord, on_delete=models.CASCADE, related_name='items')
    # Row name (Eg: SUPERSOFT, FORM) save cheyyan
    material_name = models.CharField(max_length=100) 
    # Selected code from dropdown (link to Material model)
    material_code = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True) 
    
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.material_name} for {self.production.sofa_code}"
    
