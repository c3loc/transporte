from transporte import transporte
from transporte.models import *
from datetime import date, time
from random import randint, choice
import string

roles = ['helpdesk', 'user']

user = User.query.filter(User.login == 'test@psy.rocks').first()
if user is None:
    user = User(login='test@psy.rocks', role='admin')
    db.session.add(user)
    db.session.commit()

users = User.query.all()

while len(users) < 4:
    user = User(
        login='{}@test.psy.rocks'.format(''.join([choice(string.ascii_lowercase) for _ in range(5)]), role='admin'))
    db.session.add(user)
    db.session.commit()
    users.append(user)

organizers = ['CCCV', 'NOC', 'BOC', 'foobar']
addresses = ['CCCV GmbH (Lager Berlin)\nHolzhauser Straße 139\n13509 Berlin', 'Messe Leipzig\nHalle 4',
             'CCCV GmbH (Lager Leipzig)\nDiezmannstraße 20\n04207 Leipzig', 'Getränkelieferant Hamburg']
vehicles = ['car', 'trailer', 'transporter', '7.5t', '18t', '40t']
owner = ['Spedition XYZ', 'CCCV', 'Sixt', 'private']
persons = ['Fahrer XYZ, 0123456789', 'cpunkt, kennste', 'LOC', 'Nick Fahrer']
goods = ['Congress is coming, LOC Crew needs to be shipped! Defrosting initialized! Cryo capsules in wake up mode.',
         'Beverages', 'Popcorn', 'Merch', 'Everything!',
         '* Gitterboxen\r\n* Bauzaun\r\n* lauter brandschutzrelevanter Kram']
comments = ['What a greate comment!\nMultiline!\nGreat line!\n\nGreat!', 'Whoooohooo', 'Yipp yipp yipp',
            '<script>alert(1);</script>']

foo = Transport(user_id=choice(users).id, organizer=choice(organizers), needs_organization=randint(0, 1),
                origin=choice(addresses),
                destination=choice(addresses),
                date=date(year=date.today().year, month=date.today().month, day=date.today().day),
                time=time(hour=randint(0, 23),
                          minute=randint(0, 59)), vehicle=choice(vehicles),
                goods=choice(goods),
                vehicle_owner=choice(owner),
                driver_contact=choice(persons), orga_contact=choice(persons),
                comment=choice(comments))
db.session.add(foo)
db.session.commit()


for _ in range(10):
    foo = Transport(user_id=choice(users).id, organizer=choice(organizers), needs_organization=randint(0, 1),
                    origin=choice(addresses),
                    destination=choice(addresses),
                    date=date(year=2018, month=randint(date.today().month - 1, 12), day=randint(15, 26)),
                    time=time(hour=randint(0, 23),
                              minute=randint(0, 59)), vehicle=choice(vehicles),
                    goods=choice(goods),
                    vehicle_owner=choice(owner),
                    driver_contact=choice(persons), orga_contact=choice(persons),
                    comment=choice(comments))
    db.session.add(foo)
    db.session.commit()
