from crypt import methods
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g,session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from flask_babel import _, get_locale
from app import app, db
from app.forms import *
from sqlalchemy import func, select
from app.models import *
from app.email import send_password_reset_email, send_answered_notification
from sqlalchemy.sql.functions import coalesce

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    sort_by = request.args.get('sort_by')
    if form.validate_on_submit():
        # todo: refactor this to form validation

        tags = form.tag.data.split()
        post = Post(title=form.title.data, body=form.body.data, author=current_user)
        for tag in tags:
            # effiency???
            tag_obj = Tag.query.filter_by(name=tag).first()
            if tag_obj:
                post.tags.append(tag_obj)
            else:
                flash(_(f'Unsuccessful, tag "{tag}" does not exist'), 'danger')
                return redirect(url_for('index'))
                
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'), 'success')
        return redirect(url_for('index'))
    
    page = request.args.get('page', 1, type=int)
    posts = current_user.posts_from_followed_user(sort_by=sort_by).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)

    return render_template('index.html.j2', title=_('Home'), form=form,
                           posts=posts.items, pagination=posts)

@app.route('/answer_vote/<id>', methods=['POST'])
@login_required
def answer_vote(id):
    form = AnswerVoteForm()
    answer = Answer.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        vote = 1 if form.upvote.data else -1
        current_user.toggle_answer_vote(answer, vote)
        db.session.commit()
        flash(_('Vote successful!'), 'success')
        return redirect(url_for('post', id=answer.post.id))
    flash(_('Vote unsuccessful!'), 'danger')
    return redirect(url_for('post', id=answer.post.id))

@app.route('/post_vote/<id>', methods=['POST'])
@login_required
def post_vote(id):
    form = PostVoteForm()
    post = Post.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        vote = 1 if form.upvote.data else -1
        current_user.toggle_post_vote(post, vote)
        db.session.commit()
        flash(_('Vote successful!'), 'success')
        return redirect(url_for('post', id=post.id))
    flash(_('Vote unsuccessful!'), 'danger')
    return redirect(url_for('post', id=post.id))

@app.route('/edit_answer/<id>', methods=['POST'])
@login_required
def edit_answer(id):
    answer = Answer.query.filter_by(id=id).first_or_404()
    post_id = answer.post.id
    if current_user == answer.author:
        editform = AnswerForm()
        if editform.validate_on_submit():
            if editform.delete.data:
                print('delete')
                Answer.query.filter_by(id=id).delete()
                db.session.commit()
                flash(_('Answer deleted'), 'success')
                return redirect(url_for('post', id=post_id))
            answer.edit_answer(editform.body.data, current_user)
            flash(_('Answer edited'), 'success')
            return redirect(url_for('post', id=post_id))



@app.route('/edit_post/<id>', methods=['POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    editform = PostForm() if current_user == post.author else None 
    if editform.validate_on_submit():
        tags = editform.tag.data.split()
        post.edit_post(editform.title.data, editform.body.data, tags, current_user)
        flash(_('Post edited'), 'success')
        return redirect(url_for('post', id=post.id))

@app.route('/bookmark_post/<id>', methods=['GET', 'POST'])
@login_required
def bookmark_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    current_user.toggle_post_bookmark(post)
    db.session.commit()
    flash(_('Post bookmarked'), 'success')
    return redirect(url_for('post', id=post.id))

@app.route('/follow_post/<id>', methods=['GET', 'POST'])
@login_required
def follow_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    current_user.toggle_post_follow(post)
    db.session.commit()
    flash(_('Post followed'), 'success')
    return redirect(url_for('post', id=post.id))


@app.route('/post/<id>', methods=['GET', 'POST'])
@login_required
def post(id):
    sort_by = request.args.get('sort_by')
    answerform = AnswerForm()
    post = Post.query.filter_by(id=id).first_or_404()

    # needed a separate query for answers, in order to implement sorting
    if sort_by == "created":
        answers = Answer.query.join(Post).order_by(Answer.created_at.desc()).filter(Post.id == id).all()
    elif sort_by == "edited":
        answers = Answer.query.join(Post).order_by(coalesce(Answer.edited_at, Answer.created_at).desc()).filter(Post.id == id).all()
    else:
        answers = Answer.query.join(Post).order_by(coalesce(Answer.total_votes, 0).desc()).filter(Post.id == id).all()

    editform = PostForm() if current_user == post.author else None 
    if answerform.validate_on_submit():
        answer = Answer(body=answerform.body.data, author=current_user, post=post)
        db.session.add(answer)
        db.session.commit()
        # users = post.author.posts_from_followed_user
        # print(users)
        # send_answered_notification(users,post.author, post.id)
        # flash(_('answer submitted'), 'success')

    
    return render_template('post_content.html.j2',answers=answers, post=post, answerform=answerform, voteform=PostVoteForm(),votes=post.total_votes,editform=editform)


@app.route('/accept_answer/<id>', methods=['GET', 'POST'])
@login_required
def accept_answer(id):
    answer = Answer.query.filter_by(id=id).first_or_404()
    post = answer.post
    if current_user == post.author:
        post.accept_answer(answer)
        db.session.commit()
        flash(_('Answer accepted'), 'success')
    print(answer.accepted)
    return redirect(url_for('post', id=post.id))

@app.route('/explore')
@login_required
def explore():
    sort_by = request.args.get('sort_by')
    page = request.args.get('page', 1, type=int)
    posts = current_user.post_without_ignored(sort_by=sort_by).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template('index.html.j2', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url,pagination=posts)


@app.route('/tag/<id>', methods=['GET', 'POST'])
@login_required
def tag(id):
    page = request.args.get('page', 1, type=int)
    tag = Tag.query.filter_by(id=id).first_or_404()
    sort_by = request.args.get('sort_by')
    if request.method == 'POST':
        print(request.form['submit_button'].lower())
        if 'follow' in request.form['submit_button'].lower():
            current_user.toggle_follow_tag(tag)
            db.session.commit()
            flash(_('Success'), 'success')
            return redirect(url_for('tag',id=tag.id))
        elif 'ignore' in request.form['submit_button'].lower():
            current_user.toggle_ignore_tag(tag)
            db.session.commit()
            flash(_("Success"), 'success')
            return redirect(url_for('tag',id=tag.id))
        
    elif request.method == 'GET':
        posts = tag.posts_with_tag(sort_by=sort_by).paginate(
            page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
        
        return render_template('posts_with_tag.html.j2', tag=tag, posts=posts, followed=current_user.is_following_tag(tag), 
                            ignored=current_user.is_ignoring_tag(tag))


@app.route('/tags')
@login_required
def tags():
    page = request.args.get('page', 1, type=int)
    tags = Tag.query.paginate(
            page=page, per_page=app.config["TAGS_PER_PAGE"], error_out=False)
    
    return render_template('tags.html.j2', title=_('Tags'),
                           tags=tags.items, pagination=tags)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'), 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html.j2', title=_('Sign In'), form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'), 'success')
        return redirect(url_for('login'))
    if form.errors:
        for error in form.errors:
            flash(_(f'Error: {form.errors[error][0]}'), 'danger')
    return render_template('register.html.j2', title=_('Register'), form=form)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'), 'info')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html.j2',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if user is None:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'), 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html.j2', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    sort_by = request.args.get('sort_by')
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.post_by_user(sort_by=sort_by).paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)

    return render_template('user_posts.html.j2', user=user, posts=posts.items,
                            pagination=posts)

@app.route('/user/bookmarked/<username>')
def user_bookmarked(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user == user:
        page = request.args.get('page', 1, type=int)
        posts = user.bookmarked_posts().paginate(
        page=page, per_page=app.config["POSTS_PER_PAGE"], error_out=False)
        return render_template('user_bookmarked.html.j2', user=user, posts=posts.items,
                            pagination=posts)
    else:
        flash(_('You cannot view this page'), 'danger')
        return redirect(url_for('index'))


@app.route('/user/edit_profile/<username>', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user != current_user:
        flash(_('You cannot edit this profile'), 'danger')
        return redirect(url_for('index'))
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'), 'success')
        return redirect(url_for('edit_profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('user_edit_profile.html.j2', title=_('Edit Profile'),
                           form=form, user=user)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username), 'danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot follow yourself!'), 'danger')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username), 'success')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username), 'danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'), 'danger')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username), 'success')
    return redirect(url_for('user', username=username))
