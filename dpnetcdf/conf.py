from django.conf import settings
from appconf import AppConf


class NetCDFConf(AppConf):
    RESOURCE_DIR = "/tmp/netcdfs"
    SQLALCHEMY_CONNECTION = 'postgresql://buildout:buildout@localhost/dpgeo'
    SHAPE_FILE_DIR = '/tmp/shapes'

    class Meta:
        prefix = 'netcdf'
