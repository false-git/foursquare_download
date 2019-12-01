# foursquare_download

* foursquareの過去のチェックイン情報がカレンダーから見られなくなってしまい、かつ2回申請しても過去ログを送ってくれないので、自分でダウンロードすることにする。
* 参考: https://syncer.jp/foursquare-api-matome

## 前提条件

* python 3.6以降
* pipで以下のパッケージをインストールしてあること
    * keyring

## 手順

* アプリケーションの作成
    * https://developer.foursquare.com/ にアクセスする。
    * ログインして My Apps のページに行く。 https://ja.foursquare.com/developers/apps
    * Create New App
    * APP NAME と APP OR COMPANY URL を適当に入れる。
    * CLIENT ID(以降`<A>`と表記) と CLIENT SECRET(以降`<B>`と表記) が表示されるので、控えておく。
    * WEB ADDRESSED の REDIRECT URL に自分が管理しているサイトのURL(以降`<C>`)を入れて SAVE しておく。

* CLIENT ID と CLIENT SECRET を keyring に登録(控えたものを登録する)
```shell-session
% keyring set foursquare_download client_id
Password for 'client_id' in 'foursquare_download':<A>
% keyring set foursquare_download client_secret
Password for 'client_secret' in 'foursquare_download':<B>
```

* CODE を取得する
    * `<C>`を、get_token.pyの`REDIRECT_URI`に設定する。
    * 一度 get_token.py を実行すると、以下のようなURLが表示されるので、ブラウザでアクセスする。
      `https://foursquare.com/oauth2/authenticate?client_id=<A>&response_type=code&redirect_uri=<C>`
    * foursquare の認証画面になるので、許可する。
    * `<C>`にリダイレクトされるので、URLを記録する。
    * URLにある GET パラメータの code= の部分(以降`<D>`)を控えておく。
    * `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX#_=_`のような文字列なので、`#_=_`を除いた部分。

* アクセストークンを取得する(成功すると、keyringに登録される)
```shell-session
% python get_token.py <D>
```

* 過去のデータを取得する。
```shell-session
% python get_checkins.py <保存ファイル名>
```
