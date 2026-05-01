from dataclasses import asdict

from app.core.config import config
from app.core.exceptions import NotFoundError
from app.db import Table
from app.model.post_model import Post
from app.utils.ids import generate_uuid
from app.utils.time import get_current_time
from boto3.dynamodb.conditions import Key

class PostService:
    def __init__(self):
        self.db = Table(table_name=config.posts_table_name, aws_region=config.aws_region)

    def _build_post(self, **kwargs) -> Post:
        current_time = get_current_time()
        return Post(
            id=kwargs.get("id", generate_uuid()),
            author_id=kwargs["author_id"],
            location_id=kwargs["location_id"],
            title=kwargs["title"],
            content=kwargs["content"],
            created_at=kwargs.get("created_at", current_time),
            updated_at=kwargs.get("updated_at", current_time),
            deleted_at=kwargs.get("deleted_at", None)
        )

    def _serialize_post(self, post: Post) -> dict:
        item = post.model_dump()
        return item

    def create_post(
        self,
        author_id: str,
        location_id: str,
        title: str,
        content: str
    ) -> Post:
        post = self._build_post(
            author_id=author_id,
            location_id=location_id,
            title=title,
            content=content
        )
        item = self._serialize_post(post)
        self.db.put_item(item=item)
        return post
    
    def get_post_by_id(self, id: str, include_deleted: bool = False) -> Post | None:
        key = {"id": id}
        item = self.db.get_item(key)
        if not item:
            raise NotFoundError("Post not found")
        if not include_deleted and item.get("deleted_at"):
            raise NotFoundError("Post not found")
        return Post.model_validate(item)
    
    def get_posts_by_location_id(self, location_id: str, include_deleted: bool = False) -> Post | None:
        key_expression = Key("location_id").eq(location_id)
        items = self.db.query_gsi(
            index_name="location-created_at-index",
            key_expression=key_expression,
        )
        if not include_deleted:
            items = [item for item in items if not item.get("deleted_at")]
        return items
    
    def update_post(self, id: str, **kwargs) -> Post | None:
        key = {"id": id}
        item = self.db.get_item(key)

        # Verify item exists
        if not item:
            raise NotFoundError("Post not found")
        
        # Return early if no attributes are provided
        if all(value is None for value in kwargs.values()):
            return Post.model_validate(item)

        # Set updated_at timestamp
        update_expression = "SET #updated_at = :updated_at"
        names = {'#updated_at': 'updated_at'}
        values = {':updated_at': get_current_time()}

        if kwargs.get("title"):
            update_expression += ", #title = :title"
            names["#title"] = "title"
            values[":title"] = kwargs["title"]
        if kwargs.get("content"):
            update_expression += ", #content = :content"
            names["#content"] = "content"
            values[":content"] = kwargs["content"]

        updated_item = self.db.update_item(
            key=key,
            update_expression=update_expression,
            attr_names=names,
            attr_values=values,
        )
        return Post.model_validate(updated_item)
    
    def delete_post(self, id: str):
        key = {"id": id}

        item = self.db.get_item(key)
        # Verify item exists and is not already deleted
        if not item or item.get("deleted_at"):
            raise NotFoundError("Post not found")

        update_expression = "SET #deleted_at = :deleted_at"
        names = {'#deleted_at': 'deleted_at'}
        values = {':deleted_at': get_current_time()}

        # Prevent creation if the item doesn't exist
        condition_expression = "attribute_exists(id)" 

        updated_item = self.db.update_item(
            key=key,
            update_expression=update_expression,
            attr_names=names,
            attr_values=values,
            condition_expression=condition_expression
        )
        return Post.model_validate(updated_item)