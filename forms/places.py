from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed


class PlacesForm(FlaskForm):
    name = StringField('Название места', validators=[DataRequired()])
    adress = TextAreaField("Адрес", validators=[DataRequired()])
    about = TextAreaField("Описание места")
    photo = FileField('Добавить фото заведения', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Применить')

class PlacesChangeForm(FlaskForm):
    adress = TextAreaField("Адрес", validators=[DataRequired()])
    about = TextAreaField("Описание места")
    photo = FileField('Добавить фото заведения', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Применить')