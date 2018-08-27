#Import dependencies for Slack Bot as mentioned in CommitBot.txt
import os
import time
import re
from slackclient import SlackClient

#Grabs secret token exported in previous setup when CommitBot was created.

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# commitbot's user ID in Slack: value is assigned after the bot starts up
commitbot_id = None

# commit command reference. might not agree with comstants.
commits("user_id.commits.to/")
commits = commit # to hopefully parse the URL as part of the command "commit" within slack.

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
commit = "do"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)/"

#Defines user IDs for each workspace the bot is installed in, in the event the bot is mentioned.
#Then goes into an infinite loop to check for mentions.

#Definition for commands (making commits; not sure if bot will do this automatically yet or if we'll trigger to test).
def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == commitbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning, ie @CommitBot) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known. Bot will only know one command right now.
    """
    # Default response is help text for the user
    default_response = "Hmm. Doesn't look quite right. Try *{}*.".format(commit)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.startswith(commit):
        response = "Woohoo! Finish that string and you're making a commitment."

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

#Connection parameters.

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Commit Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        commitbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
        
#parse_bot_commands() function determines event contains command for CommitBot (ie making a commit). If it does, then command will contain a value and the handle_command() function determines what to do.

