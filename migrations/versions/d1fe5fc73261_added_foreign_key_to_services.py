"""Added foreign key to Services

Revision ID: d1fe5fc73261
Revises: 730138e47210
Create Date: 2025-03-28 14:54:39.090195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1fe5fc73261'
down_revision = '730138e47210'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cs_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_services_compServices", 'compServices', ['cs_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_services_compServices", type_='foreignkey')
        batch_op.drop_column('cs_id')

    # ### end Alembic commands ###
