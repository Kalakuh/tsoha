from application import app, db
from flask import redirect, render_template, request, url_for
from application.auth.models import User
from application.threads.models import Thread, Post
from application.threads.forms import ThreadForm
from application.utils.date_format import date_to_string
from application import admin_required
from flask_login import current_user
from application.categories.models import Category

THREADS_PER_PAGE = 10

@app.route("/", methods=["GET"])
def index():
	return redirect(url_for("index_by_page_id", page_id = 1))

@app.route("/<page_id>/", methods=["GET"])
def index_by_page_id(page_id):
	page_id = max(int(page_id), 1)
	begin = (page_id - 1) * THREADS_PER_PAGE
	end = page_id * THREADS_PER_PAGE

	threads = Thread.query.all()
	threads = threads[::-1]

	last_page_id = len(threads) // THREADS_PER_PAGE
	if len(threads) % THREADS_PER_PAGE != 0:
		last_page_id += 1
	last_page_id = max(1, last_page_id)

	display_threads = threads[begin:end]

	return render_template("index.html", threads = display_threads, page_id = page_id, last_page_id = last_page_id, active = User.active_users(), user_count = db.session().query(User).count(), post_count = db.session().query(Post).count())

@app.route("/404/")
def error404():
	return render_template("404.html")

@app.errorhandler(500)
def on500(e):
	# Error 500 happens currently basically only if the user tries to put invalid url,
	#  because then e.g. a string is tried to be parsed as a string, which leads to an error.
	# For database errors the page still displays a regular error message instead of 404 page,
	#  so this should not cause trouble on finding them.
	return render_template("404.html")

@app.errorhandler(404)
def on404(e):
	return render_template("404.html")