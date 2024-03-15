"""Add content column to posts table

Revision ID: 980bf5b8c4fa
Revises: 4c4ad4be7b93
Create Date: 2024-03-14 14:18:59.719014

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "980bf5b8c4fa"
down_revision: Union[str, None] = "4c4ad4be7b93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade():
    op.drop_column("posts", "content")
    pass
