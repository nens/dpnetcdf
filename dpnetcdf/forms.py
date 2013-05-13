from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import ugettext_lazy as _

from dpnetcdf.models import MapLayer, Datasource, Style


class MapLayerAdminForm(forms.ModelForm):
    class Meta:
        model = MapLayer

    def clean_parameter(self):
        """
        Enforce lower case parameters only. Using upper case characters
        does not work: issues with table and query creation and calling by
        GeoServer.

        """
        value = self.cleaned_data['parameter']
        if not value == unicode(value).lower():
            raise forms.ValidationError(
                _("For the parameter, only use lower case letters and "
                  "underscores."))
        return value
