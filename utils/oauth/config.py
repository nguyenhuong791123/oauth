class SystemConfig:
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset={charset}'.format(**{
        'host': 'sc-m-db'
        ,'port': 3306
        ,'username': 'root'
        ,'password': 'scmysql080'
        ,'database': 'sc_oauth'
        ,'charset': 'UTF8MB4'
    })

Config = SystemConfig