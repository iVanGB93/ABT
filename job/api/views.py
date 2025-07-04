from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser

from job.api.serializers import JobSerializer, InvoiceSerializer, SpentSerializer, ChargeSerializer
from job.models import Job, Spent, Invoice, Charge
from item.models import Item_List, Item
from user.models import Profile
from client.models import Client


class JobsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        provider_user = User.objects.get(username=provider)
        jobs = Job.objects.filter(provider=provider_user)
        data = []
        for job in jobs:
            data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)

class JobView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        job_id = self.kwargs.get('pk')
        if Job.objects.filter(id=job_id).exists():
            job = Job.objects.get(id=job_id)
            data = JobSerializer(job).data
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Job not found.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
        
    def post(self, request, queryset=None, **kwargs):
        provider = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        response = {'OK': False}
        if action == 'close':
            if Job.objects.filter(id=provider).exists():
                job = Job.objects.get(id=provider)
                job.closed = True
                job.status = 'finished'
                job.save()
                response['message'] = "Job Closed."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Job not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Job.objects.filter(id=provider).exists():
                job = Job.objects.get(id=provider)
                job.delete()
                response['message'] = "Job Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Job not found."
                return Response(status=status.HTTP_200_OK, data=response)
        provider_user = User.objects.get(username=provider)
        if action == 'new':
            data = request.data
            name = data['name']
            if not Client.objects.filter(name=name).exists():
                response['message'] = "Client does not exits."
                return Response(status=status.HTTP_200_OK, data=response)
            client = Client.objects.get(name=name)
            new_job = Job(client=client, provider=provider_user, description=data['description'], address=data['address'], price=data['price'])
            new_job.save()
            response['message'] = "New job created."
            response['OK'] = True
        if action == 'update':
            data = request.data
            if Job.objects.filter(id=data['id']).exists():
                job = Job.objects.get(id=data['id'])
                job.description = data.get('description', job.description)
                job.price = data.get('price', job.price)
                job.address = data.get('address', job.address)
                job.image = data.get('image', job.image)
                job.save()
                response['message'] = "Job Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Job not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)

class SpentView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        if pk == 'all':
            spent_list = Spent.objects.all()
            data = []
            for item in spent_list:
                data.append(SpentSerializer(item).data)
        else:
            job = Job.objects.get(id=pk)
            spents = job.spent.all()
            data = []
            for spent in spents:
                data.append(SpentSerializer(spent).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        print("SPENT DATA", pk, data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            job = Job.objects.get(id=data['job_id'])
            new_spent = Spent(job=job, description=data['description'], amount=data['amount'])
            if data['use_item'] == 'true':
                item_list = Item_List.objects.get(name=data['description'])
                item = Item(list=item_list, job=job, name=item_list.name, description=item_list.description, price=item_list.price)
                item.image = data.get('image', item_list.image)
                new_spent.image = data.get('image', item.image)
                item.save()
                item_list.amount = item_list.amount - 1
                item_list.save()
            else:
                new_spent.image = data.get('image', new_spent.image)
            new_spent.save()
            job.status = 'active'
            job.save()
            response['message'] = "New Spent created."
            response['OK'] = True
        if action == 'update':
            if Spent.objects.filter(id=pk).exists():
                spent = Spent.objects.get(id=pk)
                spent.description = data.get('description', spent.description)
                spent.amount = data.get('price', spent.amount)
                spent.image = data.get('image', spent.image)
                spent.save()
                response['message'] = "Spent Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Spent not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Spent.objects.filter(id=pk).exists():
                spent = Spent.objects.get(id=pk)
                spent.delete()
                response['message'] = "Spent Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Spent not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)

class InvoiceView(APIView):

    def get(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        if Invoice.objects.filter(job_id=pk).exists():
            invoice = Invoice.objects.get(job_id=pk)
            provider = str(invoice.job.provider.pk).zfill(3)[:3]
            last_invoice = Invoice.objects.filter(number__startswith='2').order_by('-number').first()
            print(provider, last_invoice)
            data = {"invoice": InvoiceSerializer(invoice).data}
            charges = Charge.objects.filter(invoice=invoice)
            charges_list = []
            for charge in charges:
                charge_data = ChargeSerializer(charge).data
                charges_list.append(charge_data)
            data['charges'] = charges_list
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Invoice not created yet.'}
            return Response(status=status.HTTP_202_ACCEPTED, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        job = Job.objects.get(id=pk)
        due = int(data['price']) - int(data['paid'])
        invoice = Invoice(job=job, bill_to=job.client, total=data['price'], paid=data['paid'], due=due)
        invoice.save()
        charges = data['charges']
        if charges:
            charges_list = []
            for charge in charges:
                new_charge = Charge(invoice=invoice, description=charge['description'], amount=charge['amount'])
                new_charge.save()
                charge_data = ChargeSerializer(new_charge).data
                charges_list.append(charge_data)
        data = {"invoice": InvoiceSerializer(invoice).data}
        data['charges'] = charges_list
        return Response(status=status.HTTP_200_OK, data=data)

    def put(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        job = Job.objects.get(id=pk)
        invoice = Invoice.objects.get(job=job)
        due = int(data['price']) - int(data['paid'])
        invoice.total=data['price']
        invoice.paid = data['paid']
        invoice.due = due
        charges = data['charges']
        if charges:
            actual_charges = invoice.charges.all()
            for c in actual_charges:
                c.delete()
            charges_list = []
            for charge in charges:
                new_charge = Charge(invoice=invoice, description=charge['description'], amount=charge['amount'])
                new_charge.save()
                charge_data = ChargeSerializer(new_charge).data
                charges_list.append(charge_data)
        invoice.save()
        data = {"invoice": InvoiceSerializer(invoice).data}
        data['charges'] = charges_list
        return Response(status=status.HTTP_200_OK, data=data)

class ChargeView(APIView):

    def get(self, request, queryset=None, **kwargs):
        print("!")
        pk = self.kwargs.get('pk')
        if Invoice.objects.filter(id=pk).exists():
            invoice = Invoice.objects.get(id=pk)
            charges = Charge.objects.filter(invoice=invoice)
            data = []
            for charge in charges:
                charge_data = ChargeSerializer(charge).data
                data.append(charge_data)
            print("DATA", data)
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Invoice not created yet.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
    