from __future__ import unicode_literals

from .basemanager import BaseManager
from .constants import XERO_API_URL
from .utils import resolve_user_agent, singular


class Manager(BaseManager):
    def __init__(self, name, credentials, unit_price_4dps=False, user_agent=None):
        from xero import __version__ as VERSION  # noqa

        self.credentials = credentials
        self.name = name
        self.base_url = credentials.base_url + XERO_API_URL
        self.extra_params = {"unitdp": 4} if unit_price_4dps else {}
        self.singular = singular(name)
        self.user_agent = resolve_user_agent(
            user_agent, getattr(credentials, "user_agent", None)
        )

        for method_name in self.DECORATED_METHODS:
            method = getattr(self, "_%s" % method_name)
            setattr(self, method_name, self._get_data(method))
        
        if self.name == "ContactGroups":
            def create(self, name):
                return self.save_or_put(data={"Name": name}, method="put")

            def add_contacts(self, id, contacts):
                data = [{"ContactID": c} for c in contacts]
                return self.save_or_put(data={"Contacts": data}, method="put", headers={"Content-Type": "application/json"}, url_suffix=f"{id}/Contacts", as_json=True)

            def clear_contacts(self, id):
                return self._delete(id, url_suffix="Contacts")

            def delete_contact(self, id, contact_id):
                return self._delete(id, url_suffix=f"Contacts/{contact_id}")

            
            setattr(self, "create", self._get_data(create.__get__(self)))
            setattr(self, "add_contacts", self._get_data(add_contacts.__get__(self)))
            setattr(self, "clear_contacts", self._get_data(clear_contacts.__get__(self)))
            setattr(self, "delete_contact", self._get_data(delete_contact.__get__(self)))

        if self.name in self.OBJECT_DECORATED_METHODS.keys():
            object_decorated_methods = self.OBJECT_DECORATED_METHODS[self.name]
            for method_name in object_decorated_methods:
                method = getattr(self, "_%s" % method_name)
                setattr(self, method_name, self._get_data(method))
