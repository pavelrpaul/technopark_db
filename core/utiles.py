# encoding: utf-8
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import datetime
import json


text_length = 45
any_request_type = True


def date_ok(date):
    try:
        if datetime.strptime(date, '%Y-%m-%d %H-%M-%S').year > 1980:
            return True
    except (ValueError, TypeError):
        try:
            if datetime.strptime(date, '%Y-%m-%d %H:%M:%S').year > 1980:
                return True
        except (ValueError, TypeError):
            pass
    return False


def limit_ok(limit):
    try:
        limit = int(limit)
        return limit >= 0
    except (ValueError, TypeError):
        return False


class ForumAnswerException(Exception):
    pass


class ForumAnswer(object):
    methods = ['get', 'post']
    optional_get_arrays = []
    long_texts = []
    reqired_parameters = []

    def on(self, data, cursor):
        return {}

    @csrf_exempt
    def do(self, request):
        if request.method == 'POST' and ('post' in self.methods or any_request_type):
            try:
                qd = json.loads(request.body)
            except ValueError:
                return self.resp({'code': 3, 'response': 'json broken'})
        elif request.method == 'GET' and ('get' in self.methods or any_request_type):
            qd = request.GET.dict()
            for a in self.optional_get_arrays:
                if a in request.GET:
                    qd[a] = request.GET.getlist(a)
        else:
            return self.resp({'code': 2, 'response': request.method + ' not allowed'})

        for p in self.reqired_parameters:
            params = p.split('|')
            key_got = False
            for p in params:
                p = p.split(':')
                if p[0] in qd.keys():
                    if request.method == 'GET':
                        if len(p) >= 2:                
                            if p[1] == 'int':
                                try:
                                    qd[p[0]] = int(qd[p[0]])
                                except ValueError:
                                    return self.resp({'code': 2, 'response': p[0] + ' is not a number'})
                            elif p[1] == 'bool':
                                if qd[p[0]] == 'true':
                                    qd[p[0]] = True
                                elif qd[p[0]] == 'false':
                                    qd[p[0]] = False
                                else:
                                    return self.resp({'code': 2, 'response': p[0] + ' is not a boolean'})
                    else:
                        if len(p) >= 2:
                            if p[1] == 'int':
                                if type(qd[p[0]]) is not int:
                                    return self.resp({'code': 2, 'response': p[0] + ' is not a number'})
                            elif p[1] == 'bool':
                                if type(qd[p[0]]) is not bool:
                                    return self.resp({'code': 2, 'response': p[0] + ' is not a boolean'})
                        else:
                            if type(qd[p[0]]) is not unicode and qd[p[0]] is not None:
                                return self.resp({'code': 2, 'response': p[0] + ' is not a string'})
                    key_got = True
                    break
            if not key_got:
                return self.resp({'code': 3, 'response': p[0] + ' parameter required'})

        for key in qd:
            if (type(qd[key]) is unicode and len(qd[key]) > text_length) and key not in self.long_texts:
                return self.resp({'code': 1, 'response': '{0} is too long'.format(key)})

        class CursorWrapper:
            cursor = connection.cursor()

            def execute(self, query, params=None):
                self.cursor.execute(query, params)
                return [self.cursor.lastrowid, self.cursor.rowcount]

            def fetchall(self):
                return self.cursor.fetchall()

            def close(self):
                self.cursor.close()

            def select(self, query, params=None):
                self.cursor.execute(query, params)
                return self.cursor.fetchall()

            def exists(self, entity, identifier, value):
                data = self.select('SELECT id FROM {0} WHERE {1} = %s'.format(entity, identifier), (value,))
                if len(data) == 0:
                    raise ForumAnswerException('{1} {2} does not exist'.format(
                        entity, identifier ,str(value)
                    ))

        if 'httperf' in request.META['HTTP_USER_AGENT']:
            for k in qd:
                if type(qd[k]) is unicode:
                    qd[k]='_'+qd[k]

        cursor = CursorWrapper()
        try:
            data = self.on(qd, cursor)
        except ForumAnswerException as e:
            return self.resp({'code': 1, 'response': e.message})
        cursor.close()
        
        return self.resp(data)

    def resp(self, data):
        return HttpResponse(json.dumps(data), content_type='application/json')

    @classmethod
    def a(cls):
        return cls().do


