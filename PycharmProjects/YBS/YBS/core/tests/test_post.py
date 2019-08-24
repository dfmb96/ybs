import json

from django.test import Client
from django.test import TestCase

from YBS.core.models import DataSet, Citizen

CORRECT_DATASET = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Moscow',
            'street': 'Street1',
            'building': '1',
            'appartement': 100,
            'name': 'Name',
            'birth_date': '09.09.2000',
            'gender': 'male',
            'relatives': [2, 3],
        },
        {
            'citizen_id': 2,
            'town': 'SPb',
            'street': 'Street2',
            'building': '13a',
            'appartement': 734,
            'name': 'Name1',
            'birth_date': '21.05.1966',
            'gender': 'female',
            'relatives': [1, 3],
        },
        {
            'citizen_id': 3,
            'town': 'Moscow',
            'street': 'Street3',
            'building': '219',
            'appartement': 8,
            'name': 'Name2',
            'birth_date': '21.08.1991',
            'gender': 'male',
            'relatives': [1, 2],
        },
    ]
})

WRONG_FIELDS = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'street': 'Street1',
            'building': '1',
            'appartement': 100,
            'name': 'Name',
            'birth_date': '09.09.2000',
            'gender': 'male',
            'relatives': [],
        },
    ]
})

WRONG_DATE_FORMAT = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Moscow',
            'street': 'Street1',
            'building': '1',
            'appartement': 100,
            'name': 'Name',
            'birth_date': '9.9.2000',
            'gender': 'male',
            'relatives': [],
        },
    ]
})

WRONG_DATE = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Moscow',
            'street': 'Street1',
            'building': '1',
            'appartement': 100,
            'name': 'Name',
            'birth_date': '29.02.2001',
            'gender': 'male',
            'relatives': [],
        },
    ]
})

NULL_DATA = json.dumps({
    'citizens': [
        {
            'citizen_id': 10,
            'town': 'Moscow',
            'street': 'Street1',
            'building': None,
            'appartement': 100,
            'name': 'Name',
            'birth_date': '21.09.2010',
            'gender': 'male',
            'relatives': [],
        },
    ]
})

NEGATIVE_INTEGER_FIELD = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Moscow',
            'street': 'Street1',
            'building': '1',
            'appartement': -1,
            'name': 'Name',
            'birth_date': '28.02.2001',
            'gender': 'male',
            'relatives': [],
        },
    ]
})

WRONG_RELATIVES = json.dumps({
    'citizens': [
        {
            'citizen_id': 1,
            'town': 'Moscow',
            'street': 'Street1',
            'building': '1',
            'appartement': 100,
            'name': 'Name',
            'birth_date': '09.09.2000',
            'gender': 'male',
            'relatives': [2, 3],
        },
        {
            'citizen_id': 2,
            'town': 'SPb',
            'street': 'Street2',
            'building': '13a',
            'appartement': 734,
            'name': 'Name1',
            'birth_date': '21.05.1966',
            'gender': 'female',
            'relatives': [1, 3],
        },
        {
            'citizen_id': 3,
            'town': 'Moscow',
            'street': 'Street3',
            'building': '219',
            'appartement': 8,
            'name': 'Name2',
            'birth_date': '21.08.1991',
            'gender': 'male',
            'relatives': [1],
        },
    ]
})

WRONG_DATA = [
    WRONG_FIELDS,
    WRONG_DATE_FORMAT,
    WRONG_DATE,
    NULL_DATA,
    NEGATIVE_INTEGER_FIELD,
    WRONG_RELATIVES,
]

ERROR_CODE = 400
CORRECT_CODE = 201


class TestPost(TestCase):

    def test_wrong_request_method(self):
        c = Client()
        response = c.get('/imports')
        self.assertEqual(response.status_code, ERROR_CODE)

    def test_wrong_data(self):
        c = Client()
        for data in WRONG_DATA:
            response = c.post('/imports', data=data, content_type='application/json')
            self.assertEqual(response.status_code, ERROR_CODE)

    def test_ok(self):
        c = Client()
        response = c.post('/imports', data=CORRECT_DATASET, content_type='application/json')
        self.assertEqual(response.status_code, CORRECT_CODE)

        ds_id = json.loads(response.content)['data']['import_id']
        self.assertEqual(DataSet.objects.filter(pk=ds_id).count(), 1)
        self.assertEqual(Citizen.objects.filter(dataset_id=ds_id).count(), 3)
