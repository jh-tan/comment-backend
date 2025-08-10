from httpx import AsyncClient

from app.models.user import User
from app.models.comment import Comment


class TestGraphQLAPI:
    async def test_query_users(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test GraphQL users query."""
        query = """
        query {
            users {
                id
                username
                group
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "users" in data["data"]
        assert len(data["data"]["users"]) >= 1
        assert any(user["username"] == test_user.username for user in data["data"]["users"])
    
    async def test_query_comments(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        query = """
        query {
            comments {
                id
                content
                userId
                createdAt
                user {
                    username
                    group
                }
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "comments" in data["data"]
        assert len(data["data"]["comments"]) >= 1
        assert any(comment["id"] == test_comment.id for comment in data["data"]["comments"])
    
    async def test_query_comment_history(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        query = f"""
        query {{
            commentHistory(commentId: {test_comment.id}) {{
                id
                commentId
                timestamp
                oldValue
                newValue
            }}
        }}
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "commentHistory" in data["data"]
        assert isinstance(data["data"]["commentHistory"], list)
    
    async def test_mutation_create_user(self, client: AsyncClient, auth_headers: dict):
        mutation = """
        mutation {
            createUser(input: {
                username: "graphql_user"
                password: "graphql_password"
                group: "graphql_group"
            }) {
                id
                username
                group
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": mutation},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createUser" in data["data"]
        assert data["data"]["createUser"]["username"] == "graphql_user"
        assert data["data"]["createUser"]["group"] == "graphql_group"
    
    async def test_mutation_create_user_duplicate(self, client: AsyncClient, auth_headers: dict, test_user: User):
        mutation = f"""
        mutation {{
            createUser(input: {{
                username: "{test_user.username}"
                password: "password"
                group: "group"
            }}) {{
                id
                username
                group
            }}
        }}
        """
        
        response = await client.post(
            "/graphql",
            json={"query": mutation},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert any("already exists" in str(error) for error in data["errors"])
    
    async def test_mutation_create_comment(self, client: AsyncClient, auth_headers: dict):
        mutation = """
        mutation {
            createComment(input: {
                content: "GraphQL test comment"
            }) {
                id
                content
                userId
                user {
                    username
                }
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": mutation},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "createComment" in data["data"]
        assert data["data"]["createComment"]["content"] == "GraphQL test comment"
        assert "userId" in data["data"]["createComment"]
        assert "user" in data["data"]["createComment"]
    
    async def test_mutation_update_comment(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        mutation = f"""
        mutation {{
            updateComment(commentId: {test_comment.id}, input: {{
                content: "Updated via GraphQL"
            }}) {{
                id
                content
                userId
            }}
        }}
        """
        
        response = await client.post(
            "/graphql",
            json={"query": mutation},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "updateComment" in data["data"]
        assert data["data"]["updateComment"]["content"] == "Updated via GraphQL"
        assert data["data"]["updateComment"]["id"] == test_comment.id
    
    async def test_mutation_update_comment_not_found(self, client: AsyncClient, auth_headers: dict):
        mutation = """
        mutation {
            updateComment(commentId: 9999, input: {
                content: "This should fail"
            }) {
                id
                content
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": mutation},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
        assert any("not found" in str(error) for error in data["errors"])
    
    async def test_graphql_without_authentication(self, client: AsyncClient):
        query = """
        query {
            users {
                id
                username
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query}
        )
        
        assert response.status_code == 401 or response.status_code == 403
    
    async def test_graphql_invalid_query(self, client: AsyncClient, auth_headers: dict):
        query = """
        query {
            invalidField {
                nonExistentField
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "errors" in data
    
    async def test_graphql_complex_query(self, client: AsyncClient, auth_headers: dict, test_comment: Comment):
        query = """
        query {
            comments {
                id
                content
                createdAt
                user {
                    id
                    username
                    group
                }
            }
            users {
                id
                username
                group
            }
        }
        """
        
        response = await client.post(
            "/graphql",
            json={"query": query},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "comments" in data["data"]
        assert "users" in data["data"]
        
        if data["data"]["comments"]:
            comment = data["data"]["comments"][0]
            assert "user" in comment
            assert "username" in comment["user"]
            assert "group" in comment["user"]