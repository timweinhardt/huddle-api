import unittest
from unittest.mock import patch

from app.service.post_service import PostService


class TestCreatePost(unittest.TestCase):
    FIXED_UUID = "8ed40121-d5c4-4195-88f9-18a66c751f10"
    FIXED_TIME = "2024-01-01T00:00:00"

    def setUp(self):
        self.table_patcher = patch("app.service.post_service.Table")
        self.time_patcher = patch("app.service.post_service.get_current_time", return_value=self.FIXED_TIME)
        self.uuid_patcher = patch("app.service.post_service.generate_uuid", return_value=self.FIXED_UUID)
        self.mock_table_class = self.table_patcher.start()
        self.mock_table = self.mock_table_class.return_value
        self.mock_time = self.time_patcher.start()
        self.mock_uuid = self.uuid_patcher.start()

        self.addCleanup(self.table_patcher.stop)
        self.addCleanup(self.time_patcher.stop)
        self.addCleanup(self.uuid_patcher.stop)

        self.post_service = PostService()

    def test_create_post(self):
        post = {
            "location_id": "30023",
            "author_id": "009bf2f6-2ced-423c-9cfb-3b799aa1f01a",
            "title": "Testing title",
            "content": "Testing content"
        }

        result = self.post_service.create_post(
            location_id=post["location_id"],
            author_id=post["author_id"],
            title=post["title"],
            content=post["content"],
        )

        self.mock_table.put_item.assert_called_once()

        # Assert result
        self.assertEqual(result.id, self.FIXED_UUID)
        self.assertEqual(result.created_at, self.FIXED_TIME)
        self.assertEqual(result.updated_at, self.FIXED_TIME)
        self.assertEqual(result.deleted_at, None)
        self.assertEqual(result.author_id, post["author_id"])
        self.assertEqual(result.location_id, post["location_id"])
        self.assertEqual(result.title, post["title"])
        self.assertEqual(result.content, post["content"])