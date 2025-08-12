from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, clientes, produtos, vendas, estoque, relatorios, system

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["autenticacao"])
api_router.include_router(clientes.router, prefix="/clientes", tags=["clientes"])
api_router.include_router(produtos.router, prefix="/produtos", tags=["produtos"])
api_router.include_router(vendas.router, prefix="/vendas", tags=["vendas"])
api_router.include_router(estoque.router, prefix="/estoque", tags=["estoque"])
api_router.include_router(relatorios.router, prefix="/relatorios", tags=["relatorios-financeiros"])
api_router.include_router(system.router, prefix="/system", tags=["sistema"])
