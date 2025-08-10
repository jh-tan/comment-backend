import strawberry
from strawberry.fastapi import GraphQLRouter
from app.graphql_api.types import Query, Mutation
from app.graphql_api.context import get_context

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema, context_getter=get_context)
