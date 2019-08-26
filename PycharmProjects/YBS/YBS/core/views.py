import json
import numpy
from datetime import date

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from YBS.core.models import DataSet, Citizen


def decode_body(request):
    return json.loads(request.body.decode('utf-8'))


@csrf_exempt
def post(request):
    if request.method == 'POST':
        citizens = decode_body(request)
        try:
            ds = DataSet.create(citizens['citizens'])
        except Exception:
            return HttpResponseBadRequest()
        return JsonResponse({'data': {'import_id': ds}}, status=201)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def patch(request, import_id, citizen_id):
    if request.method == 'PATCH':
        c_id = '{} {}'.format(import_id, citizen_id)
        patch_dict = decode_body(request)
        try:
            citizen = Citizen.objects.filter(pk=c_id)
            if len(citizen) != 1:
                return HttpResponseBadRequest()
            if 'relatives' in patch_dict:
                patch_dict['relatives'] = ' '.join(list(map(str, patch_dict['relatives'])))
                old_relatives = citizen[0].relatives.split()
                for relative_id in old_relatives:
                    rel_id = '{} {}'.format(import_id, relative_id)
                    relative = Citizen.objects.filter(pk=rel_id)
                    rel_rels = relative[0].relatives.split()
                    rel_rels.remove(citizen_id)
                    rel_rels = ' '.join(rel_rels)
                    relative.update(relatives=rel_rels)
                new_rels = patch_dict['relatives']
                for relative_id in new_rels:
                    rel_id = '{} {}'.format(import_id, relative_id)
                    relative = Citizen.objects.filter(pk=rel_id)
                    rel_rels = relative[0].relatives.split()
                    rel_rels.append(citizen_id)
                    rel_rels = ' '.join(rel_rels)
                    relative.update(relatives=rel_rels)
            citizen.update(**patch_dict)
        except Exception as e:
            return HttpResponseBadRequest()
        citizen_dict = citizen.values()[0]
        citizen_dict['citizen_id'] = int(citizen_dict['citizen_id'].split()[-1])
        citizen_dict['relatives'] = list(map(int, citizen_dict['relatives'].split()))
        del(citizen_dict['dataset_id'])
        return JsonResponse({'data': citizen_dict}, status=200)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def get_citizens(request, import_id):
    if request.method == 'GET':
        try:
            citizens = Citizen.objects.filter(dataset_id=int(import_id)).values()
        except Exception:
            return HttpResponseBadRequest()
        citizens_list = []
        for citizen in citizens:
            citizen['citizen_id'] = int(citizen['citizen_id'].split()[-1])
            citizen['relatives'] = list(map(int, citizen['relatives'].split()))
            del(citizen['dataset_id'])
            citizens_list.append(citizen)
        return JsonResponse({'data': citizens_list}, status=200)
    else:
        return HttpResponseBadRequest()


@csrf_exempt
def get_presents(request, import_id):
    if request.method == 'GET':
        data = {i: [] for i in range(1, 13)}
        try:
            citizens = Citizen.objects.filter(dataset_id=int(import_id))
        except Exception:
            return HttpResponseBadRequest()
        citizens_dict = {}
        for citizen in citizens:
            inner_id = citizen.citizen_id.split()[-1]
            citizens_dict[inner_id] = int(citizen.birth_date.split('.')[1])
        for citizen in citizens:
            relatives = citizen.relatives.split()
            for relative_id in relatives:
                bday_month = citizens_dict[relative_id]

                def in_data(citizen_id, month):
                    for i in data[month]:
                        if str(i['citizen_id']) == citizen_id:
                            return i
                    return -1

                c_id = citizen.citizen_id.split()[-1]
                index = in_data(c_id, bday_month)
                if index == -1:
                    new_dict = {
                        'citizen_id': int(c_id),
                        'presents': 1,
                    }
                    data[bday_month].append(new_dict)
                else:
                    index['presents'] += 1
        return JsonResponse({'data': data}, status=200)
    else:
        return HttpResponseBadRequest()


def get_age_from_birth_date(citizen):
    today = date.today()
    b_date = list(map(int, citizen.birth_date.split('.')))
    return today.year - b_date[2] - ((today.month, today.day) < (b_date[1], b_date[0]))


def get_percentile(request, import_id):
    if request.method == 'GET':
        try:
            citizens = Citizen.objects.filter(dataset_id=int(import_id))
        except Exception:
            return HttpResponseBadRequest()
        ages_by_towns = {}
        for citizen in citizens:
            town = citizen.town
            if town in ages_by_towns:
                ages_by_towns[town].append(get_age_from_birth_date(citizen))
            else:
                ages_by_towns[town] = [get_age_from_birth_date(citizen)]
        data = []
        for town in ages_by_towns:
            percentiles = numpy.percentile(ages_by_towns[town], [50, 75, 99])
            data.append({
                'town': town,
                'p50': percentiles[0],
                'p75': percentiles[1],
                'p99': percentiles[2],
            })
        return JsonResponse({'data': data}, status=200)
    else:
        return HttpResponseBadRequest()
