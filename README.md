# soil_analysis リポジトリ
## ライブラリをインストールする
```console
pip install -r requirements.txt

-- ※開発時 現在のライブラリの状態でrequirementsを書き出す
pip freeze > requirements.txt
```

## crm
- `.env` をもらって soil_analysis フォルダに保存する
- ローカルmysqlに `soil_db` というデータベースを作成してから以下コマンドを実行する
```console
python manage.py makemigrations crm
python manage.py migrate
python manage.py loaddata .\crm\fixtures\companycategory.json
python manage.py loaddata .\crm\fixtures\company.json
python manage.py loaddata .\crm\fixtures\authuser.json
python manage.py loaddata .\crm\fixtures\crop.json
python manage.py loaddata .\crm\fixtures\landblock.json
python manage.py loaddata .\crm\fixtures\landperiod.json
python manage.py loaddata .\crm\fixtures\cultivationtype.json
python manage.py loaddata .\crm\fixtures\land.json
python manage.py loaddata .\crm\fixtures\samplingmethod.json
python manage.py loaddata .\crm\fixtures\landledger.json
python manage.py loaddata .\crm\fixtures\landreview.json
python manage.py loaddata .\crm\fixtures\landscorechemical.json
python manage.py loaddata .\crm\fixtures\device.json
```

## webアプリを動かす
```console
python manage.py runserver
python manage.py import_soil_hardness /path/to/folder
```
