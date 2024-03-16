from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from job.api.serializers import JobSerializer, ClientSerializer
from job.models import Job
from user.models import Profile


class JobsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        jobs = Job.objects.all()
        data = []
        for job in jobs:
            data.append(JobSerializer(job).data)
        return Response(status=status.HTTP_200_OK, data=data)

class ClientsView(APIView):

    def get(self, request, queryset=None, **kwargs):
        clients = Profile.objects.all()
        data = []
        for client in clients:
            data.append(ClientSerializer(client).data)
        return Response(status=status.HTTP_200_OK, data=data)

class JobView(APIView):

    def get(self, request, queryset=None, **kwargs):
        job_id = self.kwargs.get('pk')
        if Job.objects.filter(id=job_id).exists():
            job = Job.objects.get(id=job_id)
            data = JobSerializer(job).data
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Job not found.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)

class ClientView(APIView):

    def get(self, request, queryset=None, **kwargs):
        client_id = self.kwargs.get('pk') 
        client = Profile.objects.get(id=client_id)
        data = ClientSerializer(client).data
        return Response(status=status.HTTP_200_OK, data=data)
