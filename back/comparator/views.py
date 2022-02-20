from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from comparator.services import load_image


@method_decorator(csrf_exempt, name='dispatch')
class recognize(View):
    def post(self, request):
        image = request.FILES.get('file_object')
        res = load_image(image)
        return JsonResponse(res, status=200, safe=False)