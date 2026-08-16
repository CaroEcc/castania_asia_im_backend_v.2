"""add_responsable_comunidad_table

Revision ID: b1c3e7f9a2d5
Revises: a36ca27d8c42
Create Date: 2026-08-16 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c3e7f9a2d5'
down_revision: Union[str, Sequence[str], None] = 'a36ca27d8c42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Tabla pivot M:N responsable_acopio ↔ Comunidad."""
    op.create_table(
        'responsable_comunidad',
        sa.Column('usuario_id', sa.UUID(), nullable=False),
        sa.Column('comunidad_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios_sistema.id'], name='responsable_comunidad_usuario_id_fkey'),
        sa.ForeignKeyConstraint(['comunidad_id'], ['comunidades.id_comunidad'], name='responsable_comunidad_comunidad_id_fkey'),
        sa.PrimaryKeyConstraint('usuario_id', 'comunidad_id', name='responsable_comunidad_pkey'),
    )

    # Eliminar el campo suelto 'comunidad' (String) de usuarios_sistema,
    # que ya no es necesario — la relación ahora vive en responsable_comunidad.
    op.drop_column('usuarios_sistema', 'comunidad')


def downgrade() -> None:
    op.add_column(
        'usuarios_sistema',
        sa.Column('comunidad', sa.String(200), nullable=True),
    )
    op.drop_table('responsable_comunidad')
