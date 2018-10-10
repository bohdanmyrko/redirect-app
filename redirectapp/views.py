from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests, json


@csrf_exempt
def prices(request):
    if request.method == 'POST':
        print(request.POST['url'])
        response = requests.get(
            request.POST['url'], verify=False,
            stream=True)
        return HttpResponse(response.raw.read().decode('cp1251').encode('utf-8'))
        #return HttpResponse(json.dumps({space : response}))


@csrf_exempt
def clients(request):
    if request.method == 'POST':
        print(request.POST['url'])
        response = requests.get(
            request.POST['url'], verify=False,
            stream=True)
        return HttpResponse(response.raw.read())


@csrf_exempt
def bills(request):
    if request.method == 'POST':
        print(request.POST)
        try:
            response = requests.post(
                request.POST['url'],data={'BODY':request.POST['body']}, verify=False,
                stream=True)
        except Exception as e:
            print(e)
        s = response.raw.read()
        print(s.decode('utf-8'))
        return HttpResponse(s)
            #.decode('cp1251').encode('utf-8'))
