"""empty message

Revision ID: 6bf95f1a6f4b
Revises: ea544a48ff42
Create Date: 2024-02-25 15:17:10.135668

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bf95f1a6f4b'
down_revision = 'ea544a48ff42'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('looking_for_talent', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Venue', schema=None) as batch_op:
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('looking_for_talent')
        batch_op.drop_column('website_link')
        batch_op.drop_column('genres')

    # ### end Alembic commands ###
