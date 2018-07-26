from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests


@csrf_exempt
def redirect(request):
    if request.method == 'POST':
        print(request.POST['url'])
        response = requests.get(
            'https://online.medservice.kz/viortis/t/service_t.php?city_id=1000&secret=123&type=PRICELIST', verify=False,
            stream=True)
        print(response)
        return HttpResponse(response.raw.read().decode('cp1251').encode('utf-8'))
