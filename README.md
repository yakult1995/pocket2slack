## PocketしたものをSlackに流すもの

### 事前準備
* SlackBot
* MySQL
* PocketAPI(AccessTokenまで)

### 設定
#### Git
* ホームディレクトリにこのレポジトリをCloneする

#### 環境変数
* 上記の情報を`.env`に書き込む
  * `.env.sample`を参考に

#### MySQL dockerを設定する

* `./docker/docker-compose.yml`にMySQLの設定を書き加える
* `./docker/init/`の２つのファイル内の`<DATABASE>`, `<TABLE>`を任意に書き換える
* それぞれ、`.env`と統一すること


### 使用方法
#### docker-compose
* `./docker`にて`docker-compose up -d`

#### Python
* `main.py`を実行するだけ
* DBに格納されてる情報との差分のみをSlackに流す
* 個人的にはcronで毎分回してほぼリアルタイムでSlackに流している
