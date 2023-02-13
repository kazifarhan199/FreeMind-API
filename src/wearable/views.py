import json

from django.http import HttpResponse
from . import utils


def collect_garmin_daily_data_view(request):
    data = json.loads(request.body)
    utils.save_garmin_daily_data_to_db(data)
    utils.dataToDailies(data)
    return HttpResponse("<h1>Ok<h1>")


def collect_garmin_stress_data_view(request):
    data = json.loads(request.body)
    utils.save_garmin_stress_data_to_db(data)
    return HttpResponse("<h1>Ok<h1>")

def collect_garmin_sleep_data_view(request):
    data = json.loads(request.body)
    utils.save_garmin_sleep_data_to_db(data)
    utils.dataToSleep(data)
    return HttpResponse("<h1>Ok<h1>")
