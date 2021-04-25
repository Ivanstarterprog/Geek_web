from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class ArticlesForm(FlaskForm):
    title = StringField('Заголовок статьи', validators=[DataRequired()])
    previu = FileField("Превью картинка", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    content = FileField("Файл-содержание статьи", validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Применить')

class ArticlesChangeForm(FlaskForm):
    previu = FileField("Превью картинка", validators=[FileAllowed(['jpg', 'png'])])
    content = FileField("Файл-содержание статьи", validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Применить')