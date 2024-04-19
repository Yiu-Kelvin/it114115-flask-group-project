"""fixed length

Revision ID: 484bcdefdbe9
Revises: 06f5fe8dd988
Create Date: 2024-04-18 15:17:00.311870

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from app.models import Answer, User, Post, Tag
# revision identifiers, used by Alembic.
revision = '484bcdefdbe9'
down_revision = '06f5fe8dd988'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('followed_tags',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('ignored_tags',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('bookmarked_post',
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('followed_post',
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.String(length=256),
               existing_nullable=True)
        batch_op.alter_column('about_me',
               existing_type=mysql.VARCHAR(length=140),
               type_=sa.Text(),
               existing_nullable=True)

    # ### end Alembic commands ###
    seed()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('about_me',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=140),
               existing_nullable=True)
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=256),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=True)

    op.drop_table('followed_post')
    op.drop_table('bookmarked_post')
    op.drop_table('ignored_tags')
    op.drop_table('followed_tags')
    # ### end Alembic commands ###


def seed():
        op.bulk_insert(Tag.__table__,
        [
            {'name':'python',
                    'description':"Python is a dynamically typed, multi-purpose programming language. It is designed to be quick to learn, understand, and use, and enforces a clean and uniform syntax. "},
            {'name':'javascript',
                    'description':"For questions about programming in ECMAScript (JavaScript/JS) and its different dialects/implementations (except for ActionScript). Note that JavaScript is NOT Java."},
            {'name':'c#',
                    'description': "C#  is a high-level, statically typed, multi-paradigm programming language developed by Microsoft. C# code usually targets Microsofts .NET family of tools and"},
        ]
    )