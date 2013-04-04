from django.conf import settings
from appconf import AppConf


class NetCDFConf(AppConf):
    RESOURCE_DIR = "/tmp/netcdfs"

    class Meta:
        prefix = 'netcdf'
