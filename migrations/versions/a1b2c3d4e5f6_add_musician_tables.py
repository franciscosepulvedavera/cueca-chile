"""add musician tables

Revision ID: a1b2c3d4e5f6
Revises: 9e9600b917e9
Create Date: 2026-03-29 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '84ccb1c30994'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'musician',
        sa.Column('id',          sa.Integer(),     nullable=False),
        sa.Column('name',        sa.String(150),   nullable=False),
        sa.Column('description', sa.Text(),        nullable=True),
        sa.Column('image_path',  sa.String(500),   nullable=True),
        sa.Column('active',      sa.Boolean(),     nullable=True),
        sa.Column('created_at',  sa.DateTime(),    nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'musician_link',
        sa.Column('id',          sa.Integer(),     nullable=False),
        sa.Column('musician_id', sa.Integer(),     nullable=False),
        sa.Column('platform',    sa.String(30),    nullable=False),
        sa.Column('url',         sa.String(500),   nullable=False),
        sa.Column('label',       sa.String(100),   nullable=True),
        sa.ForeignKeyConstraint(['musician_id'], ['musician.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'musician_contact',
        sa.Column('id',          sa.Integer(),     nullable=False),
        sa.Column('musician_id', sa.Integer(),     nullable=False),
        sa.Column('kind',        sa.String(20),    nullable=False),
        sa.Column('value',       sa.String(200),   nullable=False),
        sa.Column('label',       sa.String(100),   nullable=True),
        sa.ForeignKeyConstraint(['musician_id'], ['musician.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('musician_contact')
    op.drop_table('musician_link')
    op.drop_table('musician')
