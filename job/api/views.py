from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.parsers import MultiPartParser, FormParser

from job.api.serializers import JobSerializer, ClientSerializer, ItemListSerializer, ItemSerializer, SpentSerializer
from job.models import Job, Spent
from item.models import Item_List, Item
from user.models import Profile


class JobsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        job_id = self.kwargs.get('pk')
        print('pk', job_id)
        if job_id != 'all':
            client = Profile.objects.get(id=job_id)
            jobs = Job.objects.filter(client=client)
        else:
            jobs = Job.objects.all()
        data = []
        for job in jobs:
            data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)

class ClientsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        clients = Profile.objects.filter(is_client=True)
        data = []
        for client in clients:
            data.append(ClientSerializer(client).data)
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
        pk = self.kwargs.get('pk')
        data = request.data
        print("JOBS DATA", data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            data = request.data
            username = data['name']
            if not User.objects.filter(username=username).exists():
                response['message'] = "Client does not exits."
                return Response(status=status.HTTP_200_OK, data=response)
            user = User.objects.get(username=username)
            new_job = Job(client=user.profile, description=data['description'], address=data['address'], price=data['price'])
            new_job.save()
            response['message'] = "New job created."
            response['OK'] = True
        if action == 'update':
            data = request.data
            if Job.objects.filter(id=pk).exists():
                job = Job.objects.get(id=pk)
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
        if action == 'delete':
            if Job.objects.filter(id=pk).exists():
                job = Job.objects.get(id=pk)
                job.delete()
                response['message'] = "Job Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Job not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'close':
            if Job.objects.filter(id=pk).exists():
                job = Job.objects.get(id=pk)
                job.closed = True
                job.status = 'finished'
                job.save()
                response['message'] = "Job Closed."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Job not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)

class ClientView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        client_id = self.kwargs.get('pk') 
        client = Profile.objects.get(id=client_id)
        data = ClientSerializer(client).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        print("CLIENt DATA", data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            username = data['name']
            email = data['email']
            if User.objects.filter(username=username).exists():
                response['message'] = "Name is already taken."
                return Response(status=status.HTTP_200_OK, data=response)
            new_user = User(username=username, email=email)
            new_user.first_name = username
            new_user.set_password('temporaryPassword')
            new_user.save()
            profile = Profile.objects.get(user=new_user)
            profile.phone = data.get('phone', profile.phone)
            profile.address = data.get('address', profile.address)
            profile.image = data.get('image', profile.image)
            profile.save()
            response['message'] = "New client created."
            response['OK'] = True
        if action == 'update':
            if not data.get('id'):
                response['message'] = "Client id required."
                return Response(status=status.HTTP_200_OK, data=response)
            if Profile.objects.filter(id=pk).exists():
                profile = Profile.objects.get(id=pk)
                profile.phone = data.get('phone', profile.phone)
                profile.address = data.get('address', profile.address)
                profile.image = data.get('image', profile.image)
                profile.save()
                user = profile.user
                user.username = data['name']
                user.first_name = data['name']
                user.email = data.get('email', user.email)
                user.save()
                response['message'] = "Client Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Profile.objects.filter(id=pk).exists():
                profile = Profile.objects.get(id=pk)
                user = profile.user
                user.delete()
                response['message'] = "Client Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Client not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)

class ItemView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        if pk == 'all':
            item_list = Item_List.objects.all()
            data = []
            for item in item_list:
                data.append(ItemListSerializer(item).data)
        else:
            item_list = Item_List.objects.get(id=pk)
            used_items = item_list.item_set.all()
            data = []
            for item in used_items:
                job = item.job
                data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        print("ITEM DATA", data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            new_item_list = Item_List(name=data['name'], amount=data['amount'], price=data['price'])
            new_item_list.description = data.get('description', 'no description added')
            new_item_list.image = data.get('image', new_item_list.image)
            new_item_list.save()
            response['message'] = "New Item created."
            response['OK'] = True
        if action == 'update':
            if Item_List.objects.filter(id=pk).exists():
                item_list = Item_List.objects.get(id=pk)
                item_list.name = data.get('name', item_list.name)
                item_list.description = data.get('description', item_list.description)
                item_list.amount = data.get('amount', item_list.amount)
                item_list.price = data.get('price', item_list.price)
                item_list.image = data.get('image', item_list.image)
                item_list.save()
                response['message'] = "Item Updated."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
                return Response(status=status.HTTP_200_OK, data=response)
        if action == 'delete':
            if Item_List.objects.filter(id=pk).exists():
                item_list = Item_List.objects.get(id=pk)
                item_list.delete()
                response['message'] = "Item Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Item not found."
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
            spents = job.spent_set.all()
            data = []
            for item in spents:
                """ job = item.job """
                data.append(SpentSerializer(item).data)
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        print("LLEGO", request)
        pk = self.kwargs.get('pk')
        data = request.data
        print("SPENT DATA", pk, data)
        action = data['action']
        response = {'OK': False}
        if action == 'new':
            job = Job.objects.get(id=data['job_id'])
            new_spent = Spent(job=job, description=data['description'], amount=data['price'])
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
