# transporte
Transport planing tool

## python
use python3!

## database
for production use it is recommended to use mysql or postgresql.

## venv
use venvs!

### create venv
```
python -m venv venv
```

### activate venv
```
source venv/bin/activate
```

## copy & edit config
```
cp transporte/config.cfg.example transporte/config.cfg
nano transporte/config.cfg
```


## build
```
pip install -r requirements.txt
pip install --editable .
```


## create database
```
python -i
>>> from transporte.transporte import db
>>> db.create_all()
```

## run
```
export FLASK_APP=transporte/transporte.py
flask run
```

## debug
```
export FLASK_APP=transporte/transporte.py
export FLASK_DEBUG=True
flask run
```