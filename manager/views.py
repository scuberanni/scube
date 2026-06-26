import re
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse

from .forms import PrForm, OrderForm, PBPaidForm,SofaPaidForm
from .models import (
    Scube_ss, orders, MaterialName, Material, 
    SofaProductionRecord, ProductionMaterialItem, 
    BoardColor, BoardMaterial, ProductItem, 
    BoardProductionRecord, PB_Paid_Entry,Sofa_Paid_Entry,
    Catogory_choice, status_choice
)

def admin(request):
    return render(request, 'admin')

def image_categories(request):
    return render(request, 'image_categories.html')

def image_gallery(request, category):
    # ഇമേജ് ഇല്ലാത്തവ (Empty/Null) ഒഴിവാക്കാൻ exclude ഉപയോഗിക്കുന്നു
    base_query = Scube_ss.objects.exclude(image='').exclude(image__isnull=True)

    if category == 'ALL':
        images = base_query.order_by('-pr_date', '-id')
        page_title = "ALL PRODUCTS"
    else:
        images = base_query.filter(Catogory=category).order_by('-pr_date', '-id')
        page_title = category.replace('-', ' ')

    context = {
        'images': images,
        'page_title': page_title,
        'current_category': category,
    }
    return render(request, 'image_gallery.html', context)

def others_menu(request):
    return render(request, 'others.html')

def create(request):
    if request.method == 'POST':
        frm = PrForm(request.POST, request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('create')
    else:
        frm = PrForm()
    return render(request, 'create.html', {'frm': frm})

def all_products(request):
    Pr_data = Scube_ss.objects.filter(status="SCUBE").order_by('Catogory')
    return render(request, 'all_products.html', {'products': Pr_data})

def home(request):
    return render(request, 'index.html')

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
            item = Material.objects.get(id=item_id)
            category = MaterialName.objects.get(id=cat_id)
            
            item.material = category
            item.code = code
            item.description = description
            item.price = price
            item.save()
            
    return redirect('master_data')

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
            max_num_save = 0
            for s in sofas_check:
                match = re.search(r'SCSF(\d+)', s.sofa_code)
                if match:
                    num = int(match.group(1))
                    if num > max_num_save:
                        max_num_save = num
            sofa_code = f"SCSF{max_num_save + 1:02d}"

        other_desc = request.POST.get('other_desc', '')
        other_cost = float(request.POST.get('other_cost') or 0)
        wood_cost = float(request.POST.get('wood_cost') or 0)
        wage_cost = float(request.POST.get('wage_cost') or 0)
        profit_amount = float(request.POST.get('profit_amount') or 0)

        grand_total = other_cost + wood_cost + wage_cost + profit_amount

        production_record = SofaProductionRecord.objects.create(
            date=date,
            sofa_code=sofa_code,
            image=image,
            sofa_name=sofa_name,
            sofa_size=sofa_size,
            sofa_color=sofa_color,
            other_desc=other_desc,
            other_cost=other_cost,
            wood_cost=wood_cost,
            wage_cost=wage_cost,
            profit_amount=profit_amount,
            grand_total=0
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

        production_record.grand_total = grand_total + item_grand_total
        production_record.save()

        return redirect('production_bill', record_id=production_record.id)

    materials = Material.objects.all()
    context = {
        'materials': materials,
        'new_sofa_code': new_sofa_code
    }
    return render(request, 'production_entry.html', context)

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

def production_summary(request):
    records = SofaProductionRecord.objects.filter(is_approved=False).order_by('-date', '-id')
    return render(request, 'production_summary.html', {'records': records})

def delete_production(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
    return redirect('production_summary')

def production_bill(request, record_id):
    record = get_object_or_404(SofaProductionRecord, id=record_id)
    items = record.items.all()
    return render(request, 'production_bill.html', {'record': record, 'items': items})

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

        if remainder < 250:
            final_prize = base_amount 
        else:
            final_prize = base_amount + 500 

        s_name = record.sofa_name if record.sofa_name and record.sofa_name.strip() else None
        s_size = record.sofa_size if record.sofa_size and record.sofa_size.strip() else None
        s_color = record.sofa_color if record.sofa_color and record.sofa_color.strip() else None

        Scube_ss.objects.create(
            code=record.sofa_code,
            Catogory='SOFA',
            name=s_name,
            size=s_size,
            prize=final_prize, 
            material=cloth_code_val,
            color=s_color,
            pr_date=record.date,
            status='SCUBE',
            image=record.image,
            new_pr='NEW'
        )

        record.is_approved = True
        record.save()

    return redirect('production_summary')

def pr_img(request):
    return render(request, 'all.html')

def list(request):
    ls_data = Scube_ss.objects.filter(status="SCUBE").order_by('code')
    return render(request, 'list.html', {'prod': ls_data})

def Pr_Approvel(request):
    ls_data = Scube_ss.objects.filter(Q(prize__isnull=True) | Q(prize="0"), pr_date__gt="2024-08-01").order_by('pr_date')
    return render(request, 'Pr_Approvel.html', {'prod': ls_data})

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

def del_cnf(request, pk):
    instance_dl = Scube_ss.objects.get(pk=pk)
    if request.method == 'POST':
        instance_dl.delete()
        return redirect('list')
    return render(request, 'del_cnf.html')

def details(request, pk):
    dt_data = Scube_ss.objects.filter(pk=pk)
    return render(request, 'details.html', {'details': dt_data})

def viewimage(request, pk):
    dt_data = Scube_ss.objects.filter(pk=pk)
    return render(request, 'viewimage.html', {'viewimage': dt_data})

def order_delcnf(request, pk):
    dt_data = orders.objects.get(pk=pk)
    if request.method == 'POST':
        dt_data.delete()
        return redirect('orders_det')
    return render(request, 'order_delcnf.html')

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

def reports_s2s(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        status = request.POST.get('status')

        filters = {}
        if start_date:
            filters['sl_date__gte'] = parse_date(start_date)
        if end_date:
            filters['sl_date__lte'] = parse_date(end_date)
        if status:
            filters['status'] = status

        production_reports = Scube_ss.objects.filter(**filters).order_by('sl_date')
        context = {'PR_reports': production_reports, 'status_choice': status_choice}
    else:
        context = {'status_choice': status_choice}

    return render(request, 'reports_S2S.html', context)

def sales_reports(request):
    if request.method == 'POST':
        S_date = request.POST.get('start_date')
        E_date = request.POST.get('end_date')
        P_rep = Scube_ss.objects.filter(sl_date__gte=S_date, sl_date__lte=E_date).order_by('sl_date')
        return render(request, 'sales_reports.html', {'PR_reports': P_rep})
    else:
        return render(request, 'sales_reports.html')

def show_cupboard(request):
    ls_data = Scube_ss.objects.filter(Catogory="CUPBOARD", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def show_table(request):
    ls_data = Scube_ss.objects.filter(Catogory="TABLE", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def show_tv_stand(request):
    ls_data = Scube_ss.objects.filter(Catogory="TV-STAND", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def show_sofa(request):
    ls_data = Scube_ss.objects.filter(Catogory="SOFA", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def bedroom_set(request):
    ls_data = Scube_ss.objects.filter(Catogory="BEDROOM-SET", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def pooja_stand(request):
    ls_data = Scube_ss.objects.filter(Catogory="POOJA-STAND", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def others(request):
    ls_data = Scube_ss.objects.filter(Catogory="OTHERS", status="SCUBE").order_by('size')
    return render(request, 'all_products.html', {'products': ls_data})

def order(request):
    ls_data = Scube_ss.objects.filter(Catogory="ORDER", status="SCUBE").order_by('size')
    return render(request, 'order.html', {'products': ls_data})

def orders_det(request):
    ls_data = orders.objects.all().order_by('id')
    return render(request, 'orders.html', {'order': ls_data})

def order_det(request):
    if request.method == 'POST':
        frm = OrderForm(request.POST, request.FILES)
        if frm.is_valid():
            frm.save()
            return redirect('order')
    else:
        frm = OrderForm()
    return redirect('order')

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
    
    context = {
        'colors': colors,
        'materials': materials,
        'products': products,
        'categories': Catogory_choice,
    }
    return render(request, 'product_master.html', context)

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
            
            # പുതിയതായി ചേർത്ത Quantity Array
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
                
                # HTML ൽ നിന്നും Quantity എടുക്കുന്നു, ഇല്ലെങ്കിൽ 1 എന്ന് എടുക്കുന്നു
                try:
                    qty = int(quantities[i])
                    if qty < 1: 
                        qty = 1
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
                
                # കൊടുത്ത നമ്പറിന് (QTY) അനുസരിച്ച് ലൂപ്പ് ചെയ്ത് സേവ് ചെയ്യുന്നു
                for j in range(qty):
                    # ഒരു ഇമേജ് തന്നെ പല വട്ടം സേവ് ആകുമ്പോൾ എറർ വരാതിരിക്കാൻ
                    if img:
                        img.seek(0)
                        
                    BoardProductionRecord.objects.create(
                        cl_Catogory=cat,
                        cl_name=name,
                        cl_size=size,
                        cl_prize=prize,
                        cl_wage=wage, 
                        cl_material=material,
                        cl_color=color_name,
                        cl_pr_date=entry_date,
                        cl_status=status,
                        cl_image=img
                    )
        except Exception as e:
            print(f"Error saving data: {e}") 
            
        return redirect('board_production_entry')

    colors = BoardColor.objects.all()
    categories = Catogory_choice
    all_products = ProductItem.objects.all()
    materials = BoardMaterial.objects.all() 
    
    context = {
        'colors': colors,
        'categories': categories,
        'all_products': all_products,
        'materials': materials, 
    }
    return render(request, 'board_production_entry.html', context)

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
            return JsonResponse({
                'status': 'success',
                'id': product.id,
                'name': product.pb_name,
                'category': product.pb_category
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid_method'})

def board_production_summary(request):
    records = BoardProductionRecord.objects.filter(is_approved=False).order_by('-id')
    
    colors = BoardColor.objects.all()
    categories = Catogory_choice
    materials = BoardMaterial.objects.all()
    
    context = {
        'records': records,
        'colors': colors,
        'categories': categories,
        'materials': materials,
    }
    return render(request, 'board_production_summary.html', context)

def approve_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    
    if request.method == 'POST' and not record.is_approved:
        Scube_ss.objects.create(
            code=record.cl_code,
            Catogory=record.cl_Catogory,
            name=record.cl_name,
            size=record.cl_size,
            prize=record.cl_prize,
            material=record.cl_material,
            color=record.cl_color,
            pr_date=record.cl_pr_date,
            status='SCUBE', 
            image=record.cl_image,
        )
        record.is_approved = True
        record.save()
        
    return redirect('board_production_summary')

def bulk_approve_board_production(request):
    if request.method == 'POST':
        # ചെക്ക് ചെയ്ത എല്ലാ ഐഡികളും എടുക്കുന്നു
        record_ids = request.POST.getlist('record_ids')
        
        if record_ids:
            # ഐഡികൾക്ക് മാച്ച് ആകുന്ന അപ്രൂവ് ആവാത്ത എല്ലാ റെക്കോർഡുകളും എടുക്കുന്നു
            records = BoardProductionRecord.objects.filter(id__in=record_ids, is_approved=False)
            
            for record in records:
                # മാസ്റ്റർ ടേബിളിലേക്ക് സേവ് ചെയ്യുന്നു
                Scube_ss.objects.create(
                    code=record.cl_code,
                    Catogory=record.cl_Catogory,
                    name=record.cl_name,
                    size=record.cl_size,
                    prize=record.cl_prize,
                    material=record.cl_material,
                    color=record.cl_color,
                    pr_date=record.cl_pr_date,
                    status='SCUBE', 
                    image=record.cl_image,
                )
                record.is_approved = True
                record.save()
                
    return redirect('board_production_summary')

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
        record.cl_wage = float(request.POST.get('cl_wage') or 0)
        record.cl_prize = float(request.POST.get('cl_prize') or 0)
        
        if request.FILES.get('cl_image'):
            record.cl_image = request.FILES.get('cl_image')
            record._image_compressed = False 
            
        record.save()
    return redirect('board_production_summary')

def delete_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
    return redirect('board_production_summary')

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

    all_total_wage = BoardProductionRecord.objects.aggregate(total=Sum('cl_wage'))['total'] or 0
    all_total_paid = PB_Paid_Entry.objects.aggregate(total=Sum('amount'))['total'] or 0

    prev_total_wage = BoardProductionRecord.objects.filter(cl_pr_date__lt=start_of_month).aggregate(total=Sum('cl_wage'))['total'] or 0
    prev_total_paid = PB_Paid_Entry.objects.filter(date__lt=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_month_balance = prev_total_wage - prev_total_paid

    current_month_wages_list = BoardProductionRecord.objects.filter(
        cl_pr_date__gte=start_of_month, cl_pr_date__lte=end_of_month
    ).order_by('cl_pr_date', 'id')
    current_month_total_wage = current_month_wages_list.aggregate(total=Sum('cl_wage'))['total'] or 0

    current_month_payments_list = PB_Paid_Entry.objects.filter(
        date__gte=start_of_month, date__lte=end_of_month
    ).order_by('date', 'id')
    current_month_total_paid = current_month_payments_list.aggregate(total=Sum('amount'))['total'] or 0

    excel_total_due = previous_month_balance + current_month_total_wage
    excel_current_balance = excel_total_due - current_month_total_paid

    context = {
        'year': year,
        'month_obj': start_of_month,
        'prev_month': prev_m_m,
        'prev_year': prev_m_y,
        'next_month': next_m_m,
        'next_year': next_m_y,
        'wages': current_month_wages_list,
        'payments': current_month_payments_list,
        'total_w_monthly': current_month_total_wage,
        'prev_balance': previous_month_balance,
        'excel_total_due': excel_total_due,
        'current_paid_monthly': current_month_total_paid,
        'current_balance': excel_current_balance,
        'payment_form': payment_form,
    }
    return render(request, 'monthly_wage_paid.html', context)

def edit_payment(request, payment_id):
    payment = get_object_or_404(PB_Paid_Entry, id=payment_id)
    if request.method == 'POST':
        payment.date = request.POST.get('date')
        payment.amount = request.POST.get('amount')
        payment.description = request.POST.get('description')
        payment.payment_mode = request.POST.get('payment_mode')
        payment.save()
        
        # എറർ പരിഹരിക്കാനുള്ള വരി (String-നെ ശരിയായ Date Object ആക്കാൻ)
        payment.refresh_from_db()
        
        messages.success(request, 'Payment updated successfully.')
    
    # എഡിറ്റ് ചെയ്ത ശേഷം ആ മാസത്തെ റിപ്പോർട്ടിലേക്ക് തന്നെ തിരികെ പോകാൻ
    if payment.date:
        return redirect('wage_report', year=payment.date.year, month=payment.date.month) 
    return redirect('wage_report_current')

def delete_payment(request, payment_id):
    payment = get_object_or_404(PB_Paid_Entry, id=payment_id)
    year, month = payment.date.year, payment.date.month
    if request.method == 'POST':
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
    return redirect('wage_report', year=year, month=month)

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
        record.cl_wage = float(request.POST.get('cl_wage') or 0)
        record.cl_prize = float(request.POST.get('cl_prize') or 0)
            
        record.save()

    return redirect(request.META.get('HTTP_REFERER', 'board_production_summary'))

def delete_board_production(request, record_id):
    record = get_object_or_404(BoardProductionRecord, id=record_id)
    if request.method == 'POST':
        record.delete()
        
    return redirect(request.META.get('HTTP_REFERER', 'board_production_summary'))

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

    # Calculations for Sofa (Using wage_cost from SofaProductionRecord)
    prev_total_wage = SofaProductionRecord.objects.filter(date__lt=start_of_month).aggregate(total=Sum('wage_cost'))['total'] or 0
    prev_total_paid = Sofa_Paid_Entry.objects.filter(date__lt=start_of_month).aggregate(total=Sum('amount'))['total'] or 0
    previous_month_balance = prev_total_wage - prev_total_paid

    current_month_wages_list = SofaProductionRecord.objects.filter(
        date__gte=start_of_month, date__lte=end_of_month
    ).order_by('date', 'id')
    current_month_total_wage = current_month_wages_list.aggregate(total=Sum('wage_cost'))['total'] or 0

    current_month_payments_list = Sofa_Paid_Entry.objects.filter(
        date__gte=start_of_month, date__lte=end_of_month
    ).order_by('date', 'id')
    current_month_total_paid = current_month_payments_list.aggregate(total=Sum('amount'))['total'] or 0

    excel_total_due = previous_month_balance + current_month_total_wage
    excel_current_balance = excel_total_due - current_month_total_paid

    context = {
        'year': year,
        'month_obj': start_of_month,
        'prev_month': prev_m_m,
        'prev_year': prev_m_y,
        'next_month': next_m_m,
        'next_year': next_m_y,
        'wages': current_month_wages_list,
        'payments': current_month_payments_list,
        'total_w_monthly': current_month_total_wage,
        'prev_balance': previous_month_balance,
        'excel_total_due': excel_total_due,
        'current_paid_monthly': current_month_total_paid,
        'current_balance': excel_current_balance,
        'payment_form': payment_form,
    }
    return render(request, 'sofa_monthly_wage_paid.html', context)

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

def delete_sofa_payment(request, payment_id):
    payment = get_object_or_404(Sofa_Paid_Entry, id=payment_id)
    year, month = payment.date.year, payment.date.month
    if request.method == 'POST':
        payment.delete()
    return redirect('sofa_wage_report', year=year, month=month)