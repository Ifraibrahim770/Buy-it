from django.shortcuts import redirect
from django.utils.http import *

from .models import *


def Processorder(request):
    transaction_id = datetime.datetime.now().timestamp()
    print(transaction_id)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    order.transaction_id = transaction_id
    order.complete = True
    order.save()
    return redirect('store')