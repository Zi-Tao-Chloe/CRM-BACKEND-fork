from django.shortcuts import render
# Allow other domains to access our API methods
from django.views.decorators.csrf import csrf_exempt
# To Parse the incoming data into data model
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from .serializers import ContactSerializer
from .models import Contact
from .models import User
from django.contrib.auth.decorators import login_required


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
    


class ContactListView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        contacts = Contact.objects.filter(belong_to_user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            # Check if the contact is a user
            try:
                user = User.objects.get(email=serializer.validated_data['email'])  # Assuming 'email' is the field in Contact model
                # Set the is_user field in validated_data
                serializer.validated_data['is_user'] = user
                # Synchronize user profile to contact info
                for field in ['first_name', 'last_name', 'date_of_birth', 'street_address', 'city',
                              'state', 'postcode', 'phone', 'profile_picture']:
                    serializer.validated_data[field] = getattr(user, field)
            except User.DoesNotExist:
                serializer.validated_data['is_user'] = None
            serializer.validated_data['belong_to_user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    


class ContactDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Contact.objects.get(pk=pk)
        except Contact.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        contact = self.get_object(pk)
        if not contact:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContactSerializer(contact)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        contact = self.get_object(pk)
        if not contact:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        contact = self.get_object(pk)
        if not contact:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)

        contact.delete()
        return Response({'message': 'Contact was deleted successfully!'}, status=status.HTTP_204_NO_CONTENT)
