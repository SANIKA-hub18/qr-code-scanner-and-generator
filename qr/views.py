from django.views.generic import TemplateView
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import numpy as np
import cv2  # ✅ Using OpenCV instead of pyzbar
from PIL import Image
from django.http import HttpResponse


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


class QrCodeScan(TemplateView):
    template_name = 'qrscanner.html'

    def post(self, request):
        image = request.POST['image']
        image_data = base64.b64decode(image.split(',')[1])

        img = BytesIO(image_data)
        data = self.qrcodeReader(img)
        if data is False:
            return HttpResponse('No Qr code found! Sorry.')
        return HttpResponse(data)

    def qrcodeReader(self, img):
        # Read the uploaded image with Pillow
        image = Image.open(img).convert('RGB')
        # Convert to NumPy array (OpenCV format)
        np_image = np.array(image)
        # Convert RGB to BGR (as OpenCV uses BGR format)
        bgr_image = cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)
        
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(bgr_image)
        if data:
            return data
        else:
            return False
