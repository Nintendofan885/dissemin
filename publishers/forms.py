from django import forms
from django.utils.translation import ugettext_lazy as _
from haystack.forms import SearchForm

from publishers.models import OA_STATUS_CHOICES_WITHOUT_HELPTEXT as OA_STATUS
from publishers.models import Publisher


class PublisherForm(SearchForm):
    SORT_CHOICES = [
        ('num_papers', _('popularity')),
        ('name', _('name')),
    ]
    ORDER_CHOICES = [
        ('dec', _('decreasing')),
        ('inc', _('increasing')),
    ]
    oa_status = forms.MultipleChoiceField(
        choices=OA_STATUS,
        label=_('Filter by publisher policy'),
        widget=forms.CheckboxSelectMultiple,
        required=False)
    sort_by = forms.ChoiceField(choices=SORT_CHOICES, required=False)
    reverse_order = forms.ChoiceField(choices=ORDER_CHOICES, required=False)

    def search(self):
        queryset = self.searchqueryset.models(Publisher).load_all()

        q = self.cleaned_data['q']
        if q:
            self.queryset = self.queryset.auto_query(q)

        if self.cleaned_data['oa_status']:
            queryset = queryset.filter(
                oa_status__in=self.cleaned_data['oa_status'])

        # Default ordering by decreasing popularity
        order = self.cleaned_data['sort_by'] or 'num_papers'
        reverse_order = self.cleaned_data['reverse_order'] != 'inc'
        if reverse_order:
            order = '-' + order

        queryset = queryset.order_by(order)

        return queryset
