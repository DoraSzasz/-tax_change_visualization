from django.shortcuts import render
from . import TaxChange
# Create your views here.

def index (request):
    context={"div":TaxChange.div, "js":TaxChange.js, "cdn_js":TaxChange.cdn_js, "cdn_css":TaxChange.cdn_css}
    return render(request,'bokehapp/index.html',context)
