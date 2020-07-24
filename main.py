from cleaner.cleaner import Cleaner
from cleaner.utils.fake_client import log
from pyrogram import User, TermsOfService
from pyrogram.errors import RPCError, BadRequest, FloodWait, SessionPasswordNeeded
import time
import sys


def get_phone_number(app):
    while True:
        try:
            if not app.phone_number:
                while True:
                    value = input("Enter phone number:")
                    if not value:
                        continue
                    confirm = input("Is \"{}\" correct? (y/N): ".format(value)).lower()
                    if confirm == "y":
                        break
                app.phone_number = value
        except BadRequest as e:
            app.phone_number = None
        except FloodWait as e:
            time.sleep(e.x)
        else:
            break


def sign_in(app, sent_code):
    while True:
        if not app.phone_code:
            app.phone_code = input("Enter confirmation code: ")

        try:
            signed_in = app.sign_in(app.phone_number, sent_code.phone_code_hash, app.phone_code)
            return signed_in
        except BadRequest as e:
            print(e.MESSAGE)
            app.phone_code = None
        except SessionPasswordNeeded as e:
            print(e.MESSAGE)

            while True:
                print("Password hint: {}".format(app.get_password_hint()))

                if not app.password:
                    app.password = input("Enter password (empty to recover): ")

                try:
                    if not app.password:
                        confirm = input("Confirm password recovery (y/n): ")

                        if confirm == "y":
                            email_pattern = app.send_recovery_code()
                            print("The recovery code has been sent to {}".format(email_pattern))

                            while True:
                                recovery_code = input("Enter recovery code: ")

                                try:
                                    return app.recover_password(recovery_code)
                                except BadRequest as e:
                                    print(e.MESSAGE)
                                except FloodWait as e:
                                    print(e.MESSAGE.format(x=e.x))
                                    time.sleep(e.x)
                                except Exception as e:
                                    log.error(e, exc_info=True)
                                    raise
                        else:
                            app.password = None
                    else:
                        return app.check_password(app.password)
                except BadRequest as e:
                    print(e.MESSAGE)
                    app.password = None
                except FloodWait as e:
                    print(e.MESSAGE.format(x=e.x))
                    time.sleep(e.x)
        except FloodWait as e:
            print(e.MESSAGE.format(x=e.x))
            time.sleep(e.x)


def main():
    cleaner = Cleaner()
    try:
        is_authorized = cleaner.connect()
        if not is_authorized:
            try:
                get_phone_number(cleaner)
                sent_code = cleaner.send_code(cleaner.phone_number)
                if cleaner.force_sms:
                    sent_code = cleaner.resend_code(cleaner.phone_number, sent_code.phone_code_hash)
                signed_in = sign_in(cleaner, sent_code)
                if isinstance(signed_in, User):
                    return signed_in

                name = input("Enter phone number:")
                signed_up = cleaner.sign_up(cleaner.phone_code, sent_code.phone_code_hash, name)

                if isinstance(signed_in, TermsOfService):
                    cleaner.accept_terms_of_service(signed_in.id)

                return signed_up
            except RPCError as e:
                raise e
            finally:
                cleaner.disconnect()
                sys.exit(0)
        else:
            if cleaner.is_connected:
                cleaner.disconnect()
            cleaner.run()
    except ConnectionError:
        log.warning('connection error')


if __name__ == '__main__':
    main()
