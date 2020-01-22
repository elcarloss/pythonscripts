import os, slackclient

VALET_SLACK_NAME = "gsboy"
VALET_SLACK_TOKEN = "xoxb-3339495132-661396845351-AWiv7I35p2jCNTJ1QvyLGFvh"
# initialize slack client
valet_slack_client = slackclient.SlackClient(VALET_SLACK_TOKEN)
# check if everything is alright
print(VALET_SLACK_NAME)
print(VALET_SLACK_TOKEN)
is_ok = valet_slack_client.api_call("users.list").get('ok')
print(is_ok)

if(is_ok):
    for user in valet_slack_client.api_call("users.list").get('members'):
        if user.get('name') == VALET_SLACK_NAME:
            print(user.get('id'))
