from django.shortcuts import render
from django.http.response import HttpResponse, JsonResponse
import jwt
from rest_framework.views import APIView
from rest_framework import (mixins, generics, status, permissions)
from rest_framework.response import Response
from .models import *
from .serializers import *
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from .ml import extract_faces
import base64
from django.core.files.base import ContentFile
import cv2

class EvidenceView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EvidenceSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # print(serializer.validated_data['video'])
            Evidence.objects.get_or_create(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
class EvidenceListView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = EvidenceSerializer

    user_id_param = openapi.Parameter(
        'user_id',
        openapi.IN_QUERY,
        description="User ID",
        type=openapi.TYPE_INTEGER,
    )

    location_param = openapi.Parameter(
        'location',
        openapi.IN_QUERY,
        description="Location",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[user_id_param, location_param])
    def get(self, request):
        user_id = request.query_params.get('user_id', None)
        location = request.query_params.get('location', None)

        if user_id and location:
            evidences = Evidence.objects.filter(user_id=user_id, location=location)
            if evidences.count() == 0:
                return JsonResponse({'error': 'No evidences found for this user and location'}, status=status.HTTP_400_BAD_REQUEST)
        elif user_id:
            evidences = Evidence.objects.filter(user_id=user_id)
            if evidences.count() == 0:
                return JsonResponse({'error': 'No evidences found for this user'}, status=status.HTTP_400_BAD_REQUEST)
        elif location:
            evidences = Evidence.objects.filter(location=location)
            if evidences.count() == 0:
                return JsonResponse({'error': 'No evidences found for this location'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({'error': 'Invalid query parameters'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(evidences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SuspectsView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SuspectSerializer

    def post(self, request, evidence_id):
        evidence = Evidence.objects.get(id=evidence_id)
        if not evidence:
            return JsonResponse({'error': 'No evidence found with this id'}, status=status.HTTP_400_BAD_REQUEST)
        suspects = evidence.suspect_set.all()
        if suspects.count() != 0:
            suspect_faces = []
            for suspect in suspects:
                with open(suspect.image.path, 'rb') as f:
                    image_data = f.read()
                    image_data_b64 = base64.b64encode(image_data).decode('utf-8')
                    suspect_faces.append({
                        'url': suspect.image.url,
                        'data': image_data_b64
                    })
            suspect_names = [suspect.name for suspect in suspects]
            return JsonResponse({'suspect_faces': suspect_faces, 'suspect_names': suspect_names}, status=status.HTTP_200_OK)
        faces = extract_faces(evidence.video.path, evidence_id)
        for item in faces:
            # Encode the face image as a JPEG and save it to a ContentFile
            retval, buffer = cv2.imencode('.jpg', item[1])
            image_file = ContentFile(buffer.tobytes(), item[0])
            serializer = self.serializer_class(data={'image': image_file})
            if serializer.is_valid():
                print("Serializer valid")
                serializer.save()
                suspect = Suspect.objects.create(**serializer.validated_data)
                evidence.suspect_set.add(suspect)
            else:
                print(serializer.errors)
        suspects = evidence.suspect_set.all()
        suspect_faces = []
        for suspect in suspects:
            with open(suspect.image.path, 'rb') as f:
                image_data = f.read()
                image_data_b64 = base64.b64encode(image_data).decode('utf-8')
                suspect_faces.append({
                    'url': suspect.image.url,
                    'data': image_data_b64
                })
        suspect_names = [suspect.name for suspect in suspects]
        return JsonResponse({'suspect_faces': suspect_faces, 'suspect_names': suspect_names}, status=status.HTTP_200_OK)