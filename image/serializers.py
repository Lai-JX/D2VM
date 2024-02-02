from rest_framework import serializers
from .models import Image

from datetime import datetime


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
        # fields = ['name', 'image', 'published_date']
    
    
    # def validate(self, attrs):
    #     # print('validate', attrs)
        
    #     # attrs['file'] = attrs['name'] + '-' + attrs['image']

    #     # Check if published_date is not provided, then set it to the current date
    #     # if not attrs.get('published_date'):
    #     #     attrs['published_date'] = datetime.now()

    #     return attrs