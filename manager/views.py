import re
import datetime
import json
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User

from .forms import PrForm, OrderForm, PBPaidForm, SofaPaidForm
from .models import (
    Scube_ss, orders, MaterialName, Material, 
    SofaProductionRecord, ProductionMaterialItem, 
    BoardColor, BoardMaterial, ProductItem, 
    BoardProductionRecord, PB_Paid_Entry, Sofa_Paid_Entry,
    Invoice, InvoiceItem, StockMaterialCategory, StockItem,
    Catogory_choice, status_choice
)

# ==============================================================================
# 0. USER ACCESS CONTROL FUNCTIONS
# ==============================================================================

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def is_sofa_worker_or_admin(user):
    return user.is_authenticated and (user.is_superuser or user.username == 'sofa_worker')

def is_pb_worker_or_admin(user):
    return user.is_authenticated and (user.is_superuser or user.username == 'pb_worker')

# ==============================================================================
# 1. PUBLIC VIEWS
# ==============================================================================

def home(request):
    return render(request, 'index.html')

def image_categories(request):
    return render(request, 'image_categories.html')

def image_gallery(request, category):
    base_query = Scube_ss.objects.exclude(image='').exclude(image__isnull=True)
    if category == 'ALL':
        context = {
            'grouped_images': {
                cat: {
                    'unshow': base_query.filter(Catogory=cat, gallery_status='UNSHOW').order_by('sort_order', '-pr_date')
                } for cat in [c[0] for c in Catogory_choice]
            },
            'is_all': True,
            'page_title': "ALL PRODUCTS GALLERY"
        }
    else:
        cat_images = base_query.filter(Catogory=category)
        context = {
            'pending_images': cat_images.filter(gallery_status='PENDING').order_by('sort_order', '-pr_date'),
            'show_images': cat_images.filter(gallery_status='SHOW').order_by('sort_order', '-pr_date'),
            'unshow_images': cat_images.filter(gallery_status='UNSHOW').order_by('sort_order', '-pr_date'),
            'page_title': category.replace('-', ' '),
            'current_category': category,
            'is_all': False
        }
    return render(request, 'image_gallery.html', context)

# 🟢 1. Bulk Update Status (Show/Hide)
@user_passes_test(is_admin)
def bulk_update_gallery_status(request):
    if request.method == 'POST':
        action = request.POST.get('action') 
        item_ids = request.POST.getlist('item_ids') 
        if item_ids and action in ['SHOW', 'UNSHOW']:
            Scube_ss.objects.filter(id__in=item_ids).update(gallery_status=action)
    return redirect(request.META.get('HTTP_REFERER', 'image_categories'))

# 🟢 2. Bulk Delete Images Only (NEW FUNCTION)
@user_passes_test(is_admin)
def bulk_delete_gallery_items(request):
    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        if item_ids:
            items = Scube_ss.objects.filter(id__in=item_ids)
            for item in items:
                if item.image:
                    image_name = item.image.name
                    shared_count = Scube_ss.objects.filter(image=image_name).count()
                    
                    if shared_count > 1:
                        # 🌟 ഇമേജ് ഒന്നിലധികം കാർഡുകളിൽ ഉണ്ടെങ്കിൽ: കാർഡിൽ നിന്ന് മാത്രം ഒഴിവാക്കുന്നു
                        item.image = None
                        item.save()
                    else:
                        # 🌟 ഇമേജ് ഈ കാർഡിൽ മാത്രമേ ഉള്ളൂ എങ്കിൽ: സ്റ്റോറേജിൽ നിന്ന് പൂർണ്ണമായി ഡിലീറ്റ് ചെയ്യുന്നു
                        item.image.delete(save=False)
                        item.image = None
                        item.save()
    return redirect(request.META.get('HTTP_REFERER', 'image_categories'))

# 🟢 3. Single Image Delete
@user_passes_test(is_admin)
def delete_gallery_item(request, item_id):
    item = get_object_or_404(Scube_ss, id=item_id)
    if item.image:
        image_name = item.image.name
        shared_count = Scube_ss.objects.filter(image=image_name).count()
        if shared_count > 1:
            item.image = None
            item.save()
        else:
            item.image.delete(save=False)
            item.image = None
            item.save() 
    return redirect(request.META.get('HTTP_REFERER', 'image_categories'))

# Category display functions
def show_cupboard2(request):
    ls_data = Scube_ss.objects.filter(Catogory="CUPBOARD", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def show_table2(request):
    ls_data = Scube_ss.objects.filter(Catogory="TABLE", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def show_tv_stand2(request):
    ls_data = Scube_ss.objects.filter(Catogory="TV-STAND", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def show_sofa2(request):
    ls_data = Scube_ss.objects.filter(Catogory="SOFA", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def bedroom_set2(request):
    ls_data = Scube_ss.objects.filter(Catogory="BEDROOM-SET", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def pooja_stand2(request):
    ls_data = Scube_ss.objects.filter(Catogory="POOJA-STAND", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def others2(request):
    ls_data = Scube_ss.objects.filter(Catogory="OTHERS", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def order2(request):
    ls_data = Scube_ss.objects.filter(Catogory="ORDER", new_pr="NEW").order_by('size')
    return render(request, 'all_products1.html', {'products': ls_data})

def all_img(request):
    ls_data = Scube_ss.objects.all().order_by('Catogory')
    return render(request, 'all_products1.html', {'products': ls_data})

# ==============================================================================
# 2. SOFA WORKER VIEWS (Sofa Worker & Admin)
# ==============================================================================

@user_passes_test(is_sofa_worker_or_admin)
def master_data_page(request):
    if request.method == 'POST':
        if 'add_material_name' in request.POST:
            name = request.POST.get('mat_name')
            if name:
                MaterialName.objects.create(name=name)
                return redirect('master_data')

        elif 'add_material_item' in request.POST:
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

    material_names = MaterialName.objects.all()
    materials_list = Material.objects.all().select_related('material').order_by('material__name', 'code')
    context = {'material_names': material_names, 'materials_list': materials_list}
    return render(request, 'master_data.html', context)

@user_passes_test(is_sofa_worker_or_admin)
def edit_material(request, item_id):
    if request.method == 'POST':
        cat_id = request.POST.get('material_cat_id')
        code = request.POST.get('code')
        description = request.POST.get('description')
        price = request.POST.get('price')

        if cat_id and code and price:
            item = Material.objects.get(id=item_id)
            category = MaterialName.objects.get(id=cat_id)
            item.material = category
            item.code = code
            item.description = description
            item.price = price
            item.save()
    return redirect('master_data')

@user_passes_test(is_sofa_worker_or_admin)
def production_entry(request):
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

    if request.method == 'POST':
        date = request.POST.get('date')
        sofa_code = request.POST.get('sofa_code')
        image = request.FILES.get('image')
        sofa_name = request.POST.get('sofa_name', '')
        sofa_size = request.POST.get('sofa_size', '')
        sofa_color = request.POST.get('sofa_color', '')
        
        if SofaProductionRecord.objects.filter(sofa_code=sofa_code).exists():
            sofas_check = SofaProductionRecord.objects.filter(sofa_code__startswith='SCSF')
            max_num_save = max([int(re.search(r'SCSF(\d+)', s.sofa_code).group(1)) for s in sofas_check if re.search(r'SCSF(\d+)', s.sofa_code)] + [0])
            sofa_code = f"SCSF{max_num_save + 1:02d}"

        other_desc = request.POST.get('other_desc', '')
        other_cost = float(request.POST.get('other_cost') or 0)
        wood_cost = float(request.POST.get('wood_cost') or 0)
        wage_cost = float(request.POST.get('wage_cost') or 0)
        profit_amount = float(request.POST.get('profit_amount') or 0)

        grand_total = other_cost + wood_cost + wage_cost + profit_amount

        production_record = SofaProductionRecord.objects.create(
            date=date, sofa_code=sofa_code, image=image, sofa_name=sofa_name,
            sofa_size=sofa_size, sofa_color=sofa_color, other_desc=other_desc,
            other_cost=other_cost, wood_cost=wood_cost, wage_cost=wage_cost,
            profit_amount=profit_amount, grand_total=0
        )

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
                        production=production_record, material_name=mat_name,
                        material_code=mat_obj, quantity=q, price=p, total=t
                    )
                    item_grand_total += t
                except Exception as e:
                    print("Error saving item:", e)

        production_record.grand_total = grand_total + item_grand_total
        production_record.save()
        return redirect('production_bill', record_id=production_record.id)

    materials = Material.objects.all()
    context = {'materials': materials, 'new_sofa_code': new_sofa_code}
    return render(request, 'production_entry.html', context)

@user_passes_test(is_sofa_worker_or_admin)
def edit_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    if request.method == 'POST':
        record.date = request.POST.get('date')
        record.sofa_name = request.POST.get('sofa_name', '')
        record.sofa_size = request.POST.get('sofa_size', '')
        record.sofa_color = request.POST.get('sofa_color', '')
        
        if request.FILES.get('image'):
            record.image = request.FILES.get('image')
            
        record.other_desc = request.POST.get('other_desc', '')
        record.other_cost = float(request.POST.get('other_cost') or 0)
        record.wood_cost = float(request.POST.get('wood_cost') or 0)
        
        if request.user.is_superuser:
            record.wage_cost = float(request.POST.get('wage_cost') or 0)
            
        record.profit_amount = float(request.POST.get('profit_amount') or 0)
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
                        production=record, material_name=mat_name, material_code=mat_obj,
                        quantity=float(qty) if qty.strip() else 0.0,
                        price=float(price) if price.strip() else 0.0, total=t
                    )
                    item_grand_total += t
                except Exception as e:
                    pass

        record.grand_total = (
            Decimal(str(record.other_cost)) + 
            Decimal(str(record.wood_cost)) + 
            Decimal(str(record.wage_cost)) + 
            Decimal(str(record.profit_amount)) + 
            Decimal(str(item_grand_total))
        )
        record.save()
        return redirect('production_bill', record_id=record.id)

    materials = Material.objects.all()
    items = record.items.all()
    return render(request, 'production_edit.html', {'record': record, 'items': items, 'materials': materials})

@user_passes_test(is_sofa_worker_or_admin)
def production_summary(request):
    records = SofaProductionRecord.objects.filter(is_approved=False).order_by('-date', '-id')
    return render(request, 'production_summary.html', {'records': records})

@user_passes_test(is_sofa_worker_or_admin)
def production_bill(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    items = record.items.all()
    return render(request, 'production_bill.html', {'record': record, 'items': items})

@user_passes_test(is_sofa_worker_or_admin)
def delete_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
    return redirect('production_summary')

@user_passes_test(is_sofa_worker_or_admin)
def sofa_wage_paid_report(request, year=None, month=None):
    today = datetime.date.today()
    if year is None: year = today.year
    if month is None: month = today.month

    start_of_month = datetime.date(year, month, 1)
    next_m_y = year + (month // 12)
    next_m_m = (month % 12) + 1
    end_of_month = datetime.date(next_m_y, next_m_m, 1) - datetime.timedelta(days=1)
    prev_m_y = year + ((month - 2) // 12)
    prev_m_m = ((month - 2) % 12) + 1
    
    payment_form = SofaPaidForm()
    
    if request.method == 'POST':
        if 'add_payment' in request.POST:
            form = SofaPaidForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Payment added successfully.')
                return redirect('sofa_wage_report', year=year, month=month)
            else:
                payment_form = form

    prev_total_wage = SofaProductionRecord.objects.filter(date__lt=start_of_month).aggregate(total=Sum('wage_cost'))['total'] or 0
    prev_total_paid = Sofa_Paid_Entry.objects.filter(date__lt=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_month_balance = prev_total_wage - prev_total_paid

    current_month_wages_list = SofaProductionRecord.objects.filter(date__gte=start_of_month, date__lte=end_of_month).order_by('date', 'id')
    current_month_total_wage = current_month_wages_list.aggregate(total=Sum('wage_cost'))['total'] or 0

    current_month_payments_list = Sofa_Paid_Entry.objects.filter(date__gte=start_of_month, date__lte=end_of_month).order_by('date', 'id')
    current_month_total_paid = current_month_payments_list.aggregate(total=Sum('amount'))['total'] or 0

    excel_total_due = previous_month_balance + current_month_total_wage
    excel_current_balance = excel_total_due - current_month_total_paid

    context = {
        'year': year, 'month_obj': start_of_month, 'prev_month': prev_m_m, 'prev_year': prev_m_y,
        'next_month': next_m_m, 'next_year': next_m_y, 'wages': current_month_wages_list,
        'payments': current_month_payments_list, 'total_w_monthly': current_month_total_wage,
        'prev_balance': previous_month_balance, 'excel_total_due': excel_total_due,
        'current_paid_monthly': current_month_total_paid, 'current_balance': excel_current_balance,
        'payment_form': payment_form,
    }
    return render(request, 'sofa_monthly_wage_paid.html', context)

# ==============================================================================
# 3. PB WORKER VIEWS (PB Worker & Admin)
# ==============================================================================

@user_passes_test(is_pb_worker_or_admin)
def product_master(request):
    if request.method == 'POST':
        if 'add_color' in request.POST:
            color_name = request.POST.get('color')
            if color_name:
                BoardColor.objects.get_or_create(color=color_name)
                
        elif 'add_material' in request.POST:
            material_name = request.POST.get('material')
            if material_name:
                BoardMaterial.objects.get_or_create(material=material_name)
                
        elif 'add_product' in request.POST:
            ProductItem.objects.create(
                pb_category=request.POST.get('pb_category'),
                pb_name=request.POST.get('pb_name'),
                pb_size=request.POST.get('pb_size'),
                pb_material=request.POST.get('pb_material'),
                pb_wage=float(request.POST.get('pb_wage') or 0),
                pb_prize=float(request.POST.get('pb_prize') or 0),
                pb_description=request.POST.get('pb_description', '')
            )
        return redirect('product_master')

    colors = BoardColor.objects.all()
    materials = BoardMaterial.objects.all()
    products = ProductItem.objects.all().order_by('-id')
    
    context = {'colors': colors, 'materials': materials, 'products': products, 'categories': Catogory_choice}
    return render(request, 'product_master.html', context)

@user_passes_test(is_pb_worker_or_admin)
def edit_product(request, item_id):
    product = get_object_or_404(ProductItem, id=item_id)
    if request.method == 'POST':
        product.pb_category = request.POST.get('pb_category')
        product.pb_name = request.POST.get('pb_name')
        product.pb_size = request.POST.get('pb_size')
        product.pb_material = request.POST.get('pb_material')
        product.pb_wage = float(request.POST.get('pb_wage') or 0)
        product.pb_prize = float(request.POST.get('pb_prize') or 0)
        product.pb_description = request.POST.get('pb_description', '')
        product.save()
    return redirect('product_master')

@user_passes_test(is_pb_worker_or_admin)
def board_production_entry(request):
    if request.method == 'POST':
        try:
            entry_date = request.POST.get('entry_date')
            product_ids = request.POST.getlist('product_ids[]')
            color_ids = request.POST.getlist('color_ids[]')
            custom_names = request.POST.getlist('custom_names[]')
            custom_sizes = request.POST.getlist('custom_sizes[]')
            custom_materials = request.POST.getlist('custom_materials[]')
            custom_wages = request.POST.getlist('custom_wages[]')
            custom_prizes = request.POST.getlist('custom_prizes[]')
            quantities = request.POST.getlist('quantities[]') 
            images = request.FILES.getlist('product_images[]')

            image_index = 0 
            for i in range(len(custom_names)):
                c_name = custom_names[i].strip()
                p_id = product_ids[i] if i < len(product_ids) else ""
                
                if not p_id and not c_name: 
                    continue 
                
                c_id = color_ids[i] if i < len(color_ids) else ""
                color_name = ""
                if c_id:
                    try:
                        color_obj = BoardColor.objects.get(id=c_id)
                        color_name = color_obj.color
                    except BoardColor.DoesNotExist:
                        pass
                
                try:
                    qty = int(quantities[i])
                    if qty < 1: qty = 1
                except (IndexError, ValueError):
                    qty = 1

                img = None
                if len(images) > image_index:
                    img = images[image_index]
                    image_index += 1

                if c_name: 
                    cat = "ORDER"
                    name = c_name
                    size = custom_sizes[i] if i < len(custom_sizes) else ""
                    material = custom_materials[i] if i < len(custom_materials) else ""
                    
                    try:
                        wage = float(custom_wages[i]) if i < len(custom_wages) and custom_wages[i].strip() else 0.0
                    except ValueError:
                        wage = 0.0
                        
                    try:
                        prize = float(custom_prizes[i]) if i < len(custom_prizes) and custom_prizes[i].strip() else 0.0
                    except ValueError:
                        prize = 0.0
                    status = "SCUBE"
                else:
                    try:
                        product_obj = ProductItem.objects.get(id=p_id)
                        cat = product_obj.pb_category
                        name = product_obj.pb_name
                        size = product_obj.pb_size
                        material = product_obj.pb_material
                        wage = product_obj.pb_wage
                        prize = product_obj.pb_prize
                        status = "SCUBE"
                    except ProductItem.DoesNotExist:
                        continue
                
                for j in range(qty):
                    if img:
                        img.seek(0)
                        
                    BoardProductionRecord.objects.create(
                        cl_Catogory=cat, cl_name=name, cl_size=size, cl_prize=prize,
                        cl_wage=wage, cl_material=material, cl_color=color_name,
                        cl_pr_date=entry_date, cl_status=status, cl_image=img
                    )
        except Exception as e:
            print(f"Error saving data: {e}") 
            
        return redirect('board_production_entry')

    colors = BoardColor.objects.all()
    categories = Catogory_choice
    all_products = ProductItem.objects.all()
    materials = BoardMaterial.objects.all() 
    
    context = {'colors': colors, 'categories': categories, 'all_products': all_products, 'materials': materials}
    return render(request, 'board_production_entry.html', context)

@user_passes_test(is_pb_worker_or_admin)
def ajax_add_product(request):
    if request.method == 'POST':
        try:
            product = ProductItem.objects.create(
                pb_category=request.POST.get('pb_category'),
                pb_name=request.POST.get('pb_name'),
                pb_size=request.POST.get('pb_size'),
                pb_material=request.POST.get('pb_material'),
                pb_wage=float(request.POST.get('pb_wage') or 0),
                pb_prize=float(request.POST.get('pb_prize') or 0),
                pb_description=request.POST.get('pb_description', '')
            )
            return JsonResponse({'status': 'success', 'id': product.id, 'name': product.pb_name, 'category': product.pb_category})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid_method'})

@user_passes_test(is_pb_worker_or_admin)
def board_production_summary(request):
    records = BoardProductionRecord.objects.filter(is_approved=False).order_by('-id')
    colors = BoardColor.objects.all()
    categories = Catogory_choice
    materials = BoardMaterial.objects.all()
    context = {'records': records, 'colors': colors, 'categories': categories, 'materials': materials}
    return render(request, 'board_production_summary.html', context)

@user_passes_test(is_pb_worker_or_admin)
def edit_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    if request.method == 'POST':
        record.cl_code = request.POST.get('cl_code')
        record.cl_status = request.POST.get('cl_status')
        record.cl_pr_date = request.POST.get('cl_pr_date')
        record.cl_Catogory = request.POST.get('cl_Catogory')
        record.cl_name = request.POST.get('cl_name')
        record.cl_size = request.POST.get('cl_size')
        record.cl_material = request.POST.get('cl_material')
        record.cl_color = request.POST.get('cl_color')
        
        if request.user.is_superuser:
            record.cl_wage = float(request.POST.get('cl_wage') or 0)
            
        record.cl_prize = float(request.POST.get('cl_prize') or 0)
        if request.FILES.get('cl_image'):
            record.cl_image = request.FILES.get('cl_image')
            record._image_compressed = False 
        record.save()
    return redirect(request.META.get('HTTP_REFERER', 'board_production_summary'))

@user_passes_test(is_pb_worker_or_admin)
def delete_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
    return redirect(request.META.get('HTTP_REFERER', 'board_production_summary'))

@user_passes_test(is_pb_worker_or_admin)
def wage_paid_report(request, year=None, month=None):
    today = datetime.date.today()
    if year is None: year = today.year
    if month is None: month = today.month

    start_of_month = datetime.date(year, month, 1)
    next_m_y = year + (month // 12)
    next_m_m = (month % 12) + 1
    end_of_month = datetime.date(next_m_y, next_m_m, 1) - datetime.timedelta(days=1)
    prev_m_y = year + ((month - 2) // 12)
    prev_m_m = ((month - 2) % 12) + 1
    
    payment_form = PBPaidForm()
    
    if request.method == 'POST':
        if 'add_payment' in request.POST:
            form = PBPaidForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Payment added successfully.')
                return redirect('wage_report', year=year, month=month)
            else:
                payment_form = form

        elif 'add_product_item' in request.POST:
            create(request) 
            messages.success(request, 'Production Record added successfully.')
            return redirect('wage_report', year=year, month=month)

    prev_total_wage = BoardProductionRecord.objects.filter(cl_pr_date__lt=start_of_month).aggregate(total=Sum('cl_wage'))['total'] or 0
    prev_total_paid = PB_Paid_Entry.objects.filter(date__lt=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_month_balance = prev_total_wage - prev_total_paid

    current_month_wages_list = BoardProductionRecord.objects.filter(cl_pr_date__gte=start_of_month, cl_pr_date__lte=end_of_month).order_by('cl_pr_date', 'id')
    current_month_total_wage = current_month_wages_list.aggregate(total=Sum('cl_wage'))['total'] or 0

    current_month_payments_list = PB_Paid_Entry.objects.filter(date__gte=start_of_month, date__lte=end_of_month).order_by('date', 'id')
    current_month_total_paid = current_month_payments_list.aggregate(total=Sum('amount'))['total'] or 0

    excel_total_due = previous_month_balance + current_month_total_wage
    excel_current_balance = excel_total_due - current_month_total_paid

    context = {
        'year': year, 'month_obj': start_of_month, 'prev_month': prev_m_m, 'prev_year': prev_m_y,
        'next_month': next_m_m, 'next_year': next_m_y, 'wages': current_month_wages_list,
        'payments': current_month_payments_list, 'total_w_monthly': current_month_total_wage,
        'prev_balance': previous_month_balance, 'excel_total_due': excel_total_due,
        'current_paid_monthly': current_month_total_paid, 'current_balance': excel_current_balance,
        'payment_form': payment_form,
    }
    return render(request, 'monthly_wage_paid.html', context)

# ==============================================================================
# 4. SUPERUSER / ADMIN VIEWS (Admin Only)
# ==============================================================================

@user_passes_test(is_admin)
def edit_payment(request, payment_id):
    payment = get_object_or_404(PB_Paid_Entry, id=payment_id)
    if request.method == 'POST':
        payment.date = request.POST.get('date')
        payment.amount = request.POST.get('amount')
        payment.description = request.POST.get('description')
        payment.payment_mode = request.POST.get('payment_mode')
        payment.save()
        payment.refresh_from_db()
        messages.success(request, 'Payment updated successfully.')
    if payment.date:
        return redirect('wage_report', year=payment.date.year, month=payment.date.month) 
    return redirect('wage_report_current')

@user_passes_test(is_admin)
def delete_payment(request, payment_id):
    payment = get_object_or_404(PB_Paid_Entry, id=payment_id)
    year, month = payment.date.year, payment.date.month
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
    return redirect('wage_report', year=year, month=month)

@user_passes_test(is_admin)
def edit_sofa_payment(request, payment_id):
    payment = get_object_or_404(Sofa_Paid_Entry, id=payment_id)
    if request.method == 'POST':
        payment.date = request.POST.get('date')
        payment.amount = request.POST.get('amount')
        payment.description = request.POST.get('description')
        payment.payment_mode = request.POST.get('payment_mode')
        payment.save()
        payment.refresh_from_db()
    if payment.date:
        return redirect('sofa_wage_report', year=payment.date.year, month=payment.date.month) 
    return redirect('sofa_wage_report_current')

@user_passes_test(is_admin)
def delete_sofa_payment(request, payment_id):
    payment = get_object_or_404(Sofa_Paid_Entry, id=payment_id)
    year, month = payment.date.year, payment.date.month
    if request.method == 'POST':
        payment.delete()
    return redirect('sofa_wage_report', year=year, month=month)

# ==============================================================================
# 5. GENERAL ADMIN FUNCTIONS
# ==============================================================================

@user_passes_test(is_admin)
def admin(request):
    return render(request, 'admin')

@user_passes_test(is_admin)
def others_menu(request):
    return render(request, 'others.html')

@user_passes_test(is_admin)
def pr_img(request):
    return render(request, 'all.html')

@user_passes_test(is_admin)
def all_products(request):
    Pr_data = Scube_ss.objects.filter(status="SCUBE").order_by('Catogory')
    return render(request, 'all_products.html', {'products': Pr_data})

@user_passes_test(is_admin)
def details(request, pk):
    dt_data = Scube_ss.objects.filter(pk=pk)
    return render(request, 'details.html', {'details': dt_data})

@user_passes_test(is_admin)
def viewimage(request, pk):
    dt_data = Scube_ss.objects.filter(pk=pk)
    return render(request, 'viewimage.html', {'viewimage': dt_data})

@user_passes_test(is_admin)
def order(request):
    ls_data = Scube_ss.objects.filter(Catogory="ORDER", status="SCUBE").order_by('size')
    return render(request, 'order.html', {'products': ls_data})

@user_passes_test(is_admin)
def show_cupboard(request):
    ls_data = Scube_ss.objects.filter(Catogory="CUPBOARD", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def show_table(request):
    ls_data = Scube_ss.objects.filter(Catogory="TABLE", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def show_tv_stand(request):
    ls_data = Scube_ss.objects.filter(Catogory="TV-STAND", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def show_sofa(request):
    ls_data = Scube_ss.objects.filter(Catogory="SOFA", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def bedroom_set(request):
    ls_data = Scube_ss.objects.filter(Catogory="BEDROOM-SET", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def pooja_stand(request):
    ls_data = Scube_ss.objects.filter(Catogory="POOJA-STAND", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def others(request):
    ls_data = Scube_ss.objects.filter(Catogory="OTHERS", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

@user_passes_test(is_admin)
def create(request):
    if request.method == 'POST':
        frm = PrForm(request.POST, request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('create')
    else:
        frm = PrForm()
    return render(request, 'create.html', {'frm': frm})

@user_passes_test(is_admin)
def list(request):
    ls_data = Scube_ss.objects.filter(status="SCUBE").order_by('code')
    return render(request, 'list.html', {'prod': ls_data})

@user_passes_test(is_admin)
def Pr_Approvel(request):
    ls_data = Scube_ss.objects.filter(Q(prize__isnull=True) | Q(prize="0"), pr_date__gt="2024-08-01").order_by('pr_date')
    return render(request, 'Pr_Approvel.html', {'prod': ls_data})

@user_passes_test(is_admin)
def edit(request, pk):
    instance_edit = Scube_ss.objects.get(pk=pk)
    if request.method == 'POST':
        frm = PrForm(request.POST, request.FILES, instance=instance_edit)
        if frm.is_valid():
            instance_edit.save()
            return redirect('home')
    else:
       frm = PrForm(instance=instance_edit)
    return render(request, 'create.html', {'frm': frm})

@user_passes_test(is_admin)
def edit2(request, pk):
    instance_edit = Scube_ss.objects.get(pk=pk)
    if request.method == 'POST':
        frm = PrForm(request.POST, request.FILES, instance=instance_edit)
        if frm.is_valid():
            instance_edit.save()
            return redirect('Pr_Approvel')
    else:
       frm = PrForm(instance=instance_edit)
    return render(request, 'create.html', {'frm': frm})

@user_passes_test(is_admin)
def del_cnf(request, pk):
    instance_dl = Scube_ss.objects.get(pk=pk)
    if request.method == 'POST':
        instance_dl.delete()
        return redirect('list')
    return render(request, 'del_cnf.html')

@user_passes_test(is_admin)
def approve_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    if not record.is_approved:
        cloth_item = record.items.filter(material_name__iexact='CLOTH').first()
        cloth_code_val = ""
        if cloth_item and cloth_item.material_code:
            cloth_code_val = cloth_item.material_code.code

        original_total = int(record.grand_total)
        base_amount = (original_total // 500) * 500 
        remainder = original_total % 500 
        final_prize = base_amount if remainder < 250 else base_amount + 500 

        s_name = record.sofa_name if record.sofa_name and record.sofa_name.strip() else None
        s_size = record.sofa_size if record.sofa_size and record.sofa_size.strip() else None
        s_color = record.sofa_color if record.sofa_color and record.sofa_color.strip() else None

        Scube_ss.objects.create(
            code=record.sofa_code, Catogory='SOFA', name=s_name, size=s_size,
            prize=final_prize, material=cloth_code_val, color=s_color,
            pr_date=record.date, status='SCUBE', image=record.image, new_pr='NEW'
        )
        record.is_approved = True
        record.save()
    return redirect('production_summary')

@user_passes_test(is_admin)
def approve_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    if request.method == 'POST' and not record.is_approved:
        Scube_ss.objects.create(
            code=record.cl_code, Catogory=record.cl_Catogory, name=record.cl_name,
            size=record.cl_size, prize=record.cl_prize, material=record.cl_material,
            color=record.cl_color, pr_date=record.cl_pr_date, status='SCUBE', image=record.cl_image,
        )
        record.is_approved = True
        record.save()
    return redirect('board_production_summary')

@user_passes_test(is_admin)
def bulk_approve_board_production(request):
    if request.method == 'POST':
        record_ids = request.POST.getlist('record_ids')
        if record_ids:
            records = BoardProductionRecord.objects.filter(id__in=record_ids, is_approved=False)
            for record in records:
                Scube_ss.objects.create(
                    code=record.cl_code, Catogory=record.cl_Catogory, name=record.cl_name,
                    size=record.cl_size, prize=record.cl_prize, material=record.cl_material,
                    color=record.cl_color, pr_date=record.cl_pr_date, status='SCUBE', image=record.cl_image,
                )
                record.is_approved = True
                record.save()
    return redirect('board_production_summary')

@user_passes_test(is_admin)
def update_sort_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_ids = data.get('order', [])
            for index, item_id in enumerate(order_ids):
                Scube_ss.objects.filter(id=item_id).update(sort_order=index)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid_method'})

@user_passes_test(is_admin)
def change_gallery_status(request, item_id, status):
    item = get_object_or_404(Scube_ss, id=item_id)
    if status in ['SHOW', 'UNSHOW', 'PENDING']:
        item.gallery_status = status
        item.save()
    return redirect(request.META.get('HTTP_REFERER', 'image_categories'))

@user_passes_test(is_admin)
def orders_det(request):
    ls_data = orders.objects.all().order_by('id')
    return render(request, 'orders.html', {'order': ls_data})

@user_passes_test(is_admin)
def order_det(request):
    if request.method == 'POST':
        frm = OrderForm(request.POST, request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('order')
    else:
        frm = OrderForm()
    return redirect('order')

@user_passes_test(is_admin)
def order_delcnf(request, pk):
    dt_data = orders.objects.get(pk=pk)
    if request.method == 'POST':
        dt_data.delete()
        return redirect('orders_det')
    return render(request, 'order_delcnf.html')

@user_passes_test(is_admin)
def reports(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        category = request.POST.get('category')
        filters = {}
        if start_date: filters['pr_date__gte'] = parse_date(start_date)
        if end_date: filters['pr_date__lte'] = parse_date(end_date)
        if category: filters['Catogory'] = category
        production_reports = Scube_ss.objects.filter(**filters).order_by('pr_date')
        context = {'PR_reports': production_reports, 'Catogory_choice': Catogory_choice}
    else:
        context = {'Catogory_choice': Catogory_choice}
    return render(request, 'reports.html', context)

@user_passes_test(is_admin)
def reports_s2s(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')
        filters = {}
        if start_date: filters['sl_date__gte'] = parse_date(start_date)
        if end_date: filters['sl_date__lte'] = parse_date(end_date)
        if status: filters['status'] = status
        production_reports = Scube_ss.objects.filter(**filters).order_by('sl_date')
        context = {'PR_reports': production_reports, 'status_choice': status_choice}
    else:
        context = {'status_choice': status_choice}
    return render(request, 'reports_S2S.html', context)

@user_passes_test(is_admin)
def sales_reports(request):
    if request.method == 'POST':
        S_date = request.POST.get('start_date')
        E_date = request.POST.get('end_date')
        P_rep = Scube_ss.objects.filter(sl_date__gte=S_date, sl_date__lte=E_date).order_by('sl_date')
        return render(request, 'sales_reports.html', {'PR_reports': P_rep})
    else:
        return render(request, 'sales_reports.html')

# ==============================================================================
# 6. SALES BILL & INVOICE
# ==========================================

@user_passes_test(is_admin)
def sales_bill(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        cust_status = request.POST.get('customer_name') # Status from dropdown
        
        last_inv = Invoice.objects.order_by('-id').first()
        if last_inv:
            inv_no = f"INV{int(last_inv.id) + 1:04d}"
        else:
            inv_no = "INV0001"
            
        invoice = Invoice.objects.create(
            invoice_number=inv_no, date=date, customer_name=cust_status
        )
        
        p_ids = request.POST.getlist('product_ids[]')
        qtys = request.POST.getlist('quantities[]')
        prices = request.POST.getlist('prices[]')
        totals = request.POST.getlist('totals[]')
        
        g_total = 0
        for i in range(len(p_ids)):
            if p_ids[i]:
                try:
                    prod = Scube_ss.objects.get(id=p_ids[i])
                    q = int(qtys[i]) if i < len(qtys) else 1
                    p = float(prices[i]) if i < len(prices) else 0.0
                    t = float(totals[i]) if i < len(totals) else 0.0
                    
                    InvoiceItem.objects.create(
                        invoice=invoice, category=prod.Catogory, product=prod,
                        quantity=q, price=p, total=t
                    )
                    g_total += t
                    
                    prod.status = cust_status     
                    prod.sl_date = date           
                    prod.prize = int(p)           
                    prod.save()
                except Exception as e:
                    print(e)
        
        invoice.grand_total = g_total
        invoice.save()
        messages.success(request, f"Invoice {inv_no} created successfully!")
        return redirect('sales_bill')
        
    categories = Catogory_choice
    statuses = status_choice  
    scube_products = Scube_ss.objects.filter(status='SCUBE').order_by('Catogory', 'name')
    
    return render(request, 'sales_bill.html', {
        'categories': categories, 
        'statuses': statuses, 
        'scube_products': scube_products
    })

@user_passes_test(is_admin)
def get_scube_products(request):
    cat = request.GET.get('category')
    products = Scube_ss.objects.filter(Catogory=cat, status='SCUBE').values('id', 'name', 'code', 'prize')
    return JsonResponse({'products': list(products)})

@user_passes_test(is_admin)
def invoice_history(request):
    today = datetime.date.today()
    first_day_of_month = today.replace(day=1)
    
    start_date = request.GET.get('start_date') or first_day_of_month.strftime('%Y-%m-%d')
    end_date = request.GET.get('end_date') or today.strftime('%Y-%m-%d')
    status = request.GET.get('status')

    invoices = Invoice.objects.filter(date__gte=start_date, date__lte=end_date)
    
    if status:
        invoices = invoices.filter(customer_name=status)
        
    invoices = invoices.order_by('-date', '-id')

    context = {
        'invoices': invoices,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'statuses': status_choice
    }
    return render(request, 'invoice_history.html', context)

@user_passes_test(is_admin)
def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = invoice.items.all()
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'items': items})

# ==============================================================================
# 7. STOCK MANAGEMENT
# ==============================================================================

@user_passes_test(is_admin)
def stock_management(request):
    sofa_categories = StockMaterialCategory.objects.filter(material_type='SOFA')
    pb_categories = StockMaterialCategory.objects.filter(material_type='PB')
    
    active_cat_id = request.GET.get('cat_id')
    
    if active_cat_id:
        active_category = get_object_or_404(StockMaterialCategory, id=active_cat_id)
    else:
        active_category = sofa_categories.first() if sofa_categories.exists() else None

    items = StockItem.objects.filter(material=active_category) if active_category else []
    all_categories = StockMaterialCategory.objects.all()

    context = {
        'sofa_categories': sofa_categories,
        'pb_categories': pb_categories,
        'active_category': active_category,
        'items': items,
        'all_categories': all_categories,
    }
    return render(request, 'stock_management.html', context)

@user_passes_test(is_admin)
def add_stock_category(request):
    if request.method == 'POST':
        m_type = request.POST.get('material_type')
        c_name = request.POST.get('category_name')
        if m_type and c_name:
            StockMaterialCategory.objects.create(material_type=m_type, category_name=c_name)
            messages.success(request, 'Category Added Successfully!')
    return redirect('stock_management')

@user_passes_test(is_admin)
def edit_stock_category(request, cat_id):
    category = get_object_or_404(StockMaterialCategory, id=cat_id)
    if request.method == 'POST':
        category.category_name = request.POST.get('category_name')
        category.save()
        messages.success(request, 'Category Updated Successfully!')
    return redirect(f"/stock-management/?cat_id={category.id}")

@user_passes_test(is_admin)
def add_stock_item(request):
    if request.method == 'POST':
        cat_id = request.POST.get('category_id')
        category = get_object_or_404(StockMaterialCategory, id=cat_id)
        
        StockItem.objects.create(
            material=category,
            name=request.POST.get('name'),
            color=request.POST.get('color'),
            size=request.POST.get('size'),
            prize=request.POST.get('prize', 0),
            stock=request.POST.get('stock', 0),
            image=request.FILES.get('image')
        )
        messages.success(request, 'Item Added Successfully!')
        return redirect(f"/stock-management/?cat_id={cat_id}")
    return redirect('stock_management')

@user_passes_test(is_admin)
def edit_stock_item(request, item_id):
    item = get_object_or_404(StockItem, id=item_id)
    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.color = request.POST.get('color')
        item.size = request.POST.get('size')
        item.prize = request.POST.get('prize', 0)
        item.stock = request.POST.get('stock', 0)
        
        if request.FILES.get('image'):
            item.image = request.FILES.get('image')
            
        item.save()
        messages.success(request, 'Item Updated Successfully!')
    return redirect(f"/stock-management/?cat_id={item.material.id}")

@user_passes_test(is_admin)
def delete_stock_item(request, item_id):
    item = get_object_or_404(StockItem, id=item_id)
    cat_id = item.material.id
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Item Deleted!') 
    return redirect(f"/stock-management/?cat_id={cat_id}")