from alembic import op
import sqlalchemy as sa

revision = "create user"
down_revision = None

def upgrade():
    op.create_table(
        "user",
        sa.Column('id', sa.Integer, primary_key=True, index=True, nullable=False),
        sa.Column('first_name', sa.String(50), nullable=False),
        sa.Column('last_name', sa.String(50), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password', sa.String(300), nullable=False),
        sa.Column('is_active', sa.Boolean, default=False),
        sa.Column('is_verified', sa.Boolean, default=False),
        sa.Column('created_date', sa.Date, nullable=True),
        sa.Column('modified_date', sa.Date, nullable=True)
    )

def downgrade():
    op.drop_table("user")