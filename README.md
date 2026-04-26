# Diwakar Yadav - Data Science & AI/ML Portfolio

A professional portfolio website showcasing data science projects, skills, certifications, and expertise in machine learning and artificial intelligence.

## 🌐 Live Demo

Visit the live portfolio: [https://my-portfolio-railway.app](https://my-portfolio-railway.app)

## 📋 Features

### Public Pages
- **Home** - Welcome section with featured projects and latest articles
- **About** - Professional biography, education, experience, and social links
- **Projects** - Showcase of data science and ML projects with detailed descriptions
- **Skills** - Technical skills organized by category with proficiency levels
- **Datasets** - Collection of datasets used in projects
- **Blog** - Technical articles and insights on data science
- **Certifications** - Professional certifications and credentials
- **Resume** - Downloadable resume with PDF viewer
- **Contact** - Contact form for inquiries

### Admin Features
- **Dashboard** - Central admin control panel
- **Content Management** - Add/edit/delete projects, skills, education, experience, certifications, datasets, and blog articles
- **Resume Management** - Upload and manage multiple resumes with active/inactive status
- **Message Management** - View and manage contact form submissions
- **Dark Mode** - Toggle between light and dark themes

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite (local) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Deployment**: Railway.app
- **Version Control**: Git & GitHub

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip (Python package manager)
- Git

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/diwakar221718/my_portfolio.git
   cd my_portfolio
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   The app will be available at `http://localhost:5000`

## 🔐 Admin Access

- **URL**: `/admin/login`
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin123`

⚠️ **Important**: Change these credentials in production!

## 📁 Project Structure

```
my_portfolio/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── runtime.txt           # Python version specification
├── .env.example          # Environment variables template
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   ├── uploads/          # User uploaded images
│   └── resumes/          # Resume files
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── about.html        # About page
│   ├── projects.html     # Projects listing
│   ├── skills.html       # Skills & certifications
│   ├── blog.html         # Blog articles
│   ├── resume.html       # Resume viewer
│   ├── contact.html      # Contact form
│   ├── 404.html          # 404 error page
│   ├── 500.html          # 500 error page
│   └── admin/            # Admin templates
│       ├── dashboard.html
│       ├── about_form.html
│       ├── project_form.html
│       └── ...
└── __pycache__/          # Python cache files
```

## 🎨 Features in Detail

### Description Formatting
All description fields support flexible formatting:
- **Point-wise**: Each point on a new line (displays as bullet list)
- **Paragraph-wise**: Separate paragraphs with blank line (displays with spacing)

Example:
```
Developed machine learning model
Achieved 95% accuracy
Deployed to production

Implemented real-time predictions
Reduced inference time by 40%
```

### Dark Mode
- Toggle dark/light theme using the theme button in navigation
- Preferences are saved in browser localStorage
- All pages are fully styled for both themes

### Responsive Design
- Mobile-first approach
- Optimized for all screen sizes
- Touch-friendly interface
- Fast loading times

## 🚀 Deployment

### Deploy to Railway.app

1. **Connect GitHub repository**
   - Push code to GitHub
   - Connect Railway to your GitHub account

2. **Configure environment**
   - Set environment variables in Railway dashboard
   - Configure database (PostgreSQL)

3. **Deploy**
   - Railway automatically deploys on push to main branch
   - View logs in Railway dashboard

### Environment Variables

```
FLASK_ENV=production
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

## 📝 Usage

### Adding a Project

1. Go to Admin Dashboard → Projects
2. Click "Add New Project"
3. Fill in project details:
   - Title, description, detailed description
   - Technologies used
   - GitHub URL, notebook URL, demo URL
   - Performance metrics, outcomes
4. Save

### Adding Skills

1. Go to Admin Dashboard → Skills
2. Click "Add New Skill"
3. Select category and enter skill name
4. Save

### Managing Resume

1. Go to Admin Dashboard → Resume
2. Click "Add Resume"
3. Upload resume file or provide external URL
4. Toggle to set as active
5. Only active resume displays on resume page

### Publishing Blog Articles

1. Go to Admin Dashboard → Blog
2. Click "Add Article"
3. Enter article details and external URL
4. Save

## 🔧 Configuration

### Database
- **Local**: SQLite (app.db)
- **Production**: PostgreSQL

### File Uploads
- Images: `static/uploads/`
- Resumes: `static/resumes/`
- Datasets: `static/resumes/datasets/`

### Security
- Admin login required for all admin pages
- CSRF protection enabled
- Secure file upload validation
- SQL injection prevention

## 🐛 Troubleshooting

### Resume not showing
- Ensure resume is set as **active** in admin panel
- Check that file_url or file_path is populated
- Clear browser cache and refresh

### Images not displaying
- Verify image URL is correct
- Check file permissions in uploads folder
- Ensure image format is supported (JPG, PNG, etc.)

### Database errors
- Delete `app.db` and reinitialize database
- Check database connection string in .env
- Verify PostgreSQL is running (production)

## 📞 Contact

For inquiries or feedback, use the contact form on the website or reach out via:
- **Email**: [Your Email]
- **LinkedIn**: [Your LinkedIn]
- **GitHub**: [Your GitHub]

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with Flask and Bootstrap
- Deployed on Railway.app
- Icons from Font Awesome
- Inspired by modern portfolio designs

---

**Last Updated**: April 2026
**Version**: 1.0.0
