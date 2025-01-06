from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class RegisterForm(FlaskForm):
    username = StringField("მომხმარებლის სახელი", validators=[DataRequired()])
    email = StringField("მეილი", validators=[DataRequired(), Email()])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=8, message="პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო")])
    confirm_password = PasswordField("დაადასტურეთ პაროლი", validators=[DataRequired(), EqualTo('password', message="პაროლები არ ემთხვევა")])  # Ensure confirm_password is compared with 'password'
    birthday = DateField("დაბადების თარიღი", format='%Y-%m-%d', validators=[DataRequired()])
    country = SelectField("ქვეყანა", choices=[  # List of countries
        ('georgia', 'Georgia/საქართველო'),
        ('usa', 'United States/შეერთებული შტატები'),
        ('uk', 'United Kingdom/დიდი ბრიტანეთი'),
        ('germany', 'Germany/გერმანია'),
        ('france', 'France/ფრანგეთი'),
        ('spain', 'Spain/ესპანეთი'),
        ('italy', 'Italy/იტალია'),
        ('canada', 'Canada/კანადა'),
        ('brazil', 'Brazil/ბრაზილია'),
        ('india', 'India/ინდია'),
        ('australia', 'Australia/ავსტრალია'),
        ('japan', 'Japan/იაპონია'),
        ('china', 'China/ჩინეთი')
    ], validators=[DataRequired()])
    gender = SelectField("სქესი", choices=[  # Gender options
        ('', 'Select your gender/აირჩიეთ სქესი'),
        ('male', 'Male/კაცი'),
        ('female', 'Female/გოგო'),
        ('other', 'Other/სხვა')
    ], validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField("მომხმარებლის სახელი", validators=[DataRequired()])
    password = PasswordField("პაროლი", validators=[DataRequired(), Length(min=8, message="პაროლი უნდა იყოს მინიმუმ 8 სიმბოლო")])
