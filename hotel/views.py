from django.shortcuts import render, redirect
from django.contrib.auth.models import auth
from django.contrib import messages
from users.models import CustomUser
from .models import Room, Booking, Hotel, Region
from django.template.defaulttags import register
from .forms import RegionForm, RoomForm ,HotelForm, PersonalForm
from datetime import datetime, date, timedelta
import re

# Settings Imports
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token


# Create your views here.

def index(request):
    return render(request, 'index.html')

def search(request):

    if request.method == 'POST':
        destination = request.POST.get('dest')
        if destination not in list(Region.objects.values_list('name', flat=True)):
            messages.error(request, 'Please Choose Valid Destination ...!')
            return redirect('/')
        check_in =  datetime.strptime(request.POST.get('start'), '%Y-%m-%d').date()
        check_out = datetime.strptime(request.POST.get('end'), '%Y-%m-%d').date()
        region = Region.objects.get(name=destination)

        availble_rooms = {}
        for hotel in Hotel.objects.filter(region = region):
            availble_rooms[hotel.name] = dict()
        # print(list(availble_rooms.keys()))
        for room in Room.objects.all():
            # print(room.hotel.name)
            if room.hotel.name in list(availble_rooms.keys()):
                availble_rooms[room.hotel.name][room.number] = True
        for booking in Booking.objects.all():
            if booking.room.hotel.name in availble_rooms.keys():
                if  (( check_in > booking.check_in and check_in > booking.check_out ) or ( check_out < booking.check_in and check_out < booking.check_out )):
                    pass
                else: availble_rooms[booking.room.hotel.name][booking.room.number] = False
        print(availble_rooms)
        final_available_rooms = {}
        for hotel in availble_rooms:
            # print(hotel)
            # print(type(availble_rooms[hotel]))
            if len(availble_rooms[hotel]) > 0:
                for room in availble_rooms[hotel]:
                    if availble_rooms[hotel][room]:
                        if hotel in final_available_rooms.keys():
                            final_available_rooms[hotel].append(room)
                        else:
                            final_available_rooms[hotel] = list()
                            final_available_rooms[hotel].append(room)
        print(final_available_rooms)
        hotels = []
        for hotel in list(final_available_rooms.keys()):
            hotels.append(Hotel.objects.get(name=hotel))
        context = {
            'hotels' : zip(hotels, list(final_available_rooms.values())),
            # 'rooms': final_available_rooms,
            'check_in':str(check_in),
            'check_out':str(check_out),
            'empty':len(hotels) == 0,
        }
        print(check_in)
        print(str(check_in))
        print(type(check_out))
        return render(request, 'index.html', context)
    return index(request)

def show_hotel_in_duration(request, hotel_id, check_in, check_out, rooms):
    hotel = Hotel.objects.get(id=hotel_id)
    # print(rooms)
    rooms = rooms[1:-1].split(',')
    final_rooms = []
    for i in rooms:
        final_rooms.append(Room.objects.get(hotel=hotel, number=i))
    return render(request, 'hotel.html', {'rooms': final_rooms, 'rooms_count': len(rooms), 'hotel' : hotel, 'check_in': check_in, 'check_out': check_out})

def signup_page(request):
    if request.user.is_authenticated: return redirect('/')
    return render(request, 'signup.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else: 
            messages.info(request, 'Wrong Username or Password')
            return redirect('signup_page')
    else:
        return redirect('signup_page')

def activate_email(request, user, to_email):
    mail_subject =  'Activate your user account.'
    message = render_to_string('email_template.html', {
        'user' : user.username,
        'domain' : get_current_site(request).domain,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : account_activation_token.make_token(user),
        'protocol' : 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on received activation link\
                                    to confirm and complete the registeration. <b>Note:</b> Check your spam foledr.')
    else:
        messages.error(request, f'Problem sending email to <b>{to_email}</b>, check if you typed it correctly.')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        print(type(username))
        print(type(email))
        print(type(password))
        print(type(password2))
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'This username is alredy taken, please choose another one')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'This email is alredy taken, please choose another one')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password, phone=phone)
                user.is_active = False
                user.save()
                activate_email(request, user, email)
                return redirect('/')
            return redirect('/signup_page')

        else:
            messages.info(request, 'The two passwords are not the sane')
        return redirect('/')
    else: return redirect('/')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your confirmation. Please login to enter your account')
        return redirect('/signup')
    else:
        messages.error(request, 'Activation link is invalid.')
        return redirect('/')

# def control_panel(request):
#     if request.user.is_superuser:
#         return render(request, 'control_panel.html')
#     messages.error(request, 'Forbidden Page...!')
#     return redirect('/')

def add_page(request, category, id):
    if request.user.is_superuser:
        match category:
            case 'region':
                form = RegionForm
            case 'hotel':
                form = HotelForm
            case 'room':
                form = RoomForm
            case _:
                return redirect('/')
        return render(request, 'form.html', {"form" : form, 'category': category, 'id': id })
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def add_region(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name')
            if not Region.objects.filter(name=name).exists():
                region = Region.objects.create(name=name)
                region.save()
            else: 
                messages.error(request, 'This Hotel is Alerdy Existed ...!')
        return redirect('/show')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def add_hotel(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.POST.get('image')
            if not Hotel.objects.filter(name=name).exists():
                hotel = Hotel.objects.create(name=name, region=Region.objects.get(id=id), description=description)
                if image != '':
                    hotel.image = '/static/img/' + image
                hotel.save()
            else: 
                messages.error(request, 'This Hotel is Alerdy Existed ...!')
        return redirect(f'/show/{id}')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def add_room(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            hotel = Hotel.objects.get(id=id)
            number = int(request.POST.get('number'))
            capacity = int(request.POST.get('capacity'))

            if not Room.objects.filter(number=number, hotel=hotel).exists():
                room = Room.objects.create(number=number, hotel=hotel, capacity=capacity)
                room.save()
            else: 
                messages.error(request, 'This Room is Alerdy Existed ...!')
        return redirect(f'/show/{hotel.region.id}/{hotel.id}')
    return redirect('/')

def edit_page(request, category, item_id):
    if request.user.is_superuser:
        match category:
            case 'region':
                form = RegionForm(instance=Region.objects.get(id=item_id))
            case 'hotel':
                form = HotelForm(instance=Hotel.objects.get(id=item_id))
            case 'room':
                form = RoomForm(instance=Room.objects.get(id=item_id))
            case _:
                return redirect('/')
        context = {
            "form" : form,
            'category': category,
            # 'category_id': category_id,
            'item_id':item_id
        }
        return render(request, 'form_edit.html', context)
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def edit_region(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name')
            if not Region.objects.filter(id=id).exists():
                messages.error(request, 'This Region is not Existed to be Edit ...!')
            else:
                if not Region.objects.filter(name=name).exists():
                    region = Region.objects.get(id=id)
                    region.name = name
                    region.save()
                    messages.success(request, 'The Region is Succesfuly Edited.')
                else: messages.error(request, 'This is Region is Already Existed')

        return redirect('/show')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def edit_hotel(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            name = request.POST.get('name')
            description = request.POST.get('description')
            image = request.POST.get('image')
            if not Hotel.objects.filter(id=id).exists():
                messages.error(request, 'This Hotel is not Existed to be Edit ...!')
            else:
                hotel = Hotel.objects.get(id=id)
                if (not Hotel.objects.filter(name=name, region=hotel.region.id).exists()) or name == hotel.name:
                    hotel.name = name
                    hotel.description = description
                    if image != '':
                        hotel.image = '/static/img/' + image
                    hotel.save()
                    messages.success(request, 'The Hotel Scuccesfuly edited')
                else: messages.error(request, 'There are the Same Hotel Name in this Region ...!')
        return redirect(f'/show/{hotel.region.id}')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def edit_room(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            number = int(request.POST.get('number'))
            capacity = int(request.POST.get('capacity'))

            if not Room.objects.filter(id=id).exists():
                messages.error(request, 'This Room is not Existed to be Edit ...!')
            else:
                room = Room.objects.get(id=id)
                if (not Room.objects.filter(number=number, hotel=room.hotel).exists()) or room.number == number :
                    room.number = number
                    room.capacity = capacity
                    room.save()
                else: messages.error(request, 'This Room is Already Existed in this Hotel ...!')
        return redirect(f'/show/{room.hotel.region.id}/{room.hotel.id}')
    return redirect('/')

def delete_region(request, id):
    if request.user.is_superuser:
        Region.objects.get(id=id).delete()
        messages.success(request, 'The Region has been Deleted ...!')
        return redirect('/show')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def delete_hotel(request, id):
    if request.user.is_superuser:
        url_id = Hotel.objects.get(id=id).region.id
        Hotel.objects.get(id=id).delete()
        return redirect(f'/show/{url_id}')
    messages.error(request, 'Forbidden Page...!')
    return redirect('/')

def delete_room(request, id):
    if request.user.is_superuser:
        if request.method == 'POST':
            number = int(request.POST.get('number'))
            capacity = int(request.POST.get('capacity'))

            if not Room.objects.filter(id=id).exists():
                messages.error(request, 'This Room is not Existed to be Edit ...!')
            else:
                room = Room.objects.get(id=id)
                if (not Room.objects.filter(number=number, hotel=room.hotel).exists()) or room.number == number :
                    room.number = number
                    room.capacity = capacity
                    room.save()
                else: messages.error(request, 'This Room is Already Existed in this Hotel ...!')
        return redirect(f'/show/{room.hotel.region.id}/{room.hotel.id}')
    return redirect('/')

def add_booking(request, id, check_in, check_out):
    if request.user.is_authenticated:
        if check_in.count('-') != 2:
            check_in = change(check_in)
            check_out = change(check_out)
        check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out, '%Y-%m-%d').date()
        if check_out < check_in:
            messages.error(request, 'Invailed duration, Please choose the check in and check out time carefully ...!')
            return redirect('/')
        else:
            room = Room.objects.get(id=id)
            year = datetime.today().date().year
            start_date = check_in
            end_date = check_out

            flg = True
            for book in Booking.objects.filter(room=room):
                if book.check_in < check_in:
                    if book.check_out >= check_in:
                        flg = False; break
                elif book.check_in == check_in:
                    flg = False; break
                else:
                    if book.check_in <= check_out:
                        flg=False
            if flg:
                booking = Booking.objects.create(user=request.user,room=Room.objects.get(id=id), check_in=check_in,check_out=check_out)
                booking.save()
                messages.success(request, 'Your Booking Has Been Added Succsesfuly')
                return redirect('/confirmed')
            else:
                messages.error(request, 'This room is not availble in this duration, please try again ...!')
                return redirect('/')
    else:
        messages.error(request, 'You Need to sign in to Book your Booking ...!')
        return redirect('/')

def change(s):
    l = re.split('. | \  | ,',s)
    d={
        'Jan':1,
        'Feb':2,
        'Marc':3,
        'Apri':4,
        'Ma':5,
        'Jun':6,
        'Jul':7,
        'Aug':8,
        'Sept':9,
        'Oct':10,
        'Nov':11,
        'Dec':12,
    }
    r = f'{l[2]}-{d[l[0]]}-{l[1]}'
    print(s)
    print(l)
    print(r)
    return r

def show_regions(request):
    return render(request, 'show_regions.html', {'regions': Region.objects.all()})

def show_hotels(request, region):
    return render(request, 'show_hotels.html', {'hotels': Hotel.objects.filter(region=Region.objects.get(id=region)), 'region_id': region })

def show_rooms(request, region, hotel):
    return render(request, 'show_rooms.html', {'rooms': Room.objects.filter(hotel=Hotel.objects.get(id=hotel)), 'hotel_id': hotel })

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def show_room(request, region, hotel, room):
    year = datetime.today().date().year
    start_date = date(year, 1, 1)
    end_date = date(year+1, 12, 31)

    l = []
    d = {}
    for i,single_date in enumerate(daterange(start_date, end_date)):
        d[single_date] = i
        l.append(0)
    l.append(0)
    for book in Booking.objects.filter(room=Room.objects.get(id=room)):
        l[d[book.check_in]]+=1
        l[d[book.check_out]+1]-=1
    for i in range(1,len(l)):
        l[i] += l[i-1]
    for i in range(len(l)):
        l[i] = not bool(l[i])
    for i,x in enumerate(daterange(start_date, datetime.today().date())):
        l[i] = False
    print(d)
    print(l)
    return render(request, 'show_room.html', {'dates': zip(d.keys(), l), 'room_id' : room})

def confirmed(request):
    if request.user.is_authenticated: return render(request, 'confirmed.html', {'bookings': Booking.objects.filter(user=request.user)})
    messages.error(request, 'forbidden Page...!')
    return redirect('/')















@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)