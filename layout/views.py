from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import DetailView

from layout.models import RawImage


@method_decorator(login_required, name='dispatch')
class RawImageLayoutDetailView(DetailView):
    model = RawImage