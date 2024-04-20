
from datetime import datetime, timedelta, timezone
from hashlib import md5
from app import app, db, login
import jwt
from sqlalchemy import and_, func, select
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from werkzeug.security import generate_password_hash, check_password_hash


followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

post_tags = db.Table(
    'post_tags',    
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)
followed_tags = db.Table(
    'followed_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
ignored_tags = db.Table(
    'ignored_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
bookmarked_post = db.Table(
    'bookmarked_post',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

followed_post = db.Table(
    'followed_post',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    bookmarked_post = db.relationship('Post', secondary=bookmarked_post, lazy='dynamic', backref=db.backref('bookmarked_by_user', lazy='dynamic'))
    followed_post = db.relationship('Post', secondary=followed_post, lazy='dynamic', backref=db.backref('followed_post', lazy='dynamic'))
    answers = db.relationship('Answer', backref='author', lazy='dynamic')
    about_me = db.Column(db.Text)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed_tags = db.relationship('Tag', secondary=followed_tags, lazy='dynamic', backref=db.backref('followed_by_user', lazy='dynamic'))
    ignored_tags = db.relationship('Tag', secondary=ignored_tags, lazy='dynamic', backref=db.backref('ingored_by_user', lazy='dynamic'))

    
    post_votes = db.relationship('PostVote', backref='user')
    answer_votes = db.relationship('AnswerVote', backref='user')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def post_without_ignored(self):
        return Post.query.filter(~Post.tags.any(Tag.id.in_([tag.id for tag in self.ignored_tags]))).order_by(Post.created_at.desc())
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
    
    def is_following_tag(self, tag):
        return self.followed_tags.filter(followed_tags.c.tag_id == tag.id).count() > 0
    
    def toggle_follow_tag(self, tag):
        if not self.is_following_tag(tag):
            self.stop_ignoring_tag(tag)
            self.followed_tags.append(tag)
        else:
            self.followed_tags.remove(tag)
            
    def unfollow_tag(self, tag):
        if self.is_following_tag(tag):
            self.followed_tags.remove(tag)

    def toggle_ignore_tag(self, tag):
        if not self.is_ignoring_tag(tag):
            self.unfollow_tag(tag)
            self.ignored_tags.append(tag)
        else:
            self.ignored_tags.remove(tag)

    def stop_ignoring_tag(self, tag):
        if self.is_ignoring_tag(tag):
            self.ignored_tags.remove(tag)

    def is_ignoring_tag(self, tag):
        return self.ignored_tags.filter(ignored_tags.c.tag_id == tag.id).count() > 0
            
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def posts_from_followed_user(self):
        followed = Post.query.join(
            followers, followers.c.followed_id == Post.user_id
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.created_at.desc())
    def toggle_post_vote(self, post, vote):
        post_vote = PostVote.query.filter_by(user_id=self.id, post=post).first()
        if post_vote is None:
            post_vote = PostVote(user_id=self.id, post=post, votes=vote)
            db.session.add(post_vote)
        else:
            if post_vote.votes == vote:
                db.session.delete(post_vote)
            else:
                post_vote.votes = vote
        db.session.commit()

    def toggle_answer_vote(self, answer, vote):
        answer_vote = AnswerVote.query.filter_by(user_id=self.id, answer=answer).first()
        if answer_vote is None:
            answer_vote = AnswerVote(user_id=self.id, answer=answer, votes=vote)
            db.session.add(answer_vote)
        else:
            if answer_vote.votes == vote:
                db.session.delete(answer_vote)
            else:
                answer_vote.votes = vote
        db.session.commit()
        
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({"reset_password": self.id,
                           "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)},
                          app.config["SECRET_KEY"], algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
        except:           
            return None
        return User.query.get(id)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tags = db.relationship('Tag', secondary=post_tags, lazy='dynamic', backref=db.backref('posts', lazy='dynamic'))
    votes = db.relationship('PostVote', backref='post')
    answers = db.relationship('Answer', backref='post')

    def total_votes(self):
        return Post.query.with_entities(func.sum(PostVote.votes)).filter(PostVote.post_id == self.id).scalar() or 0
    
    def __repr__(self) -> str:
        return f'<Post {self.body}>'
    
    def is_tag_added(self, tag):
        return self.tags.filter(post_tag.c.tag_id == tag.id).count() > 0

    def remove_tag(self, tag):
        if self.is_tag_added(tag):
            self.tags.remove(tag)

            
    def total_votes(self):
        return Post.query.with_entities(func.sum(PostVote.votes)).filter(PostVote.post_id == self.id).scalar() or 0

    def edit_post(self, title, body, tags, user):
        if self.author == user:
            self.tags = []
            self.add_tag(tags)
            self.title = title
            self.body = body
            self.edited_at = datetime.utcnow()
            db.session.commit()

class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('votes=-1 OR votes=0 OR votes=1', name='check_post_vote_value'),
    )


class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    votes = db.relationship('AnswerVote', backref='answer', lazy='dynamic')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    edited_at = db.Column(db.DateTime, nullable=True)

    @hybrid_property            
    def total_votes(self):
        return self.votes.with_entities(func.sum(AnswerVote.votes)).scalar() or 0

    @total_votes.expression
    def total_votes(cls):
        return (
            select(func.sum(AnswerVote.votes))
            # impacts performance, but oh well
            .where(AnswerVote.answer_id == cls.id)
            .label("total_votes")
        )

    # def total_votes(self):
    #     return Answer.query.with_entities(func.sum(AnswerVote.votes)).filter(AnswerVote.answer_id == self.id).scalar() or 0
    
    def edit_answer(self, body, user):
        if self.author == user:
            self.body = body
            self.edited_at = datetime.utcnow()
            db.session.commit()

class AnswerVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answer.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


    __table_args__ = (
        db.CheckConstraint('votes=-1 OR votes=0 OR votes=1', name='check_answer_vote_value'),
    )

class PostVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    votes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint('votes=-1 OR votes=0 OR votes=1', name='check_post_vote_value'),
    )

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.Text)

    def posts_with_tag(self):
        posts = Post.query.join(post_tags, and_(post_tags.c.tag_id == self.id, post_tags.c.post_id == Post.id ))
        return posts

    def __repr__(self) -> str:
        return f'<Tag {self.name}>'
