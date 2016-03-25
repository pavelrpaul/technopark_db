from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import json
from django.db import connections

# Create your views here.
def db_connection():
	db_conn = connections['default']
	return db_conn

def index(request):
	return HttpResponse("Hello, world. You're at the polls index.")

def clear(request):
	response_data = {}
	if request.method == 'POST':
		cursor = db_connection().cursor()
		cursor.execute("DELETE FROM follow")
		# cursor.execute("select * from instaMe_photo")
		row = cursor.fetchall()
	
		cursor.execute("DELETE FROM subscribe")
		row += cursor.fetchall()

		cursor.execute("DELETE FROM post WHERE id > 0")
		row += cursor.fetchall()
	
		cursor.execute("DELETE FROM thread WHERE id > 0")
		row += cursor.fetchall()
		
		cursor.execute("DELETE FROM forum WHERE id > 0")
		row += cursor.fetchall()

		cursor.execute("DELETE FROM user WHERE id > 0")
		row += cursor.fetchall()
		print row
		response_data['code'] = '0'
		response_data['response'] = 'OK'
	else:
		response_data['code'] = '3'
		response_data['response'] = 'error message'
	return JsonResponse(response_data)

def status(request):
	response_data = {}
	if request.method == 'GET':
		cursor = db_connection().cursor()
		cursor.execute("SELECT COUNT(*) count FROM user")
		respUsers = cursor.fetchone()[0]

		cursor.execute("SELECT COUNT(*) count FROM thread")
		respThreads = cursor.fetchone()[0]

		cursor.execute("SELECT COUNT(*) count FROM forum")
		respForums = cursor.fetchone()[0]

		cursor.execute("SELECT COUNT(*) count FROM post")
		respPosts = cursor.fetchone()[0]

		responseCode = '0'
		responseMsg = {
			'user':   respUsers,
			'thread': respThreads,
			'forum':  respForums,
			'post':   respPosts,
		}
		response_data['code'] = responseCode
		response_data['response'] = responseMsg
		# {"code": 0, "response": {"user": 100000, "thread": 1000, "forum": 100, "post": 1000000}}
	return JsonResponse(response_data)