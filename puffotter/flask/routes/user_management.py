import os
from typing import Union
from werkzeug import Response
from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user, logout_user, login_user
from puffotter.crypto import generate_hash, generate_random
from puffotter.recaptcha import verify_recaptcha
from puffotter.smtp import send_email
from puffotter.flask.base import app, db
from puffotter.flask.Config import Config
from puffotter.flask.db.User import User
from puffotter.flask.db.TelegramChatId import TelegramChatId


def define_blueprint(blueprint_name: str) -> Blueprint:
    """
    Defines the blueprint for this route
    :param blueprint_name: The name of the blueprint
    :return: The blueprint
    """
    blueprint = Blueprint(blueprint_name, __name__)

    @blueprint.route("/login", methods=["GET", "POST"])
    def login() -> Union[Response, str]:
        """
        Page that allows the user to log in
        :return: The response
        """
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"]
            remember_me = request.form.get("remember_me") in ["on", True]

            user: User = User.query.filter_by(username=username).first()

            if user is None:
                flash(Config.STRINGS["user_does_not_exist"], "danger")
            elif current_user.is_authenticated:
                flash(Config.STRINGS["user_already_logged_in"], "info")
            elif not user.confirmed:
                flash(Config.STRINGS["user_is_not_confirmed"], "danger")
            elif not user.verify_password(password):
                flash(Config.STRINGS["invalid_password"], "danger")
            else:
                login_user(user, remember=remember_me)
                flash(Config.STRINGS["logged_in"], "success")
                app.logger.info(f"User {current_user.username} logged in.")
                return redirect(url_for("static.index"))
            return redirect(url_for("user_management.login"))
        else:
            return render_template(
                "user_management/login.html",
                **Config.TEMPLATE_EXTRAS["login"]()
            )

    @blueprint.route("/logout", methods=["GET"])
    @login_required
    def logout() -> Union[Response, str]:
        """
        Logs out the user
        :return: The response
        """
        app.logger.info("User {} logged out.".format(current_user.username))
        logout_user()
        flash(Config.STRINGS["logged_out"], "info")
        return redirect(url_for("static.index"))

    @blueprint.route("/register", methods=["GET", "POST"])
    def register() -> Union[Response, str]:
        """
        Page that allows a new user to register
        :return: The response
        """
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            password_repeat = request.form["password-repeat"]
            recaptcha_result = verify_recaptcha(
                request.remote_addr,
                request.form.get("g-recaptcha-response", ""),
                Config.RECAPTCHA_SECRET_KEY
            )

            all_users = User.query.all()
            usernames = [user.username for user in all_users]
            emails = [user.email for user in all_users]

            _min, _max = Config.MIN_USERNAME_LENGTH, Config.MAX_USERNAME_LENGTH

            if len(username) < _min or len(username) > _max:
                flash(Config.STRINGS["username_length"]
                      .format(_min, _max), "danger")
            elif password != password_repeat:
                flash(Config.STRINGS["passwords_do_not_match"], "danger")
            elif username in usernames:
                flash(Config.STRINGS["username_already_exists"], "danger")
            elif email in emails:
                flash(Config.STRINGS["email_already_in_use"], "danger")
            elif not recaptcha_result:
                flash(Config.STRINGS["recaptcha_incorrect"], "danger")
            else:
                confirmation_key = generate_random(32)
                confirmation_hash = generate_hash(confirmation_key)
                user = User(
                    username=username,
                    email=email,
                    password_hash=generate_hash(password),
                    confirmation_hash=confirmation_hash
                )
                db.session.add(user)
                db.session.commit()
                email_msg = render_template(
                    "email/registration.html",
                    domain_name=Config.DOMAIN_NAME,
                    host_url=Config.base_url(),
                    target_url=os.path.join(Config.base_url(), "confirm"),
                    username=username,
                    user_id=user.id,
                    confirm_key=confirmation_key,
                    **Config.TEMPLATE_EXTRAS["registration_email"]()
                )
                send_email(
                    email,
                    Config.STRINGS["registration_email_title"],
                    email_msg,
                    Config.SMTP_HOST,
                    Config.SMTP_ADDRESS,
                    Config.SMTP_PASSWORD,
                    Config.SMTP_PORT
                )
                app.logger.info("User {} registered.".format(user.username))
                flash(Config.STRINGS["registration_successful"], "info")
                return redirect(url_for("static.index"))
            return redirect(url_for("user_management.register"))
        else:
            return render_template(
                "user_management/register.html",
                **Config.TEMPLATE_EXTRAS["register"]()
            )

    @blueprint.route("/confirm", methods=["GET"])
    def confirm() -> Union[Response, str]:
        """
        Confirms a user
        :return: The response
        """
        user_id = int(request.args["user_id"])
        confirm_key = request.args["confirm_key"]
        user: User = User.query.get(user_id)

        if user is None:
            flash(Config.STRINGS["user_does_not_exist"], "danger")
        elif user.confirmed:
            flash(Config.STRINGS["user_already_confirmed"], "warning")
        elif not user.verify_confirmation(confirm_key):
            flash(Config.STRINGS["confirmation_key_invalid"], "warning")
        else:
            user.confirmed = True
            db.session.commit()
            flash(Config.STRINGS["user_confirmed_successfully"], "success")
        return redirect(url_for("static.index"))

    @blueprint.route("/forgot", methods=["POST", "GET"])
    def forgot() -> Union[Response, str]:
        """
        Allows a user to reset their password
        :return: The response
        """
        if request.method == "POST":
            email = request.form["email"]
            recaptcha_result = verify_recaptcha(
                request.remote_addr,
                request.form.get("g-recaptcha-response", ""),
                Config.RECAPTCHA_SECRET_KEY
            )
            user: User = User.query.filter_by(email=email).first()

            if not recaptcha_result:
                flash(Config.STRINGS["recaptcha_incorrect"], "danger")
                return redirect(url_for("user_management.forgot"))
            else:
                if user is None:
                    # Fail silently to ensure that a potential attacker can't
                    # use the response to figure out information
                    # on registered users
                    pass
                else:
                    new_pass = generate_random(20)
                    user.password_hash = generate_hash(new_pass)
                    db.session.commit()

                    email_msg = render_template(
                        "email/forgot_password.html",
                        domain_name=Config.DOMAIN_NAME,
                        host_url=Config.base_url(),
                        target_url=os.path.join(Config.base_url(), "login"),
                        password=new_pass,
                        username=user.username,
                        **Config.TEMPLATE_EXTRAS["forgot_email"]()
                    )
                    send_email(
                        email,
                        Config.STRINGS["password_reset_email_title"],
                        email_msg,
                        Config.SMTP_HOST,
                        Config.SMTP_ADDRESS,
                        Config.SMTP_PASSWORD,
                        Config.SMTP_PORT
                    )
                flash(Config.STRINGS["password_was_reset"], "success")
                return redirect(url_for("static.index"))

        else:
            return render_template(
                "user_management/forgot.html",
                **Config.TEMPLATE_EXTRAS["forgot"]()
            )

    @blueprint.route("/profile", methods=["GET"])
    @login_required
    def profile() -> Union[Response, str]:
        """
        Allows a user to edit their profile details
        :return: The response
        """
        chat_id = TelegramChatId.query.filter_by(user=current_user).first()
        return render_template(
            "user_management/profile.html",
            **Config.TEMPLATE_EXTRAS["profile"](),
            telegram_chat_id=chat_id
        )

    @blueprint.route("/change_password", methods=["POST"])
    @login_required
    def change_password() -> Union[Response, str]:
        """
        Allows the user to change their password
        :return: The response
        """
        old_password = request.form["old_password"]
        new_password = request.form["new_password"]
        password_repeat = request.form["password_repeat"]
        user: User = current_user

        if new_password != password_repeat:
            flash(Config.STRINGS["passwords_do_not_match"], "danger")
        elif not user.verify_password(old_password):
            flash(Config.STRINGS["invalid_password"], "danger")
        else:
            user.password_hash = generate_hash(new_password)
            db.session.commit()
            flash(Config.STRINGS["password_changed"], "success")
        return redirect(url_for("user_management.profile"))

    @blueprint.route("/delete_user", methods=["POST"])
    @login_required
    def delete_user() -> Union[Response, str]:
        """
        Allows a user to delete their account
        :return: The response
        """
        password = request.form["password"]
        user: User = current_user

        if not user.verify_password(password):
            flash(Config.STRINGS["invalid_password"], "danger")
        else:
            app.logger.info("Deleting user {}".format(user))
            db.session.delete(user)
            db.session.commit()
            logout_user()
            flash(Config.STRINGS["user_was_deleted"], "success")
            return redirect(url_for("static.index"))
        return redirect(url_for("user_management.profile"))

    @blueprint.route("/register_telegram", methods=["POST"])
    @login_required
    def register_telegram() -> Union[Response, str]:
        """
        Allows the user to register a telegram chat ID
        :return: The response
        """
        telegram_chat_id = request.form["telegram_chat_id"]
        user: User = current_user
        chat_id = TelegramChatId.query.filter_by(user=user).first()

        if chat_id is None:
            chat_id = TelegramChatId(user=user, chat_id=telegram_chat_id)
            db.session.add(chat_id)
        else:
            chat_id.chat_id = telegram_chat_id
        db.session.commit()

        flash(Config.STRINGS["telegram_chat_id_set"], "success")
        chat_id.send_message(Config.STRINGS["telegram_chat_id_set"])
        return redirect(url_for("user_management.profile"))

    return blueprint
