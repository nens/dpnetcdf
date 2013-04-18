from django.conf import settings
from appconf import AppConf


class NetCDFConf(AppConf):
    RESOURCE_DIR = "/tmp/netcdfs"
    # SQLALCHEMY_CONNECTION for PostGis DB that holds GeoServer datastores
    SQLALCHEMY_CONNECTION = 'postgresql://user:passwd@host/db'
    SHAPE_FILE_DIR = '/tmp/shapes'
    REFERENCE_YEAR = 2015
    # GeoServer settings
    WORKSPACE_NAME = 'netcdf_workspace'
    DATASTORE_NAME = 'netcdf'

    class Meta:
        prefix = 'netcdf'
