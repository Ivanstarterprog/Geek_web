from flask import Flask
from data import db_session
from forms.user import RegisterForm
from flask import render_template, redirect, request, abort
from data.users import User
from flask_login import LoginManager, login_user, current_user
from forms.user import LoginForm
from flask_login import login_required, logout_user
from data.blogs import Blogs
from forms.blogs import BlogsForm, BlogsChangeForm
from flask_restful import abort, Api
import api.BlogsResource as BlogsResource
import api.UserAdminResource as UserAdminResource
from data.Places import Places
from forms.places import PlacesForm, PlacesChangeForm
from data.articles import Articles
from forms.articles import ArticlesForm, ArticlesChangeForm
from forms.comments import CommentsForm
from data.comments import Comments
from requests import post


from flask_ngrok import run_with_ngrok

app = Flask(__name__)
app.config['SECRET_KEY'] = 'geeks_are_cool'

login_manager = LoginManager()
login_manager.init_app(app)

api = Api(app)

run_with_ngrok(app)

def main():
    api.add_resource(BlogsResource.BlogsListResource, '/api/blogs/<string:secret_key>')
    api.add_resource(BlogsResource.BlogResource, '/api/blog/<int:blog_id>/<string:secret_key>')
    api.add_resource(UserAdminResource.AdminResource, '/api/admins/<int:user_id>/<string:secret_key>')
    api.add_resource(UserAdminResource.AdminsListResource, '/api/admins/<string:secret_key>')
    db_session.global_init("db/geeks.db")
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        comments = db_sess.query(Comments).filter(Comments.id_post == current_user.id, Comments.type == 'юзер')
        form = CommentsForm()
        if request.method == "POST":
            comment = Comments()
            comment.id_post = current_user.id
            comment.type = 'юзер'
            comment.photo = 'none'
            comment.commentariy = form.content.data
            current_user.comments.append(comment)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect(f'/user/{current_user.id}')
        return render_template("user.html", user=current_user, title='Главная страница', form=form, coms=comments)
    else:
        return render_template('index_guest.html', title='Главная страница')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Человек с таким ником уже есть, поэтому вам нужно сменить ник")
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Данная почта уже занята")
        avatar = form.avatar.data
        if avatar:
            filename = f'{form.name.data}.{avatar.filename.split(".")[1]}'
            avatar.save('static/img/avatars/' + filename)
        else:
            filename = 'default.jpg'
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
            avatar=filename
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    comments = db_sess.query(Comments).filter(Comments.id_post == user_id, Comments.type == 'юзер')
    form = CommentsForm()
    if request.method == "POST":
        comment = Comments()
        comment.id_post = current_user.id
        comment.type = 'юзер'
        comment.photo = 'none'
        comment.commentariy = form.content.data
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/user/{user_id}')
    return render_template("user.html", user=user, title='Профиль', form=form, coms=comments)


@app.route('/user_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def user_delete(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    if user and user.id == current_user.id or current_user.admin:
        comms = db_sess.query(Comments).filter(Comments.id_post == id, Comments.type == 'юзер')
        for comments in comms:
            db_sess.delete(comments)
        db_sess.delete(user)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/blogs/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_blog(id):
    form = BlogsChangeForm()
    db_sess = db_session.create_session()
    blog = db_sess.query(Blogs).filter(Blogs.id == id).first()
    if request.method == "GET":
        if blog:
            form.previue.data = blog.previue
            form.content.data = blog.content
            form.photo.data = blog.photo
        else:
            abort(404)
    if form.validate_on_submit():
        if db_sess.query(Blogs).filter(
                Blogs.title == blog.title).first():
            blog.previue = form.previue.data
            blog.content = form.content.data
            photo_blog = form.photo.data
            blog.changed = True
            if photo_blog:
                f = photo_blog
                filename = f'{blog.title}.{f.filename.split(".")[1]}'
                f.save('static/img/blogs_photos/' + filename)
                blog.photo = filename
            else:
                blog.photo = 'none'
            db_sess.commit()
        else:
            abort(404)

        return redirect('/blogs')
    return render_template('blogchange.html',
                        title='Редактирование блога', item=blog,
                        form=form
                           )

@app.route('/blogs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def blogs_delete(id):
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.id == id).first()
    if blogs and blogs.user.id == current_user.id or current_user.admin:
        comms = db_sess.query(Comments).filter(Comments.id_post==id, Comments.type=='блог')
        for comments in comms:
            db_sess.delete(comments)
        db_sess.delete(blogs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/blogs/')

@app.route('/comm_delete/<string:type>/<int:id>', methods=['GET', 'POST'])
@login_required
def comments_delete(type, id):
    db_sess = db_session.create_session()
    if type == 'blog':
        comment = db_sess.query(Comments).filter(Comments.id == id, Comments.type == 'блог').first()
        place = '../../blogs/blog/' + str(comment.id_post)
    if type == 'place':
        comment = db_sess.query(Comments).filter(Comments.id == id, Comments.type == 'место').first()
        place = '../../places/place/' + str(comment.id_post)
    if type == 'article':
        comment = db_sess.query(Comments).filter(Comments.id == id, Comments.type == 'статья').first()
        place = '../../articles/article/' + str(comment.id_post)
    if type == 'user':
        comment = db_sess.query(Comments).filter(Comments.id == id, Comments.type == 'юзер').first()
        place = '../../user/' + str(comment.id_post)
    if comment and comment.user.id == current_user.id or current_user.admin:
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect(place)

@app.route("/blogs/")
def blogs():
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter()
    return render_template("blogs.html", blogs=blogs, title='Блоги')

@app.route("/blogs/blog/<int:blog_id>", methods=['GET', 'POST'])
def blog(blog_id):
    db_sess = db_session.create_session()
    blogs = db_sess.query(Blogs).filter(Blogs.id == blog_id).first()
    comments = db_sess.query(Comments).filter(Comments.id_post == blog_id, Comments.type == 'блог')
    form = CommentsForm()
    if request.method == "POST":
        comment = Comments()
        comment.id_post = blog_id
        comment.type = 'блог'
        comment.commentariy = form.content.data
        photo_comment = form.photo.data
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        comments = db_sess.query(Comments).filter(Comments.id_post == blog_id, Comments.type == 'блог').first()
        if photo_comment:
            filename = f'{comments.id}.{photo_comment.filename.split(".")[1]}'
            photo_comment.save('static/img/comments_photo/blogs/' + filename)
            comments.photo = filename
        else:
            comments.photo = 'none'
        db_sess.commit()
        return redirect(f'/blogs/blog/{blog_id}')
    return render_template("blog.html", item=blogs, title='Блог', form=form, coms=comments)

@app.route('/blogs/new',  methods=['GET', 'POST'])
@login_required
def add_blogs():
    form = BlogsForm()
    if form.validate_on_submit():

        db_sess = db_session.create_session()
        blog = Blogs()
        if db_sess.query(Blogs).filter(
                Blogs.title == form.title.data).first():
            return render_template(
                'newblogs.html', title='Написание блога', form=form,
                message="К сожалению (или счастью, уже и не разберёшь), блог с таким названием уже создан")
        blog.title = form.title.data
        blog.previue = form.previue.data
        blog.content = form.content.data
        photo_blog = form.photo.data
        if photo_blog:
            f = photo_blog
            filename = f'{blog.title}.{f.filename.split(".")[1]}'
            f.save('static/img/blogs_photos/' + filename)
            blog.photo = filename
        else:
            blog.photo = 'none'
        current_user.blogs.append(blog)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/blogs/')
    return render_template('newblogs.html', title='Написание блога',
                           form=form)

@app.route("/places/")
def places():
    db_sess = db_session.create_session()
    places = db_sess.query(Places).filter()
    return render_template("places.html", title='Крутые места', places=places)

@app.route("/places/place/<int:place_id>" ,  methods=['GET', 'POST'])
def place(place_id):
    db_sess = db_session.create_session()
    place = db_sess.query(Places).filter(Places.id == place_id).first()
    comments = db_sess.query(Comments).filter(Comments.id_post == place_id, Comments.type == 'место')
    form = CommentsForm()
    if request.method == "POST":
        comment = Comments()
        comment.id_post = place_id
        comment.type = 'место'
        comment.commentariy = form.content.data
        photo_comment = form.photo.data
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        comments = db_sess.query(Comments).filter(Comments.id_post == place_id, Comments.type == 'место').first()
        if photo_comment:
            filename = f'{comments.id}.{photo_comment.filename.split(".")[1]}'
            photo_comment.save('static/img/comments_photo/places/' + filename)
            comments.photo = filename
        else:
            comments.photo = 'none'
        db_sess.commit()
        return redirect(f'/places/place/{place_id}')
    return render_template("place.html", item=place, title='Место', form=form, coms=comments)

@app.route('/places/new',  methods=['GET', 'POST'])
@login_required
def add_places():
    form = PlacesForm()
    if form.validate_on_submit():

        db_sess = db_session.create_session()
        place = Places()
        if db_sess.query(Places).filter(
                Places.name == form.name.data).first() or db_sess.query(Places).filter(
                Places.adress == form.adress.data).first():
            return render_template(
                'newplace.html', form=form, title='Добавление места',
                message="К сожалению (или счастью, уже и не разберёшь), об этом месте уже рассказали")
        place.name = form.name.data
        place.adress = form.adress.data
        place.content = form.about.data
        photo_place = form.photo.data
        if photo_place:
            f = photo_place
            filename = f'{place.name}.{f.filename.split(".")[1]}'
            f.save('static/img/places_photos/' + filename)
            place.photo = filename
        else:
            place.photo = 'none'
        current_user.places.append(place)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/places/')
    return render_template('newplace.html', title='Добавление места',
                           form=form)

@app.route('/places/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_place(id):
    form = PlacesChangeForm()
    db_sess = db_session.create_session()
    place = db_sess.query(Places).filter(Places.id == id).first()
    if request.method == "GET":
        if blog:
            form.about.data = blog.content
            form.photo.data.filename = blog.photo
        else:
            abort(404)
    if form.validate_on_submit():
        if db_sess.query(Places).filter(
                Places.title == place.title).first():
            place.content = form.about.data
            photo_place = form.photo.data
            place.changed = True
            if photo_place:
                filename = f'{place.title}.{photo_place.filename.split(".")[1]}'
                photo_place.save('static/img/places_photos/' + filename)
                place.photo = filename
            else:
                place.photo = 'none'
            db_sess.commit()
        else:
            abort(404)
        return redirect('/places')
    return render_template('placechange.html',
                        title='Редактирование информации о месте', item=place,
                        form=form
                           )

@app.route('/places_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def places_delete(id):
    db_sess = db_session.create_session()
    place = db_sess.query(Places).filter(Places.id == id).first()
    if place and place.user.id == current_user.id or current_user.admin:
        comms = db_sess.query(Comments).filter(Comments.id_post == id, Comments.type == 'место')
        for comments in comms:
            db_sess.delete(comments)
        db_sess.delete(place)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/places/')

@app.route("/articles/")
def articles():
    db_sess = db_session.create_session()
    articles = db_sess.query(Articles).filter()
    return render_template("Articles.html", title='Статьи', articles=articles)

@app.route("/articles/article/<int:article_id>",  methods=['GET', 'POST'])
def article(article_id):
    db_sess = db_session.create_session()
    article = db_sess.query(Articles).filter(Articles.id == article_id).first()
    comments = db_sess.query(Comments).filter(Comments.id_post == article_id, Comments.type == 'статья')
    form = CommentsForm()
    if request.method == "POST":
        comment = Comments()
        comment.id_post = article_id
        comment.type = 'статья'
        comment.commentariy = form.content.data
        photo_comment = form.photo.data
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        comment = db_sess.query(Comments).filter(Comments.id_post == article_id, Comments.type == 'статья').first()
        if photo_comment:
            filename = f'{comment.id}.{photo_comment.filename.split(".")[1]}'
            photo_comment.save('static/img/comments_photo/' + filename)
            comment.photo = filename
        else:
            comment.photo = 'none'
        db_sess.commit()
        return redirect(f'/articles/article/{article_id}')
    return render_template("article.html", item=article, title='Место', form=form, coms=comments)

@app.route('/articles/new',  methods=['GET', 'POST'])
@login_required
def add_article():
    form = ArticlesForm()
    if form.validate_on_submit():

        db_sess = db_session.create_session()
        article = Articles()
        if db_sess.query(Articles).filter(
                Articles.title == form.title.data).first():
            return render_template(
                'newplace.html', form=form, title='Написание статьи',
                message="К сожалению (или счастью, уже и не разберёшь), статья с таким названием уже написана")
        article.title = form.title.data
        article_previu = form.previu.data
        if article_previu:
            filename = f'{article.title}.{article_previu.filename.split(".")[1]}'
            article_previu.save('static/articles/previu/' + filename)
            article.previu = filename
        else:
            article.previu = 'none'
        article_self = form.content.data
        if article_self:
            filename = f'{article.title}.pdf'
            article_self.save('static/articles/' + filename)
            article.content = filename
        else:
            article.content = 'none'
        current_user.articles.append(article)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/articles/')
    return render_template('newarticle.html', title='Написание статьи',
                           form=form)

@app.route('/articles/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    form = ArticlesChangeForm()
    db_sess = db_session.create_session()
    article = db_sess.query(Articles).filter(Articles.id == id).first()
    if request.method == "GET":
        if not article:
            abort(404)
    if form.validate_on_submit():
        if db_sess.query(Articles).filter(
                Articles.title == article.title).first():
            article.changed = True
            article_previu = form.previu.data
            if article_previu:
                filename = f'{article.title}.{article_previu.filename.split(".")[1]}'
                article_previu.save('static/articles/previu/' + filename)
                article.previu = filename
            else:
                article.previu = 'none'
            article_self = form.content.data
            if article_self:
                filename = f'{article.title}.pdf'
                article_self.save('static/articles/' + filename)
                article.content = filename
            db_sess.commit()
        else:
            abort(404)
        return redirect('/articles')
    return render_template('articlechange.html',
                        title='Редактирование статьи', item=place,
                        form=form
                           )

@app.route('/articles_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def articles_delete(id):
    db_sess = db_session.create_session()
    article = db_sess.query(Articles).filter(Articles.id == id).first()
    if article and article.user.id == current_user.id or current_user.admin:
        comms = db_sess.query(Comments).filter(Comments.id_post == id, Comments.type == 'статья')
        for comments in comms:
            db_sess.delete(comments)
        db_sess.delete(article)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/articles/')

if __name__ == '__main__':
    main()