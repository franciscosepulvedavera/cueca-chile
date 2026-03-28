"""contact nullable and bases optional

Revision ID: 25066bc8fc7c
Revises: 65a4165243cc
Create Date: 2025-10-02 16:33:47.330751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25066bc8fc7c'
down_revision = '65a4165243cc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('event') as batch_op:
        batch_op.alter_column('contact', existing_type=sa.String(length=120), nullable=True)

def downgrade():
    with op.batch_alter_table('event') as batch_op:
        batch_op.alter_column('contact', existing_type=sa.String(length=120), nullable=False)


    # ### end Alembic commands ###
