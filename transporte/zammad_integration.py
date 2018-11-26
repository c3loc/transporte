from pprint import pprint
from zammad_py import ZammadAPI
import os
from .transporte import app, db
from .models import User, Transport
from flask_login import current_user
import datetime

def close_ticket(transport_data, reason):
  client = ZammadAPI(username=app.config['ZAMMAD_USER'], password=app.config['ZAMMAD_PASS'], host=app.config['ZAMMAD_HOST'], is_secure=app.config['ZAMMAD_SECURE'])

  messagebody = reason

  if transport_data.time == None:
    transport_data.time = datetime.time()
  ### Set pseudotime if time is not set

  ##
  ## if new helpdesk user is closing a ticket, we need to create the user in the ticket system
  ##
  zammad_user_id = client.user.search({'query': current_user.login})
  if not zammad_user_id:
    pprint('user does not exist')
    client.user.create({'firstname': current_user.login, 'email': current_user.login})
    zammad_user_id = client.user.search({'query': current_user.login})
  
  ticketTemplate = {
    'id': transport_data.ticket_id,
    'title': '[Transport] from: ' + transport_data.location_from + ' to: ' + transport_data.location_to,
    'group_id': '17',
    'owner_id': '270',
    'customer_id': zammad_user_id[0]['id'],
    'state_id': '4',
    'priority_id': '2',
    'article': {'from':
                    '35c3'
                'to' '\"test@psy.rocks\" <test@psy.rocks>',
                'cc': current_user.login,
                'body': messagebody,
                'type_id': 1,
                'sender_id': 1,
                'form_id': '850048713',
                'content_type': 'text/html'},
    'tags': '',
    'pending_time': transport_data.date.isoformat() + transport_data.time.isoformat()+'Z',
    'note': messagebody,
  }

  client.ticket.update(transport_data.ticket_id, ticketTemplate)
  pass


def update_ticket(transport_data):

    
  client = ZammadAPI(username=app.config['ZAMMAD_USER'], password=app.config['ZAMMAD_PASS'], host=app.config['ZAMMAD_HOST'], is_secure=app.config['ZAMMAD_SECURE'])

  if transport_data.time == None:
    transport_data.time = datetime.time()
  ### Set pseudotime if time is not set

  messagebody = (transport_data.organizer + '\n Transport from: ' + transport_data.location_from + ' to: ' + transport_data.location_to + '\n' +
    'date: ' + transport_data.date.isoformat() + ' time: ' + transport_data.time.isoformat() + '\n Vehicle + owner: ' + transport_data.vehicle + ', ' + transport_data.vehicle_owner + '\n Goods: ' + transport_data.goods + '\n Driver Contact: ' + 
    transport_data.driver_contact + '\n Orga contact: ' + transport_data.orga_contact + '\n Comment: ' + transport_data.comment + '\n Link: ' 'https://fixmeurl.de/transports/show/' + str(transport_data.id) )
  ### FIXME: url in messagebody

  ##
  ## Create user if not exists
  ##
  zammad_user_id = client.user.search({'query': current_user.login})
  if not zammad_user_id:
    pprint('user does not exist')
    client.user.create({'firstname': current_user.login, 'email': current_user.login})
    zammad_user_id = client.user.search({'query': current_user.login})

  ##
  ## Create a new ticket, if the transport has no ticket_id in the db
  ##
  if transport_data.ticket_id == None:
    print('new')
    ticketTemplate = {
      'title': '[Transport] from: ' + transport_data.location_from + ' to: ' + transport_data.location_to,
      'group_id': '17',
      'owner_id': '270',
      'customer_id': zammad_user_id[0]['id'],
      'state_id': '2',
      'priority_id': '2',
      'article': {'from':
                      '35c3'
                  'to' '\"test@psy.rocks\" <test@psy.rocks>',
                  'cc': current_user.login,
                  'body': messagebody,
                  'type_id': 1,
                  'sender_id': 1,
                  'form_id': '850048713',
                  'content_type': 'text/html'},
      'tags': '',
      'pending_time': transport_data.date.isoformat() + transport_data.time.isoformat() + 'Z',
      'note': messagebody,
    }
    new_ticket = client.ticket.create(ticketTemplate)
    transport_data.ticket_id = new_ticket['id']

    ##
    ## return updated transport object for db update
    ##
    return transport_data.ticket_id

  else:
    print('old')
    if transport_data.time == None:
      transport_data.time = datetime.time()
      ### Set pseudotime if time is not set
    ticketTemplate = {
      'id': transport_data.ticket_id,
      'title': '[Transport] from: ' + transport_data.location_from + ' to: ' + transport_data.location_to,
      'group_id': '17',
      'owner_id': '270',
      'customer_id': zammad_user_id[0]['id'],
      'state_id': '2',
      'priority_id': '2',
      'article': {'from':
                      '35c3'
                  'to' '\"test@psy.rocks\" <test@psy.rocks>',
                  'cc': current_user.login,
                  'body': messagebody,
                  'type_id': 1,
                  'sender_id': 1,
                  'form_id': '850048713',
                  'content_type': 'text/html'},
      'tags': '',
      'pending_time': transport_data.date.isoformat() + transport_data.time.isoformat() + 'Z',
      'note': messagebody,
    }
    client.ticket.update(transport_data.ticket_id, ticketTemplate)

  pass
