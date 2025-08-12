"""adicionar_rastreamento_funcionario_separacao

Revision ID: 5c6f05fcfc50
Revises: 9f28235c2e93
Create Date: 2025-08-08 11:46:43.701138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c6f05fcfc50'
down_revision: Union[str, Sequence[str], None] = '9f28235c2e93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar coluna para rastrear funcionário que fez a separação
    op.add_column('vendas', sa.Column('funcionario_separacao_id', sa.Integer(), nullable=True))
    
    # Adicionar coluna para data/hora da separação
    op.add_column('vendas', sa.Column('data_separacao', sa.DateTime(timezone=True), nullable=True))
    
    # Criar foreign key para funcionario_separacao_id
    op.create_foreign_key(
        'fk_vendas_funcionario_separacao',
        'vendas', 'usuarios',
        ['funcionario_separacao_id'], ['id']
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remover foreign key
    op.drop_constraint('fk_vendas_funcionario_separacao', 'vendas', type_='foreignkey')
    
    # Remover colunas
    op.drop_column('vendas', 'data_separacao')
    op.drop_column('vendas', 'funcionario_separacao_id')
