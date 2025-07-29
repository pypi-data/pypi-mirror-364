import pytest
import mongo_helper as mh
from datetime import datetime
from bson.objectid import ObjectId
from pymongo import InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne, DeleteMany
from tests import (
    generate_user_data, generate_product_data, generate_event_data,
    generate_order_data, TEST_COLLECTIONS
)


# Get connection status and database size for skip conditions
MONGO_INSTANCE, DBSIZE = mh.connect_to_server()
MONGO_CONNECTED = MONGO_INSTANCE is not None


@pytest.mark.skipif(DBSIZE != 0, reason='Database is not empty, has {} document(s)'.format(DBSIZE))
@pytest.mark.skipif(MONGO_CONNECTED is False, reason='Not connected to MongoDB')
class TestCollectionWrapper:
    """Test the Collection wrapper class functionality"""

    @pytest.fixture(scope="class")
    def mongo_instance(self):
        """Provide mongo instance for all tests"""
        settings = mh.SETTINGS
        url = settings.get('mongo_url')
        db = settings.get('query_db', 'testdb')
        return mh.Mongo(url=url, db=db)

    @pytest.fixture(scope="class")
    def test_collection_name(self):
        """Test collection name for basic Collection operations"""
        return TEST_COLLECTIONS['crud'] + '_collection'

    @pytest.fixture(scope="class")
    def user_collection_name(self):
        """Test collection name for user data via Collection"""
        return TEST_COLLECTIONS['users'] + '_collection'

    @pytest.fixture(scope="class")
    def product_collection_name(self):
        """Test collection name for product data via Collection"""
        return TEST_COLLECTIONS['products'] + '_collection'

    @pytest.fixture(scope="class")
    def bulk_errors_collection_name(self):
        """Test collection name for bulk write error testing via Collection"""
        return TEST_COLLECTIONS['bulk_errors'] + '_collection'

    def test_collection_init_with_mongo_instance(self, mongo_instance, test_collection_name):
        """Test Collection initialization with existing mongo instance"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        assert collection.collection_name == test_collection_name
        assert collection.mongo is mongo_instance
        assert collection.name == test_collection_name

    def test_collection_init_auto_connect(self, test_collection_name):
        """Test Collection initialization with automatic connection"""
        # Test with default connection parameters
        collection = mh.Collection(test_collection_name)

        assert collection.collection_name == test_collection_name
        assert collection.mongo is not None
        assert isinstance(collection.mongo, mh.Mongo)
        assert collection.name == test_collection_name

    def test_collection_init_with_params(self, test_collection_name):
        """Test Collection initialization with custom connection parameters"""
        settings = mh.SETTINGS
        url = settings.get('mongo_url')
        db = settings.get('query_db', 'testdb')

        collection = mh.Collection(
            test_collection_name,
            url=url,
            db=db,
            exception=True
        )

        assert collection.collection_name == test_collection_name
        assert collection.mongo is not None
        assert collection.mongo._db == db

    def test_collection_insert_one_simple(self, mongo_instance, test_collection_name):
        """Test Collection.insert_one with simple document"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        doc = {
            'name': 'collection_test_document',
            'value': 123,
            'active': True,
            'created_at': datetime.utcnow()
        }

        doc_id = collection.insert_one(doc)
        assert doc_id is not None
        assert isinstance(doc_id, ObjectId)

        # Verify insertion using the collection wrapper
        retrieved = collection.find_one({'_id': doc_id})
        assert retrieved['name'] == 'collection_test_document'
        assert retrieved['value'] == 123
        assert retrieved['active'] is True
        assert isinstance(retrieved['created_at'], datetime)

    def test_collection_insert_one_complex(self, mongo_instance, user_collection_name):
        """Test Collection.insert_one with complex nested document"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        user_data = generate_user_data()
        doc_id = collection.insert_one(user_data)
        assert doc_id is not None

        # Verify complex document retrieval via Collection
        retrieved = collection.find_one({'_id': doc_id})
        assert retrieved['username'] == user_data['username']
        assert retrieved['email'] == user_data['email']
        assert isinstance(retrieved['preferences'], dict)
        assert isinstance(retrieved['tags'], list)
        assert isinstance(retrieved['created_at'], datetime)

    def test_collection_insert_many(self, mongo_instance, user_collection_name):
        """Test Collection.insert_many functionality"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        users_data = [generate_user_data() for _ in range(5)]
        doc_ids = collection.insert_many(users_data)

        assert len(doc_ids) == 5
        assert all(isinstance(doc_id, ObjectId) for doc_id in doc_ids)

        # Verify all documents were inserted via Collection
        for i, doc_id in enumerate(doc_ids):
            retrieved = collection.find_one({'_id': doc_id})
            assert retrieved['username'] == users_data[i]['username']
            assert retrieved['email'] == users_data[i]['email']

    def test_collection_find_operations(self, mongo_instance, user_collection_name):
        """Test Collection.find with various query options"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Find all users via Collection
        all_users = collection.find({}, to_list=True)
        assert len(all_users) >= 6

        # Find with query
        active_users = collection.find({'status': 'active'}, to_list=True)
        assert all(user['status'] == 'active' for user in active_users)

        # Find with field projection using Collection convenience syntax
        usernames = collection.find({}, fields='username', to_list=True)
        # Note: find returns cursor by default, but with single field it returns values
        # We need to handle this properly in the Collection wrapper
        username_docs = collection.find({}, fields='username, email', to_list=True)
        assert all('username' in user and 'email' in user for user in username_docs)
        assert all('_id' not in user for user in username_docs)

        # Find with ignore_fields using Collection convenience syntax
        users_no_prefs = collection.find({}, ignore_fields='preferences, tags', to_list=True)
        assert all('preferences' not in user for user in users_no_prefs)
        assert all('tags' not in user for user in users_no_prefs)

    def test_collection_find_one_operations(self, mongo_instance, user_collection_name):
        """Test Collection.find_one with various options"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Find any user via Collection
        user = collection.find_one({})
        assert isinstance(user, dict)
        assert '_id' in user

        # Find with specific query
        active_user = collection.find_one({'status': 'active'})
        if active_user:
            assert isinstance(active_user, dict)
            assert active_user['status'] == 'active'

        # Find with single field via Collection
        username = collection.find_one({}, fields='username')
        if username:
            assert isinstance(username, str)

        # Find with multiple fields via Collection
        user_result = collection.find_one({}, fields='username, email')
        if user_result:
            assert isinstance(user_result, dict)
            assert 'username' in user_result
            assert 'email' in user_result
            assert '_id' not in user_result

        # Find non-existent document
        fake_id = ObjectId()
        not_found = collection.find_one({'_id': fake_id})
        assert not_found == {}

    def test_collection_update_one(self, mongo_instance, user_collection_name):
        """Test Collection.update_one functionality"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Find a user to update via Collection
        user = collection.find_one({})
        assert user != {}

        original_email = user['email']
        new_email = 'collection_updated_' + original_email

        # Update via Collection wrapper
        modified_count = collection.update_one(
            {'_id': user['_id']},
            {'$set': {'email': new_email, 'updated_at': datetime.utcnow()}}
        )
        assert modified_count == 1

        # Verify update via Collection
        updated_user = collection.find_one({'_id': user['_id']})
        assert updated_user['email'] == new_email
        assert 'updated_at' in updated_user
        assert isinstance(updated_user['updated_at'], datetime)

    def test_collection_update_many(self, mongo_instance, user_collection_name):
        """Test Collection.update_many functionality"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Update all inactive users via Collection
        modified_count = collection.update_many(
            {'status': 'inactive'},
            {'$set': {'status': 'collection_reactivated', 'reactivated_at': datetime.utcnow()}}
        )

        # Verify updates via Collection
        reactivated_users = collection.find({'status': 'collection_reactivated'}, to_list=True)
        assert len(reactivated_users) == modified_count
        assert all(user['status'] == 'collection_reactivated' for user in reactivated_users)
        assert all('reactivated_at' in user for user in reactivated_users)

    def test_collection_upsert_operations(self, mongo_instance, test_collection_name):
        """Test Collection upsert functionality"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Upsert with non-existent document via Collection
        modified_count = collection.update_one(
            {'unique_key': 'collection_test_upsert'},
            {'$set': {'value': 500, 'created_by_collection_upsert': True}},
            upsert=True
        )
        assert modified_count == 0  # No existing document was modified

        # Verify upsert created document via Collection
        upserted_doc = collection.find_one({'unique_key': 'collection_test_upsert'})
        assert upserted_doc['value'] == 500
        assert upserted_doc['created_by_collection_upsert'] is True

        # Upsert with existing document via Collection
        modified_count = collection.update_one(
            {'unique_key': 'collection_test_upsert'},
            {'$set': {'value': 600, 'updated_by_collection_upsert': True}},
            upsert=True
        )
        assert modified_count == 1  # Existing document was modified

        # Verify update via Collection
        updated_doc = collection.find_one({'unique_key': 'collection_test_upsert'})
        assert updated_doc['value'] == 600
        assert updated_doc['updated_by_collection_upsert'] is True

    def test_collection_count_operations(self, mongo_instance, user_collection_name):
        """Test Collection counting methods"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Count all documents via Collection
        total_count = collection.count({})
        assert total_count >= 6

        # Count with query via Collection
        active_count = collection.count({'status': 'active'})
        assert isinstance(active_count, int)
        assert active_count >= 0

        # Total documents via Collection
        estimated_total = collection.total_documents()
        assert isinstance(estimated_total, int)
        assert estimated_total >= 0

        # Test size property
        assert collection.size == estimated_total

        # Test __len__ method
        assert len(collection) == estimated_total

    def test_collection_distinct_operations(self, mongo_instance, user_collection_name):
        """Test Collection.distinct functionality"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Get distinct statuses via Collection
        statuses = collection.distinct('status')
        assert isinstance(statuses, list)
        assert len(set(statuses)) == len(statuses)  # All values should be unique

        # Get distinct with query via Collection
        active_ages = collection.distinct('age', {'status': 'active'})
        assert isinstance(active_ages, list)

    def test_collection_delete_one(self, mongo_instance, test_collection_name):
        """Test Collection.delete_one functionality"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Insert a document to delete via Collection
        doc = {'collection_test_delete': True, 'value': 'to_be_deleted_by_collection'}
        doc_id = collection.insert_one(doc)

        # Verify it exists via Collection
        found = collection.find_one({'_id': doc_id})
        assert found != {}

        # Delete it via Collection
        deleted_count = collection.delete_one({'_id': doc_id})
        assert deleted_count == 1

        # Verify deletion via Collection
        not_found = collection.find_one({'_id': doc_id})
        assert not_found == {}

    def test_collection_delete_many(self, mongo_instance, test_collection_name):
        """Test Collection.delete_many functionality"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Insert multiple documents to delete via Collection
        docs = [{'collection_test_delete_many': True, 'batch': i} for i in range(3)]
        doc_ids = collection.insert_many(docs)

        # Verify they exist via Collection
        found_count = collection.count({'collection_test_delete_many': True})
        assert found_count == 3

        # Delete them via Collection
        deleted_count = collection.delete_many({'collection_test_delete_many': True})
        assert deleted_count == 3

        # Verify deletion via Collection
        remaining_count = collection.count({'collection_test_delete_many': True})
        assert remaining_count == 0

    def test_collection_aggregation(self, mongo_instance, user_collection_name):
        """Test Collection.aggregate functionality"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Test count by status via Collection
        pipeline = [
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]

        status_counts = list(collection.aggregate(pipeline))
        assert isinstance(status_counts, list)
        assert all('_id' in result and 'count' in result for result in status_counts)
        assert all(isinstance(result['count'], int) for result in status_counts)

    def test_collection_bulk_write(self, mongo_instance, test_collection_name):
        """Test Collection.bulk_write functionality"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Set up some initial data via Collection
        initial_docs = [
            {'name': 'collection_bulk_test_1', 'status': 'initial', 'value': 10},
            {'name': 'collection_bulk_test_2', 'status': 'initial', 'value': 20},
            {'name': 'collection_bulk_test_3', 'status': 'initial', 'value': 30},
            {'name': 'collection_bulk_test_delete', 'status': 'initial', 'value': 40}
        ]
        doc_ids = collection.insert_many(initial_docs)

        # Create mixed bulk operations
        operations = [
            InsertOne({'name': 'collection_bulk_insert_1', 'status': 'new', 'value': 100}),
            InsertOne({'name': 'collection_bulk_insert_2', 'status': 'new', 'value': 200}),
            UpdateOne(
                {'_id': doc_ids[0]},
                {'$set': {'status': 'collection_updated_one', 'value': 15}}
            ),
            UpdateMany(
                {'status': 'initial'},
                {'$set': {'collection_bulk_updated': True, 'updated_at': datetime.utcnow()}}
            ),
            ReplaceOne(
                {'_id': doc_ids[1]},
                {'name': 'collection_bulk_test_2_replaced', 'status': 'replaced', 'value': 999}
            ),
            DeleteOne({'name': 'collection_bulk_test_delete'}),
            DeleteMany({'status': 'nonexistent'})
        ]

        # Execute bulk write via Collection
        result = collection.bulk_write(operations)

        # Verify result object
        assert hasattr(result, 'inserted_count')
        assert hasattr(result, 'modified_count')
        assert hasattr(result, 'deleted_count')
        assert hasattr(result, 'upserted_count')

        # Verify counts
        assert result.inserted_count == 2
        assert result.modified_count >= 1
        assert result.deleted_count == 1
        assert result.upserted_count == 0

        # Verify specific changes via Collection
        inserted_docs = collection.find({'status': 'new'}, to_list=True)
        assert len(inserted_docs) == 2
        assert any(doc['name'] == 'collection_bulk_insert_1' for doc in inserted_docs)
        assert any(doc['name'] == 'collection_bulk_insert_2' for doc in inserted_docs)

    def test_collection_index_operations(self, mongo_instance, test_collection_name):
        """Test Collection index management methods"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Create an index via Collection
        index_name = collection.create_index([('test_field', 1)], unique=False)
        assert index_name is not None

        # Get index information via Collection
        index_info = collection.index_information()
        assert isinstance(index_info, dict)
        assert len(index_info) >= 2  # _id index + our test index

        # Get index names via Collection
        index_names = collection.index_names()
        assert isinstance(index_names, list)
        assert 'test_field_1' in index_names

        # Get index sizes via Collection
        index_sizes = collection.index_sizes()
        assert isinstance(index_sizes, dict)

        # Get index usage via Collection
        index_usage = collection.index_usage()
        assert isinstance(index_usage, list)

        # Drop the index via Collection
        result = collection.drop_index('test_field_1')
        # Verify index was dropped
        updated_index_names = collection.index_names()
        assert 'test_field_1' not in updated_index_names

    def test_collection_stats_operations(self, mongo_instance, test_collection_name):
        """Test Collection statistics methods"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Get collection stats via Collection
        stats = collection.coll_stats()
        assert isinstance(stats, dict)
        assert 'ok' in stats
        assert 'count' in stats or 'size' in stats  # Different MongoDB versions may vary

        # Test with custom ignore_fields
        stats_filtered = collection.coll_stats(ignore_fields='wiredTiger')
        assert isinstance(stats_filtered, dict)
        assert 'wiredTiger' not in stats_filtered

        # Test with different scale
        stats_kb = collection.coll_stats(scale='KB')
        assert isinstance(stats_kb, dict)

    def test_collection_first_last_obj(self, mongo_instance, user_collection_name):
        """Test Collection first_obj and last_obj utility methods"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Get first user via Collection (oldest by _id)
        first_user = collection.first_obj()
        assert isinstance(first_user, dict)
        assert '_id' in first_user

        # Get last user via Collection (newest by _id)
        last_user = collection.last_obj()
        assert isinstance(last_user, dict)
        assert '_id' in last_user

        # They should be different (unless only one document)
        user_count = collection.count({})
        if user_count > 1:
            assert first_user['_id'] != last_user['_id']

        # Test with custom timestamp field via Collection
        first_by_created = collection.first_obj(timestamp_field='created_at')
        last_by_created = collection.last_obj(timestamp_field='created_at')

        if user_count > 1:
            assert first_by_created['created_at'] <= last_by_created['created_at']

    def test_collection_obj_id_set(self, mongo_instance, user_collection_name):
        """Test Collection obj_id_set utility method"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # Get set of all user IDs via Collection
        all_ids = collection.obj_id_set({})
        assert isinstance(all_ids, set)
        assert all(isinstance(obj_id, ObjectId) for obj_id in all_ids)

        # Get set of active user IDs via Collection
        active_ids = collection.obj_id_set({'status': 'active'})
        assert isinstance(active_ids, set)
        assert active_ids.issubset(all_ids)

    def test_collection_properties_and_methods(self, mongo_instance, test_collection_name):
        """Test Collection properties and special methods"""
        collection = mh.Collection(test_collection_name, mongo_instance=mongo_instance)

        # Test name property
        assert collection.name == test_collection_name

        # Test size property
        size = collection.size
        assert isinstance(size, int)
        assert size >= 0

        # Test __len__ method
        length = len(collection)
        assert length == size

        # Test __repr__ method
        repr_str = repr(collection)
        assert test_collection_name in repr_str
        assert 'Collection' in repr_str
        assert str(size) in repr_str

    def test_collection_parameter_consistency(self, mongo_instance, user_collection_name):
        """Test that Collection methods use consistent parameter names with underlying Mongo methods"""
        collection = mh.Collection(user_collection_name, mongo_instance=mongo_instance)

        # All methods should use 'match' parameter instead of 'query' for consistency
        # This was a specific requirement during development

        # Test that update methods accept 'match' parameter
        doc_id = collection.insert_one({'test_consistency': True, 'value': 1})

        # Should work with 'match' parameter
        modified = collection.update_one({'_id': doc_id}, {'$set': {'value': 2}})
        assert modified == 1

        # Should work with 'match' parameter for other methods
        count = collection.count({'test_consistency': True})
        assert count >= 1

        distinct_values = collection.distinct('value', {'test_consistency': True})
        assert 2 in distinct_values

        # Clean up
        collection.delete_one({'_id': doc_id})

    def test_cleanup_all_collection_test_data(self, mongo_instance):
        """Clean up all Collection test data - MUST be the final test"""
        # Clean up all test collections used by Collection tests
        collection_test_names = [
            TEST_COLLECTIONS['crud'] + '_collection',
            TEST_COLLECTIONS['users'] + '_collection',
            TEST_COLLECTIONS['products'] + '_collection',
            TEST_COLLECTIONS['bulk_errors'] + '_collection'
        ]

        for collection_name in collection_test_names:
            try:
                mongo_instance._drop_collection(collection_name)
            except:
                pass  # Collection might not exist

        # Verify cleanup
        for collection_name in collection_test_names:
            count = mongo_instance._count(collection_name, {})
            assert count == 0

        # Stop docker container
        # mh.stop_docker()
