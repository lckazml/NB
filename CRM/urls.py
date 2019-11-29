from django.conf.urls import url

from CRM.views import consultant
from CRM.views import teacher
urlpatterns = [

    url(r'customer_list/', consultant.CustomerList.as_view(), name='customer'),
    # 私库
    url(r'my_customer/', consultant.CustomerList.as_view(), name='my_customer'),
    # 增加客户
    url(r'customer/add/', consultant.customer, name='add_customer'),
    # 编辑客户
    url(r'customer/edit/(\d+)', consultant.customer, name='edit_customer'),
    # 添加报名记录
    url(r'enrollment/add/(?P<customer_id>\d+)', consultant.enrollment, name='add_enrollment'),
    # 展示跟进记录
    url(r'consult_record_list/(?P<customer_id>\d+)', consultant.ConsultRecord.as_view(), name='consult_record'),
    # 添加跟进记录
    url(r'consult_record/add/', consultant.consult_record, name='add_consult_record'),
    # 编辑跟进记录
    url(r'consult_record/edit/(\d+)/', consultant.consult_record, name='edit_consult_record'),
    # 展示报名记录
    url(r'enrollment_list/(?P<customer_id>\d+)', consultant.EnrollmentList.as_view(), name='enrollment'),
    # 编辑报名记录
    url(r'enrollment/edit/(?P<edit_id>\d+)', consultant.enrollment, name='edit_enrollment'),
    # 班级列表
    url(r'class_list/',teacher.ClassList.as_view(),name='class_list'),
    # 添加班级
    url(r'class/add/',teacher.classes,name='add_class'),
    # 编辑班级
    # 展示某个班级的课程记录
    # 添加课程记录
    # 编辑课程记录


]
