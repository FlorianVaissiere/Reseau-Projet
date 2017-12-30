# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import select
from select import select

import socket
from socket import socket
from socket import SOL_SOCKET
from socket import SO_REUSEADDR


# groupe[nom] : [[modo] [user] [topic]]
groupe = {
    'group': 'agora',
    'user' : '',
    'modo' : '(None)',
    'topic': '(None)'
}

BUFF_SZ       = 1024
DEFAULT_PORT  = 7326
ENCODING      = 'utf-8'
IP_NO_FILTER  = '0.0.0.0'
PENDING_SLOTS = 3
TAB_SZ        = 5

CMD_GROUP = '/g'
CMD_HELP  = '/?'
CMD_MSG   = '/m'
CMD_NAME  = '/name'
CMD_PASS  = '/pass'
CMD_QUIT  = '/q'
CMD_TOPIC = '/topic'
CMD_WHOIS = '/w'


def create_sock():
    """ TODO: function definition
    """
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind((IP_NO_FILTER, DEFAULT_PORT))
    return s

def display_help(c):
    """ TODO: function definition
    """
    msg='[=Help=] Server supports following commands:\n'
    c.send(msg.encode(ENCODING))
    msg='[=Help=] beep boot g m name nobeep pass topic w \n'
    c.send(msg.encode(ENCODING))

def group_cmd(t, c):
    """ TODO: function definition
    """
    if len(t[1:]) < 2:
        msg = '[=Error=] Missing a Group Name'
        c.send(msg.encode(ENCODING))
        serv_print('Missing a Group Name', 'Debug')
        return
    else:
        serv_print('Group name Detected: {}'.format(t[2:]), 'Debug')

    for i in range (groupe['group']):
        if t.getpeername()[0] in groupe[i][[user]]:
            groupe[i]['user'].remove(t.getpeername()[0])
            msg = '[=Depart=] {} just left\n'.format(t.getpeername()[0])
            c.send(msg.encode(ENCODING))

    groupe['group'].append(format(t[2:]))
    groupe[format(t[2:])]['user'].append(t.getpeername()[0])

    msg = '[=Status=] You are now in groupe {} as moderator\n'.format(format(t[2:]))
    c.send(msg.encode(ENCODING))

def msg_cmd(t, c):
    """ TODO: function definition
    """
    if len(t[1:]) < 2:
        msg = '[=Error=] Missing a Recipient'
        c.send(msg.encode(ENCODING))
        serv_print('Missing a Recipient', 'Debug')
        return
    else:
        serv_print('Username Detected: {}'.format(t[2:]), 'Debug')
    
    data = t.recv(1024)
    who  = t.getpeername()[0]
    msg  = '<* {} *> {}\n'.format(who, data.strip())
    c.send(msg.encode(ENCODING))

def name_cmd(t, c):
    """ TODO: function definition
    """
    if len(t[1:]) < 2:
        msg = '[=Name=] Your nickname is {}\n'.format(t.getpeername()[0])
        c.send(msg.encode(ENCODING))
        serv_print('Missing a Nickname or check his name', 'Debug')
        return
    else:
        serv_print('Group name Detected: {}'.format(t[2:]), 'Debug')

    oldNick = t.getpeername()[0]
    t.getpeername()[0] = format(t[2:])
    msg = '[=Name=] {} changed nicname to {}\n'.format(oldNick, t.getpeername()[0])
    for i in range (groupe['group']):
        if oldNick in groupe[i]['user']:
            groupe[i]['user'].remove(oldNick)
            groupe[i]['user'].append(format(t[2:]))

    serv_print('NickName Detected: {}'.format(t[2:]), 'Debug')

def pass_cmd(t, c):
    """ TODO: function definition
    """
    who=t.getpeername()[0]
    for i in range (groupe['group']):
        if who in groupe[i]['user']:
            if groupe[i]['modo'] == '':
                groupe[i]['modo'] = who
    msg='[=Notify=] Server has passed moderation to {} \n'.format(who)
    c.send(msg.encode(ENCODING))

def quit_cmd(t, c, socks):
    """ TODO: function definition
    """
    who = t.getpeername()[0]
    msg = '[=Sign-off=] {} JustLeft \n'.format(who)
    c.send(msg.encode(ENCODING))

    socks.remove(t)

    for i in range (groupe['group']):
        if who in groupe[i]['user']:
            groupe[i]['user'].remove(who)

def serv_print(msg='', subj=''):
    """ TODO: function definition
    """
    serv_printing = ''
    if not subj :
        serv_printing += '[={}=] '.format(subj)
    print(serv_printing + msg)

def topic_cmd(t, c):
    """ TODO: function definition
    """
    if len(t[1:]) < 2:
        msg='[=Error=] Missing a Topic'
        c.send(msg.encode(ENCODING))

        serv_print('[=Debug=] Missing a Topic', 'Debug')
        return
    else:
        serv_print('Topic Detected: {}'.format(t[2:]), 'Debug')

    who=t.getpeername()[0]
    for i in range (groupe['group']):
        if who in groupe[i]['user']:
            groupe[i]['topic'] = format(t[2:])

def whois(c):
    """ TODO: function definition
    """
    msg = 'Group : {}\tModo: {}\tTopic: {}\n'
    msg = msg.format(
            groupe['group'], 
            groupe['group']['modo'], 
            groupe['group']['topic']
        )
    msg.expandtabs(TAB_SZ)
    c.send(msg.encode(ENCODING))

    for i in range (groupe['group']):
        msg = '{}\n'.format(groupe[i]['user'])
        c.send(msg.encode(ENCODING))


if __name__ == '__main__':
    # création du socket
    s = create_sock()
    s.listen(PENDING_SLOTS)
    serv_print('Listening on port {}'.format(DEFAULT_PORT))

    # liste des sockets ouvert
    socks = [s]

    while True:
      # wait for an incoming message
      lin, lout, lex = select(socks, [], []) 
      serv_print('select got {} read events'.format(len(lin)))

      for t in lin:
        groupe['group']['user'].append(t.getpeername()[0])
        
        if t == s: # this is an incoming connection
            c, addr = s.accept()
            serv_print('Hello {}\n'.format(addr[0]))
            socks.append(c)
            c.send(msg.encode(ENCODING))

        # Command /whois
            if t.startswith(CMD_WHOIS):
                whois(c)
                serv_print('General Location', 'Debug')

        # Command /message
            elif t.startswith(CMD_MSG):
                msg_cmd(t, c)

        # Command /group
            elif t.startswith(CMD_GROUP):
                group_cmd(t, c)

        # Command /name
            elif t.startswith(CMD_NAME):
                name_cmd(t, c)

        # Command /topic
            elif t.startswith(CMD_TOPIC):
                topic_cmd(t, c)
                

        # Command /pass
            elif t.startswith(CMD_PASS):
                pass_cmd(t, c)
                serv_print ('Server has passed moderation to {}!\n'.format(who), 'Debug')

        # Command /?
            elif t.startswith(CMD_HELP):
                display_help(c)
                serv_print ('Help command {}!\n', 'Debug')

        # Command /quit
            elif t.startswith(CMD_QUIT):
                quit_cmd(t, c, socks)
                serv_print ('Drop Connection {}!\n'.format(who), 'Debug')

        # Standart message
            else: # someone is speaking
                data = t.recv(BUFF_SZ)
                who  = t.getpeername()[0]

                if not data:
                    socks.remove(t)
                    msg = '[=Sign-off=] Drop Connection {}!\n'.format(who)
                else:
                    msg = '{}: {}\n'.format(who, data.strip())
                
                serv_print (msg)
                for c in socks[1:]:
                    c.send(msg)
