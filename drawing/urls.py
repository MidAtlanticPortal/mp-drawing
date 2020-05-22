try:
    from django.urls import re_path, include
except (ModuleNotFoundError, ImportError) as e:
    from django.conf.urls import url as re_path, include
from .views import *

urlpatterns = [
    #'',
    #drawings
    re_path(r'^get_drawings$', get_drawings),
    #feature reports
    re_path(r'^wind_report/(\d+)', wind_analysis, name='wind_analysis'), #user requested wind energy site analysis
    re_path(r'^aoi_report/(\d+)', aoi_analysis, name='aoi_analysis'), #user requested area of interest analysis
]
