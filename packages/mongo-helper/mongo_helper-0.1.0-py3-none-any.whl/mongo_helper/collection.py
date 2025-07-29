import mongo_helper as mh


class Collection(object):
    """Convenient wrapper for MongoDB collection operations

    Provides a simplified interface to MongoDB collection operations by wrapping
    the underlying Mongo class methods with more convenient defaults and
    input handling.
    """

    def __init__(self, collection_name, mongo_instance=None, url=None, db=None,
                 use_none_cert=None, attempt_docker=True, exception=True, show=False):
        """Initialize Collection instance

        - collection_name: name of the MongoDB collection to work with
        - mongo_instance: optional Mongo instance to use; if None, creates one
        - url: MongoDB connection URL (passed to connect_to_server if needed)
        - db: database name (passed to connect_to_server if needed)
        - use_none_cert: SSL certificate setting (passed to connect_to_server if needed)
        - attempt_docker: whether to attempt docker startup (passed to connect_to_server if needed)
        - exception: whether to raise exceptions (passed to connect_to_server if needed)
        - show: whether to show output (passed to connect_to_server if needed)
        """
        self.collection_name = collection_name

        if mongo_instance is None:
            mongo_instance, _ = mh.connect_to_server(
                url=url,
                db=db,
                use_none_cert=use_none_cert,
                attempt_docker=attempt_docker,
                exception=exception,
                show=show
            )
            if mongo_instance is None:
                raise Exception("Unable to connect to MongoDB server")

        self.mongo = mongo_instance
        if db is not None:
            self.mongo.change_database(db)

    def insert_one(self, document):
        """Add a document to the collection and return inserted_id

        - document: a dict of info to be inserted
        """
        return self.mongo._insert_one(self.collection_name, document)

    def insert_many(self, documents):
        """Add several documents to the collection and return inserted_ids

        - documents: list of dicts to insert
        """
        return self.mongo._insert_many(self.collection_name, documents)

    def find_one(self, query={}, fields='', ignore_fields='', **kwargs):
        """Return a single document matching the query

        - query: dict representing the search criteria
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any of , ; |
        - kwargs: additional arguments passed to underlying _find_one method
        """
        return self.mongo._find_one(
            self.collection_name, query,
            fields=fields, ignore_fields=ignore_fields, **kwargs
        )

    def find(self, query={}, fields='', ignore_fields='', to_list=False, **kwargs):
        """Return documents matching the query

        - query: dict representing the search criteria
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any of , ; |
        - to_list: if True, return a list instead of cursor
        - kwargs: additional arguments passed to underlying _find method
        """
        return self.mongo._find(
            self.collection_name, query,
            fields=fields, ignore_fields=ignore_fields, to_list=to_list, **kwargs
        )

    def update_one(self, match, update, upsert=False):
        """Update one matching document and return number modified

        - match: a dict of the query matching document to update
        - update: dict of modifications to apply
        - upsert: if True, perform an insert if no documents match
        """
        return self.mongo._update_one(self.collection_name, match, update, upsert=upsert)

    def update_many(self, match, update, upsert=False):
        """Update all matching documents and return number modified

        - match: a dict of the query matching documents to update
        - update: dict of modifications to apply
        - upsert: if True, perform an insert if no documents match
        """
        return self.mongo._update_many(self.collection_name, match, update, upsert=upsert)

    def delete_one(self, match):
        """Delete one matching document and return number deleted

        - match: a dict of the query matching document to delete
        """
        return self.mongo._delete_one(self.collection_name, match)

    def delete_many(self, match):
        """Delete all matching documents and return number deleted

        - match: a dict of the query matching documents to delete
        """
        return self.mongo._delete_many(self.collection_name, match)

    def count(self, match={}, **kwargs):
        """Return count of documents matching criteria

        - match: a dict of the query matching documents to count
        - kwargs: additional arguments passed to underlying _count method
        """
        return self.mongo._count(self.collection_name, match, **kwargs)

    def total_documents(self):
        """Return total count of documents in collection"""
        return self.mongo.total_documents(self.collection_name)

    def distinct(self, key, match={}, **kwargs):
        """Return list of distinct values for key among documents in collection

        - key: field name to get distinct values for
        - match: a dict of the query matching documents
        - kwargs: additional arguments passed to underlying _distinct method
        """
        return self.mongo._distinct(self.collection_name, key, match, **kwargs)

    def aggregate(self, pipeline, **kwargs):
        """Return cursor from aggregation pipeline

        - pipeline: list of aggregation pipeline stages
        - kwargs: additional arguments passed to underlying _aggregate method
        """
        return self.mongo._aggregate(self.collection_name, pipeline, **kwargs)

    def bulk_write(self, operations, ordered=True, bypass_document_validation=False, debug=False):
        """Execute a list of mixed write operations and return result

        - operations: list of write operation objects (InsertOne, UpdateOne,
          UpdateMany, ReplaceOne, DeleteOne, DeleteMany)
        - ordered: if True, operations are executed in order and execution stops
          after the first error; if False, operations may be reordered and all
          operations are attempted
        - bypass_document_validation: if True, allows write operations to bypass
          document level validation
        - debug: if True, drop into debugger if BulkWriteError is raised
        """
        return self.mongo._bulk_write(
            self.collection_name, operations, ordered=ordered,
            bypass_document_validation=bypass_document_validation, debug=debug
        )

    def create_index(self, keys, unique=False, ttl=None, sparse=False, background=False, **kwargs):
        """Create an index on the collection

        - keys: list of 2-item tuples where first item is a field name
          and second item is a direction (1 for ascending, -1 for descending)
        - unique: if True, create a uniqueness constraint
        - ttl: int representing "time to live" (in seconds) for documents
        - sparse: if True, only index documents that contain the indexed field
        - background: if True, create the index in the background
        - kwargs: additional arguments passed to underlying _create_index method
        """
        return self.mongo._create_index(
            self.collection_name, keys, unique=unique, ttl=ttl,
            sparse=sparse, background=background, **kwargs
        )

    def drop_index(self, name, **kwargs):
        """Drop an index from the collection

        - name: name of the index to drop
        - kwargs: additional arguments passed to underlying _drop_index method
        """
        return self.mongo._drop_index(self.collection_name, name, **kwargs)

    def drop_indexes(self, **kwargs):
        """Drop all indexes from the collection

        - kwargs: additional arguments passed to underlying _drop_indexes method
        """
        return self.mongo._drop_indexes(self.collection_name, **kwargs)

    def drop_collection(self, **kwargs):
        """Drop the collection from the database

        - kwargs: additional arguments passed to underlying _drop_collection method
        """
        return self.mongo._drop_collection(self.collection_name, **kwargs)

    def index_information(self):
        """Return dict of info about indexes on collection"""
        return self.mongo._index_information(self.collection_name)

    def index_names(self):
        """Return list of index names"""
        return self.mongo._index_names(self.collection_name)

    def index_sizes(self, scale='bytes'):
        """Return dict of index sizes

        - scale: one of bytes, KB, MB, GB
        """
        return self.mongo._index_sizes(self.collection_name, scale=scale)

    def index_usage(self, name='', full=False):
        """Return index usage statistics

        - name: name of specific index
        - full: if True, return full list of dicts from $indexStats aggregation
        """
        return self.mongo._index_usage(self.collection_name, name=name, full=full)

    def coll_stats(self, ignore_fields='wiredTiger, indexDetails', scale='bytes'):
        """Return a dict of info about the collection

        - ignore_fields: string containing output fields to ignore, separated by
          any of , ; |
        - scale: one of bytes, KB, MB, GB
            - NOTE: avgObeSize is always in bytes no matter what the scale is

        See: https://docs.mongodb.com/manual/reference/command/collStats/#output
        """
        return self.mongo.coll_stats(self.collection_name, ignore_fields=ignore_fields, scale=scale)

    def first_obj(self, match={}, timestamp_field='_id', fields='', ignore_fields='', **kwargs):
        """Return first object in collection

        - match: query criteria passed to _find_one
        - timestamp_field: name of timestamp field to sort on
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any of , ; |
        - kwargs: additional arguments passed to underlying first_obj method
        """
        return self.mongo.first_obj(
            self.collection_name, match, timestamp_field=timestamp_field,
            fields=fields, ignore_fields=ignore_fields, **kwargs
        )

    def last_obj(self, match={}, timestamp_field='_id', fields='', ignore_fields='', **kwargs):
        """Return last object in collection

        - match: query criteria passed to _find_one
        - timestamp_field: name of timestamp field to sort on
        - fields: string containing fields to return, separated by any of , ; |
        - ignore_fields: string containing fields to ignore, separated by any of , ; |
        - kwargs: additional arguments passed to underlying last_obj method
        """
        return self.mongo.last_obj(
            self.collection_name, match, timestamp_field=timestamp_field,
            fields=fields, ignore_fields=ignore_fields, **kwargs
        )

    def obj_id_set(self, match):
        """Return set of ObjectIds for matching documents

        - match: dictionary representing the documents to match
        """
        return self.mongo.obj_id_set(self.collection_name, match)

    @property
    def size(self):
        """Return number of documents in the collection"""
        return self.total_documents()

    @property
    def name(self):
        """Return the collection name"""
        return self.collection_name

    def __len__(self):
        """Return number of documents in the collection"""
        return self.size

    def __repr__(self):
        """Return string representation of Collection"""
        return "Collection('{}', size={})".format(self.collection_name, self.size)
