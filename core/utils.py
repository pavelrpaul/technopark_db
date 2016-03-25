from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.db import connections

def is_json(myjson):
	try:
		json_object = json.loads(myjson)
	except ValueError, e:
		return False
	return True

def createResponse(code, message):
	response_data = {
		'code': code
		'response': message
	}
	response = JsonResponse(response_data)
	if !is_json(response):
		print 'ERROR encoging JSON'

	return response

def createInvalidJsonResponse(request):
	responseCode = '3'
	errorMessage = 'Invalid json'
	print("Invalid JSON:\turl= %s\tjson= %s", request.path, json.loads(request.body))
	
	return createResponse(responseCode, errorMessage)

def getFromJson(myjson, *args):
	