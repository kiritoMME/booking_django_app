from django import forms
from .models import Region, Hotel, Room


class RegionForm(forms.ModelForm):
    class Meta:
        model = Region
        fields = '__all__'

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'description', 'image']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'capacity']

class PersonalForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'capacity']