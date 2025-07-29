import datetime
from collections import OrderedDict

import django

from django import forms
import jdatetime
from jalali_date.widgets import AdminJalaliDateWidget

from rangefilter2.filters import DateRangeFilter

if django.VERSION >= (2, 0, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _  # pylint: disable=E0611
from jalali_date.fields import JalaliDateField


class JalaliDateRangeFilter(DateRangeFilter):
    def get_template(self):
        return "rangefilter2/jalali_date_filter.html"  

    template = property(get_template)

    def _get_form_fields(self):
        return OrderedDict(
            (
                (
                    self.lookup_kwarg_gte,
                    JalaliDateField(
                        label="",
                        widget=AdminJalaliDateWidget(attrs={"placeholder": _("از تاریخ"),'readonly': True}),
                        localize=True,
                        required=False,
                        initial=self.default_gte,
                    ),
                ),
                (
                    self.lookup_kwarg_lte,
                    JalaliDateField(
                        label="",
                        widget=AdminJalaliDateWidget(attrs={"placeholder": _("تا تاریخ"),'readonly': True}),
                        localize=True,
                        required=False,
                        initial=self.default_lte,
                    ),
                ),
            )
        )

    def get_form(self, _request):
        fields = self._get_form_fields()

        # تعریف فرم با متد clean برای تبدیل تاریخ جلالی به میلادی
        class JalaliDateRangeForm(forms.BaseForm):
            base_fields = fields

            def clean(self):
                cleaned_data = super().clean()
                for key in cleaned_data:
                    val = cleaned_data.get(key)
                    if val and isinstance(val, str):
                        # تبدیل رشته جلالی به شیء jdatetime.date
                        try:
                            parts = val.split("/")
                            if len(parts) == 3:
                                jy, jm, jd = map(int, parts)
                                jdate = jdatetime.date(jy, jm, jd)
                                gdate = jdate.togregorian()
                                cleaned_data[key] = gdate
                        except Exception:
                            # اگر خطایی بود می‌توان اجازه دهیم فرم خطا بدهد
                            pass
                return cleaned_data

        form_class = JalaliDateRangeForm

        # خطوط زیر برای سازگاری با Django 5+ در صورت نیاز
        if django.VERSION[:2] >= (5, 0):
            for name, value in self.used_parameters.items():
                if isinstance(value, list):
                    self.used_parameters[name] = value[-1]

        return form_class(self.used_parameters or None)

    def _make_query_filter(self, request, validated_data):
        # همان کد قبلی برای تبدیل jdatetime به میلادی
        query_params = {}
        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)

        if date_value_gte:
            if isinstance(date_value_gte, jdatetime.date):
                date_value_gte = date_value_gte.togregorian()
            query_params["{0}__gte".format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_gte, datetime.time.min),
                self.get_timezone(request),
            )
        if date_value_lte:
            if isinstance(date_value_lte, jdatetime.date):
                date_value_lte = date_value_lte.togregorian()
            query_params["{0}__lte".format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(date_value_lte, datetime.time.max),
                self.get_timezone(request),
            )

        return query_params
