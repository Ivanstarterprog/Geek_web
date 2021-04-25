from flask_wtf import FlaskForm
from wtforms import StringField, FileField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class CommentsForm(FlaskForm):
    content = StringField('Комментарий', validators=[DataRequired()])
    photo = FileField("Фото к коментарию", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Отправить комментарий')
