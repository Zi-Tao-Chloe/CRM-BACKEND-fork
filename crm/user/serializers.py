from rest_framework import serializers
from .models import User
from django.core.files.base import ContentFile
import base64
import six
import uuid

class Base64ImageField(serializers.ImageField):
    """
    A Django Rest Framework Field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.
    """

    def to_internal_value(self, data):
        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class UserSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True, required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'date_of_birth', 'street_address',
            'city', 'state', 'postcode', 'email', 'phone', 'profile_picture'
        ]
        extra_kwargs = {
            'user_password': {'write_only': True}
        }

    def create(self, validated_data):
        # Override the create method to handle user_password hashing
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            date_of_birth=validated_data.get('date_of_birth'),
            street_address=validated_data.get('street_address'),
            city=validated_data.get('city'),
            state=validated_data.get('state'),
            postcode=validated_data.get('postcode'),
            phone=validated_data.get('phone'),
            profile_picture=validated_data.get('profile_picture')
        )
        user.set_password(validated_data['user_password'])
        user.save()
        return user