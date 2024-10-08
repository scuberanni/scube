from django.shortcuts import render , redirect ,HttpResponse
from.forms import PrForm,OrderForm
from.models import Scube_ss,orders
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.db.models import Sum
from django.db.models import Q


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