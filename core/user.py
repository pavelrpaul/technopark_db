from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.db import connections
from core.info import db_connection
from core.utils import is_json, createInvalidJsonResponse


def create(request):
	response_data = {}
	if request.method == 'POST':
		query = 'INSERT INTO user (username, about, name, email, isAnonymous) VALUES(?, ?, ?, ?, ?)'

		received_json_data = json.loads(request.body)
		if !is_json(received_json_data):
			return createInvalidJsonResponse(request)
		