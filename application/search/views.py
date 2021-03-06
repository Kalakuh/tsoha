from application import app, db
from flask import redirect, render_template, request, url_for
from application.categories.models import Category
from application.search.forms import SearchForm
from datetime import datetime, date, timedelta
from application.threads.models import Thread, Post
from application.auth.models import User
from application.utils.date_format import date_to_string
from flask_login import current_user

ITEMS_PER_PAGE = 10

def get_params(request):
	page_id = max(int(request.form.get("page_id")), 1)
	category_id = request.form.get("category_id")
	query_type = request.form.get("type")
	ordering = request.form.get("ordering")
	ascending = request.form.get("ascending")

	form = SearchForm(request.form)

	contains = form.contains.data
	name = form.name.data
	after_date = form.after_date.data
	before_date = form.before_date.data

	if not after_date:
		after_date = date(1900, 1, 1)
	if not before_date:
		before_date = date.today()

	before_date += timedelta(1)

	return [page_id, category_id, query_type, ordering, ascending, form, contains, name, after_date, before_date]


@app.route("/search/", methods=["GET", "POST"])
def search():
	if request.method == "GET":
		categories = Category.query.all()
		form = SearchForm()
		return render_template("search/search.html", categories = categories, form = form, results = [], type = "None", ascending = "false", ordering = "date", category_id = 0, page_id = 1, last_page_id = 1)

	page_id, category_id, query_type, ordering, ascending, form, contains, name, after_date, before_date = get_params(request)

	results = []

	if query_type == "thread":
		results = Thread.search_query(contains, name, after_date, before_date, ordering, ascending, category_id)
	elif query_type == "post":
		results = Post.search_query(contains, name, after_date, before_date, ordering, ascending, category_id)

	results = results[::-1]

	begin = (page_id - 1) * ITEMS_PER_PAGE
	end = page_id * ITEMS_PER_PAGE

	last_page_id = len(results) // ITEMS_PER_PAGE
	if len(results) % ITEMS_PER_PAGE != 0:
		last_page_id += 1
	last_page_id = max(1, last_page_id)

	results = results[begin:end]

	return render_template("search/search.html", categories = Category.query.all(), form = form, results = results, type = query_type, ascending = ascending, ordering = ordering, category_id = int(category_id), page_id = page_id, last_page_id = last_page_id)