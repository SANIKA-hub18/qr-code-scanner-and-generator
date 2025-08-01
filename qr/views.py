from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Muster  # तुमचा model import करा

import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import numpy as np
import cv2
from PIL import Image
import json


class QrCodeView(TemplateView):
    template_name = 'qr.html'

    def get_context_data(self, **kwargs):
        context = super(QrCodeView, self).get_context_data(**kwargs)
        qrcode_img = self.get_qrcode_svg('{}&{}'.format('This is the qrcode data guys.', 'bip-zip'))
        context.update({"qrcode": qrcode_img})
        return context

    def get_qrcode_svg(self, text):
        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(text, image_factory=factory, box_size=30)
        stream = BytesIO()
        img.save(stream)
        base64_image = base64.b64encode(stream.getvalue()).decode()
        return 'data:image/svg+xml;utf8;base64,' + base64_image


@method_decorator(csrf_exempt, name='dispatch')  # CSRF exemption for class based view
class QrCodeScan(View):

    def get(self, request):
        return render(request, 'qrscanner.html')  # तुमचा scanner चा template

    def post(self, request):
        try:
            data_json = json.loads(request.body)  # JSON मध्ये data येईल असं assume
            image_data = data_json.get('image')
            if not image_data:
                return JsonResponse({'status': 'fail', 'message': 'No image found'}, status=400)

            # Base64 image decode करा
            image_bytes = base64.b64decode(image_data.split(',')[1])
            img = BytesIO(image_bytes)

            # QR code वाचा
            qr_text = self.qrcodeReader(img)

            if qr_text:
                # DB मध्ये save करा
                muster_obj = Muster.objects.create(data=qr_text)
                return JsonResponse({'status': 'success', 'data': qr_text, 'id': muster_obj.id})
            else:
                return JsonResponse({'status': 'fail', 'message': 'No QR code detected'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'fail', 'message': f'Exception occurred: {str(e)}'}, status=500)

    def qrcodeReader(self, img):
        try:
            image = Image.open(img).convert('RGB')
            np_image = np.array(image)
            bgr_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(bgr_image)
            return data if data else None
        except Exception as e:
            print("Error in QR decode:", str(e))
            return None
