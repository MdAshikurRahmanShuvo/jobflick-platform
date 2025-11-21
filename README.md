JobFlick – Short-Term Job Platform

A modern web platform for finding short-term, hourly, and task-based jobs.
Built for students, freelancers, and part-time workers who want quick jobs nearby — with a clean UI and fast workflow.


| Users                       | Employers                     |
| --------------------------- | ----------------------------- |
| 🔍 Browse nearby short jobs | 📝 Post jobs easily           |
| 📍 Filter by location       | 🗂 Manage job listings        |
| 💬 Contact employers        | 📬 Receive applications       |
| 📱 Responsive UI            | 📈 Real-time updates (future) |


| Layer               | Technology       |
| ------------------- | ---------------- |
| **Backend**         | Django           |
| **Frontend**        | Bootstrap 5      |
| **Database**        | SQLite (default) |
| **Templating**      | Django Templates |
| **Version Control** | Git & GitHub     |


jobflick/
│── jobflick/                  # Main project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│
│── pages/                     # Static pages (Home, About, Contact)
│   ├── templates/pages/
│   │    ├── home.html
│   │    ├── about.html
│   │    └── contact.html
│   ├── urls.py
│   └── views.py
│
│── jobs/                      # Job posting module
│   ├── templates/jobs/
│   │    └── post_job.html
│   ├── urls.py
│   └── views.py
│
│── templates/
│   ├── base.html
│   └── include/
│        ├── navbar.html
│        └── footer.html
│
│── static/
│   └── images/
│        ├── logo.png
│        └── about_jobflick.png
│
│── db.sqlite3
│── manage.py
│── requirements.txt
│── README.md


Installation Guide
1️⃣ Clone the repository
git clone https://github.com/your-username/jobflick.git
cd jobflick
