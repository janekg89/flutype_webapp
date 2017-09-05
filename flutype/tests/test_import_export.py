from flutype.data_management.fill_database import Database,fill_database, path_master, path_master2
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs


from django.test import TestCase

class LoadDataFromDataBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-19_E5_X31"
        ])



    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def test_load_database_from_master(self):
        print(Database.load_database())
        return Database.load_database()



