from django.db import models
from users.models import CustomUser

# Create your models here.

class Region(models.Model):
    name = models.CharField(max_length=500)
    def __str__(self):
        return f'{self.name}'

class Hotel(models.Model):
    name = models.CharField(max_length=100000)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000000)
    image = models.ImageField(upload_to='static/img' , default='static/img/hotel.jpeg')
    def __str__(self):
        return f'{self.name} hotel in {self.region}'

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    number = models.IntegerField()
    capacity = models.IntegerField()
    def __str__(self):
        return f'room {self.number} in {self.hotel} '

class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    def __str__(self):
        return f'{self.user} has booked {self.room} from {self.check_in} to {self.check_out}'