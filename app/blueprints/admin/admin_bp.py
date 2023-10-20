from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
import uuid
from sqlalchemy import or_

from app import login_required, current_user, db, logout_user

from app.utils import logging
from app.forms import AddUserForm 
from app.models import Users
from config import *

admin_bp = Blueprint(
	"admin",
	__name__,
	template_folder="templates"
	)

@admin_bp.route("/manage_users")
def manage_users():
	get_user_list = Users.query.all()
	return render_template("ap_users.html",userList=get_user_list)


@admin_bp.route("/manage_users/add_user",methods=["POST"])
def manage_users_add_user():
	data = request.form
	if data["password"] == data["AddRepeatPassword"]:
		if data["name"] and data["firstname"] and  data["username"] and data["password"] and data["role"] and data["email"] and data["job"]:
			form = AddUserForm(data=data)
			if AddUserForm.validate(form):
				if Users.query.filter_by(username=data["username"]).first() == None:
					guuid = str(uuid.uuid4())
					useradd = Users(uuid=guuid,username=data["username"],name=data["name"],firstname=data["firstname"],role=data["role"],email=data["email"],job=data["job"],enable=1)
					useradd.set_password(data["password"])
					db.session.add(useradd)
					db.session.commit()
					print("New user added",data["username"])
					return "ok"
				else:
					return "This username already exists"
			else:
				keys = list(dict(form.errors.items()))
				return jsonify(dict(form.errors.items())[keys[0]][0] )
		else:
			flash("please fields all input")
			return "Please fields all input"
	else:
		return "Password fields are not the same "

@admin_bp.route("/manage_users/mod_user",methods=["POST"])
def manage_users_mod_user():
	data = request.form
	form = AddUserForm(data=data)
	if "uuid" in request.form:
		guuid = request.form["uuid"]
		queryUser = Users.query.filter_by(uuid=guuid).first()
		if Users.query.filter_by(uuid=guuid).first() != None:
			if form.firstname.validate(form) and form.name.validate(form) and form.username.validate(form) and form.role.validate(form) and form.email.validate(form) and form.job.validate(form):
				if request.form["password"] != "" and request.form["EditRepeatPassword"] != "":
					if request.form["password"] == request.form["EditRepeatPassword"]:
						if form.password.validate(form):
							queryUser.password = data["password"]
						else:
							keys = list(dict(form.errors.items()))
							return dict(form.errors.items())[keys[0]][0]
					else:
						return "Password fields are not the same"
				queryUser.username = data["username"]
				queryUser.name = data["name"]
				queryUser.firstname = data["firstname"]
				queryUser.email = data["email"]
				queryUser.job = data["job"]
				db.session.flush()
				db.session.commit()
				return "ok"
			else:
				keys = list(dict(form.errors.items()))
				return jsonify(dict(form.errors.items())[keys[0]][0])
		else:
			logout_user()
			return "user not found"
	else:
		logout_user()
		return "user not found"


@admin_bp.route("/manage_users/mod_user/query",methods=["POST"])
def manage_users_mod_user_query():
	if "uuid" in request.form:
		guuid = request.form["uuid"]
		user = Users.query.filter_by(uuid=guuid).first()
		if user != None:
			return jsonify({"uuid":user.uuid,"name":user.name,"firstname":user.firstname,"username":user.username,"email":user.email,"job":user.job,"totp":True if user.OTPSecret else False,"role":user.role})
		else:
			return "user not found"	
	else:
		logout_user()
		return "user not found"

@admin_bp.route("/manage_users/del_user",methods=["POST"])
def manage_users_del_user():
	if "uuid" in request.form:
		guuid = request.form["uuid"]
		search = Users.query.filter_by(uuid=guuid).first()
		if search != None:
			db.session.delete(search)
			db.session.commit()
			return "ok"
		else:
			return "user not found"
	else:
		logout_user()
		return "user not found"

@admin_bp.route("/manage_users/able_user",methods=["POST"])
def manage_users_able_user():
	if "uuid" in request.form:
		guuid = request.form["uuid"]
		search = Users.query.filter_by(uuid=guuid).first()
		if search != None:
			if search.enable == 1:
				search.enable = 0
			elif search.enable == 0:
				search.enable = 1
			db.session.commit()
			return "ok"
		else:
			return "user not found"
	else:
		logout_user()
		return "user not found"