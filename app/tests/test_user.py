import os, sys
os.environ['testdb'] = "True"
sys.path.append('/workspaces/it114115-flask-project-individual')
from app import config
from datetime import datetime, timedelta
import unittest
from app.models import *
from app import app, db

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))
    def test_follow(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])

        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 1)
        self.assertEqual(u1.followed.first().username, 'susan')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'john')

        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.followed.count(), 0)
        self.assertEqual(u2.followers.count(), 0)

    def test_follow_posts(self):
        # create four users
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        # create four posts
        now = datetime.utcnow()
        p1 = Post(body="post from john", author=u1,
                  created_at=now + timedelta(seconds=1))
        p2 = Post(body="post from susan", author=u2,
                  created_at=now + timedelta(seconds=4))
        p3 = Post(body="post from mary", author=u3,
                  created_at=now + timedelta(seconds=3))
        p4 = Post(body="post from david", author=u4,
                  created_at=now + timedelta(seconds=2))
        db.session.add_all([p1, p2, p3, p4])
        db.session.commit()

        # setup the followers
        u1.follow(u2)  # john follows susan
        u1.follow(u4)  # john follows david
        u2.follow(u3)  # susan follows mary
        u3.follow(u4)  # mary follows david
        db.session.commit()

        # check the followed posts of each user
        f1 = u1.followed_posts().all()
        f2 = u2.followed_posts().all()
        f3 = u3.followed_posts().all()
        f4 = u4.followed_posts().all()
        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])


    def test_toggle_follow_tags(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        t1 = Tag(name='python', description='Python programming language')
        t2 = Tag(name='flask', description='Flask web framework')
        t3 = Tag(name='sqlalchemy', description='SQLAlchemy database toolkit')
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        u1.toggle_follow_tag(t1)
        u1.toggle_follow_tag(t2)
        u2.toggle_follow_tag(t2)
        u2.toggle_follow_tag(t3)
        db.session.commit()

        self.assertTrue(u1.is_following_tag(t1))
        self.assertTrue(u1.is_following_tag(t2))
        self.assertFalse(u1.is_following_tag(t3))
        self.assertTrue(u2.is_following_tag(t2))
        self.assertTrue(u2.is_following_tag(t3))
        self.assertFalse(u2.is_following_tag(t1))
        
    def test_toggle_ignore_tags(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        t1 = Tag(name='python', description='Python programming language')
        t2 = Tag(name='flask', description='Flask web framework')
        t3 = Tag(name='sqlalchemy', description='SQLAlchemy database toolkit')
        db.session.add_all([t1, t2, t3])
        db.session.commit()

        # add posts with tags
        p1 = Post(body="post from john", author=u1)
        p1.tags.append(t1)
        p2 = Post(body="post from susan", author=u2)
        p2.tags.append(t2)
        p3 = Post(body="post from mary", author=u1)
        p3.tags.append(t3)
        db.session.add_all([p1, p2, p3])

        u1.toggle_ignore_tag(t1)
        u1.toggle_ignore_tag(t2)
        u2.toggle_ignore_tag(t2)
        u2.toggle_ignore_tag(t3)
        db.session.commit()

        self.assertTrue(u1.is_ignoring_tag(t1))
        self.assertTrue(u1.is_ignoring_tag(t2))
        self.assertFalse(u1.is_ignoring_tag(t3))
        self.assertTrue(u2.is_ignoring_tag(t2))
        self.assertTrue(u2.is_ignoring_tag(t3))
        self.assertFalse(u2.is_ignoring_tag(t1))

        
        self.assertEqual(u1.post_without_ignored().all(), [p3])
        self.assertEqual(u2.post_without_ignored().all(), [p1])


if __name__ == '__main__':
    unittest.main(verbosity=2)