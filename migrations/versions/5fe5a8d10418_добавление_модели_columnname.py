"""Добавление модели ColumnName

Revision ID: 5fe5a8d10418
Revises: e5b7ebd19046
Create Date: 2024-12-18 14:03:25.393922

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5fe5a8d10418'
down_revision = 'e5b7ebd19046'
branch_labels = None
depends_on = None





def upgrade():
    # Создание таблицы column_names
    op.create_table(
        'column_names',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('column_key', sa.String(length=150), nullable=False),
        sa.Column('column_name', sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('column_key')
    )


def downgrade():
    # Удаление таблицы column_names при откате миграции
    op.drop_table('column_names')

    # ### end Alembic commands ###
