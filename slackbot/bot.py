import os, slackclient

VALET_SLACK_NAME = "gsboy"
VALET_SLACK_TOKEN = "xoxb-3339495132-661396845351-AWiv7I35p2jCNTJ1QvyLGFvh"
VALED_SLACK_ID = "WKDGE9A5N"
# initialize slack client
valet_slack_client = slackclient.SlackClient(VALET_SLACK_TOKEN)
# check if everything is alright

print(VALET_SLACK_NAME)
print(VALET_SLACK_TOKEN)
is_ok = valet_slack_client.api_call("users.list").get('ok')
print(is_ok)

def is_for_me(event):
    # TODO Implement later
    return True
def handle_message(message, user, channel):
    # TODO Implement later
    post_message(message='Hello', channel=channel)
def post_message(message, channel):
    valet_slack_client.api_call('chat.postMessage', channel=channel,
                          text=message, as_user=True)
def run():
    if valet_slack_client.rtm_connect():
        print('[.] Valet de Machin is ON...')
        while True:
            event_list = valet_slack_client.rtm_read()
            if len(event_list) > 0:
                for event in event_list:
                    print(event)
                    if is_for_me(event):
                        handle_message(message=event.get('text'), user=event.get('user'), channel=event.get('channel'))
            time.sleep(SOCKET_DELAY)
    else:
        print('[!] Connection to Slack failed.')

if __name__=='__main__':
    run()
