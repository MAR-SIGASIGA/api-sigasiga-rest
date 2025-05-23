import os

class Config:
    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-por-defecto')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'clave-jwt-por-defecto')
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 14400))
    MODE = os.getenv('MODE', 'development')

    # Configuración de Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis-sigasiga')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    MYSQL_USER = str(os.getenv('MYSQL_USER', 'root'))
    MYSQL_PASSWORD = str(os.getenv('MYSQL_PASSWORD', 'Marcos12root'))
    MYSQL_HOSTNAME = str(os.getenv('MYSQL_HOSTNAME', 'mariadb'))
    MYSQL_DB_NAME = str(os.getenv('MYSQL_DB_NAME', 'sigasiga'))
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOSTNAME + ':' + str(MYSQL_PORT) + '/' + MYSQL_DB_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # SQLALCHEMY_DATABASE_URI = 'mysql://' + MYSQL_USER + ':' + MYSQL_PASSWORD + '@' + MYSQL_HOSTNAME + + '/' + MYSQL_DB_NAME