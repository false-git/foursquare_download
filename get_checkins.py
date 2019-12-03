import datetime
import json
import os
import sys
import urllib.parse
import urllib.request
import keyring
import icalendar

ITEMS_PER_PAGE = 250
access_token = keyring.get_password("foursquare_download", "access_token")


def get_page(p):
    """
    1ページ分のCheckin履歴を取得する。

    Parameters
    ----------
    p : int
        取得するページ(0〜)

    Returns
    -------
    json_result : dict
        取得したjson
    """
    # 特定の日付以前のデータのみ取り出したい場合は、beforeTimestampパラメータを追加する(未検証)
    params = urllib.parse.urlencode(
        {
            "oauth_token": access_token,
            "v": "20191201",
            "limit": ITEMS_PER_PAGE,
            "offset": p * ITEMS_PER_PAGE,
        }
    )

    req = "https://api.foursquare.com/v2/users/self/checkins?{}".format(params)

    request = urllib.request.Request(req)

    json_result = None

    with urllib.request.urlopen(request) as res:
        json_result = json.loads(res.read().decode("utf-8"))

    return json_result


def get_all_page():
    """
    全ページ分のCheckin履歴を取得する。

    Returns
    -------
    allpage : dict
        取得したjson
    """
    current_page = 0
    allpage = get_page(current_page)
    allitems = allpage["response"]["checkins"]["items"]
    # count と実際に取得件数に乖離があるため、終了条件に使えない
    # count = allpage["response"]["checkins"]["count"]
    read_items = len(allitems)
    while read_items == ITEMS_PER_PAGE:
        current_page += 1
        p = get_page(current_page)
        read_items = len(p["response"]["checkins"]["items"])
        allitems.extend(p["response"]["checkins"]["items"])
    return allpage


def get_value(dic, key, defaultValue):
    """
    dictionaryからkeyに対応する値を取得する。

    Parameters
    ----------
    dic : dict
        dictionary
    key : objeect
        key of dictionary
    defaultValue : object
        デフォルト値

    Returns
    -------
    value : object
        keyに対応する値。なかったらdefaultValue
    """
    value = defaultValue
    if key in dic:
        value = dic[key]
    return value


def item2event(item):
    """
    foursquareのitemからicalendarのeventに変換する。

    Parameters
    ----------
    item : dict
        foursquareのjsonのitem

    Returns
    -------
    event : Event
        event
    """
    tz, shout, venueName, venueUrl = None, "", "", ""
    uid = "{}@foursquare".format(item["id"])
    tzoffset = get_value(item, "timeZoneOffset", None)
    if tzoffset is not None:
        tz = datetime.timezone(datetime.timedelta(minutes=tzoffset))
    checkinDate = datetime.datetime.fromtimestamp(item["createdAt"], tz)
    shout = get_value(item, "shout", "")
    if "venue" in item:
        venue = item["venue"]
        venueName = get_value(venue, "name", "")
        if "id" in venue:
            venueUrl = "https://foursquare.com/v/{}".format(venue["id"])
    description = "I'm at {}!\n{}\nVenue: {}".format(venueName, shout, venueUrl)
    event = icalendar.Event()
    event.add("uid", uid)
    event.add("dtstamp", checkinDate)
    event.add("dtstart", checkinDate)
    event.add("dtend", checkinDate)
    event.add("description", description)
    event.add("location", venueName)
    event.add("summary", "@{}".format(venueName))
    return event


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} dumpfile".format(args[0]))
        exit(1)
    filename, ext = os.path.splitext(args[1])
    dumpfile = filename + ".json"
    icsfile = filename + ".ics"
    if os.path.exists(dumpfile):
        with open(dumpfile, "rt") as f:
            allpage = json.load(f)
    else:
        allpage = get_all_page()
        with open(dumpfile, "wt") as f:
            json.dump(allpage, f)
    cal = icalendar.Calendar()
    cal.add("prodid", "-//false-git//foursquare_download//")
    cal.add("version", "2.0")
    for item in allpage["response"]["checkins"]["items"]:
        cal.add_component(item2event(item))
    with open(icsfile, "wb") as f:
        f.write(cal.to_ical())
