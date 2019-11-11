from django import forms
from CRM import models
from django.core.exceptions import ValidationError


class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})


class RegForm(BaseForm):
    password = forms.CharField(
        label='密码',
        widget=forms.widgets.PasswordInput(),
        min_length=6,
        error_messages={'min_length': '最小长度为6'}
    )
    re_password = forms.CharField(
        label='确认密码',
        widget=forms.widgets.PasswordInput(),
    )

    class Meta:
        model = models.UserProfile
        fields = ['username', 'password', 're_password', 'name', 'department']
        widgets = {
            'username': forms.widgets.EmailInput,
        }
        labels = {
            'username': '用户名',
            'name': '名字',
            'department': '部门',
        }
        error_messages = {
            'username': {
                'required': '用户名不能为空',
            }
        }

    def clean(self):
        pwd = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_password')
        if pwd == re_pwd:
            return self.cleaned_data
        self.add_error('re_password', '两次密码不一致')
        raise ValidationError('两次密码不一致')


def mobile_validate(value):
    import re
    mobile_re = re.compile("^1[3-9]\\d{9}$")
    if not mobile_re.match(value):
        raise forms.ValidationError('手机号不正确')


class CustomerForm(BaseForm):
    phone = forms.CharField(
        validators=[mobile_validate, ],
        error_messages={
            'required': '手机号不能为空'
        }
    )

    class Meta:
        model = models.Customer
        fields = '__all__'
        widgets = {
            'course': forms.widgets.SelectMultiple
        }
        error_messages = {
            'qq': {
                'required': '用户名不能为空',
            },
            'course': {
                'required': '课程不能为空',
            },
            'class_list': {
                'required': '请选择报名的课程',
            },
        }


class EnrollmentForm(BaseForm):
    class Meta:
        model = models.Enrollment
        exclude = ['delete_status', 'contract_approved']
        labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制当前的客户只能是传的id对应的客户
        self.fields['customer'].widget.choices = [(self.instance.customer_id, self.instance.customer), ]
        # 限制当前可报名的班级是当前客户的意向班级
        self.fields['enrolment_class'].widget.choices = [(i.id, i) for i in self.instance.customer.class_list.all()]


class ConsultRecordForm(BaseForm):
    class Meta:
        model = models.ConsultRecord
        exclude = ['delete_status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # [print(it.id,it) for it in self.instance.consultant.customers.all()]
        customer_choice = [(i.id, i) for i in self.instance.consultant.customers.all()]
        customer_choice.insert(0, ('', '--------'))

        self.fields['customer'].widget.choices = customer_choice
        self.fields['consultant'].widget.choices = [(self.instance.consultant_id, self.instance.consultant), ]
