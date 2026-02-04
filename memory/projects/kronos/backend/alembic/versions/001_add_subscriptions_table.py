"""Add subscriptions table for multi-product support

Revision ID: 001_subscriptions
Revises: 
Create Date: 2026-02-01 17:31:00

SAFE MIGRATION - Keeps existing columns for backwards compatibility
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_subscriptions'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_type', sa.String(length=50), nullable=False),
        sa.Column('stripe_subscription_id', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('stripe_subscription_id', name='uq_subscriptions_stripe_id'),
        sa.UniqueConstraint('user_id', 'product_type', name='uq_user_product')
    )
    
    # Create indexes
    op.create_index('idx_subscriptions_user', 'subscriptions', ['user_id'])
    op.create_index('idx_subscriptions_stripe', 'subscriptions', ['stripe_subscription_id'])
    
    # Migrate existing subscription data from users table
    # This assumes existing subs are for 'automation' product
    op.execute("""
        INSERT INTO subscriptions (user_id, product_type, stripe_subscription_id, status, current_period_end)
        SELECT 
            id,
            'automation' as product_type,
            stripe_subscription_id,
            COALESCE(subscription_status, 'none') as status,
            subscription_ends_at
        FROM users
        WHERE stripe_subscription_id IS NOT NULL 
           OR subscription_status IS NOT NULL 
           OR subscription_ends_at IS NOT NULL
    """)
    
    # NOTE: OLD COLUMNS KEPT FOR BACKWARDS COMPATIBILITY
    # Do NOT drop: stripe_subscription_id, subscription_status, subscription_ends_at
    # These will be removed in a future migration after code is updated


def downgrade():
    # Drop indexes
    op.drop_index('idx_subscriptions_stripe', table_name='subscriptions')
    op.drop_index('idx_subscriptions_user', table_name='subscriptions')
    
    # Drop table
    op.drop_table('subscriptions')
