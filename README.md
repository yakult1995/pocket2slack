## PocketしたものをSlackに流すもの

### 事前準備
* SlackBot
* MySQL
* PocketAPI(AccessTokenまで)

### 設定
* ホームディレクトリにこのレポジトリをCloneする
* 上記の情報を`.env`に書き込む
  * `.env.sample`を参考に

### 使用方法
* `main.py`を実行するだけ
* DBに格納されてる情報との差分のみをSlackに流す
* 個人的にはcronで毎分回してほぼリアルタイムでSlackに流している

### TODO
* MySQLの設定を追加する