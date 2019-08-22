from django.db import models


class Citizen(models.Model):
    GENDER = [
        ('male', 'm'),
        ('female', 'f'),
    ]

    citizen_id = models.CharField(primary_key=True, max_length=1000)
    town = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    appartement = models.IntegerField()
    name = models.CharField(max_length=100)
    birth_date = models.CharField(max_length=100)
    gender = models.CharField(max_length=6, choices=GENDER)
    relatives = models.CharField(max_length=1000)
    dataset = models.ForeignKey('DataSet', on_delete=models.CASCADE)

    @classmethod
    def create(cls, citizen, ds_id):
        citizen['citizen_id'] = '{} {}'.format(ds_id, citizen.get('id'))
        del(citizen['id'])
        citizen['relatives'] = ' '.join(list(map(str, citizen.get('relatives'))))
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
        DataSet.objects.create(id=c_id)
        for citizen in citizens:
            Citizen.create(citizen, c_id)
        return c_id
