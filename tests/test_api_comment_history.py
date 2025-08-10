from httpx import AsyncClient

from app.models.comment import Comment
from app.models.comment_history import CommentHistory


class TestCommentHistoryAPI:
    async def test_get_comment_history(self, client: AsyncClient, auth_headers: dict, test_comment: Comment, test_comment_history: CommentHistory):
        response = await client.get(
            f"/api/v1/users/comment/{test_comment.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(history["id"] == test_comment_history.id for history in data)
    
    async def test_get_comment_history_with_pagination(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        response = await client.get(
            f"/api/v1/users/comment/{test_comment.id}",
            headers=auth_headers,
            params={"skip": 0, "limit": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
    
    async def test_get_comment_history_comment_not_found(self, client: AsyncClient, auth_headers: dict):
        response = await client.get(
            "/api/v1/users/comment/9999",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Comment not found"
    
    async def test_get_comment_history_different_group_forbidden(self, client: AsyncClient, auth_headers_2: dict, test_comment: Comment):
        response = await client.get(
            f"/api/v1/users/comment/{test_comment.id}",
            headers=auth_headers_2
        )
        
        assert response.status_code == 403
        assert "permissions" in response.json()["detail"]
    
    async def test_comment_history_created_on_comment_creation(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "New comment with history"}
        
        response = await client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        comment_id = response.json()["id"]
        
        history_response = await client.get(
            f"/api/v1/users/comment/{comment_id}",
            headers=auth_headers
        )
        
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data) == 1
        assert history_data[0]["old_value"] is None
        assert history_data[0]["new_value"] == "New comment with history"
    
    async def test_comment_history_created_on_comment_update(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "Original content"}
        create_response = await client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers=auth_headers
        )
        comment_id = create_response.json()["id"]
        
        update_data = {"content": "Updated content"}
        await client.put(
            f"/api/v1/comments/{comment_id}",
            json=update_data,
            headers=auth_headers
        )
        
        history_response = await client.get(
            f"/api/v1/users/comment/{comment_id}",
            headers=auth_headers
        )
        
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data) == 2  # Creation + Update
        
        update_history = next(h for h in history_data if h["old_value"] == "Original content")
        assert update_history["new_value"] == "Updated content"