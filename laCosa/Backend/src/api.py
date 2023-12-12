"""Defines Partidas API."""
from fastapi import APIRouter
from partidas.endpoints import partidas

# Agrego 'partidas' al router general
api_router = APIRouter()
api_router.include_router(partidas, prefix="/partidas", tags=["partidas"])