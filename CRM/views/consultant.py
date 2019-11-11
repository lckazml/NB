from django.shortcuts import render, redirect, reverse, HttpResponse
from django.contrib import auth
from CRM import models
from CRM.forms import *
from utils.pagination import Pagination
from django.views import View
from django.db.models import Q
from django.db import transaction
from django.http import QueryDict
import copy
from django.utils.safestring import mark_safe
from django.conf import settings


def login(request):
    err_msg = ''
    if request.user:
        return redirect(reverse('customer'))
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        obj = auth.authenticate(request, username=username, password=password)
        if obj:
            auth.login(request, obj)
            return redirect(reverse('customer'))
        err_msg = '用户名或密码错误'

    return render(request, 'login.html', {'err_msg': err_msg})


# 注册
def reg(request):
    form_obj = RegForm()
    if request.method == 'POST':
        form_obj = RegForm(request.POST)
        if form_obj.is_valid():
            # 创建新用户
            # 方法一
            # form_obj.cleaned_data.pop('re_password')
            # models.UserProfile.objects.create_user(**form_obj.cleaned_data)

            # 方法二
            obj = form_obj.save()
            obj.set_password(obj.password)
            obj.save()

            return redirect('/login/')
    return render(request, 'reg.html', {'form_obj': form_obj})


# def customer_list(request):
#     all_customer = models.Customer.objects.all()
#     page = Pagination(request, all_customer.count())
#     return render(request, 'crm/customer_list.html',
#                   {'all_customer': all_customer[page.start():page.end()], 'pagination': page.show_li})

class CustomerList(View):
    def get(self, request):
        q = self.get_search_contion(['qq', 'name', 'last_consult_date'])

        if request.path_info == reverse('customer'):
            # Q()
            all_customer = models.Customer.objects.filter(q)
        else:
            all_customer = models.Customer.objects.filter(q, consultant=request.user)
        query_params = request.GET.copy()
        page = Pagination(request, all_customer.count(), query_params, )
        return render(request, 'crm/consultant/customer_list.html',
                      {"all_customer": all_customer[page.start:page.end], 'pagination': page.show_li,
                       'query_params': query_params})

    def post(self, request):
        action = request.POST.get('action')
        if not hasattr(self, action):
            return HttpResponse('非法操作')
        ret = getattr(self, action)()
        if ret:
            return ret
        return self.get(request)

    # 放入私库
    def multi_apply(self):
        ids = self.request.POST.getlist('id')
        apply_num = len(ids)
        if self.request.user.customers.count() + apply_num > settings.CUSTOMER_MAX_NUM:
            return HttpResponse('做人不要太贪心，给别人的机会')
        # 事务
        with transaction.atomic():
            obj_list = models.Customer.objects.filter(id__in=ids, consultant__isnull=True).select_for_update()
            if apply_num == len(obj_list):
                obj_list.update(consultant=self.request.user)
            else:
                return HttpResponse('你手速太慢了，已经被别人抢走了')

    # 放入公库
    def multi_pub(self):
        ids = self.request.POST.getlist('id')
        self.request.user.customers.remove(*models.Customer.objects.filter(id__in=ids))

    def multi_delete(self):
        ids = self.request.POST.getlist('id')
        models.Customer.objects.filter(id__in=ids).delete()

    def get_search_contion(self, fields_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in fields_list:
            q.children.append(Q(("{}__contains".format(i), query)))
        return q

    def get_add_btn(self):
        url = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()
        add_btn = '<a href="{}?{}" class="btn btn-primary btn-sm">添加</a>'.format(reverse('add_customer'), query_params)
        return mark_safe(add_btn), query_params


# 新增和编辑客户
def customer(request, edit_id=None):
    obj = models.Customer.objects.filter(id=edit_id).first()
    form_obj = CustomerForm(instance=obj)
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('customer'))
    return render(request, 'crm/consultant/add_customer.html', {"form_obj": form_obj, "edit_id": edit_id})


class ConsultRecord(View):
    def get(self, request, customer_id):

        if customer_id == '0':
            all_consult_record = models.ConsultRecord.objects.filter(delete_status=False, consultant=request.user)
        else:
            all_consult_record = models.ConsultRecord.objects.filter(customer_id=customer_id, delete_status=False)
        return render(request, 'crm/consultant/consult_record_list.html',{'all_consult_record': all_consult_record})


def enrollment(request, customer_id=None, edit_id=None):
    obj = models.Enrollment.objects.filter(id=edit_id).first() or models.Enrollment(customer_id=customer_id)
    form_obj = EnrollmentForm(instance=obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=obj)
        if form_obj.is_valid():
            enrollment_obj = form_obj.save()
            # 修改客户的状态
            enrollment_obj.customer.status = 'signed'
            enrollment_obj.customer.save()
            next = request.GET.get('next')
            if next:
                return redirect(next)
            else:
                return redirect(reverse('my_customer'))
    return render(request, 'crm/consultant/enrollment.html', {'form_obj': form_obj})


# 新增和编辑跟进记录
def consult_record(request, edit_id=None):
    obj = models.ConsultRecord.objects.filter(id=edit_id).first() or models.ConsultRecord(consultant=request.user)
    form_obj = ConsultRecordForm(instance=obj)
    if request.method == 'POST':
        form_obj = ConsultRecordForm(request.POST, instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record', args=(0,)))
    return render(request, 'crm/consultant/edit_consult_record.html', {'form_obj': form_obj})

# 展示报名记录
class EnrollmentList(View):
    def get(self,request,customer_id):
        if customer_id=='0':
            all_record=models.Enrollment.objects.filter(delete_status=False,customer__consultant=request.user)
        else:
            all_record=models.Enrollment.objects.filter(delete_status=False,customer_id=customer_id)
        query_params=self.get_query_params()
        return render(request,'crm/consultant/enrollment_list.html',{
            'all_record':all_record,
            'query_params':query_params
        })


    def get_query_params(self):
        url=self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()

        return query_params