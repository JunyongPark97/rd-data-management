from django.db import models
from layout.models import RawImage, LayoutEquationBox, LayoutBox
from django.contrib.auth.models import User, AbstractUser
from text.models import TextWordEquationImage, TextWordBox
# Create your models here.


PRECISION = 4
THRESHOLD = 0.1 ** PRECISION
CANDIDATES_COUNT = 100

class EquationImageTestset(models.Model): #LayoutImage가 여러 줄 인 경우 잘라서 여기에 저장해서 사용. 만약 한줄이도 잘라서 저장, wordbox에서 나온 수식은 그냥 바로 사용
    orig_image = models.ForeignKey(LayoutEquationBox, related_name='testsets', on_delete=models.CASCADE)
    image = models.ImageField()
    mathpix_latex = models.CharField(max_length=500, blank=True)
    latex = models.CharField(max_length=500, blank=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)
    valid = models.NullBooleanField(default=None)

# 애초에 이미지를 clone 을 해 올까?


class EquationDetailBox(models.Model):
    """
    Character 정보를 저장하는 box.
    """
    testset = models.ForeignKey(EquationImageTestset, related_name='boxes', on_delete=models.CASCADE)
    left = models.DecimalField(max_digits=PRECISION+1, decimal_places=PRECISION)
    top = models.DecimalField(max_digits=PRECISION+1, decimal_places=PRECISION)
    right = models.DecimalField(max_digits=PRECISION+1, decimal_places=PRECISION)
    bottom = models.DecimalField(max_digits=PRECISION+1, decimal_places=PRECISION)
    input_text = models.CharField(max_length=200, help_text='Boxing UI에서 입력한 값')
    unicode_value = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    work_user = models.ForeignKey(User, null=True, blank=True, related_name='worked_box', on_delete=models.CASCADE)

