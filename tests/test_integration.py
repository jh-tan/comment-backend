from httpx import AsyncClient

class TestIntegration:
    async def test_complete_user_workflow(self, client: AsyncClient):
        user_data = {
            "username": "integration_user",
            "password": "integration_password",
            "group": "integration_group"
        }
        
        create_response = await client.post("/api/v1/users/", json=user_data)
        assert create_response.status_code == 200
        user = create_response.json()
        user_id = user["id"]
        
        login_response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": user_data["username"],
                "password": user_data["password"]
            }
        )
        assert login_response.status_code == 200
        token_data = login_response.json()
        
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        profile_response = await client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["username"] == user_data["username"]
    
    async def test_complete_comment_lifecycle(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "Initial comment content"}
        create_response = await client.post(
            "/api/v1/comments/",
            json=comment_data,
            headers=auth_headers
        )
        assert create_response.status_code == 200
        comment = create_response.json()
        comment_id = comment["id"]
        
        read_response = await client.get(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert read_response.status_code == 200
        read_comment = read_response.json()
        assert read_comment["content"] == "Initial comment content"
        
        update_data = {"content": "Updated comment content"}
        update_response = await client.put(
            f"/api/v1/comments/{comment_id}",
            json=update_data,
            headers=auth_headers
        )
        assert update_response.status_code == 200
        updated_comment = update_response.json()
        assert updated_comment["content"] == "Updated comment content"
        
        history_response = await client.get(
            f"/api/v1/users/comment/{comment_id}",
            headers=auth_headers
        )
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) == 2  
        
        delete_response = await client.delete(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        get_deleted_response = await client.get(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        assert get_deleted_response.status_code == 404
    
    
    async def test_graphql_rest_consistency(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "Consistency test comment"}
        rest_create_response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        rest_comment = rest_create_response.json()
        comment_id = rest_comment["id"]
        
        rest_read_response = await client.get(f"/api/v1/comments/{comment_id}", headers=auth_headers)
        rest_comment_data = rest_read_response.json()
        
        graphql_query = f"""
        query {{
            comments {{
                id
                content
                userId
                user {{
                    username
                    group
                }}
            }}
        }}
        """
        
        graphql_response = await client.post("/graphql", json={"query": graphql_query}, headers=auth_headers)
        graphql_data = graphql_response.json()["data"]["comments"]
        graphql_comment = next(c for c in graphql_data if str(c["id"]) == str(comment_id))
        
        assert rest_comment_data["content"] == graphql_comment["content"]
        assert rest_comment_data["user_id"] == int(graphql_comment["userId"])
        assert rest_comment_data["user"]["username"] == graphql_comment["user"]["username"]
        assert rest_comment_data["user"]["group"] == graphql_comment["user"]["group"]
    
    async def test_comment_history_integration(self, client: AsyncClient, auth_headers: dict):
        comment_data = {"content": "Version 1"}
        create_response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
        comment_id = create_response.json()["id"]
        
        updates = ["Version 2", "Version 3", "Final version"]
        for update_content in updates:
            await client.put(
                f"/api/v1/comments/{comment_id}",
                json={"content": update_content},
                headers=auth_headers
            )
        
        history_response = await client.get(f"/api/v1/users/comment/{comment_id}", headers=auth_headers)
        history = history_response.json()
        
        assert len(history) == 4
        
        versions = ["Version 1", "Version 2", "Version 3", "Final version"]
        history_values = [h["new_value"] for h in sorted(history, key=lambda x: x["id"])]
        assert history_values == versions
        
        graphql_query = f"""
        query {{
            commentHistory(commentId: {comment_id}) {{
                id
                oldValue
                newValue
                timestamp
            }}
        }}
        """
        
        graphql_response = await client.post("/graphql", json={"query": graphql_query}, headers=auth_headers)
        graphql_history = graphql_response.json()["data"]["commentHistory"]
        
        assert len(graphql_history) == len(history)
    
    async def test_error_handling_workflow(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/v1/comments/99999", headers=auth_headers)
        assert response.status_code == 404
        
        response = await client.post("/api/v1/comments/", json={}, headers=auth_headers)
        assert response.status_code == 422
        
        response = await client.put("/api/v1/comments/99999", json={"content": "test"}, headers=auth_headers)
        assert response.status_code == 404
        
        response = await client.delete("/api/v1/comments/99999", headers=auth_headers)
        assert response.status_code == 404
        
        response = await client.get("/api/v1/comments/")
        assert response.status_code == 403
    
    async def test_pagination_workflow(self, client: AsyncClient, auth_headers: dict):
        comments_created = []
        for i in range(15):
            comment_data = {"content": f"Comment {i+1}"}
            response = await client.post("/api/v1/comments/", json=comment_data, headers=auth_headers)
            comments_created.append(response.json()["id"])
        
        page1_response = await client.get("/api/v1/comments/?skip=0&limit=5", headers=auth_headers)
        page1_data = page1_response.json()
        assert len(page1_data) == 5
        
        page2_response = await client.get("/api/v1/comments/?skip=5&limit=5", headers=auth_headers)
        page2_data = page2_response.json()
        assert len(page2_data) == 5
        
        page1_ids = {comment["id"] for comment in page1_data}
        page2_ids = {comment["id"] for comment in page2_data}
        assert page1_ids.isdisjoint(page2_ids)
        
        if comments_created:
            comment_id = comments_created[0]
            for i in range(10):
                await client.put(
                    f"/api/v1/comments/{comment_id}",
                    json={"content": f"Updated content {i+1}"},
                    headers=auth_headers
                )
            
            history_page1 = await client.get(
                f"/api/v1/users/comment/{comment_id}?skip=0&limit=5",
                headers=auth_headers
            )
            assert len(history_page1.json()) == 5