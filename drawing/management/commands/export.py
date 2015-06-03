import tempfile
import datetime
from django.core.management.base import NoArgsCommand
import sys
import os
from drawing.models import AOI
import shapefile
import io
import zipfile


def zip_objects(items, compress_type=zipfile.ZIP_DEFLATED):
    """Given an array of items, write them all to a zip file (stored in memory).

    Items is an array of dictionaries:
    [{
        "timestamp": datetime.datetime(),
        "bytes": BytesIO object,
        "name": file name to use
    }, ...]

    Returns a BytesIO object containing zipped data.
    """

    zip = io.BytesIO()
    with zipfile.ZipFile(zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for item in items:
            info = zipfile.ZipInfo(item['name'], item['timestamp'])
            item['bytes'].seek(0)
            zf.writestr(info, item['bytes'].read(), compress_type=compress_type)

    zip.seek(0)
    return zip


def geometries_to_shp_zip(base_name, geom_attrs):
    """Produce a zip file containing shp, shx, and dbf files.
    base_name is the base name for the shape files.

    Geometries and attributes are provided as a list of tuples in geom_attrs:
    geom_attrs = ((geom1, geom1_attrs), (geom2, geom2_attrs), ...)

    Geometries are a tuple of points (currently) assumed to be a polygon.
    Data can be generated via geodjango GEOSGeometry.tuple()

    Attributes is a dictionary of {field_name: value}
    Field type is determined based on content.
    bool -> L, logical
    str -> C, character
    int -> N, number with 0 decimal places
    float -> N, number with 4 decimal places
    datetime -> D, YYYYMMDD date stamp

    field_names and types are determined by the first attribute dictionary,
    i.e., names from from geom_attrs[0][1].keys(), and types come from examining
    geom_attrs[0][1].values()
    """
    shp_bytes = io.BytesIO()
    shx_bytes = io.BytesIO()
    dbf_bytes = io.BytesIO()

    writer = shapefile.Writer()

    field_data = geom_attrs[0][1]
    type_map = {
        bool: {"fieldType": "L", "size": "1"},
        str: {"fieldType": "C"},
        int: {"fieldType": "N", "size": "18", "decimal": 0},
        float: {"fieldType": "N", "size": "18", "decimal": 4},
        datetime: {"fieldType": "D", "size": 8},
    }
    type_map[unicode] = type_map[str]
    for name, field_type in field_data.iteritems():
        args = type_map[type(field_type)]
        args['name'] = name
        writer.field(**args)

    field_transform = {
        bool: lambda s: ['F', 'T'][s],
        str: lambda s: s,
        int: lambda s: str(s),
        float: lambda s: '%.4f' % s,
        datetime: lambda s: s.strftime('%Y%m%d'),
    }
    field_transform[unicode] = field_transform[str]

    for geometry, attrs in geom_attrs:
        writer.poly(parts=geometry)
        transformed_attrs = dict((k, field_transform[type(v)](v))
                                 for k, v in attrs.iteritems())
        writer.record(**transformed_attrs)

    writer.saveShp(shp_bytes)
    writer.saveShx(shx_bytes)
    writer.saveDbf(dbf_bytes)

    shp_bytes.seek(0)
    shx_bytes.seek(0)
    dbf_bytes.seek(0)

    now = datetime.datetime.now().timetuple()

    items = [
        {'name': '%s.shp' % base_name, 'timestamp': now, 'bytes': shp_bytes},
        {'name': '%s.shx' % base_name, 'timestamp': now, 'bytes': shx_bytes},
        {'name': '%s.dbf' % base_name, 'timestamp': now, 'bytes': dbf_bytes},
    ]
    zip = zip_objects(items)

    out = os.environ['TMPDIR']
    out = os.path.join(out, 'shape.zip')
    with open(out, 'wb') as f:
        f.write(zip.read())


class Command(NoArgsCommand):
    help = ("Test thingy for exporting.")

    def handle_noargs(self, **options):
        drawings = AOI.objects.filter()
        sys.stdout.write("Exporting %s" % drawings)
        # drawings_to_shp(drawings)
        geom_attrs = []
        for d in drawings:
            geom = d.geometry_final.tuple
            attrs = {'AREA': d.geometry_final.area, 'DESC': d.description}
            geom_attrs.append([geom, attrs])

        geometries_to_shp_zip('test_shape', geom_attrs)
