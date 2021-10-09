from office365.runtime.client_object import ClientObject
from office365.runtime.client_result import ClientResult
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.types.EventHandler import EventHandler


class ClientObjectCollection(ClientObject):

    def __init__(self, context, child_item_type, resource_path=None):
        """Client object collection

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type child_item_type: type[ClientObject]
        :type resource_path: office365.runtime.resource_path.ResourcePath
        """
        super(ClientObjectCollection, self).__init__(context, resource_path)
        self._data = []
        self._item_type = child_item_type
        self.page_loaded = EventHandler(False)
        self._default_page_size = 100
        self._paged_mode = True
        self._page_index = 0
        self.next_request_url = None

    @property
    def entity_type_name(self):
        name = super(ClientObjectCollection, self).entity_type_name
        return "Collection({0})".format(name)

    def get(self):
        """
        :rtype: ClientObjectCollection
        """
        return super(ClientObjectCollection, self).get()

    def clear(self):
        self._data = []

    def create_typed_object(self, properties=None, persist_changes=False):
        """
        :type properties: dict
        :type persist_changes: bool
        :rtype: ClientObject
        """
        if properties is None:
            properties = {}
        if self._item_type is None:
            raise AttributeError("No class for object type '{0}' found".format(self._item_type))

        client_object = self._item_type(self.context)
        client_object._parent_collection = self
        for k, v in properties.items():
            client_object.set_property(k, v, persist_changes)
        return client_object

    def set_property(self, name, value, persist_changes=False):
        """
        :type name: str
        :type value: any
        :type persist_changes: bool
        """
        child_client_object = self.create_typed_object(value)
        self.add_child(child_client_object)

    def add_child(self, client_object):
        """
        Adds client object into collection

        :type client_object: ClientObject
        """
        client_object._parent_collection = self
        self._data.append(client_object)

    def remove_child(self, client_object):
        """
        :type client_object: ClientObject
        """
        self._data = [item for item in self._data if item != client_object]

    def __iter__(self):
        """
        :rtype: collections.Iterable[ClientObject]
        """
        for cur_item in self._data:
            yield cur_item

        if self._paged_mode:
            while self.next_request_url:
                for cur_item in self._get_next_items():
                    yield cur_item

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        """

        :type index: int
        :rtype: ClientObject
        """
        item_iterator = iter(self)
        while len(self._data) <= index:
            next(item_iterator)
        return self._data[index]

    def to_json(self, json_format=None):
        return [item.to_json(json_format) for item in self._data]

    def filter(self, expression):
        """
        Sets OData $filter query option

        :type expression: str
        """
        self.query_options.filter = expression
        return self

    def order_by(self, value):
        """
        Sets OData $orderBy query option

        :type value: int
        """
        self.query_options.orderBy = value
        return self

    def skip(self, value):
        """
        Sets $skip system query option

        :type value: int
        """
        self.query_options.skip = value
        return self

    def top(self, value):
        """
        :type value: int
        """
        self._paged_mode = False
        self.query_options.top = value
        return self

    def get_items_count(self):
        """
        Gets total items count
        :return: ClientResult
        """
        result = ClientResult(self.context)

        def _calc_items_count(resp):
            list(iter(self))
            result.value = len(self)

        self.context.load(self)
        self.context.after_execute(_calc_items_count)
        return result

    def _load_paged_items(self):
        request = RequestOptions(self.next_request_url)
        response = self.context.execute_request_direct(request)
        json = response.json()
        self.next_request_url = None
        self.context.pending_request().map_json(json, self)

    def _get_next_items(self):
        self._page_index += 1
        next_index = self._default_page_size * self._page_index
        self._load_paged_items()
        self.page_loaded.notify(len(self._data))
        return self._data[next_index:]
