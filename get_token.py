import json
import sys
import urllib.parse
import urllib.request
import keyring

# REDIRECT_URLに、あなたが持っているサイトのURLを設定してください。
# https://ja.foursquare.com/developers/apps の自分のアプリの REDIRECT URL として指定したものです。
REDIRECT_URI = "https://www.example.com/"


def get_code_url(client_id):
    """
    CODEを取得するURLを取得する

    Parameters
    ----------
    client_id : string
        CLIENT ID

    Returns
    -------
    req : string
        URL
    """
    params = urllib.parse.urlencode(
        {"client_id": client_id, "response_type": "code", "redirect_uri": REDIRECT_URI}
    )

    req = "https://foursquare.com/oauth2/authenticate?{}".format(params)
    return req


def get_token_url(client_id, client_secret, code):
    """
    アクセストークンを取得するURLを取得する

    Parameters
    ----------
    client_id : string
        CLIENT ID
    client_secret : string
        CLIENT SECRET
    code : string
        CODE

    Returns
    -------
    req : string
        URL
    """
    params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": code,
        }
    )

    req = "https://foursquare.com/oauth2/access_token?{}".format(params)
    return req


if __name__ == "__main__":
    client_id = keyring.get_password("foursquare_download", "client_id")
    client_secret = keyring.get_password("foursquare_download", "client_secret")
    args = sys.argv
    if len(args) < 2:
        print("Usage: {} code".format(args[0]))
        print("If you don't have code, access following URL.")
        print(get_code_url(client_id))
        exit(1)
    code = args[1]

    req = get_token_url(client_id, client_secret, code)

    request = urllib.request.Request(req)

    with urllib.request.urlopen(request) as res:
        json_result = json.loads(res.read().decode("utf-8"))
        access_token = json_result["access_token"]
        keyring.set_password("foursquare_download", "access_token", access_token)
        print(access_token)
