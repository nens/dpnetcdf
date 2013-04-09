from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.models import MapLayer, Datasource, Style


class MapLayerAdminForm(forms.ModelForm):
    class Meta:
        model = MapLayer

    datasources = forms.ModelMultipleChoiceField(
        queryset=Datasource.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('datasources'),
            is_stacked=False
        )
    )

    styles = forms.ModelMultipleChoiceField(
        queryset=Style.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('styles'),
            is_stacked=False
        )
    )

    def __init__(self, *args, **kwargs):
        super(MapLayerAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['datasources'].initial = self.instance.datasources.all()
            self.fields['styles'].initial = self.instance.styles.all()

    def save(self, commit=True):
        maplayer = super(MapLayerAdminForm, self).save(commit=False)
        if commit:
            maplayer.save()

        if maplayer.pk:
            maplayer.datasources = self.cleaned_data['datasources']
            maplayer.styles = self.cleaned_data['styles']
            self.save_m2m()

        return maplayer
