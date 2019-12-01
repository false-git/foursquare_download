import json
import sys
import urllib.parse
import urllib.request
import keyring

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


if __name__ == "__main__":
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} dumpfile".format(args[0]))
        exit(1)
    dumpfile = args[1]
    allpage = get_all_page()
    with open(dumpfile, "wt") as f:
        json.dump(allpage, f)
