from zammad_py import ZammadAPI
from flask import render_template
from .transporte import app
from datetime import datetime


def close_ticket(transport, reason):
    client = ZammadAPI(username=app.config['ZAMMAD_USER'], password=app.config['ZAMMAD_PASS'],
                       host=app.config['ZAMMAD_HOST'], is_secure=app.config['ZAMMAD_SECURE'])

    messagebody = reason

    ##
    ## if new helpdesk user is closing a ticket, we need to create the user in the ticket system
    ##
    zammad_search_result = client.user.search({'query': transport.user.login})
    if zammad_search_result:
        zammad_user = zammad_search_result[0]
    else:
        zammad_user = client.user.create({'firstname': transport.user.login, 'email': transport.user.login})

    ticketTemplate = {
        'id': transport.ticket_id,
        'title': '[Transport] from: ' + transport.origin + ' to: ' + transport.destination,
        'group_id': app.config['ZAMMAD_GROUP_ID'],
        'customer_id': zammad_user['id'],
        'state_id': '4',
        'article': {'from': '35c3',
                    'to': transport.user.login,
                    'body': messagebody,
                    'type_id': 1,
                    'content_type': 'text/html'},
        'note': messagebody,
    }

    client.ticket.update(transport.ticket_id, ticketTemplate)


def update_ticket(transport):
    client = ZammadAPI(username=app.config['ZAMMAD_USER'], password=app.config['ZAMMAD_PASS'],
                       host=app.config['ZAMMAD_HOST'], is_secure=app.config['ZAMMAD_SECURE'])

    ##
    ## Create user if not exists
    ##
    zammad_search_result = client.user.search({'query': transport.user.login})
    if zammad_search_result:
        zammad_user = zammad_search_result[0]
    else:
        zammad_user = client.user.create({'firstname': transport.user.login, 'email': transport.user.login})

    messagebody = render_template('email_transport_update.html', transport=transport)

    ticketTemplate = {
        'title': '[Transport] from: ' + transport.origin + ' to: ' + transport.destination,
        'group_id': app.config['ZAMMAD_GROUP_ID'],
        'customer_id': zammad_user['id'],
        'state_id': '3' if transport.needs_organization else '2',
        'article': {'from': '35c3',
                    'to': transport.user.login,
                    'body': messagebody,
                    'type_id': 1,
                    'content_type': 'text/html'},
        'tags': 'transport',
        'pending_time': '{}Z'.format(datetime.utcnow().isoformat()),
        'note': messagebody,
    }

    ##
    ## Create a new ticket, if the transport has no ticket_id in the db
    ##
    if transport.ticket_id == None:
        transport.ticket_id = client.ticket.create(ticketTemplate)['id']

    else:
        ticketTemplate['id'] = transport.ticket_id
        client.ticket.update(transport.ticket_id, ticketTemplate)

    return transport.ticket_id
