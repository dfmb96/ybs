import json

from django.test import Client
from django.test import TestCase

from YBS.core.models import DataSet, Citizen

from YBS.core.tests.test_post import CORRECT_DATASET

WRONG_DATA = [
]

ERROR_CODE = 400
CORRECT_CODE = 200


class TestPatch(TestCase):

    def setUp(self):
        c = Client()
        c.post('/imports', data=CORRECT_DATASET, content_type='application/json')

    def test_wrong_c_id(self):
        c = Client()
        id = DataSet.objects.all().count()
        response = c.patch('/imports/{}/citizens/{}'.format(id, 100), data=json.dumps({}), content_type='application/json')
        self.assertEqual(response.status_code, ERROR_CODE)
