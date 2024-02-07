from django.shortcuts import render , redirect 
from.forms import PrForm,OrderForm
from.models import Scube_ss,orders
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
    Pr_data=Scube_ss.objects.exclude(status="SALE" ).order_by('Catogory')
    return render(request,'all_products.html',{'products':Pr_data})

def home(request):
    return render(request,'index.html')


def list(request):
    ls_data=Scube_ss.objects.exclude(status="SALE" ).order_by('code')

    print(ls_data)     
    return render(request,'list.html',{'prod':ls_data})

def Pr_Approvel(request):
    ls_data = Scube_ss.objects.filter(Q(prize__isnull=True) | Q(prize="0"), pr_date__gt="2024-01-01").order_by('pr_date')

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


def reports(request):
    if request.method=='POST':
        
        S_date=request.POST.get('start_date')
        E_date=request.POST.get('end_date')
        P_rep=Scube_ss.objects.filter(pr_date__gte=S_date,pr_date__lte=E_date).order_by('pr_date')

       
        return render ( request,'reports.html',{'PR_reports':P_rep})
    else:
        
        return render(request,'reports.html',)
    
def sales_reports(request):
    if request.method=='POST':
        
        S_date=request.POST.get('start_date')
        E_date=request.POST.get('end_date')
        P_rep=Scube_ss.objects.filter(sl_date__gte=S_date,sl_date__lte=E_date).order_by('sl_date')

       
        return render ( request,'sales_reports.html',{'PR_reports':P_rep})
    else:
        
        return render(request,'sales_reports.html',)   
    
  
    
def show_cupboard(request):
    ls_data=Scube_ss.objects.filter(Catogory="CUPBOARD").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def show_table(request):
    ls_data=Scube_ss.objects.filter(Catogory="TABLE").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def show_tv_stand(request):
    ls_data=Scube_ss.objects.filter(Catogory="TV-STAND").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def show_sofa(request):
    ls_data=Scube_ss.objects.filter(Catogory="SOFA").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def bedroom_set(request):
    ls_data=Scube_ss.objects.filter(Catogory="BEDROOM-SET").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def pooja_stand(request):
    ls_data=Scube_ss.objects.filter(Catogory="POOJA-STAND").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def others(request):
    ls_data=Scube_ss.objects.filter(Catogory="OTHERS").exclude(status="SALE").order_by('size')

    print(ls_data)     
    return render(request,'all_products.html',{'products':ls_data})

def order(request):
    ls_data=Scube_ss.objects.filter(Catogory="ORDER").exclude(status="SALE").order_by('size')
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













    

    
