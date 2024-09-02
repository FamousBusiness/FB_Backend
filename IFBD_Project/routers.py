# # routers.py
# from django.apps import apps

# class ReadWriteRouter:
#     def __init__(self):
#         self.read_apps = [app.name for app in apps.get_app_configs()]

#     def db_for_read(self, model, **hints):
#         return 'slave' if model._meta.app_label in self.read_apps else None

#     def db_for_write(self, model, **hints):
#         return 'default' if model._meta.app_label in self.read_apps else None

#     def allow_relation(self, obj1, obj2, **hints):
#         return None

#     def allow_migrate(self, db, app_label, model_name=None, **hints):
#         return db == 'default' if app_label in self.read_apps else None
