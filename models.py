from pony.orm import Database, Required, Json

from settings import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserStates(db.Entity):
    user_id = Required(int, unique=True)
    scenario_name = Required(str)
    step = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    user_name = Required(str)
    email = Required(str)


db.generate_mapping(create_tables=True)
