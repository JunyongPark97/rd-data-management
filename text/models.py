from django.db import models
from layout.models import RawImage
from django.contrib.auth.models import User, AbstractUser
# Create your models here.

PRECISION = 4
THRESHOLD = 0.1 ** PRECISION
CANDIDATES_COUNT = 100

class TextLineBox(models.Model):
    raw_image = models.ForeignKey(RawImage, null=True, blank=True, related_name='charboxes', on_delete=models.CASCADE)
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    input_text = models.CharField(max_length=200, null=True, blank=True, help_text='wordbox 에서 입력한 값')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)
    valid = models.NullBooleanField()


class TextWordBox(models.Model):
    raw_image = models.ForeignKey(RawImage, related_name='wordboxes', on_delete=models.CASCADE)
    parent_line_box = models.ForeignKey(TextLineBox, null=True, blank=True, related_name='child-wordboxes', on_delete=models.CASCADE)
    box_type = models.IntegerField(default=0, choices=((0, 'normal'), (1, 'equation')))
    language = models.IntegerField(default=0, choices=((0, 'korean'), (1, 'japanese'), (2, 'english')))
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    input_text = models.CharField(max_length=100, null=True, blank=True, help_text='charbox 에서 입력한 값')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)
    valid = models.NullBooleanField()
    text_valid = models.NullBooleanField()


class TextWordEquationImage(models.Model):#word:box_type = 1 # 외래키를 걸어도 되고, 아니면 box 정보 wordbox 모델에서 저장하고 이미지만 clone 해도 됨
    raw_image = models.ForeignKey(RawImage, related_name='layout-equations', on_delete=models.CASCADE)
    box_info = models.OneToOneField(TextWordBox, related_name='equation-image', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='equation_image')
    mathpix_latex = models.CharField(max_length=500, blank=True)
    latex = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    valid = models.NullBooleanField()


class TextCharBox(models.Model):
    raw_image = models.ForeignKey(RawImage, null=True, blank=True, related_name='charboxes', on_delete=models.CASCADE)
    parent_word_box = models.ForeignKey(TextWordBox, null=True, blank=True, related_name='child-charboxes', on_delete=models.CASCADE)
    left = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION + 1, decimal_places=PRECISION)
    input_text = models.CharField(max_length=50, help_text='Boxing UI에서 입력한 값')
    unicode_value = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)
    valid = models.NullBooleanField()

