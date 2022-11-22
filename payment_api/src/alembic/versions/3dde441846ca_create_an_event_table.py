"""Create an event table

Revision ID: 3dde441846ca
Revises: 04e6ac0f42b2
Create Date: 2022-11-22 09:12:27.703450

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3dde441846ca'
down_revision = '04e6ac0f42b2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('events',
    sa.Column('payment_system_id', sa.String(), nullable=True),
    sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('processed', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('received_at'),
    postgresql_partition_by='RANGE(received_at)'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('events')
    # ### end Alembic commands ###
