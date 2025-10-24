from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os

# --- Local imports ---
from models.recommendation_model import JobRecommender
from utils.api_client import generate_jobs_with_ai
from config import Config

# --- App Initialization ---
app = Flask(__name__)
load_dotenv()
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

print(f"GOOGLE_API_KEY Loaded: {bool(app.config.get('GOOGLE_API_KEY'))}")

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    skills = db.Column(db.Text)
    experience = db.Column(db.Integer)
    preferences = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_title = db.Column(db.String(150))
    company = db.Column(db.String(150))
    status = db.Column(db.String(50), default='Applied')


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


with app.app_context():
    db.create_all()


# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')


# ---------- Authentication ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# ---------- Profile ----------
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.skills = request.form['skills']
        current_user.experience = int(request.form['experience'])
        current_user.preferences = request.form['preferences']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('recommendations'))
    return render_template('profile.html')


# ---------- Recommendations ----------
@app.route('/recommendations')
@login_required
def recommendations():
    if not current_user.skills:
        flash('Please complete your profile first.', 'info')
        return redirect(url_for('profile'))

    skills = [s.strip() for s in current_user.skills.split(',')]
    prefs = [p.strip() for p in current_user.preferences.split(',')] if current_user.preferences else []
    search_keywords = skills + prefs

    if not search_keywords:
        flash('Please add some skills or preferences to your profile.', 'warning')
        return redirect(url_for('profile'))

    jobs_df = generate_jobs_with_ai(keywords=search_keywords)

    if jobs_df.empty:
        flash('Could not generate job recommendations. Try again later.', 'danger')
        return render_template('recommendations.html', jobs=[])

    recommender = JobRecommender()
    recommender.fit(jobs_df)

    user_profile = {
        'skills': skills,
        'experience': current_user.experience,
        'preferences': prefs
    }

    recommended_jobs = recommender.recommend(user_profile)
    jobs_for_template = [job.to_dict() for job in recommended_jobs]

    return render_template('recommendations.html', jobs=jobs_for_template)


# ---------- Apply Job ----------
@app.route('/apply', methods=['POST'])
@login_required
def apply_job():
    job_title = request.form.get('job_title')
    company = request.form.get('company')

    # Prevent duplicate applications
    existing = JobApplication.query.filter_by(user_id=current_user.id, job_title=job_title, company=company).first()
    if existing:
        flash(f'You already applied for "{job_title}" at {company}.', 'warning')
        return redirect(url_for('recommendations'))

    application = JobApplication(user_id=current_user.id, job_title=job_title, company=company)
    db.session.add(application)
    db.session.commit()

    flash(f'You successfully applied for "{job_title}" at {company}.', 'success')
    return redirect(url_for('applications'))


# ---------- My Applications ----------
@app.route('/applications')
@login_required
def applications():
    apps = JobApplication.query.filter_by(user_id=current_user.id).all()
    return render_template('applications.html', applications=apps)


# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)



