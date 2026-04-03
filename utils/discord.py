import requests
import json
from datetime import datetime

now = datetime.now()

critical_url = os.environ.get("DISCORD_CRITICAL")
warning_url = os.environ.get("DISCORD_WARNING")
info_url = os.environ.get("DISCORD_INFO")
test_url = os.environ.get("DISCORD_TEST")

critical_prefix = "CRITICAL ALERT: "
warning_prefix = "Warning: "
info_prefix = "Information: "
test_prefix = "Test: "


def discord_post(message_content, urgent=9, username=None):
    dt_string = now.strftime(" %d/%m/%Y %H:%M:%S")
    if urgent == 9:
        url = test_url
        message = test_prefix + message_content + dt_string
    elif urgent == 0:
        url = info_url
        message = info_prefix + message_content + dt_string
    elif urgent == 1:
        url = warning_url
        message = warning_prefix + message_content + dt_string
    elif urgent == 2:
        url = critical_url
        message = critical_prefix + message_content + dt_string

    data = {}
    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data["content"] = message
    data["username"] = username

    # leave this out if you dont want an embed
    data["embeds"] = []
    embed = {}
    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    # embed["description"] = "text in embed"
    # embed["title"] = "embed title"
    # data["embeds"].append(embed)

    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})

    try:
        result.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(err)
    else:
        print("Payload delivered successfully, code {}.".format(result.status_code))






