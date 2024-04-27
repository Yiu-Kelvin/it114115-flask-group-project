import os, sys
os.environ['testdb'] = "True"
sys.path.append('/workspaces/it114115-flask-project-individual')
from app import config
from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import *

class PostModelCase(unittest.TestCase):
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # one to many
    def test_add_answer_to_posts(self):
        u1 = User(username='joshn', email='johnd@example.com')
        u2 = User(username='susasn', email='susad@example.com')
        db.session.add_all([u1, u2])
        db.session.commit()

        now = datetime.utcnow()
        p1 = Post(title="python stuff", body="some error with python", author=u1,
                  created_at=now + timedelta(seconds=1))
        p2 = Post(title="java stuff", body="some error with java", author=u2,
                  created_at=now + timedelta(seconds=4))
        db.session.add_all([p1, p2])
        db.session.commit()

        a1 = Answer(post=p1, author=u2, body="just google it", created_at= now + timedelta(seconds=4))
        a2 = Answer(post=p2, author=u1, body="just bing it?", created_at= now + timedelta(seconds=1))
        db.session.add_all([a1, a2])
        db.session.commit()
        
        # print(p1.answers)
        self.assertEqual(p1.answers,[a1])
        self.assertEqual(p2.answers,[a2])

    def test_voting(self):
        u1 = User(username='joshn', email='johnd@example.com')
        u2 = User(username='susasn', email='susad@example.com')
        u3 = User(username='johnd', email='asdf@asdf.com')
        db.session.add_all([u1, u2])
        db.session.commit()

        now = datetime.utcnow()
        p1 = Post(title="python stuff", body="some error with python", author=u1,
                  created_at=now + timedelta(seconds=1))
        p2 = Post(title="java stuff", body="some error with java", author=u2,
                  created_at=now + timedelta(seconds=4))
        db.session.add_all([p1, p2])
        db.session.commit()

        pv1 = PostVote(user=u1, post=p1, votes=1, created_at=now + timedelta(seconds=1))
        pv2 = PostVote(user=u2, post=p2, votes=-1, created_at=now + timedelta(seconds=4))
        pv3 = PostVote(user=u3, post=p1, votes=-1, created_at=now + timedelta(seconds=4))
        db.session.add_all([pv1, pv2, pv3])

        db.session.commit()

        total = p1.total_votes()

        self.assertEqual(total, 0)

        total = p2.total_votes()

        self.assertEqual(total, -1)

        u1.toggle_post_vote(p1, 1)
        u2.toggle_post_vote(p2, -1)
        u3.toggle_post_vote(p1, 1)

        db.session.commit()

        total = p1.total_votes()

        self.assertEqual(total, 1)

        total = p2.total_votes()

        self.assertEqual(total, 0)

        # answer voting

        a1 = Answer(post=p1, author=u2, body="just google it", created_at= now + timedelta(seconds=4))
        a2 = Answer(post=p2, author=u1, body="just bing it?", created_at= now + timedelta(seconds=1))
        db.session.add_all([a1, a2])
        db.session.commit()

        av1 = AnswerVote(user=u1, answer=a1, votes=1, created_at=now + timedelta(seconds=1))
        av2 = AnswerVote(user=u2, answer=a2, votes=-1, created_at=now + timedelta(seconds=4))
        db.session.add_all([av1, av2])

        db.session.commit()

        self.assertEqual(a1.total_votes(), 1)
        self.assertEqual(a2.total_votes(), -1)

        u1.toggle_answer_vote(a1, 1)
        u2.toggle_answer_vote(a2, -1)
        db.session.commit()

        self.assertEqual(a1.total_votes(), 0)
        self.assertEqual(a2.total_votes(), 0)
        