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


# 班级列表展示
class ClassList(View):
    def get(self, request):
        # 模糊搜索
        q = self.get_search_contion(['course', 'semester'])
        all_class = models.ClassList.objects.filter(q)
        # 获取下一级url的跳转
        query_params = self.get_query_params()
        # 分页的应用
        page = Pagination(request, len(all_class), request.GET.copy())
        return render(request, 'crm/teacher/class_list.html', {
            'all_class': all_class[page.start:page.end], 'query_params': query_params, 'pagination': page.show_li
        })

    # 关键字搜索
    def get_search_contion(self, fields_list):
        query = self.request.GET.get('query', '')
        q = Q()
        q.connector = 'OR'
        for i in fields_list:
            q.children.append(Q(('{}__contains'.format(i), query)))
        return q

    def get_query_params(self):
        # 保存当前的全路劲
        url = self.request.get_full_path()
        qd = QueryDict()
        qd._mutable = True
        qd['next'] = url
        query_params = qd.urlencode()
        return query_params

def classes(request,edit_id=None):
    obj=models.ClassList.objects.filter(id=edit_id).first()
    form_obj=ClassForm(instance=obj)
    title='编辑班级' if obj else '添加班级'
    if request.method=='POST':
        form_obj = ClassForm(request.POST,instance=obj)
        if form_obj.is_valid():
            form_obj.save()
            next=request.GET.get('next')
            if next:
                return redirect(next)
            return redirect(reverse('class_list'))
    return render(request,'crm/form.html',{'title':title,'form_obj':form_obj})