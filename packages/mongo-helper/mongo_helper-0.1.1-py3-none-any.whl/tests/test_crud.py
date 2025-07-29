import pytest
import mongo_helper as mh
from datetime import datetime, date
from bson.objectid import ObjectId
from pymongo import InsertOne, UpdateOne, UpdateMany, ReplaceOne, DeleteOne, DeleteMany
from pymongo.errors import BulkWriteError, InvalidOperation
from tests import (
    generate_user_data, generate_product_data, generate_event_data,
    generate_order_data, TEST_COLLECTIONS
)


# Get connection status and database size for skip conditions
MONGO_INSTANCE, DBSIZE = mh.connect_to_server()
MONGO_CONNECTED = MONGO_INSTANCE is not None


@pytest.mark.skipif(DBSIZE != 0, reason='Database is not empty, has {} document(s)'.format(DBSIZE))
@pytest.mark.skipif(MONGO_CONNECTED is False, reason='Not connected to MongoDB')
class TestMongoCRUD:

    @pytest.fixture(scope="class")
    def mongo_instance(self):
        """Provide mongo instance for all tests"""
        settings = mh.SETTINGS
        url = settings.get('mongo_url')
        db = settings.get('query_db', 'testdb')
        return mh.Mongo(url=url, db=db)

    @pytest.fixture(scope="class")
    def test_collection(self):
        """Test collection name for basic CRUD operations"""
        return TEST_COLLECTIONS['crud']

    @pytest.fixture(scope="class")
    def user_collection(self):
        """Test collection name for user data"""
        return TEST_COLLECTIONS['users']

    @pytest.fixture(scope="class")
    def product_collection(self):
        """Test collection name for product data"""
        return TEST_COLLECTIONS['products']

    @pytest.fixture(scope="class")
    def bulk_errors_collection(self):
        """Test collection name for bulk write error testing"""
        return TEST_COLLECTIONS['bulk_errors']

    def test_mongo_connection(self, mongo_instance):
        """Test basic mongo connection and database operations"""
        # Test database listing
        databases = mongo_instance.get_databases()
        assert isinstance(databases, list)

        # Test collections listing
        collections = mongo_instance.get_collections()
        assert isinstance(collections, list)

        # Test database stats
        stats = mongo_instance.db_stats()
        assert isinstance(stats, dict)
        assert 'ok' in stats

    def test_insert_one_simple(self, mongo_instance, test_collection):
        """Test inserting a single simple document"""
        doc = {
            'name': 'test_document',
            'value': 42,
            'active': True,
            'created_at': datetime.utcnow()
        }

        doc_id = mongo_instance._insert_one(test_collection, doc)
        assert doc_id is not None
        assert isinstance(doc_id, ObjectId)

        # Verify insertion
        retrieved = mongo_instance._find_one(test_collection, {'_id': doc_id})
        assert retrieved['name'] == 'test_document'
        assert retrieved['value'] == 42
        assert retrieved['active'] is True
        assert isinstance(retrieved['created_at'], datetime)

    def test_insert_one_complex(self, mongo_instance, user_collection):
        """Test inserting a complex document with nested data"""
        user_data = generate_user_data()

        doc_id = mongo_instance._insert_one(user_collection, user_data)
        assert doc_id is not None

        # Verify complex document retrieval
        retrieved = mongo_instance._find_one(user_collection, {'_id': doc_id})
        assert retrieved['username'] == user_data['username']
        assert retrieved['email'] == user_data['email']
        assert isinstance(retrieved['preferences'], dict)
        assert isinstance(retrieved['tags'], list)
        assert isinstance(retrieved['created_at'], datetime)

    def test_insert_many(self, mongo_instance, user_collection):
        """Test inserting multiple documents"""
        users_data = [generate_user_data() for _ in range(5)]

        doc_ids = mongo_instance._insert_many(user_collection, users_data)
        assert len(doc_ids) == 5
        assert all(isinstance(doc_id, ObjectId) for doc_id in doc_ids)

        # Verify all documents were inserted
        for i, doc_id in enumerate(doc_ids):
            retrieved = mongo_instance._find_one(user_collection, {'_id': doc_id})
            assert retrieved['username'] == users_data[i]['username']
            assert retrieved['email'] == users_data[i]['email']

    def test_find_operations(self, mongo_instance, user_collection):
        """Test various find operations and projections"""
        # Find all users
        all_users = list(mongo_instance._find(user_collection, {}))
        assert len(all_users) >= 6  # 1 from complex + 5 from insert_many

        # Find with query
        active_users = list(mongo_instance._find(user_collection, {'status': 'active'}))
        assert all(user['status'] == 'active' for user in active_users)

        # Find with field projection
        usernames = mongo_instance._find(user_collection, {}, fields='username')
        assert isinstance(usernames, list)
        assert all(isinstance(username, str) for username in usernames if username is not None)

        # Find with multiple field projection
        user_info = list(mongo_instance._find(user_collection, {}, fields='username, email'))
        assert all('username' in user and 'email' in user for user in user_info)
        assert all('_id' not in user for user in user_info)  # _id should be excluded

        # Find with ignore_fields
        users_no_prefs = list(mongo_instance._find(user_collection, {}, ignore_fields='preferences, tags'))
        assert all('preferences' not in user for user in users_no_prefs)
        assert all('tags' not in user for user in users_no_prefs)

    def test_find_one_operations(self, mongo_instance, user_collection):
        """Test find_one with various options"""
        # Find any user
        user = mongo_instance._find_one(user_collection, {})
        assert isinstance(user, dict)
        assert '_id' in user

        # Find with specific query
        active_user = mongo_instance._find_one(user_collection, {'status': 'active'})
        if active_user:  # May not exist depending on random data
            assert isinstance(active_user, dict)
            assert active_user['status'] == 'active'

        # Find with single field
        username = mongo_instance._find_one(user_collection, {}, fields='username')
        if username:
            assert isinstance(username, str)

        # Find with multiple fields
        user_result = mongo_instance._find_one(user_collection, {}, fields='username, email')
        if user_result:
            assert isinstance(user_result, dict)
            assert 'username' in user_result
            assert 'email' in user_result
            assert '_id' not in user_result

        # Find non-existent document
        fake_id = ObjectId()
        not_found = mongo_instance._find_one(user_collection, {'_id': fake_id})
        assert not_found == {}

    def test_update_one(self, mongo_instance, user_collection):
        """Test updating a single document"""
        # Find a user to update
        user = mongo_instance._find_one(user_collection, {})
        assert user != {}

        original_email = user['email']
        new_email = 'updated_' + original_email

        # Update the user
        modified_count = mongo_instance._update_one(
            user_collection,
            {'_id': user['_id']},
            {'$set': {'email': new_email, 'updated_at': datetime.utcnow()}}
        )
        assert modified_count == 1

        # Verify update
        updated_user = mongo_instance._find_one(user_collection, {'_id': user['_id']})
        assert updated_user['email'] == new_email
        assert 'updated_at' in updated_user
        assert isinstance(updated_user['updated_at'], datetime)

    def test_update_many(self, mongo_instance, user_collection):
        """Test updating multiple documents"""
        # Update all inactive users
        modified_count = mongo_instance._update_many(
            user_collection,
            {'status': 'inactive'},
            {'$set': {'status': 'reactivated', 'reactivated_at': datetime.utcnow()}}
        )

        # Verify updates
        reactivated_users = list(mongo_instance._find(user_collection, {'status': 'reactivated'}))
        assert len(reactivated_users) == modified_count
        assert all(user['status'] == 'reactivated' for user in reactivated_users)
        assert all('reactivated_at' in user for user in reactivated_users)

    def test_upsert_operations(self, mongo_instance, test_collection):
        """Test upsert functionality"""
        # Upsert with non-existent document
        modified_count = mongo_instance._update_one(
            test_collection,
            {'unique_key': 'test_upsert'},
            {'$set': {'value': 100, 'created_by_upsert': True}},
            upsert=True
        )
        assert modified_count == 0  # No existing document was modified, but one was inserted

        # Verify upsert created document
        upserted_doc = mongo_instance._find_one(test_collection, {'unique_key': 'test_upsert'})
        assert upserted_doc['value'] == 100
        assert upserted_doc['created_by_upsert'] is True

        # Upsert with existing document
        modified_count = mongo_instance._update_one(
            test_collection,
            {'unique_key': 'test_upsert'},
            {'$set': {'value': 200, 'updated_by_upsert': True}},
            upsert=True
        )
        assert modified_count == 1  # Existing document was modified

        # Verify update
        updated_doc = mongo_instance._find_one(test_collection, {'unique_key': 'test_upsert'})
        assert updated_doc['value'] == 200
        assert updated_doc['updated_by_upsert'] is True

    def test_count_operations(self, mongo_instance, user_collection):
        """Test document counting"""
        # Count all documents
        total_count = mongo_instance._count(user_collection, {})
        assert total_count >= 6

        # Count with query
        active_count = mongo_instance._count(user_collection, {'status': 'active'})
        assert isinstance(active_count, int)
        assert active_count >= 0

        # Total documents (estimation)
        estimated_total = mongo_instance.total_documents(user_collection)
        assert isinstance(estimated_total, int)
        assert estimated_total >= 0

    def test_distinct_operations(self, mongo_instance, user_collection):
        """Test distinct value queries"""
        # Get distinct statuses
        statuses = mongo_instance._distinct(user_collection, 'status')
        assert isinstance(statuses, list)
        assert len(set(statuses)) == len(statuses)  # All values should be unique

        # Get distinct with query
        active_ages = mongo_instance._distinct(
            user_collection,
            'age',
            {'status': 'active'}
        )
        assert isinstance(active_ages, list)

    def test_delete_one(self, mongo_instance, test_collection):
        """Test deleting a single document"""
        # Insert a document to delete
        doc = {'test_delete': True, 'value': 'to_be_deleted'}
        doc_id = mongo_instance._insert_one(test_collection, doc)

        # Verify it exists
        found = mongo_instance._find_one(test_collection, {'_id': doc_id})
        assert found != {}

        # Delete it
        deleted_count = mongo_instance._delete_one(test_collection, {'_id': doc_id})
        assert deleted_count == 1

        # Verify deletion
        not_found = mongo_instance._find_one(test_collection, {'_id': doc_id})
        assert not_found == {}

    def test_delete_many(self, mongo_instance, test_collection):
        """Test deleting multiple documents"""
        # Insert multiple documents to delete
        docs = [{'test_delete_many': True, 'batch': i} for i in range(3)]
        doc_ids = mongo_instance._insert_many(test_collection, docs)

        # Verify they exist
        found_count = mongo_instance._count(test_collection, {'test_delete_many': True})
        assert found_count == 3

        # Delete them
        deleted_count = mongo_instance._delete_many(test_collection, {'test_delete_many': True})
        assert deleted_count == 3

        # Verify deletion
        remaining_count = mongo_instance._count(test_collection, {'test_delete_many': True})
        assert remaining_count == 0

    def test_complex_product_operations(self, mongo_instance, product_collection):
        """Test CRUD operations with complex product data"""
        # Insert products
        products = [generate_product_data() for _ in range(10)]
        product_ids = mongo_instance._insert_many(product_collection, products)
        assert len(product_ids) == 10

        # Test complex queries
        expensive_products = list(mongo_instance._find(
            product_collection,
            {'price': {'$gte': 100}}
        ))
        assert all(product['price'] >= 100 for product in expensive_products)

        # Test nested field queries
        large_products = list(mongo_instance._find(
            product_collection,
            {'dimensions.length': {'$gte': 30}}
        ))
        assert all(product['dimensions']['length'] >= 30 for product in large_products)

        # Test array field queries
        featured_products = list(mongo_instance._find(
            product_collection,
            {'featured': True}
        ))
        assert all(product['featured'] is True for product in featured_products)

        # Update product ratings
        mongo_instance._update_many(
            product_collection,
            {'rating': {'$lt': 3.0}},
            {'$set': {'needs_improvement': True}}
        )

        # Verify updates
        flagged_products = list(mongo_instance._find(
            product_collection,
            {'needs_improvement': True}
        ))
        assert all(product['rating'] < 3.0 for product in flagged_products)

    def test_temporal_queries(self, mongo_instance, user_collection):
        """Test queries with datetime fields using query helper functions"""
        # Find users created in the last 365 days
        last_year_query = mh.get_days_ago_query(days_ago=365, timestamp_field='created_at')
        recent_users = list(mongo_instance._find(user_collection, last_year_query))
        # Note: All test users should match since they're created with random dates within 365 days

        # Find users who logged in within the last 24 hours
        last_day_query = mh.get_hours_ago_query(hours_ago=24, timestamp_field='last_login')
        recent_logins = list(mongo_instance._find(user_collection, last_day_query))
        # Note: May be empty depending on random test data

        # Find users using ObjectId timestamp (within last 10 minutes of creation)
        recent_by_id = mh.get_minutes_ago_query(minutes_ago=10)
        recently_created = list(mongo_instance._find(user_collection, recent_by_id))
        # Should include users created during this test run

        # Verify query structure
        assert '_id' in recent_by_id
        assert '$gte' in recent_by_id['_id']
        assert '$lt' in recent_by_id['_id']
        assert isinstance(recent_by_id['_id']['$gte'], ObjectId)
        assert isinstance(recent_by_id['_id']['$lt'], ObjectId)

        # Test with custom timestamp field
        days_query = mh.get_days_ago_query(days_ago=30, timestamp_field='created_at')
        assert 'created_at' in days_query
        assert '$gte' in days_query['created_at']
        assert isinstance(days_query['created_at']['$gte'], datetime)

    def test_aggregation_basics(self, mongo_instance, user_collection):
        """Test basic aggregation functionality"""
        # Test count by status
        pipeline = [
            {'$group': {'_id': '$status', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]

        status_counts = list(mongo_instance._aggregate(user_collection, pipeline))
        assert isinstance(status_counts, list)
        assert all('_id' in result and 'count' in result for result in status_counts)
        assert all(isinstance(result['count'], int) for result in status_counts)

    def test_first_last_obj(self, mongo_instance, user_collection):
        """Test first_obj and last_obj utility methods"""
        # Get first user (oldest by _id)
        first_user = mongo_instance.first_obj(user_collection)
        assert isinstance(first_user, dict)
        assert '_id' in first_user

        # Get last user (newest by _id)
        last_user = mongo_instance.last_obj(user_collection)
        assert isinstance(last_user, dict)
        assert '_id' in last_user

        # They should be different (unless only one document)
        user_count = mongo_instance._count(user_collection, {})
        if user_count > 1:
            assert first_user['_id'] != last_user['_id']

        # Test with custom timestamp field
        first_by_created = mongo_instance.first_obj(
            user_collection,
            timestamp_field='created_at'
        )
        last_by_created = mongo_instance.last_obj(
            user_collection,
            timestamp_field='created_at'
        )

        if user_count > 1:
            assert first_by_created['created_at'] <= last_by_created['created_at']

    def test_obj_id_set(self, mongo_instance, user_collection):
        """Test obj_id_set utility method"""
        # Get set of all user IDs
        all_ids = mongo_instance.obj_id_set(user_collection, {})
        assert isinstance(all_ids, set)
        assert all(isinstance(obj_id, ObjectId) for obj_id in all_ids)

        # Get set of active user IDs
        active_ids = mongo_instance.obj_id_set(user_collection, {'status': 'active'})
        assert isinstance(active_ids, set)
        assert active_ids.issubset(all_ids)

    def test_error_handling(self, mongo_instance, test_collection):
        """Test error handling in CRUD operations"""
        # Test field/ignore_fields mutual exclusion
        with pytest.raises(Exception, match='Cannot specify both'):
            mongo_instance._find_one(
                test_collection,
                {},
                fields='name',
                ignore_fields='value'
            )

        with pytest.raises(Exception, match='Cannot specify both'):
            mongo_instance._find(
                test_collection,
                {},
                fields='name',
                ignore_fields='value'
            )

    def test_bulk_write_mixed_operations(self, mongo_instance, test_collection):
        """Test bulk write operations with mixed operation types"""
        # Set up some initial data
        initial_docs = [
            {'name': 'bulk_test_1', 'status': 'initial', 'value': 10},
            {'name': 'bulk_test_2', 'status': 'initial', 'value': 20},
            {'name': 'bulk_test_3', 'status': 'initial', 'value': 30},
            {'name': 'bulk_test_delete', 'status': 'initial', 'value': 40}
        ]
        doc_ids = mongo_instance._insert_many(test_collection, initial_docs)

        # Create mixed bulk operations
        operations = [
            # Insert new documents
            InsertOne({'name': 'bulk_insert_1', 'status': 'new', 'value': 100}),
            InsertOne({'name': 'bulk_insert_2', 'status': 'new', 'value': 200}),

            # Update one specific document
            UpdateOne(
                {'_id': doc_ids[0]},
                {'$set': {'status': 'updated_one', 'value': 15}}
            ),

            # Update many documents matching criteria
            UpdateMany(
                {'status': 'initial'},
                {'$set': {'bulk_updated': True, 'updated_at': datetime.utcnow()}}
            ),

            # Replace one document
            ReplaceOne(
                {'_id': doc_ids[1]},
                {'name': 'bulk_test_2_replaced', 'status': 'replaced', 'value': 999}
            ),

            # Delete one specific document
            DeleteOne({'name': 'bulk_test_delete'}),

            # Delete many documents (none should match this criteria yet)
            DeleteMany({'status': 'nonexistent'})
        ]

        # Execute bulk write
        result = mongo_instance._bulk_write(test_collection, operations)

        # Verify result object
        assert hasattr(result, 'inserted_count')
        assert hasattr(result, 'modified_count')
        assert hasattr(result, 'deleted_count')
        assert hasattr(result, 'upserted_count')

        # Verify counts
        assert result.inserted_count == 2  # 2 InsertOne operations
        assert result.modified_count >= 1  # At least UpdateOne should modify 1 doc
        assert result.deleted_count == 1   # 1 DeleteOne operation (DeleteMany matched 0)
        assert result.upserted_count == 0  # No upserts in this test

        # Verify specific changes
        # Check inserted documents
        inserted_docs = list(mongo_instance._find(test_collection, {'status': 'new'}))
        assert len(inserted_docs) == 2
        assert any(doc['name'] == 'bulk_insert_1' for doc in inserted_docs)
        assert any(doc['name'] == 'bulk_insert_2' for doc in inserted_docs)

        # Check updated document
        updated_doc = mongo_instance._find_one(test_collection, {'_id': doc_ids[0]})
        assert updated_doc['status'] == 'updated_one'
        assert updated_doc['value'] == 15

        # Check bulk updated documents
        bulk_updated_docs = list(mongo_instance._find(test_collection, {'bulk_updated': True}))
        assert len(bulk_updated_docs) >= 1

        # Check replaced document
        replaced_doc = mongo_instance._find_one(test_collection, {'_id': doc_ids[1]})
        assert replaced_doc['name'] == 'bulk_test_2_replaced'
        assert replaced_doc['status'] == 'replaced'
        assert replaced_doc['value'] == 999

        # Check deleted document
        deleted_doc = mongo_instance._find_one(test_collection, {'name': 'bulk_test_delete'})
        assert deleted_doc == {}

    def test_bulk_write_ordered_vs_unordered(self, mongo_instance, test_collection):
        """Test difference between ordered and unordered bulk operations"""
        # Test ordered operations (default)
        operations_ordered = [
            InsertOne({'name': 'ordered_test_1', 'value': 1}),
            InsertOne({'name': 'ordered_test_2', 'value': 2}),
            InsertOne({'name': 'ordered_test_3', 'value': 3})
        ]

        result_ordered = mongo_instance._bulk_write(test_collection, operations_ordered, ordered=True)
        assert result_ordered.inserted_count == 3

        # Test unordered operations
        operations_unordered = [
            InsertOne({'name': 'unordered_test_1', 'value': 1}),
            InsertOne({'name': 'unordered_test_2', 'value': 2}),
            InsertOne({'name': 'unordered_test_3', 'value': 3})
        ]

        result_unordered = mongo_instance._bulk_write(test_collection, operations_unordered, ordered=False)
        assert result_unordered.inserted_count == 3

        # Verify all documents were inserted
        ordered_docs = list(mongo_instance._find(test_collection, {'name': {'$regex': '^ordered_test'}}))
        unordered_docs = list(mongo_instance._find(test_collection, {'name': {'$regex': '^unordered_test'}}))
        assert len(ordered_docs) == 3
        assert len(unordered_docs) == 3

    def test_bulk_write_error_handling(self, mongo_instance, bulk_errors_collection):
        """Test bulk write error handling and BulkWriteError"""
        # Create a unique index to cause duplicate key errors
        mongo_instance._create_index(bulk_errors_collection, [('unique_field', 1)], unique=True)

        # Insert initial document
        mongo_instance._insert_one(bulk_errors_collection, {'unique_field': 'duplicate_value', 'data': 'original'})

        # Create operations that will cause a duplicate key error
        operations_with_error = [
            InsertOne({'unique_field': 'valid_value_1', 'data': 'first'}),
            InsertOne({'unique_field': 'duplicate_value', 'data': 'duplicate'}),  # This will fail
            InsertOne({'unique_field': 'valid_value_2', 'data': 'second'})
        ]

        # Test ordered operations (should stop at first error)
        with pytest.raises(BulkWriteError) as exc_info:
            mongo_instance._bulk_write(bulk_errors_collection, operations_with_error, ordered=True)

        bulk_error = exc_info.value
        assert hasattr(bulk_error, 'details')

        # In ordered mode, only the first operation should succeed
        # The second fails, so third is not attempted
        valid_docs = list(mongo_instance._find(bulk_errors_collection, {'unique_field': {'$in': ['valid_value_1', 'valid_value_2']}}))
        assert len(valid_docs) == 1  # Only first should be inserted
        assert valid_docs[0]['unique_field'] == 'valid_value_1'

        # Clean up for next test
        mongo_instance._delete_many(bulk_errors_collection, {'unique_field': 'valid_value_1'})

        # Test unordered operations (should attempt all operations)
        with pytest.raises(BulkWriteError) as exc_info:
            mongo_instance._bulk_write(bulk_errors_collection, operations_with_error, ordered=False)

        bulk_error = exc_info.value
        assert hasattr(bulk_error, 'details')

        # In unordered mode, first and third operations should succeed
        valid_docs = list(mongo_instance._find(bulk_errors_collection, {'unique_field': {'$in': ['valid_value_1', 'valid_value_2']}}))
        assert len(valid_docs) == 2  # Both valid operations should be inserted

        # Clean up index
        mongo_instance._drop_index(bulk_errors_collection, 'unique_field_1')

    def test_bulk_write_empty_operations(self, mongo_instance, test_collection):
        """Test bulk write with empty operations list"""
        with pytest.raises(InvalidOperation):
            result = mongo_instance._bulk_write(test_collection, [])

    def test_bulk_write_with_upsert(self, mongo_instance, test_collection):
        """Test bulk write operations with upsert functionality"""
        # Create operations with upserts
        operations = [
            # Update with upsert - document doesn't exist, should insert
            UpdateOne(
                {'name': 'upsert_test_1'},
                {'$set': {'status': 'upserted', 'value': 100}},
                upsert=True
            ),
            # Replace with upsert - document doesn't exist, should insert
            ReplaceOne(
                {'name': 'upsert_test_2'},
                {'name': 'upsert_test_2', 'status': 'replaced_upsert', 'value': 200},
                upsert=True
            ),
            # Update existing document
            UpdateOne(
                {'name': 'upsert_test_1'},
                {'$set': {'updated': True}}
            )
        ]

        result = mongo_instance._bulk_write(test_collection, operations)

        # Should have upserted 2 documents
        assert result.upserted_count == 2
        assert result.modified_count == 1  # The second UpdateOne on existing doc

        # Verify upserted documents
        upsert_doc_1 = mongo_instance._find_one(test_collection, {'name': 'upsert_test_1'})
        assert upsert_doc_1['status'] == 'upserted'
        assert upsert_doc_1['value'] == 100
        assert upsert_doc_1['updated'] is True

        upsert_doc_2 = mongo_instance._find_one(test_collection, {'name': 'upsert_test_2'})
        assert upsert_doc_2['status'] == 'replaced_upsert'
        assert upsert_doc_2['value'] == 200

    def test_cleanup_all_test_data(self, mongo_instance):
        """Clean up all test data - MUST be the final test"""
        # Clean up all test collections
        for collection_name in TEST_COLLECTIONS.values():
            try:
                mongo_instance._drop_collection(collection_name)
            except:
                pass  # Collection might not exist

        # Verify cleanup
        for collection_name in TEST_COLLECTIONS.values():
            count = mongo_instance._count(collection_name, {})
            assert count == 0

        # Stop docker container
        # mh.stop_docker()
