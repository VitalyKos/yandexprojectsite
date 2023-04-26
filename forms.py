__all__ = ["RegisterForm", "LoginForm", "MessageForm", "ForumForm", "CategoryForm"]

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import DateField, EmailField, FileField, IntegerField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

from database import Session, User


def unique():
    def check(form, field):
        with Session() as session:
            user = session.query(User).filter(getattr(User, field.name) == field.data).first()
        if user is not None:
            raise ValidationError("Уже занято!")

    return check


class RegisterForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired(), unique()])
    email = EmailField('Почта', validators=[DataRequired(), unique()])
    born_at = DateField("Дата рождения", validators=[DataRequired()])
    hashed_password = PasswordField('Пароль', validators=[DataRequired()])
    city = StringField("Город (опционально)")
    status = StringField("Статус (опционально)")
    icon = FileField("Иконка (опционально)", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Зарегистрироваться')


def check_exist():
    def _check_exist(form, field):
        with Session() as session:
            user = session.query(User).filter(User.nickname == field.data).first()
        if user is None:
            raise ValidationError("Пользователя с таким никнеймом не существует.")

    return _check_exist


def check_password():
    def _check_password(form, field):
        with Session() as session:
            user = session.query(User).filter(User.nickname == form.nickname.data).first()
        if not user or not user.check_password(field.data):
            raise ValidationError("Пароли не совпадают!")

    return _check_password


class LoginForm(FlaskForm):
    nickname = StringField('Никнейм', validators=[DataRequired(), check_exist()])
    password = PasswordField('Пароль', validators=[DataRequired(), check_password()])
    submit = SubmitField('Войти')


class MessageForm(FlaskForm):
    text = TextAreaField("Сообщение", validators=[DataRequired()])
    submit = SubmitField("Отправить сообщение")


class ForumForm(FlaskForm):
    category_id = IntegerField("Айди категории", validators=[DataRequired()])
    author_id = IntegerField("Айди создателя", validators=[DataRequired()])
    title = StringField("Заголовок", validators=[DataRequired()])
    icon = FileField("Иконка (опционально)", validators=[FileAllowed(['jpg', 'jpeg', 'png'])])
    first_message = TextAreaField("Первое сообщение", validators=[DataRequired()])
    submit = SubmitField("Создать форум")


class CategoryForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired()])
    submit = SubmitField("Создать категорию")
