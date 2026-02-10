class ClerkRouter:
    """
    A router to control all database operations on models in the
    clerks application.
    """
    route_app_labels = {'clerks'}

    def db_for_read(self, model, **hints):
        """
        Attempts to read user models go to 'default' (Cler).
        Specific legacy models go to their respective DBs.
        """
        if model._meta.app_label == 'clerks':
            # --- Marriage DB ---
            if model.__name__ in ['Allmarriages', 'Civilunion', 'Marriagelicense', 'Marriagesfrombooks']:
                return 'marriage'
            
            # --- Vets DB ---
            elif model.__name__ in ['Vet', 'Refbranch']:
                return 'vets'
            
            # --- Transmittal DB ---
            elif model.__name__ in ['Transactions', 'Accounts', 'Departments']:
                return 'transmitel'
            
            # --- Vitals DB ---
            elif model.__name__ in ['Deaths']:
                return 'vitals'

        return 'default'

    def db_for_write(self, model, **hints):
        """
        Writes always go to default unless explicitly routed.
        (Usually legacy DBs are read-only, but adjust here if you need to write).
        """
        if model._meta.app_label == 'clerks':
            if model.__name__ in ['Allmarriages', 'Civilunion', 'Marriagelicense', 'Marriagesfrombooks']:
                return 'marriage'
            elif model.__name__ in ['Vet', 'Refbranch']:
                return 'vets'
            elif model.__name__ in ['Transactions', 'Accounts', 'Departments']:
                return 'transmitel'
            elif model.__name__ in ['Deaths']:
                return 'vitals'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if involved models are in the same db.
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'default' database.
        """
        if app_label == 'clerks':
            # If we define unmanaged legacy models, prevent migrations for them
            # Logic: if model is Import/App tables -> default. If legacy -> specific DB.
            # faster to just use 'managed = False' on the legacy models.
            return True
        return None
