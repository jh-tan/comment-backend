import pytest
from fastapi import HTTPException

from app.utils.permissions import check_comment_permission, ensure_comment_permission
from app.models.user import User
from app.models.comment import Comment


class TestPermissions:
    @pytest.fixture
    def user_group_a(self):
        user = User(
            id=1,
            username="user_a",
            hashed_password="hashed",
            group="group_a"
        )
        return user
    
    @pytest.fixture
    def user_group_b(self):
        user = User(
            id=2,
            username="user_b",
            hashed_password="hashed",
            group="group_b"
        )
        return user
    
    @pytest.fixture
    def comment_by_user_a(self, user_group_a):
        comment = Comment(
            id=1,
            content="Comment by user A",
            user_id=user_group_a.id
        )
        comment.user = user_group_a
        return comment
    
    def test_check_read_permission_same_group(self, user_group_a, comment_by_user_a):
        result = check_comment_permission(user_group_a, comment_by_user_a, "read")
        assert result is True
    
    def test_check_read_permission_different_group(self, user_group_b, comment_by_user_a):
        result = check_comment_permission(user_group_b, comment_by_user_a, "read")
        assert result is False
    
    def test_check_update_permission_same_user(self, user_group_a, comment_by_user_a):
        result = check_comment_permission(user_group_a, comment_by_user_a, "update")
        assert result is True
    
    def test_check_update_permission_different_user_same_group(self, comment_by_user_a):
        other_user_same_group = User(
            id=99,
            username="other_user",
            hashed_password="hashed",
            group="group_a"
        )
        
        result = check_comment_permission(other_user_same_group, comment_by_user_a, "update")
        assert result is False
    
    def test_check_update_permission_different_user_different_group(self, user_group_b, comment_by_user_a):
        result = check_comment_permission(user_group_b, comment_by_user_a, "update")
        assert result is False
    
    def test_check_delete_permission_same_user(self, user_group_a, comment_by_user_a):
        result = check_comment_permission(user_group_a, comment_by_user_a, "delete")
        assert result is True
    
    def test_check_delete_permission_different_user(self, user_group_b, comment_by_user_a):
        result = check_comment_permission(user_group_b, comment_by_user_a, "delete")
        assert result is False
    
    def test_check_unknown_permission(self, user_group_a, comment_by_user_a):
        result = check_comment_permission(user_group_a, comment_by_user_a, "unknown_action")
        assert result is False
    
    def test_ensure_read_permission_allowed(self, user_group_a, comment_by_user_a):
        ensure_comment_permission(user_group_a, comment_by_user_a, "read")
    
    def test_ensure_read_permission_forbidden(self, user_group_b, comment_by_user_a):
        with pytest.raises(HTTPException) as exc_info:
            ensure_comment_permission(user_group_b, comment_by_user_a, "read")
        
        assert exc_info.value.status_code == 403
        assert "permissions" in exc_info.value.detail
        assert "group" in exc_info.value.detail
    
    def test_ensure_update_permission_allowed(self, user_group_a, comment_by_user_a):
        ensure_comment_permission(user_group_a, comment_by_user_a, "update")
    
    def test_ensure_update_permission_forbidden(self, user_group_b, comment_by_user_a):
        with pytest.raises(HTTPException) as exc_info:
            ensure_comment_permission(user_group_b, comment_by_user_a, "update")
        
        assert exc_info.value.status_code == 403
        assert "permissions" in exc_info.value.detail
        assert "own comments" in exc_info.value.detail
    
    def test_ensure_delete_permission_allowed(self, user_group_a, comment_by_user_a):
        ensure_comment_permission(user_group_a, comment_by_user_a, "delete")
    
    def test_ensure_delete_permission_forbidden(self, user_group_b, comment_by_user_a):
        with pytest.raises(HTTPException) as exc_info:
            ensure_comment_permission(user_group_b, comment_by_user_a, "delete")
        
        assert exc_info.value.status_code == 403
        assert "permissions" in exc_info.value.detail
        assert "own comments" in exc_info.value.detail
    
    def test_permission_consistency(self, user_group_a, user_group_b, comment_by_user_a):
        actions = ["read", "update", "delete"]
        users = [user_group_a, user_group_b]
        
        for user in users:
            for action in actions:
                check_result = check_comment_permission(user, comment_by_user_a, action)
                
                if check_result:
                    try:
                        ensure_comment_permission(user, comment_by_user_a, action)
                        ensure_success = True
                    except HTTPException:
                        ensure_success = False
                    
                    assert ensure_success, f"Inconsistency for user {user.id}, action {action}"
                else:
                    with pytest.raises(HTTPException):
                        ensure_comment_permission(user, comment_by_user_a, action)