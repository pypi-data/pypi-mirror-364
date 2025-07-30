[![PyPI version](https://badge.fury.io/py/signate.svg)](https://badge.fury.io/py/signate)

# **SIGNATE CLI**
[SIGNATE](https://user.competition.signate.jp) の公式APIコマンドラインインターフェイス(以下：SIGNATE CLI)です。
SIGNATEはData Science Competitionのご提供を始めとした、データサイエンティストの皆様のための統合プラットフォームです。

**※SIGNATE CLIの動作にはPython3.8 以降の環境が必要です。**
※当CLIはβ版であり、予告なく変更させていただく可能性がございます。予めご了承ください。
※SIGNATE CLIはMac OSおよびLinuxをサポートしております。

# **インストールと事前準備**

以下のコマンドでインストールをお願いいたします。

```
$ pip install signate
```

インストール後、以下の手順を実施ください。

 1. [SIGNATE](https://user.competition.signate.jp) でアカウント登録 ※メールアドレス/パスワード 認証でのみ SIGNATE CLIをご利用いただけます。
 2. 以下のコマンドで登録したメールアドレス指定して実行

```
$ signate token -e xxxxx@example.co.jp
```
 3. パスワードを入力してサインイン（入力値は表示されません）

```
Password:
```
 4. 以下のメッセージが表示されたら利用準備完了です。

```
The API Token has been downloaded successfully.
```

``signate: command not found`` と表示される場合、環境変数$PATH のディレクトリ内にsignateが存在していることをご確認ください。``pip uninstall signate``コマンドで

 - signateコマンドがインストールされているディレクトリの確認
 - signateコマンドのアンインストール

が可能です。

# **利用方法**
SIGNATE CLIでは以下の機能が利用できます。

```bash
$ signate --help
Usage: signate [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  competition-list
  download
  file-list
  submit
  task-list
  token
```

### **① 投稿可能なコンペティション一覧の取得**
```
$ signate competition-list
```
投稿可能なコンペティション一覧を表示します。

``` bash
$ signate competition-list

public_key                        title               remaining      reward           entry_count
--------------------------------  ------------------  -------------  -------------  -------------
0001d2723faa40b5a597832319f4722c  コンペティション1       360 seconds        100万円               1
c1001e081ca645dd9eb5c5a027fd8ecd  コンペティション2           26 days                             5
```

### **② 投稿可能な課題一覧の取得**
```
$ signate task-list --competition_key=<competition-key>
```
投稿可能な課題一覧を表示します。

``` bash
$ signate task-list --competition_key=<competition-key>

public_key                        task_name
--------------------------------  -----------
4d63b1cf2dd3462d902ac805f60d96ca  分類課題 データ1
4d63b1cf2dawega346gg02awe60d96cb  回帰課題 データ2
```

### **③ コンペティションが提供するファイル一覧の取得**
**こちらの機能をご利用の場合、コンペティションへの参加に同意いただく必要がございます(同意前の場合)。**
コンペティションへの参加はブラウザから実行してください。

```
$ signate file-list --task_key=<task-key>
```

課題のファイル一覧を表示します。

``` bash
$ signate file-list --task_key=<task-key>

public_key                        file_name              title                  file_size
--------------------------------  ---------------------  ---------------------  -----------
sa9bc5b1f9ef45f6b79bdbeb281895f3  sample1.zip            学習用画像データ               60.65 MB
g5609de723b148fe8635754dcd1706fa  test_images.zip        評価用画像データ               26.49 MB
```

### **④ コンペティションが提供するファイルのダウンロード**
**こちらの機能をご利用の場合、コンペティションへの参加に同意いただく必要がございます(同意前の場合)。**
コンペティションへの参加はブラウザから実行してください。

```
$ signate download --task_key=<task-key> --file_key=<file-key> [--path=<path>]
```

ファイルをダウンロードします。
デフォルトではカレントディレクトリにファイルがダウンロードされます。
`--path=`を指定すると、ダウンロード先のパスを指定できます。

``` bash
$ signate download --task_key=<task-key> --file_key=<file-key> --path=/tmp/test.zip
```

### **⑤ 投稿の実施**
**こちらの機能をご利用の場合、コンペティションへの参加に同意いただく必要がございます(同意前の場合)。**
コンペティションへの参加はブラウザから実行してください。

```
$ signate submit --task_key=<task-key> <結果ファイルのパス> --memo “comment”
```

コンペティションに投稿を実施します。

``` bash
$ signate submit --task_key=<task-key> ~/test.zip --memo "xxx"

Submission completed successfully.
```

### **補足**
#### コンペティションへの同意
以下のようなメッセージが出力された際は
```
If you haven’t joined the competition yet, please do so through your browser.
```
ブラウザにて該当コンペティションに参加をお願いいたします。

# **ライセンス**
SIGNATE CLIは[Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0). を適用しております。
