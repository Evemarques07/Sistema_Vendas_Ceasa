# Alembic migration script: adiciona_campo_cpf_ou_cnpj_usuarios
"""
adiciona campo cpf_ou_cnpj na tabela usuarios
"""
from alembic import op
import sqlalchemy as sa


# Revisão gerada por Alembic
revision = '2025_08_09_0000'
down_revision = '5c6f05fcfc50'
branch_labels = None
depends_on = None

def upgrade():
	op.add_column('usuarios', sa.Column('cpf_ou_cnpj', sa.String(length=18), unique=True, index=True, nullable=True))

def downgrade():
	op.drop_column('usuarios', 'cpf_ou_cnpj')
