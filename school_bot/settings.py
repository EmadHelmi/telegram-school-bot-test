from os import environ

DATABASE = {
    "psql": {
        "DB_HOST": environ.get("DB_HOST", "localhost"),
        "DB_PORT": int(environ.get("DB_PORT", 5432)),
        "DB_USER": environ.get("DB_USER", "postgres"),
        "DB_PASSWORD": environ.get("DB_PASSWORD", None),
        "DB_NAME": environ.get("DB_NAME", "postgres")
    }
}

BOT_TOKEN = environ['BOT_TOKEN']

REDIS = {
    "HOST": environ.get("REDIS_HOST", "localhost"),
    "PORT": int(environ.get("REDIS_PORT", 6379)),
    "PASSWORD": environ.get("REDIS_PASSWORD", None),
    "STATUS": {"status#{user_id}": "{area}#{function}#{status}"},
    "STUDENT_REGISTER": {
        "register#{user_id}": {
            "firstname": "",
            "lastname": "",
            "national_code": "",
            "phone_number": "",
            "email": "",
            "grade": ""
        }
    },
    "EXAM_REGISTER": {
        "register#{user_id}": {
            "name": "",
            "grade": "",
            "time": "",
            "creator": ""
        }
    }
}

JWT_SECRET = "X8+#VvR?u8R3KJY-y!5hL@cKCZ6S=Tyr"
