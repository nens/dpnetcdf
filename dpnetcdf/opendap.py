import os
from datetime import datetime
from urlparse import urljoin

from BeautifulSoup import BeautifulSoup
from lxml import etree
from pydap.client import open_url
import pytz
import requests


DPRD_CATALOG_URL = 'http://opendap-dm1.knmi.nl:8080/thredds/catalog/deltamodel/Deltaportaal/DPRD/catalog.xml'
MAIN_CATALOG = 'http://opendap-dm1.knmi.nl:8080/thredds/catalog/deltamodel/Deltaportaal/catalog.xml'

URL_ROOT = 'http://opendap-dm1.knmi.nl:8080/'
CATALOG_SERVICE = '/thredds/catalog/'
CATALOG_BASE = 'deltamodel/Deltaportaal'
OPENDAP_SERVICE = '/thredds/dodsC/'
HTTP_SERVICE = '/thredds/fileServer/'

NAMESPACE = "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"

# opendap nc urls are something like (URL_ROOT + OPENDAP_SERVICE + dataset.urlpath):
# http://opendap-dm1.knmi.nl:8080/thredds/dodsC/deltamodel/Deltaportaal/DPRD/199101060440_DPRD_S0v1_2100_SW_RF1p0p3.nc


def parse_timestamp(timestamp_str):
    """
    Parse timestamp string. Input can be something like 2013-01-28T11:04:15Z
    Return a datetime, preferably with UTC timezone (Z = Zulu = UTC).

    """
    ts = timestamp_str
    year = int(ts[0:4])
    month = int(ts[5:7])
    day = int(ts[8:10])
    hour = int(ts[11:13])
    minute = int(ts[14:16])
    seconds = int(ts[17:19])
    dt = datetime(year, month, day, hour, minute, seconds, tzinfo=pytz.UTC)
    return dt


def parse_dataset_urls(catalog_url):
    # TODO: rewrite with BeautifulSoup (see parse_dataset_properties(..))
    response = requests.get(catalog_url)
    xml = etree.fromstring(response.content)
    base = xml.find('.//{%s}service' % NAMESPACE)
    base_path = os.path.split(catalog_url)[0]
    for dataset in xml.iterfind('.//{%s}dataset[@urlPath]' % NAMESPACE):
        joined_url = urljoin(base.attrib['base'], dataset.attrib['name'])
        url = '/'.join([s.strip('/') for s in [base_path.replace('/catalog/', '/dodsC/'), joined_url]])
        yield url


def parse_dataset_properties(catalog_url):
    response = requests.get(catalog_url)
    soup = BeautifulSoup(response.content)
    dataset_tags = soup.findAll('dataset')
    for tag in dataset_tags:
        if not tag['name'].endswith('.nc'):
            continue
        filesize = tag.find('datasize').text
        size_units = tag.find('datasize')['units']
        timestamp_str = tag.find('date').text
        timestamp = parse_timestamp(timestamp_str)
        yield {'name': tag['name'], 'id': tag['id'], 'urlpath': tag['urlpath'],
               'size': filesize, 'size_units': size_units,
               'timestamp': timestamp}


def parse_catalog_urls(main_catalog_url):
    """
    Example XML (http://opendap-dm1.knmi.nl:8080/thredds/catalog/deltamodel/Deltaportaal/catalog.xml):

    <catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0.1">
        <service name="all" serviceType="Compound" base="">
            <service name="odap" serviceType="OPENDAP" base="/thredds/dodsC/"/>
            <service name="http" serviceType="HTTPServer" base="/thredds/fileServer/"/>
        </service>
        <dataset name="Deltaportaal" ID="deltamodel/Deltaportaal">
            <metadata inherited="true">
                <serviceName>all</serviceName>
                <dataType>GRID</dataType>
            </metadata>
            <catalogRef xlink:href="DPRD/catalog.xml" xlink:title="DPRD" ID="deltamodel/Deltaportaal/DPRD" name=""/>
            <catalogRef xlink:href="DPR/catalog.xml" xlink:title="DPR" ID="deltamodel/Deltaportaal/DPR" name=""/>
        </dataset>
    </catalog>

    :return relative catalog urls
    """
    response = requests.get(main_catalog_url)
    soup = BeautifulSoup(response.content)
    dataset_tags = soup.findAll('dataset')
    for dataset_tag in dataset_tags:
        dataset_id = dataset_tag['id']  # deltamodel/Deltaportaal
        catalog_ref_tags = dataset_tag.findAll('catalogref')  # must be lower-case
        for catalog_ref_tag in catalog_ref_tags:
            catalog_ref_href = catalog_ref_tag['xlink:href']
            title = catalog_ref_tag['xlink:title']
            url_components = [dataset_id, catalog_ref_href]
            url = '/'.join([c.strip('/') for c in url_components])
            yield {'url': url, 'name': title}  # use name for title


def get_catalog_urls():
    return [cat['url'] for cat in parse_catalog_urls(MAIN_CATALOG)]


def get_dataset_urls(catalog_url):
    return [url for url in parse_dataset_urls(catalog_url)]


def get_dataset_properties(catalog_url):
    return [props for props in parse_dataset_properties(catalog_url)]


def get_dataset(dataset_url):
    try:
        return open_url(dataset_url)
    except Exception, msg:
        print "error getting %s: %s" % (dataset_url, msg)
        raise


def urlify(*url_components):
    url = '/'.join([c.strip('/') for c in url_components])
    return url


def root_catalog_url():
    return urlify(URL_ROOT, CATALOG_SERVICE, CATALOG_BASE,
                  'catalog.xml')


def fetch_all():
    """Test method for fast testing the functions above."""
    main_catalog_url = root_catalog_url()
    relative_catalog_urls = [cat['url'] for cat in parse_catalog_urls(
        main_catalog_url)]
    catalog_urls = [urlify(URL_ROOT, CATALOG_SERVICE, cat) for cat in
                    relative_catalog_urls]
    dataset_dict = {}
    for catalog_url in catalog_urls:
        datasets = [get_dataset(url) for url in parse_dataset_urls(
            catalog_url)]
        dataset_dict[catalog_url] = datasets
    return dataset_dict


def array_by_variable(dataset, var_name):
    # put it in a pandas timeseries
    if var_name not in dataset.keys():
        print "variable '%s' not found in dataset" % var_name
        return
    var_names = [v for v in dataset.keys() if var_name in v]
    pass
