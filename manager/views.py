from django.shortcuts import render, redirect, get_object_or_404
from.forms import PrForm,OrderForm
from.models import Scube_ss,orders
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Sum
from django.db.models import Q
from .models import MaterialName, Material
import re
from .models import MaterialName, Material, Scube_ss, SofaProductionRecord, ProductionMaterialItem


# Create your views here.

def admin(request):
    return render(request,'admin')

def create(request):
    frm=PrForm()
    if request.POST:
        frm=PrForm(request.POST,request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('create')

    else:
        frm=PrForm()
    return render(request,'create.html',{'frm':frm})


def all_products(request):
    Pr_data=Scube_ss.objects.filter(status="SCUBE" ).order_by('Catogory')
    return render(request,'all_products.html',{'products':Pr_data})

def home(request):
    return render(request,'index.html')

def master_data_page(request):
    # Form 1: Add Material Name (Category)
    if request.method == 'POST' and 'add_material_name' in request.POST:
        name = request.POST.get('mat_name')
        if name:
            MaterialName.objects.create(name=name)
            return redirect('master_data') # Page refresh aakan

    # Form 2: Add Material Item
    if request.method == 'POST' and 'add_material_item' in request.POST:
        mat_id = request.POST.get('material_cat_id')
        code = request.POST.get('code')
        desc = request.POST.get('description')
        price = request.POST.get('price')
        
        if mat_id and code and price:
            category = MaterialName.objects.get(id=mat_id)
            Material.objects.create(
                material=category,
                code=code,
                description=desc,
                price=price
            )
            return redirect('master_data')

    # Dropdown-il kanikkan vendi data pass cheyyunnu
    material_names = MaterialName.objects.all()
    materials_list = Material.objects.all().select_related('material').order_by('material__name', 'code')

    context = {
        'material_names': material_names,
        'materials_list': materials_list
    }
    return render(request, 'master_data.html', context)

def edit_material(request, item_id):
    if request.method == 'POST':
        cat_id = request.POST.get('material_cat_id')
        code = request.POST.get('code')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if cat_id and code and price:
            # Edit cheyyenda item edukku
            item = Material.objects.get(id=item_id)
            # Puthiya category edukku
            category = MaterialName.objects.get(id=cat_id)
            
            # Ella details-um update cheyyunnu
            item.material = category
            item.code = code
            item.description = description
            item.price = price
            item.save()
            
    return redirect('master_data')



def production_entry(request):
    # SCSF Code Auto-Generate Logic
    sofas = SofaProductionRecord.objects.filter(sofa_code__startswith='SCSF')
    max_num = 0
    for sofa in sofas:
        match = re.search(r'SCSF(\d+)', sofa.sofa_code)
        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num
    next_num = max_num + 1
    new_sofa_code = f"SCSF{next_num:02d}"

    # DATA SAVE CHEYYANULLA LOGIC
    if request.method == 'POST':
        date = request.POST.get('date')
        sofa_code = request.POST.get('sofa_code')
        image = request.FILES.get('image')
        
        # --- PUTHIYA DETAILS ---
        sofa_name = request.POST.get('sofa_name', '')
        sofa_size = request.POST.get('sofa_size', '')
        sofa_color = request.POST.get('sofa_color', '')
        
        # Duplicate code error mattan
        if SofaProductionRecord.objects.filter(sofa_code=sofa_code).exists():
            sofas_check = SofaProductionRecord.objects.filter(sofa_code__startswith='SCSF')
            max_num_save = 0
            for s in sofas_check:
                match = re.search(r'SCSF(\d+)', s.sofa_code)
                if match:
                    num = int(match.group(1))
                    if num > max_num_save:
                        max_num_save = num
            sofa_code = f"SCSF{max_num_save + 1:02d}"

        # Fixed costs
        other_desc = request.POST.get('other_desc', '')
        other_cost = float(request.POST.get('other_cost') or 0)
        wood_cost = float(request.POST.get('wood_cost') or 0)
        wage_cost = float(request.POST.get('wage_cost') or 0)
        profit_amount = float(request.POST.get('profit_amount') or 0)

        grand_total = other_cost + wood_cost + wage_cost + profit_amount

        # Main Record Save cheyyunnu (Puthiya fields add cheythittund)
        production_record = SofaProductionRecord.objects.create(
            date=date,
            sofa_code=sofa_code,
            image=image,
            sofa_name=sofa_name,   # Puthiyath
            sofa_size=sofa_size,   # Puthiyath
            sofa_color=sofa_color, # Puthiyath
            other_desc=other_desc,
            other_cost=other_cost,
            wood_cost=wood_cost,
            wage_cost=wage_cost,
            profit_amount=profit_amount,
            grand_total=0 # temporary
        )

        # -----------------------------------------------------------------
        # MATERIAL SAVING LOGIC
        # -----------------------------------------------------------------
        material_names = request.POST.getlist('mat_name') 
        codes = request.POST.getlist('mat_code')
        qtys = request.POST.getlist('mat_qty')
        prices = request.POST.getlist('mat_price')
        totals = request.POST.getlist('mat_total')

        item_grand_total = 0

        for mat_name, code, qty, price, total in zip(material_names, codes, qtys, prices, totals):
            if code and code.strip(): 
                try:
                    mat_obj = Material.objects.get(id=code)
                    q = float(qty) if qty.strip() else 0.0
                    p = float(price) if price.strip() else 0.0
                    t = float(total) if total.strip() else 0.0
                    
                    ProductionMaterialItem.objects.create(
                        production=production_record,
                        material_name=mat_name,
                        material_code=mat_obj,
                        quantity=q,
                        price=p,
                        total=t
                    )
                    item_grand_total += t
                except Exception as e:
                    print("Error saving item:", e)

        # Final Grand Total Update
        production_record.grand_total = grand_total + item_grand_total
        production_record.save()

        return redirect('production_bill', record_id=production_record.id)

    # GET Request
    materials = Material.objects.all()
    context = {
        'materials': materials,
        'new_sofa_code': new_sofa_code
    }
    return render(request, 'production_entry.html', context)

def edit_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    
    if request.method == 'POST':
        # Main updates
        record.date = request.POST.get('date')
        record.sofa_name = request.POST.get('sofa_name', '')
        record.sofa_size = request.POST.get('sofa_size', '')
        record.sofa_color = request.POST.get('sofa_color', '')
        
        if request.FILES.get('image'):
            record.image = request.FILES.get('image')
            
        record.other_desc = request.POST.get('other_desc', '')
        record.other_cost = float(request.POST.get('other_cost') or 0)
        record.wood_cost = float(request.POST.get('wood_cost') or 0)
        record.wage_cost = float(request.POST.get('wage_cost') or 0)
        record.profit_amount = float(request.POST.get('profit_amount') or 0)

        # Pazhaya items delete cheyth puthiyathu add cheyyunnu
        record.items.all().delete()

        material_names = request.POST.getlist('mat_name')
        codes = request.POST.getlist('mat_code')
        qtys = request.POST.getlist('mat_qty')
        prices = request.POST.getlist('mat_price')
        totals = request.POST.getlist('mat_total')

        item_grand_total = 0
        for mat_name, code, qty, price, total in zip(material_names, codes, qtys, prices, totals):
            if code and code.strip():
                try:
                    mat_obj = Material.objects.get(id=code)
                    t = float(total) if total.strip() else 0.0
                    ProductionMaterialItem.objects.create(
                        production=record,
                        material_name=mat_name,
                        material_code=mat_obj,
                        quantity=float(qty) if qty.strip() else 0.0,
                        price=float(price) if price.strip() else 0.0,
                        total=t
                    )
                    item_grand_total += t
                except Exception as e:
                    print("Edit item error:", e)

        record.grand_total = record.other_cost + record.wood_cost + record.wage_cost + record.profit_amount + item_grand_total
        record.save()
        return redirect('production_bill', record_id=record.id)

    materials = Material.objects.all()
    items = record.items.all()
    return render(request, 'production_edit.html', {'record': record, 'items': items, 'materials': materials})

# ==============================================================
# 2. PRODUCTION SUMMARY PAGE (Bill Page)
# ==============================================================
def production_summary(request):
    # is_approved=False aayittulla (Pending) records mathram edukkunnu
    records = SofaProductionRecord.objects.filter(is_approved=False).order_by('-date', '-id')
    return render(request, 'production_summary.html', {'records': records})

# ==============================================================
# PUTHIYATHU: DELETE ACTION
# ==============================================================
def delete_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete() # Database-il ninnu delete cheyyunnu
    return redirect('production_summary')


# ==============================================================
# 2. PRODUCTION BILL (Single Entry View)
# ==============================================================
def production_bill(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    items = record.items.all()
    return render(request, 'production_bill.html', {'record': record, 'items': items})


# ==============================================================
# 3. APPROVE ACTION
# ==============================================================
def approve_production(request, record_id):
    # Production record edukkunnu
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    
    if not record.is_approved:
        # 1. CLOTH Code kandupidikkunnu
        cloth_item = record.items.filter(material_name__iexact='CLOTH').first()
        cloth_code_val = ""
        if cloth_item and cloth_item.material_code:
            cloth_code_val = cloth_item.material_code.code

        # 2. PRIZE ROUND OFF LOGIC
        original_total = int(record.grand_total)
        base_amount = (original_total // 500) * 500 
        remainder = original_total % 500 

        if remainder < 250:
            final_prize = base_amount 
        else:
            final_prize = base_amount + 500 

        # 3. NULL Check Logic for Name, Size, Color
        # Data empty string ('') aanenkil athine None (NULL) aakki mattunnu
        s_name = record.sofa_name if record.sofa_name and record.sofa_name.strip() else None
        s_size = record.sofa_size if record.sofa_size and record.sofa_size.strip() else None
        s_color = record.sofa_color if record.sofa_color and record.sofa_color.strip() else None

        # 4. Scube_ss model-ilekk save cheyyunnu
        Scube_ss.objects.create(
            code=record.sofa_code,
            Catogory='SOFA',
            name=s_name,    # NULL if empty
            size=s_size,    # NULL if empty
            prize=final_prize, 
            material=cloth_code_val,
            color=s_color,  # NULL if empty
            pr_date=record.date,
            status='SCUBE',
            image=record.image,
            new_pr='NEW'
        )

        record.is_approved = True
        record.save()

    return redirect('production_summary')

def pr_img(request):
    return render(request,'all.html')

def list(request):
    ls_data=Scube_ss.objects.filter(status="SCUBE" ).order_by('code')

    print(ls_data)
    return render(request,'list.html',{'prod':ls_data})

def Pr_Approvel(request):
    ls_data = Scube_ss.objects.filter(Q(prize__isnull=True) | Q(prize="0"), pr_date__gt="2024-08-01").order_by('pr_date')

    print(ls_data)
    return render(request,'Pr_Approvel.html',{'prod':ls_data})

def reports(request):
    return render(request,'reports.html')

def details(request):
    return render(request,'details.html')




def edit(request,pk):
    instance_edit=Scube_ss.objects.get(pk=pk)
    if request.POST:
        frm=PrForm(request.POST,request.FILES,instance=instance_edit)
        if frm.is_valid():
            instance_edit.save()
            return redirect('list')
    else:
       frm=PrForm(instance=instance_edit)
    return render(request,'create.html',{'frm':frm})

def edit2(request,pk):
    instance_edit=Scube_ss.objects.get(pk=pk)
    if request.POST:
        frm=PrForm(request.POST,request.FILES,instance=instance_edit)
        if frm.is_valid():
            instance_edit.save()
            return redirect('Pr_Approvel')
    else:
       frm=PrForm(instance=instance_edit)
    return render(request,'create.html',{'frm':frm})

def del_cnf(request,pk):
    instance_dl=Scube_ss.objects.get(pk=pk)
    if request.method== 'POST' :
        instance_dl.delete()
        return redirect('list')

    return render(request,'del_cnf.html')

def details(request,pk):
    dt_data=Scube_ss.objects.filter(pk=pk)

    print(dt_data)
    return render(request,'details.html',{'details':dt_data})

def viewimage(request,pk):
    dt_data=Scube_ss.objects.filter(pk=pk)

    print(dt_data)
    return render(request,'viewimage.html',{'viewimage':dt_data})

def order_delcnf(request,pk):
    dt_data=orders.objects.get(pk=pk)
    if request.method == 'POST' :
        dt_data.delete()
        return redirect('orders_det')


    return render(request,'order_delcnf.html')

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

def reports(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category = request.POST.get('category')

        filters = {}
        if start_date:
            filters['pr_date__gte'] = parse_date(start_date)
        if end_date:
            filters['pr_date__lte'] = parse_date(end_date)
        if category:
            filters['Catogory'] = category

        production_reports = Scube_ss.objects.filter(**filters).order_by('pr_date')
        
        context = {'PR_reports': production_reports, 'Catogory_choice': Catogory_choice}
    else:
        context = {'Catogory_choice': Catogory_choice}

    return render(request, 'reports.html', context)

status_choice= [ 
    ('SCUBE', 'SCUBE'),
    ('THIRUVALLA', 'THIRUVALLA'),
    ('SALE', 'SALE'),
    ('S-CUBE-DT', 'S-CUBE-DT'),
    ('ORDER','ORDER')
    ]

def reports_s2s(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')

        filters = {}
        if start_date:
            filters['pr_date__gte'] = parse_date(start_date)
        if end_date:
            filters['pr_date__lte'] = parse_date(end_date)
        if status:
            filters['status'] = status

        production_reports = Scube_ss.objects.filter(**filters).order_by('pr_date')
        
        context = {'PR_reports': production_reports, 'status_choice': status_choice}
    else:
        context = {'status_choice': status_choice}

    return render(request, 'reports_S2S.html', context)

def sales_reports(request):
    if request.method=='POST':

        S_date=request.POST.get('start_date')
        E_date=request.POST.get('end_date')
        P_rep=Scube_ss.objects.filter(sl_date__gte=S_date,sl_date__lte=E_date).order_by('sl_date')


        return render ( request,'sales_reports.html',{'PR_reports':P_rep})
    else:

        return render(request,'sales_reports.html',)


def show_cupboard(request):
    ls_data=Scube_ss.objects.filter(Catogory="CUPBOARD").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def show_table(request):
    ls_data=Scube_ss.objects.filter(Catogory="TABLE").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def show_tv_stand(request):
    ls_data=Scube_ss.objects.filter(Catogory="TV-STAND").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def show_sofa(request):
    ls_data=Scube_ss.objects.filter(Catogory="SOFA").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def bedroom_set(request):
    ls_data=Scube_ss.objects.filter(Catogory="BEDROOM-SET").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def pooja_stand(request):
    ls_data=Scube_ss.objects.filter(Catogory="POOJA-STAND").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def others(request):
    ls_data=Scube_ss.objects.filter(Catogory="OTHERS").filter(status="SCUBE").order_by('size')

    print(ls_data)
    return render(request,'all_products.html',{'products':ls_data})

def order(request):
    ls_data=Scube_ss.objects.filter(Catogory="ORDER").filter(status="SCUBE").order_by('size')
    print(ls_data)
    return render(request,'order.html',{'products':ls_data})

def orders_det(request):
    ls_data=orders.objects.all().order_by('id')

    print(ls_data)
    return render(request,'orders.html',{'order':ls_data})

def order_det(request):
    frm=OrderForm()
    if request.POST:
        frm=OrderForm(request.POST,request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('order')

    else:
        frm=OrderForm()
    return redirect('order')




def show_cupboard2(request):
    ls_data = Scube_ss.objects.filter(Catogory="CUPBOARD", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def show_table2(request):
    ls_data=Scube_ss.objects.filter(Catogory="TABLE", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def show_tv_stand2(request):
    ls_data=Scube_ss.objects.filter(Catogory="TV-STAND", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def show_sofa2(request):
    ls_data=Scube_ss.objects.filter(Catogory="SOFA", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def bedroom_set2(request):
    ls_data=Scube_ss.objects.filter(Catogory="BEDROOM-SET", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def pooja_stand2(request):
    ls_data=Scube_ss.objects.filter(Catogory="POOJA-STAND", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def others2(request):
    ls_data=Scube_ss.objects.filter(Catogory="OTHERS", new_pr="NEW").order_by('size')

    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def order2(request):
    ls_data=Scube_ss.objects.filter(Catogory="ORDER", new_pr="NEW").order_by('size')
    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})

def all_img(request):
    ls_data=Scube_ss.objects.all().order_by('Catogory')
    print(ls_data)
    return render(request,'all_products1.html',{'products':ls_data})