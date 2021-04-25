from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class BlogsForm(FlaskForm):
    title = StringField('Заголовок блога', validators=[DataRequired()])
    previue = TextAreaField("Превью-текст")
    content = TextAreaField("Содержание блога")
    photo = FileField('Добавить фото к блогу', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Применить')

class BlogsChangeForm(FlaskForm):
    previue = TextAreaField("Превью-текст")
    content = TextAreaField("Содержание блога")
    photo = FileField('Добавить фото к блогу', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Применить')