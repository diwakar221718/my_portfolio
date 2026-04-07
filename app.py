from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# PostgreSQL Configuration (Render) or MySQL (Local Development)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Render PostgreSQL - use as-is
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Fallback to MySQL for local development
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'Dy@221718')
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
    MYSQL_DB = os.getenv('MYSQL_DB', 'portfolio_db')
    
    # Build MySQL connection string
    if MYSQL_PASSWORD:
        DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    else:
        DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 3600,
}

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'resumes')
UPLOAD_FOLDER_IMAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_IMAGES, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_IMAGES'] = UPLOAD_FOLDER_IMAGES
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

db = SQLAlchemy(app)

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_image_file(filename):
    """Check if image file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# ==================== DATABASE MODELS ====================

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    detailed_description = db.Column(db.Text)
    technologies = db.Column(db.String(500))  # comma-separated
    category = db.Column(db.String(100))  # Classification, Regression, NLP, CV, etc.
    image_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    notebook_url = db.Column(db.String(500))
    demo_url = db.Column(db.String(500))
    completion_date = db.Column(db.Date)
    role = db.Column(db.String(255))
    outcomes = db.Column(db.Text)
    performance_metrics = db.Column(db.String(500))  # JSON string
    featured = db.Column(db.Boolean, default=False)  # Featured on home page
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Project {self.title}>'


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))  # ML Frameworks, Programming, Data Tools, Cloud, Methodologies
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Skill {self.name}>'


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    issuer = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    credential_url = db.Column(db.String(1000))
    image_url = db.Column(db.String(1000))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Certification {self.title}>'


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    data_type = db.Column(db.String(50))  # tabular, image, text, timeseries, audio
    size = db.Column(db.String(50))  # e.g., "500MB", "1GB"
    format = db.Column(db.String(50))  # CSV, JSON, Parquet, etc.
    download_url = db.Column(db.String(500))
    documentation_url = db.Column(db.String(500))
    creation_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Dataset {self.name}>'


class BlogArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    summary = db.Column(db.String(500))
    external_url = db.Column(db.String(500))  # External blog link
    image_url = db.Column(db.String(500))  # Blog article image
    featured = db.Column(db.Boolean, default=False)  # Featured on home page
    published_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<BlogArticle {self.title}>'


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    key_achievements = db.Column(db.Text)  # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Experience {self.job_title} at {self.company_name}>'


class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_name = db.Column(db.String(255), nullable=False)
    degree = db.Column(db.String(255), nullable=False)
    field_of_study = db.Column(db.String(255))
    graduation_date = db.Column(db.Date)
    marks = db.Column(db.String(100))  # GPA, percentage, or marks
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Education {self.degree} from {self.institution_name}>'


class About(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(255))
    biography = db.Column(db.Text)
    photo_url = db.Column(db.String(500))
    address = db.Column(db.String(255))
    post = db.Column(db.String(255))
    research_interests = db.Column(db.Text)  # comma-separated
    specializations = db.Column(db.Text)  # comma-separated
    github_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    kaggle_url = db.Column(db.String(500))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return '<About>'


class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500))
    file_path = db.Column(db.String(500))  # For uploaded files
    description = db.Column(db.Text)
    version = db.Column(db.String(50))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Resume {self.title}>'


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    inquiry_type = db.Column(db.String(50))  # collaboration, job, general, other
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContactMessage from {self.name}>'


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


# ==================== ROUTES ====================

@app.route('/')
def home():
    """Homepage"""
    featured_projects = Project.query.filter_by(featured=True).limit(5).all()
    recent_articles = BlogArticle.query.filter_by(featured=True).order_by(BlogArticle.published_date.desc()).limit(3).all()
    about = About.query.first()
    return render_template('index.html', featured_projects=featured_projects, recent_articles=recent_articles, about=about)


@app.route('/projects')
def projects():
    """Projects listing page"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', None)
    search = request.args.get('search', None)
    
    query = Project.query
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Project.title.ilike(f'%{search}%') | Project.description.ilike(f'%{search}%'))
    
    projects_paginated = query.paginate(page=page, per_page=9)
    categories = db.session.query(Project.category).distinct().all()
    
    return render_template('projects.html', projects=projects_paginated, categories=categories, search=search, category=category)


@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    """Project detail page"""
    project = Project.query.get_or_404(project_id)
    related_projects = Project.query.filter(Project.id != project_id).limit(3).all()
    return render_template('project_detail.html', project=project, related_projects=related_projects)


@app.route('/datasets')
def datasets():
    """Datasets listing page"""
    page = request.args.get('page', 1, type=int)
    data_type = request.args.get('type', None)
    search = request.args.get('search', None)
    
    query = Dataset.query
    
    if data_type:
        query = query.filter_by(data_type=data_type)
    if search:
        query = query.filter(Dataset.name.ilike(f'%{search}%') | Dataset.description.ilike(f'%{search}%'))
    
    datasets_paginated = query.paginate(page=page, per_page=12)
    data_types = db.session.query(Dataset.data_type).distinct().all()
    
    return render_template('datasets.html', datasets=datasets_paginated, data_types=data_types, data_type=data_type, search=search)


@app.route('/datasets/<int:dataset_id>')
def dataset_detail(dataset_id):
    """Dataset detail page"""
    dataset = Dataset.query.get_or_404(dataset_id)
    return render_template('dataset_detail.html', dataset=dataset)


@app.route('/blog')
def blog():
    """Blog articles listing page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', None)
    
    query = BlogArticle.query
    
    if search:
        query = query.filter(BlogArticle.title.ilike(f'%{search}%') | BlogArticle.summary.ilike(f'%{search}%'))
    
    articles_paginated = query.order_by(BlogArticle.published_date.desc()).paginate(page=page, per_page=10)
    
    return render_template('blog.html', articles=articles_paginated, search=search)


@app.route('/blog/<int:article_id>')
def blog_detail(article_id):
    """Redirect to external blog link"""
    article = BlogArticle.query.get_or_404(article_id)
    if article.external_url:
        return redirect(article.external_url)
    return redirect(url_for('blog'))


@app.route('/skills')
def skills():
    """Skills page"""
    skills_by_category = {}
    all_skills = Skill.query.all()
    certifications = Certification.query.all()
    
    for skill in all_skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    return render_template('skills.html', skills_by_category=skills_by_category, certifications=certifications)


@app.route('/about')
def about():
    """About page"""
    about = About.query.first()
    experience = Experience.query.order_by(Experience.start_date.desc()).all()
    try:
        education = Education.query.order_by(Education.graduation_date.desc()).all()
    except Exception as e:
        # Handle case where starting_date column doesn't exist yet
        print(f"Error querying education: {e}")
        education = []
    
    resume = Resume.query.filter_by(is_active=True).first()
    return render_template('about.html', about=about, experience=experience, education=education, resume=resume)


@app.route('/resume')
def resume():
    """Resume page"""
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    active_resume = Resume.query.filter_by(is_active=True).first()
    return render_template('resume.html', resumes=resumes, active_resume=active_resume)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        inquiry_type = request.form.get('inquiry_type', 'general')
        
        if name and email and subject and message:
            contact_msg = ContactMessage(
                name=name,
                email=email,
                subject=subject,
                message=message,
                inquiry_type=inquiry_type
            )
            db.session.add(contact_msg)
            db.session.commit()
            return redirect(url_for('contact_success'))
    
    return render_template('contact.html')


@app.route('/contact/success')
def contact_success():
    """Contact success page"""
    return render_template('contact_success.html')


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_id', None)
    return redirect(url_for('home'))


def admin_required(f):
    """Decorator to check if admin is logged in"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_projects = Project.query.count()
    total_datasets = Dataset.query.count()
    total_articles = BlogArticle.query.count()
    total_skills = Skill.query.count()
    total_resumes = Resume.query.count()
    total_messages = ContactMessage.query.count()
    unread_messages = ContactMessage.query.filter_by(is_read=False).count()
    
    return render_template('admin/dashboard.html', 
                         total_projects=total_projects,
                         total_datasets=total_datasets,
                         total_articles=total_articles,
                         total_skills=total_skills,
                         total_resumes=total_resumes,
                         total_messages=total_messages,
                         unread_messages=unread_messages)


@app.route('/admin/projects')
@admin_required
def admin_projects():
    """Admin projects management"""
    page = request.args.get('page', 1, type=int)
    projects_paginated = Project.query.paginate(page=page, per_page=10)
    return render_template('admin/projects.html', projects=projects_paginated)


@app.route('/admin/projects/add', methods=['GET', 'POST'])
@admin_required
def admin_add_project():
    """Add new project"""
    if request.method == 'POST':
        project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            detailed_description=request.form.get('detailed_description'),
            technologies=request.form.get('technologies'),
            category=request.form.get('category'),
            image_url=request.form.get('image_url'),
            github_url=request.form.get('github_url'),
            notebook_url=request.form.get('notebook_url'),
            demo_url=request.form.get('demo_url'),
            completion_date=datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date(),
            role=request.form.get('role'),
            outcomes=request.form.get('outcomes'),
            performance_metrics=request.form.get('performance_metrics'),
            featured=request.form.get('featured') == 'on'
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html')


@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_project(project_id):
    """Edit project"""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.detailed_description = request.form.get('detailed_description')
        project.technologies = request.form.get('technologies')
        project.category = request.form.get('category')
        project.image_url = request.form.get('image_url')
        project.github_url = request.form.get('github_url')
        project.notebook_url = request.form.get('notebook_url')
        project.demo_url = request.form.get('demo_url')
        project.completion_date = datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date()
        project.role = request.form.get('role')
        project.outcomes = request.form.get('outcomes')
        project.performance_metrics = request.form.get('performance_metrics')
        project.featured = request.form.get('featured') == 'on'
        
        db.session.commit()
        return redirect(url_for('admin_projects'))
    
    return render_template('admin/project_form.html', project=project)


@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@admin_required
def admin_delete_project(project_id):
    """Delete project"""
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('admin_projects'))


@app.route('/admin/messages')
@admin_required
def admin_messages():
    """Admin messages management"""
    page = request.args.get('page', 1, type=int)
    messages_paginated = ContactMessage.query.order_by(ContactMessage.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/messages.html', messages=messages_paginated)


@app.route('/admin/messages/<int:message_id>')
@admin_required
def admin_message_detail(message_id):
    """View message detail"""
    message = ContactMessage.query.get_or_404(message_id)
    message.is_read = True
    db.session.commit()
    return render_template('admin/message_detail.html', message=message)


@app.route('/admin/messages/<int:message_id>/delete', methods=['POST'])
@admin_required
def admin_delete_message(message_id):
    """Delete message"""
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    return redirect(url_for('admin_messages'))


# ==================== ADMIN DATASETS ROUTES ====================

@app.route('/admin/datasets')
@admin_required
def admin_datasets():
    """Admin datasets management"""
    page = request.args.get('page', 1, type=int)
    datasets_paginated = Dataset.query.paginate(page=page, per_page=10)
    return render_template('admin/datasets.html', datasets=datasets_paginated)


@app.route('/admin/datasets/add', methods=['GET', 'POST'])
@admin_required
def admin_add_dataset():
    """Add new dataset"""
    if request.method == 'POST':
        dataset = Dataset(
            name=request.form.get('name'),
            description=request.form.get('description'),
            data_type=request.form.get('data_type'),
            size=request.form.get('size'),
            format=request.form.get('format'),
            download_url=request.form.get('download_url'),
            documentation_url=request.form.get('documentation_url'),
            creation_date=datetime.strptime(request.form.get('creation_date'), '%Y-%m-%d').date() if request.form.get('creation_date') else None
        )
        db.session.add(dataset)
        db.session.commit()
        return redirect(url_for('admin_datasets'))
    
    return render_template('admin/dataset_form.html')


@app.route('/admin/datasets/<int:dataset_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_dataset(dataset_id):
    """Edit dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if request.method == 'POST':
        dataset.name = request.form.get('name')
        dataset.description = request.form.get('description')
        dataset.data_type = request.form.get('data_type')
        dataset.size = request.form.get('size')
        dataset.format = request.form.get('format')
        dataset.download_url = request.form.get('download_url')
        dataset.documentation_url = request.form.get('documentation_url')
        dataset.creation_date = datetime.strptime(request.form.get('creation_date'), '%Y-%m-%d').date() if request.form.get('creation_date') else None
        
        db.session.commit()
        return redirect(url_for('admin_datasets'))
    
    return render_template('admin/dataset_form.html', dataset=dataset)


@app.route('/admin/datasets/<int:dataset_id>/delete', methods=['POST'])
@admin_required
def admin_delete_dataset(dataset_id):
    """Delete dataset"""
    dataset = Dataset.query.get_or_404(dataset_id)
    db.session.delete(dataset)
    db.session.commit()
    return redirect(url_for('admin_datasets'))


# ==================== ADMIN BLOG ROUTES ====================

@app.route('/admin/blog')
@admin_required
def admin_blog():
    """Admin blog management"""
    page = request.args.get('page', 1, type=int)
    articles_paginated = BlogArticle.query.order_by(BlogArticle.published_date.desc()).paginate(page=page, per_page=10)
    return render_template('admin/blog.html', articles=articles_paginated)


@app.route('/admin/blog/add', methods=['GET', 'POST'])
@admin_required
def admin_add_blog():
    """Add new blog link"""
    if request.method == 'POST':
        article = BlogArticle(
            title=request.form.get('title'),
            summary=request.form.get('summary'),
            image_url=request.form.get('image_url'),
            external_url=request.form.get('external_url'),
            featured=request.form.get('featured') == 'on',
            published_date=datetime.fromisoformat(request.form.get('published_date')) if request.form.get('published_date') else None
        )
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/blog_form.html')


@app.route('/admin/blog/<int:article_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_blog(article_id):
    """Edit blog link"""
    article = BlogArticle.query.get_or_404(article_id)
    
    if request.method == 'POST':
        article.title = request.form.get('title')
        article.summary = request.form.get('summary')
        article.image_url = request.form.get('image_url')
        article.external_url = request.form.get('external_url')
        article.featured = request.form.get('featured') == 'on'
        article.published_date = datetime.fromisoformat(request.form.get('published_date')) if request.form.get('published_date') else None
        
        db.session.commit()
        return redirect(url_for('admin_blog'))
    
    return render_template('admin/blog_form.html', article=article)


@app.route('/admin/blog/<int:article_id>/delete', methods=['POST'])
@admin_required
def admin_delete_blog(article_id):
    """Delete blog article"""
    article = BlogArticle.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin_blog'))


# ==================== ADMIN SKILLS ROUTES ====================

@app.route('/admin/skills')
@admin_required
def admin_skills():
    """Admin skills management"""
    page = request.args.get('page', 1, type=int)
    skills_paginated = Skill.query.paginate(page=page, per_page=10)
    return render_template('admin/skills.html', skills=skills_paginated)


@app.route('/admin/skills/add', methods=['GET', 'POST'])
@admin_required
def admin_add_skill():
    """Add multiple skills"""
    if request.method == 'POST':
        category = request.form.get('category')
        skills_input = request.form.get('skills', '')
        skill_names = [s.strip() for s in skills_input.split(',') if s.strip()]
        
        for skill_name in skill_names:
            skill = Skill(
                name=skill_name,
                category=category
            )
            db.session.add(skill)
        db.session.commit()
        return redirect(url_for('admin_skills'))
    
    # Get category from query parameter if provided
    category = request.args.get('category', '')
    return render_template('admin/skill_form.html', skill=None, pre_selected_category=category)


@app.route('/admin/skills/<int:skill_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_skill(skill_id):
    """Edit skill"""
    skill = Skill.query.get_or_404(skill_id)
    
    if request.method == 'POST':
        category = request.form.get('category')
        skills_input = request.form.get('name', '')
        skill_names = [s.strip() for s in skills_input.split(',') if s.strip()]
        
        # Delete the old skill
        db.session.delete(skill)
        db.session.commit()
        
        # Add new skills with the same category
        for skill_name in skill_names:
            new_skill = Skill(
                name=skill_name,
                category=category
            )
            db.session.add(new_skill)
        db.session.commit()
        return redirect(url_for('admin_skills'))
    
    return render_template('admin/skill_form.html', skill=skill)


@app.route('/admin/skills/<int:skill_id>/delete', methods=['POST'])
@admin_required
def admin_delete_skill(skill_id):
    """Delete skill"""
    skill = Skill.query.get_or_404(skill_id)
    db.session.delete(skill)
    db.session.commit()
    return redirect(url_for('admin_skills'))


@app.route('/admin/certifications', methods=['GET'])
@admin_required
def admin_certifications():
    """Admin certifications management"""
    certifications = Certification.query.all()
    return render_template('admin/certifications.html', certifications=certifications)


@app.route('/admin/add-certification', methods=['GET', 'POST'])
@admin_required
def admin_add_certification():
    """Add new certification"""
    if request.method == 'POST':
        cert = Certification(
            title=request.form.get('title'),
            issuer=request.form.get('issuer'),
            issue_date=datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d') if request.form.get('issue_date') else None,
            expiry_date=datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d') if request.form.get('expiry_date') else None,
            credential_url=request.form.get('credential_url'),
            image_url=request.form.get('image_url'),
            description=request.form.get('description')
        )
        db.session.add(cert)
        db.session.commit()
        return redirect(url_for('admin_certifications'))
    
    return render_template('admin/certification_form.html', certification=None)


@app.route('/admin/edit-certification/<int:certification_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_certification(certification_id):
    """Edit certification"""
    cert = Certification.query.get_or_404(certification_id)
    
    if request.method == 'POST':
        cert.title = request.form.get('title')
        cert.issuer = request.form.get('issuer')
        cert.issue_date = datetime.strptime(request.form.get('issue_date'), '%Y-%m-%d') if request.form.get('issue_date') else None
        cert.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d') if request.form.get('expiry_date') else None
        cert.credential_url = request.form.get('credential_url')
        cert.image_url = request.form.get('image_url')
        cert.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('admin_certifications'))
    
    return render_template('admin/certification_form.html', certification=cert)


@app.route('/admin/delete-certification/<int:certification_id>', methods=['POST'])
@admin_required
def admin_delete_certification(certification_id):
    """Delete certification"""
    cert = Certification.query.get_or_404(certification_id)
    db.session.delete(cert)
    db.session.commit()
    return redirect(url_for('admin_certifications'))


# ==================== ADMIN ABOUT ROUTES ====================

@app.route('/admin/about', methods=['GET', 'POST'])
@admin_required
def admin_about():
    """Admin about management"""
    about = About.query.first()
    
    if request.method == 'POST':
        if not about:
            about = About()
            db.session.add(about)
        
        # Handle photo file upload
        if 'photo_file' in request.files:
            file = request.files['photo_file']
            if file and file.filename and allowed_image_file(file.filename):
                filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER_IMAGES'], filename))
                about.photo_url = url_for('static', filename=f'uploads/{filename}', _external=False)
        
        about.biography = request.form.get('biography')
        about.address = request.form.get('address')
        about.post = request.form.get('post')
        about.headline = request.form.get('post')
        about.research_interests = request.form.get('research_interests')
        about.specializations = request.form.get('specializations')
        about.github_url = request.form.get('github_url')
        about.linkedin_url = request.form.get('linkedin_url')
        about.kaggle_url = request.form.get('kaggle_url')
        
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/about_form.html', about=about)


# ==================== ADMIN EDUCATION ROUTES ====================

@app.route('/admin/education')
@admin_required
def admin_education():
    """Admin education management"""
    try:
        education = Education.query.all()
    except Exception as e:
        # Handle case where starting_date column doesn't exist yet
        print(f"Error querying education: {e}")
        education = []
    return render_template('admin/education.html', education=education)


@app.route('/admin/education/add', methods=['GET', 'POST'])
@admin_required
def admin_add_education():
    """Add education"""
    if request.method == 'POST':
        edu = Education(
            degree=request.form.get('degree'),
            institution_name=request.form.get('institution_name'),
            field_of_study=request.form.get('field_of_study'),
            graduation_date=datetime.strptime(request.form.get('graduation_date'), '%Y-%m-%d') if request.form.get('graduation_date') else None,
            marks=request.form.get('marks'),
            description=request.form.get('description')
        )
        db.session.add(edu)
        db.session.commit()
        return redirect(url_for('admin_education'))
    
    return render_template('admin/education_form.html', education=None)


@app.route('/admin/education/<int:education_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_education(education_id):
    """Edit education"""
    edu = Education.query.get_or_404(education_id)
    
    if request.method == 'POST':
        edu.degree = request.form.get('degree')
        edu.institution_name = request.form.get('institution_name')
        edu.field_of_study = request.form.get('field_of_study')
        edu.graduation_date = datetime.strptime(request.form.get('graduation_date'), '%Y-%m-%d') if request.form.get('graduation_date') else None
        edu.marks = request.form.get('marks')
        edu.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('admin_education'))
    
    return render_template('admin/education_form.html', education=edu)


@app.route('/admin/education/<int:education_id>/delete', methods=['POST'])
@admin_required
def admin_delete_education(education_id):
    """Delete education"""
    edu = Education.query.get_or_404(education_id)
    db.session.delete(edu)
    db.session.commit()
    return redirect(url_for('admin_education'))


# ==================== ADMIN EXPERIENCE ROUTES ====================

@app.route('/admin/experience')
@admin_required
def admin_experience():
    """Admin experience management"""
    experience = Experience.query.all()
    return render_template('admin/experience.html', experience=experience)


@app.route('/admin/experience/add', methods=['GET', 'POST'])
@admin_required
def admin_add_experience():
    """Add experience"""
    if request.method == 'POST':
        exp = Experience(
            job_title=request.form.get('job_title'),
            company_name=request.form.get('company_name'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d') if request.form.get('end_date') else None,
            is_current=request.form.get('is_current') == 'on',
            description=request.form.get('description'),
            key_achievements=request.form.get('key_achievements')
        )
        db.session.add(exp)
        db.session.commit()
        return redirect(url_for('admin_experience'))
    
    return render_template('admin/experience_form.html', experience=None)


@app.route('/admin/experience/<int:experience_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_experience(experience_id):
    """Edit experience"""
    exp = Experience.query.get_or_404(experience_id)
    
    if request.method == 'POST':
        exp.job_title = request.form.get('job_title')
        exp.company_name = request.form.get('company_name')
        exp.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        exp.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d') if request.form.get('end_date') else None
        exp.is_current = request.form.get('is_current') == 'on'
        exp.description = request.form.get('description')
        exp.key_achievements = request.form.get('key_achievements')
        db.session.commit()
        return redirect(url_for('admin_experience'))
    
    return render_template('admin/experience_form.html', experience=exp)


@app.route('/admin/experience/<int:experience_id>/delete', methods=['POST'])
@admin_required
def admin_delete_experience(experience_id):
    """Delete experience"""
    exp = Experience.query.get_or_404(experience_id)
    db.session.delete(exp)
    db.session.commit()
    return redirect(url_for('admin_experience'))


# ==================== ADMIN RESUME ROUTES ====================

@app.route('/admin/resume')
@admin_required
def admin_resume():
    """Admin resume management"""
    resumes = Resume.query.order_by(Resume.upload_date.desc()).all()
    return render_template('admin/resume.html', resumes=resumes)


@app.route('/admin/resume/add', methods=['GET', 'POST'])
@admin_required
def admin_add_resume():
    """Add new resume"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        version = request.form.get('version')
        is_active = request.form.get('is_active') == 'on'
        
        file_url = None
        file_path = None
        
        # Check if file upload or URL is provided
        if 'resume_file' in request.files and request.files['resume_file'].filename:
            file = request.files['resume_file']
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_path = f'resumes/{filename}'
            else:
                return render_template('admin/resume_form.html', error='Only PDF files are allowed'), 400
        else:
            file_url = request.form.get('file_url')
            if not file_url:
                return render_template('admin/resume_form.html', error='Please provide either a file upload or URL'), 400
        
        resume = Resume(
            title=title,
            file_url=file_url,
            file_path=file_path,
            description=description,
            version=version,
            is_active=is_active
        )
        db.session.add(resume)
        db.session.commit()
        return redirect(url_for('admin_resume'))
    
    return render_template('admin/resume_form.html')


@app.route('/admin/resume/<int:resume_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_edit_resume(resume_id):
    """Edit resume"""
    resume = Resume.query.get_or_404(resume_id)
    
    if request.method == 'POST':
        resume.title = request.form.get('title')
        resume.description = request.form.get('description')
        resume.version = request.form.get('version')
        resume.is_active = request.form.get('is_active') == 'on'
        
        # Handle file upload
        if 'resume_file' in request.files and request.files['resume_file'].filename:
            file = request.files['resume_file']
            
            if file and allowed_file(file.filename):
                # Delete old file if it exists
                if resume.file_path:
                    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.file_path.split('/')[-1])
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resume.file_path = f'resumes/{filename}'
                resume.file_url = None  # Clear URL if file is uploaded
            else:
                return render_template('admin/resume_form.html', resume=resume, error='Only PDF files are allowed'), 400
        else:
            # Update URL if provided
            file_url = request.form.get('file_url')
            if file_url:
                resume.file_url = file_url
                # Clear file_path if URL is provided
                resume.file_path = None
        
        db.session.commit()
        return redirect(url_for('admin_resume'))
    
    return render_template('admin/resume_form.html', resume=resume)


@app.route('/admin/resume/<int:resume_id>/toggle', methods=['POST'])
@admin_required
def admin_toggle_resume(resume_id):
    """Toggle resume active status"""
    resume = Resume.query.get_or_404(resume_id)
    
    # If activating this resume, deactivate all others
    if not resume.is_active:
        Resume.query.update({Resume.is_active: False})
        resume.is_active = True
    else:
        # If deactivating, just toggle it off
        resume.is_active = False
    
    db.session.commit()
    return redirect(url_for('admin_resume'))


@app.route('/admin/resume/<int:resume_id>/delete', methods=['POST'])
@admin_required
def admin_delete_resume(resume_id):
    """Delete resume"""
    resume = Resume.query.get_or_404(resume_id)
    
    # Delete file if it exists
    if resume.file_path:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume.file_path.split('/')[-1])
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(resume)
    db.session.commit()
    return redirect(url_for('admin_resume'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_about():
    """Inject about info into all templates"""
    try:
        # Try to query About, but catch any errors
        about = About.query.first()
        return dict(about=about)
    except Exception as e:
        # If any error occurs, return None
        return dict(about=None)


@app.route('/download/dataset/<int:dataset_id>')
def download_dataset(dataset_id):
    """Download dataset file"""
    dataset = Dataset.query.get_or_404(dataset_id)
    
    if not dataset.file_path:
        return redirect(url_for('dataset_detail', dataset_id=dataset_id))
    
    # Construct full file path
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', dataset.file_path)
    
    if not os.path.exists(file_path):
        return redirect(url_for('dataset_detail', dataset_id=dataset_id))
    
    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))


# ==================== MIGRATION ROUTES ====================

@app.route('/admin/migrate/dataset-file-path')
@admin_required
def migrate_dataset_file_path():
    """Migrate: Add file_path column to Dataset table"""
    try:
        from sqlalchemy import text
        
        # Check if column already exists
        result = db.session.execute(text("SHOW COLUMNS FROM dataset LIKE 'file_path'"))
        if result.fetchone():
            return jsonify({'status': 'success', 'message': "Column 'file_path' already exists in dataset table"})
        else:
            # Add file_path column
            db.session.execute(text("ALTER TABLE dataset ADD COLUMN file_path VARCHAR(500)"))
            db.session.commit()
            return jsonify({'status': 'success', 'message': "Successfully added 'file_path' column to dataset table"})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database and create default admin user"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Create default admin user if it doesn't exist
            admin_exists = Admin.query.filter_by(username='admin').first()
            if not admin_exists:
                admin = Admin(username='admin', email='admin@portfolio.com')
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Default admin user created: admin / admin123")
            else:
                print("✓ Admin user already exists")
        except Exception as e:
            print(f"✗ Database initialization error: {e}")
            db.session.rollback()


if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    
    # Get port from environment or use default 5000
    port = int(os.getenv('PORT', 5000))
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
