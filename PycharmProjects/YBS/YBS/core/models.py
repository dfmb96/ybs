import datetime
import re
from django.db import models


class Citizen(models.Model):
    GENDER = [
        ('male', 'm'),
        ('female', 'f'),
    ]

    citizen_id = models.CharField(primary_key=True, max_length=100)
    town = models.CharField(max_length=256)
    street = models.CharField(max_length=256)
    building = models.CharField(max_length=256)
    appartement = models.IntegerField()
    name = models.CharField(max_length=256)
    birth_date = models.CharField(max_length=10)
    gender = models.CharField(max_length=6, choices=GENDER)
    relatives = models.CharField(max_length=1000)
    dataset = models.ForeignKey('DataSet', on_delete=models.CASCADE)

    @classmethod
    def create(cls, citizen, ds_id):
        # Validating date of birth
        if not re.match(r'^\d\d.\d\d.\d\d\d\d$', citizen['birth_date']):
            raise Exception
        try:
            date = datetime.datetime.strptime(citizen['birth_date'], '%d.%m.%Y').date()
        except Exception:
            raise
        if date >= datetime.datetime.now().date():
            raise Exception

        citizen['citizen_id'] = '{} {}'.format(ds_id, citizen['citizen_id'])
        citizen['relatives'] = ' '.join(list(map(str, citizen['relatives'])))
        citizen['dataset'] = DataSet.objects.filter(pk=ds_id)[0]
        try:
            c_obj = Citizen.objects.create(**citizen)
        except Exception:
            raise
        return c_obj.citizen_id


class DataSet(models.Model):
    id = models.BigIntegerField(primary_key=True)

    @classmethod
    def create(cls, citizens):
        c_id = DataSet.objects.count() + 1
        relatives = {}
        list_of_fields = [f.name for f in Citizen._meta.get_fields()][:-1]

        # Validating fields
        for citizen in citizens:
            for i in list_of_fields:
                if i not in citizen:
                    raise Exception
            if int(citizen['citizen_id']) < 0 or int(citizen['appartement']) < 0:
                raise Exception
            relatives[citizen['citizen_id']] = citizen['relatives']

        # Validating relatives
        for i in relatives:
            for j in relatives[i]:
                if j not in relatives or i not in relatives[j]:
                    raise Exception

        DataSet.objects.create(id=c_id)
        try:
            for citizen in citizens:
                Citizen.create(citizen, c_id)
        except Exception:
            DataSet.objects.filter(id=c_id).delete()
            raise
        return c_id
