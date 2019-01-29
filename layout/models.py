from django.db import models
import random
import string
import json
import logging
from datetime import datetime
from io import BytesIO
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django import template
register = template.Library()

logger = logging.getLogger('test')

PRECISION = 4
THRESHOLD = 0.1 ** PRECISION
CANDIDATES_COUNT = 100

def get_box_filename():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12)) + '.jpg'


def equals(f1, f2):
    return abs(f1 - f2) < THRESHOLD


#회전된 이미지 따로 저장하는 기능 추가 해야 됨.
class RawImage(models.Model):
    image_url = models.URLField()
    ref_text = models.CharField(max_length=50)
    ocrsearchrequest_id = models.IntegerField()
    valid = models.NullBooleanField()

    def get_image_extension(self):
        return 'jpeg'

    @property
    def prev(self):
        return RawImage.objects.filter(pk__lt=self.pk).order_by('pk').last()

    @property
    def next(self):
        return RawImage.objects.filter(pk__gt=self.pk).order_by('pk').first()


class LayoutBox(models.Model):
    raw_image = models.ForeignKey(RawImage, related_name='layout-boxes', on_delete=models.CASCADE)
    box_type = models.IntegerField(choices=((0, '본문'), (1, '보기'), (2, 'Meta정보')))
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)
    valid = models.NullBooleanField()

    def validate_coordinates(self):
        if self.left >= self.right:
            raise Exception('left >= right')
        elif self.top >= self.bottom:
            raise Exception('top >= bottom')
        self.left = 0 if self.left < 0 else self.left
        self.top = 0 if self.top < 0 else self.top
        self.right = 1 if self.right > 1 else self.right
        self.bottom = 1 if self.bottom > 1 else self.bottom

    def save(self, *args, **kwargs):
        self.validate_coordinates()
        super(LayoutBox, self).save(*args, **kwargs)

    def update(self, left, top, right, bottom, **kwargs):
        if not equals(float(self.left), left) or \
                not equals(float(self.top), top) or \
                not equals(float(self.right), right) or \
                not equals(float(self.bottom), bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom
            self.save()


    def __str__(self):
        if self.id:
            return 'B%d' % self.id
        return ''


class LayoutPictureBox(models.Model):#바로 따로 저장
    raw_image = models.ForeignKey(RawImage, related_name='layout-pictures', on_delete=models.CASCADE)
    # box_info = models.OneToOneField(LayoutBox, related_name='picture-image', on_delete=models.CASCADE)
    box_type = models.IntegerField(choices=((4, '그림-도형'), (5, '그림-표'), (6, '그림-그래프')))
    image = models.ImageField(upload_to='picture-image')
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid = models.NullBooleanField()
    # picture_group = models.ForeignKey()

    def validate_coordinates(self):
        if self.left >= self.right:
            raise Exception('left >= right')
        elif self.top >= self.bottom:
            raise Exception('top >= bottom')
        self.left = 0 if self.left < 0 else self.left
        self.top = 0 if self.top < 0 else self.top
        self.right = 1 if self.right > 1 else self.right
        self.bottom = 1 if self.bottom > 1 else self.bottom

    def save(self, *args, **kwargs):
        self.validate_coordinates()
        super(LayoutPictureBox, self).save(*args, **kwargs)

    def update(self, left, top, right, bottom, **kwargs):
        if not equals(float(self.left), left) or \
                not equals(float(self.top), top) or \
                not equals(float(self.right), right) or \
                not equals(float(self.bottom), bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom
            self.save()

    def _save_picture_image(self):
        from PIL import Image
        resp = requests.get(self.raw_image.image_url)
        image = Image.open(BytesIO(resp.content))
        width, height = image.size
        left = width * self.left
        top = height * self.top
        right = width * self.right
        bottom = height * self.bottom
        crop_data = image.crop((int(left), int(top), int(right), int(bottom)))
        # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
        crop_io = BytesIO()
        crop_data.save(crop_io, format=self.raw_image.get_image_extension())
        crop_file = InMemoryUploadedFile(crop_io, None, get_box_filename(), 'image/jpeg', len(crop_io.getvalue()), None)
        self.image.save(get_box_filename(), crop_file, save=False)
        # To avoid recursive save, call super.save
        super(LayoutPictureBox, self).save()

    def __str__(self):
        if self.id:
            return 'B%d' % self.id
        return ''


class LayoutEquationBox(models.Model):#box_type = 3
    raw_image = models.ForeignKey(RawImage, related_name='layout-equations', on_delete=models.CASCADE)
    # box_info = models.OneToOneField(LayoutBox, related_name='equation-image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='equation_image')
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid = models.NullBooleanField()

    def validate_coordinates(self):
        if self.left >= self.right:
            raise Exception('left >= right')
        elif self.top >= self.bottom:
            raise Exception('top >= bottom')
        self.left = 0 if self.left < 0 else self.left
        self.top = 0 if self.top < 0 else self.top
        self.right = 1 if self.right > 1 else self.right
        self.bottom = 1 if self.bottom > 1 else self.bottom

    def save(self, *args, **kwargs):
        self.validate_coordinates()
        super(LayoutEquationBox, self).save(*args, **kwargs)

    def update(self, left, top, right, bottom, **kwargs):
        if not equals(float(self.left), left) or \
                not equals(float(self.top), top) or \
                not equals(float(self.right), right) or \
                not equals(float(self.bottom), bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom
            self.save()

    def _save_equation_image(self):
        from PIL import Image
        resp = requests.get(self.raw_image.image_url)
        image = Image.open(BytesIO(resp.content))
        width, height = image.size
        left = width * self.left
        top = height * self.top
        right = width * self.right
        bottom = height * self.bottom
        crop_data = image.crop((int(left), int(top), int(right), int(bottom)))
        # http://stackoverflow.com/questions/3723220/how-do-you-convert-a-pil-image-to-a-django-file
        crop_io = BytesIO()
        crop_data.save(crop_io, format=self.raw_image.get_image_extension())
        crop_file = InMemoryUploadedFile(crop_io, None, get_box_filename(), 'image/jpeg', len(crop_io.getvalue()), None)
        self.image.save(get_box_filename(), crop_file, save=False)
        # To avoid recursive save, call super.save
        super(LayoutEquationBox, self).save()

    def __str__(self):
        if self.id:
            return 'B%d' % self.id
        return ''
