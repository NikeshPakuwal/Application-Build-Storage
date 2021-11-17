from rest_framework import serializers
from rest_framework.serializers import Serializer
from abs_app.permissions import IsOwner
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Application, User, Version
from .serializer import ApplicationSerializer, VersionSerializer, UserSerializer
from rest_framework import status, permissions, authentication
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime
from rest_framework.decorators import api_view

from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend


class ApplicationAPI(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.IsAuthenticated, IsOwner)
    
    def get(self, request, pk = None):
        id = pk
        if id is not None:
            app = Application.objects.get(id = id)
            self.check_object_permissions(request, app)
            serializer = ApplicationSerializer(app)
            return Response(serializer.data)
        
        app = Application.objects.filter(created_by = request.user)
        serializer = ApplicationSerializer(app, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by = request.user)
            return Response({'msg':'Data Created Sucessfully!'}, status=status. HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        id = pk
        app = Application.objects.get(pk = id)
        serializer = ApplicationSerializer(app, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data Updated Succesfully!'})
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        id = pk
        app = Application.objects.get(pk=id)
        serializer = ApplicationSerializer(app, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data Updated Sucessfully!'})
        return Response(serializer.errors)

    def delete(self, request, pk):
        if request.method == 'DELETE':
            if request.user.is_admin == True:
                id = pk
                app = Application.objects.get(pk=id)
                app.delete()
                return Response({'msg':'Data Deleted Sucessfully!'})
            else:
                return Response({'msg':'You dont have permission to delete this application!'})



class VersionList(ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['version', 'build_name', 'title']


class VersionAPI(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk = None):
        id = pk
        if id is not None:
            vers = Version.objects.get(id = id)
            serializer = VersionSerializer(vers)
            return Response(serializer.data)
        
        vers = Version.objects.all()
        serializer = VersionSerializer(vers, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        data = request.data.copy()
        token = data.get('application_token')
        token_obj = Application.objects.get(token=token)
        data['application_token'] = token_obj.id
        serializer = VersionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data Created Sucessfully!'}, status=status. HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        id = pk
        vers = Version.objects.get(pk = id)
        serializer = VersionSerializer(vers, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data Updated Succesfully!'})
        return Response(serializer._errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        id = pk
        vers = Version.objects.get(pk=id)
        serializer = VersionSerializer(vers, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':'Data Updated Sucessfully!'})
        return Response(serializer.errors)

    def delete(self, request, pk):
        if request.method == 'DELETE':
            id = pk
            vers = Version.objects.get(pk=id)
            vers.delete()
            return Response({'msg':'Data Deleted Sucessfully!'})


class RegisterAPI(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginAPI(APIView):

    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.filter(username = username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Password Invalid!')
        
        payload = {
            'id' : user.id,
            'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 60),
            'iat' : datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm = 'HS256')

        response = Response()
        
        response.set_cookie(key='jwt', value=token, httponly=True)
        
        response.data = {
            'token' : token
        }
        return response


class UserAPI(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('User not Authenticated!')
        
        try:
            payload = jwt.decode(token, 'secret', algorithm = ['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('User not Authenticated!')
        
        user = User.objects.filter(id = payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class LogoutAPI(APIView):

    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message' : 'Process Successful!'
        }
        return response


@api_view(["GET"])
def report_api(request):
    from .generator import generate_version_pdf, get_version_excel
    params = request.query_params
    type_ = params.get("type")

    version = Version.objects.all()
    serializer = VersionSerializer(version, many=True).data

    if type_ == "pdf" or type_ == "excel":
        scheme = request.META["wsgi.url_scheme"]
        host = request.META["HTTP_HOST"]
        if type_ == "pdf":
            response_ = generate_version_pdf(serializer)
            report_path = f"{scheme}://{host}{response_}"
        elif type_ == "excel":
            response_ = get_version_excel()
            report_path = f"{scheme}://{host}/{response_}"
        return Response({"report": report_path}, status=200)
    return Response(serializer, status=200)