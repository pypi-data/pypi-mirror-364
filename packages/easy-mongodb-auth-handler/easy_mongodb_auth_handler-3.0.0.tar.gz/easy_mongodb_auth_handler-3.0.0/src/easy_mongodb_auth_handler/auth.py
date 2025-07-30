"""
Authentication and user management for the easy_mongodb_auth_handler package.
"""

import time
import os
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from .package_functions.func import (
    validate_email,
    hash_password,
    generate_secure_code,
    send_verification_email,
    check_password
)
from .package_functions.message import get_messages


class Auth:
    """
    Handles user authentication and management using MongoDB.
    """

    def __init__(self, conf_file=None, mongo_uri=None, db_name=None,
                 mail_info=None,
                 mail_subject="Verification Code",
                 mail_body="Your verification code is: {verifcode}",
                 blocking=True, rate_limit=0, rate_limit_penalty=0, readable_errors=True,
                 code_length=6, db_attempts=6, db_delay=10, db_timeout=5000,
                 certs=certifi.where()):
        """
        initializes the Auth class

        Args:
            conf_file (str, optional): Path to a .env configuration file.
            mongo_uri (str, optional): MongoDB connection URI.
            db_name (str, optional): Name of the database.
            mail_info (dict, optional): Email server configuration with keys:
                'server', 'port', 'username', 'password'.
            mail_subject (str, optional): Custom email subject template.
                Use {verifcode} placeholder for verification code.
                Defaults to "Verification Code".
            mail_body (str, optional): Custom email body template.
                Use {verifcode} placeholder for verification code.
                Supports both plain text and HTML.
                Defaults to "Your verification code is: {verifcode}".
            blocking (bool): Enable user blocking.
            rate_limit (int): Rate limit for user actions in seconds.
            rate_limit_penalty (int): Penalty time in seconds for rate limiting.
            readable_errors (bool): Use readable error messages.
            code_length (int): Length of the verification code.
                Defaults to 6.
            db_attempts (int): Number of connection attempts.
            db_delay (int): Delay between connection attempts in seconds.
            db_timeout (int): Timeout in milliseconds for MongoDB connection.
            certs (str): Path to CA bundle for SSL verification.
        """
        if not mongo_uri or not db_name:
            if conf_file:
                load_dotenv(conf_file)
            elif os.path.exists(".emdb_auth"):
                load_dotenv(".emdb_auth")
            else:
                raise ValueError("Missing info and configuration "
                                 "file not found or not provided.")
            mongo_uri = os.getenv("MONGO_URI", None)
            db_name = os.getenv("DB_NAME", None)
            mail_info = os.getenv("MAIL_INFO", None)
            mail_subject = os.getenv("MAIL_SUBJECT",
                                     "Verification Code")
            mail_body = os.getenv("MAIL_BODY",
                                  "Your verification code is: {verifcode}")
            blocking = bool(os.getenv("BLOCKING", "True"))
            rate_limit = int(os.getenv("RATE_LIMIT", "0"))
            rate_limit_penalty = int(os.getenv("RATE_LIMIT_PENALTY", "0"))
            readable_errors = bool(os.getenv("READABLE_ERRORS"))
            code_length = int(os.getenv("CODE_LENGTH", "6"))
            db_attempts = int(os.getenv("DB_ATTEMPTS", "1"))
            db_delay = int(os.getenv("DB_DELAY", "10"))
            db_timeout = int(os.getenv("DB_TIMEOUT", "5000"))
            certs = os.getenv("CERTS", certifi.where())
        if not mongo_uri or not db_name:
            raise ValueError("MongoDB URI and DB name must be provided.")
        self.db = None
        self.retry_count = 0
        if db_attempts < 1:
            raise ValueError("Number of attempts must be at least 1.")
        if db_delay < 0:
            raise ValueError("Delay must be a non-negative integer.")
        self.max_retries = db_attempts
        while self.db is None and self.retry_count < self.max_retries:
            try:
                self.client = MongoClient(mongo_uri,
                                          serverSelectionTimeoutMS=db_timeout,
                                          tlsCAFile=certs
                                          )
                self.db = self.client[db_name]
            except Exception:
                self.retry_count += 1
                time.sleep(db_delay)
        if self.db is None:
            raise Exception('Could not connect to MongoDB instance.')
        self.users = self.db["users"]
        self.blocked = self.db["blocked"]
        self.limit = self.db["limit"]
        self.mail_info = mail_info
        if self.mail_info:
            if not self.mail_info["server"]:
                raise ValueError("Mail server information is incomplete - missing server key.")
            if not self.mail_info["port"]:
                raise ValueError("Mail server information is incomplete - missing port key.")
            if not self.mail_info["username"]:
                raise ValueError("Mail server information is incomplete - missing username key.")
            if not self.mail_info["password"]:
                raise ValueError("Mail server information is incomplete - missing password key.")
        self.blocking = blocking
        self.rate_limit = rate_limit
        self.messages = get_messages(readable_errors)
        self.penalty = rate_limit_penalty
        self.mail_subject = mail_subject
        self.mail_body = mail_body
        self.code_length = code_length

    def __del__(self):
        """
        Ensures the MongoDB client is closed when the Auth instance is deleted.
        """
        if hasattr(self, 'client'):
            self.client.close()

    def _find_user(self, email):
        """
        Helper to find a user by email.

        Args:
            email (str): User's email address.

        Returns:
            dict: User document if found, None otherwise.
        """
        return self.users.find_one({"email": email})

    def _find_blocked_user(self, email):
        """
        Helper to find a user's entry in the blocked database by email.

        Args:
            email (str): User's email address.

        Returns:
            dict: User document if found, None otherwise.
        """
        return self.blocked.find_one({"email": email})

    def _block_checker(self, email, user):
        """
        helper to check if a user is blocked.

        Args:
            email (str): User's email address.
            user (dict): User document.

        Returns:
            dict: Error message if user is blocked or not found, None otherwise.
        """
        blocked_user = self._find_blocked_user(email)
        if not user:
            return {"success": False, "message": self.messages["user_not_found"]}
        if self.blocking:
            if not blocked_user:
                return {"success": False, "message": self.messages["not_found_blocked"]}
            if blocked_user["blocked"]:
                return {"success": False, "message": self.messages["user_blocked"]}
        return None

    def _rate_limit_checker(self, email, ignore_rate_limit, skip_update=False):
        """
        Helper to check if a user is rate limited.

        Args:
            email (str): User's email address.
            ignore_rate_limit (bool): Ignore rate limiting for this action.

        Returns:
            bool: True if the user is rate limited, False otherwise.
        """
        if self.rate_limit > 0 and not ignore_rate_limit:
            limit = self.limit.find_one({"email": email})
            if limit:
                if limit["last_action"] < time.time() and not skip_update:
                    self.limit.update_one({"email": email}, {"$set": {"last_action": time.time()}})
                if time.time() - limit["last_action"] < self.rate_limit:
                    if not skip_update:
                        self.limit.update_one({
                            "email": email}, {
                            "$set": {"last_action": int(time.time()) + self.penalty}})
                    return True
            else:
                if not skip_update:
                    self.limit.insert_one({"email": email, "last_action": time.time()})
        return False

    def is_rate_limited(self, email):
        """
        Checks if a user is rate limited.

        Args:
            email (str): User's email address.

        Returns:
            dict: Success status and message.
        """
        try:
            if self._rate_limit_checker(email, ignore_rate_limit=False, skip_update=True):
                return {"success": False, "message": self.messages["rate_limited"]}
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": True, "message": str(error)}

    def check_and_update_rate_limit(self, email):
        """
        Checks and updates the rate limit for a user.

        Args:
            email (str): User's email address.

        Returns:
            dict: Success status and message.
        """
        try:
            if self._rate_limit_checker(email, ignore_rate_limit=False):
                return {"success": False, "message": self.messages["rate_limited"]}
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def update_rate_limit(self, email):
        """
        Updates the last request time for a user.

        Args:
            email (str): User's email address.

        Returns:
            dict: Success status and message.
        """
        try:
            self._rate_limit_checker(email, ignore_rate_limit=False)
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def register_user_no_verif(self, email, password, custom_data=None,
                               ignore_rate_limit=False):
        """
        registers a user without email verification

        Args:
            email (str): User's email address.
            password (str): User's password.
            custom_data: Custom data to save with the user.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        if custom_data is None:
            custom_data = {}
        try:
            if not validate_email(email):
                return {"success": False, "message": self.messages["invalid_email"]}
            if self._find_user(email):
                return {"success": False, "message": self.messages["user_exists"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if self.blocking:
                blocked_user = self._find_blocked_user(email)
                if blocked_user:
                    if blocked_user["blocked"]:
                        return {"success": False, "message": self.messages["user_blocked"]}
                else:
                    self.blocked.insert_one({"email": email, "blocked": False})
            hashed_password = hash_password(password)
            self.users.insert_one(
                {
                    "email": email,
                    "password": hashed_password,
                    "blocked": False,
                    "verified": True,
                    "custom_data": custom_data
                }
            )
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def reset_password_no_verif(self, email, old_password, new_password,
                                ignore_rate_limit=False):
        """
        resets a user's password without email verification

        Args:
            email (str): User's email address.
            old_password (str): User's current password.
            new_password (str): New password.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if not check_password(user, old_password):
                return {"success": False, "message": self.messages["invalid_old_pass"]}
            hashed_password = hash_password(new_password)
            self.users.update_one({"email": email}, {"$set": {"password": hashed_password}})
            return {"success": True, "message": self.messages["password_reset_success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def change_email_no_verif(self, email, new_email, password,
                              ignore_rate_limit=False):
        """
        resets a user's email without previous email verification

        Args:
            email (str): User's email address.
            new_email (str): User's new email.
            password (str): password.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if self.users.find_one({"email": new_email}):
                return {"success": False, "message": self.messages["user_exists"]}
            if not check_password(user, password):
                return {"success": False, "message": self.messages["invalid_pass"]}
            self.users.update_one({"email": email}, {"$set": {"email": new_email}})
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def register_user(self, email, password, custom_data=None,
                      cust_length=None, ignore_rate_limit=False):
        """
        registers a user with email verification

        Args:
            email (str): User's email address.
            password (str): User's password.
            custom_data: Custom data to save with the user.
            cust_length (int, optional): Custom length for the verification code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        if custom_data is None:
            custom_data = {}
        if not self.mail_info:
            raise ValueError("Mail server information is required for user verification.")
        try:
            if not validate_email(email):
                return {"success": False, "message": self.messages["invalid_email"]}
            if self.users.find_one({"email": email}):
                return {"success": False, "message": self.messages["user_exists"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}

            if self.blocking:
                blocked_user = self._find_blocked_user(email)
                if blocked_user:
                    if blocked_user["blocked"]:
                        return {"success": False, "message": self.messages["user_blocked"]}
                else:
                    self.blocked.insert_one({"email": email, "blocked": False})
            hashed_password = hash_password(password)
            if cust_length:
                length = int(cust_length)
            else:
                length = self.code_length
            verification_code = generate_secure_code(length)
            send_verification_email(self.mail_info, email, verification_code,
                                    self.mail_subject, self.mail_body)
            self.users.insert_one(
                {
                    "email": email,
                    "password": hashed_password,
                    "verification_code": verification_code,
                    "blocked": False,
                    "verified": False,
                    "custom_data": custom_data,
                }
            )
            return {"success": True, "message": self.messages["verification_code_sent"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def register_user_no_pass(self, email, custom_data=None,
                              cust_length=None, ignore_rate_limit=False):
        """
        registers a user without password and instead uses email verification.

        Args:
            email (str): User's email address.
            custom_data: Custom data to save with the user.
            cust_length (int, optional): Custom length for the verification code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        if custom_data is None:
            custom_data = {}
        if not self.mail_info:
            raise ValueError("Mail server information is required for user verification.")
        try:
            if not validate_email(email):
                return {"success": False, "message": self.messages["invalid_email"]}
            if self.users.find_one({"email": email}):
                return {"success": False, "message": self.messages["user_exists"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}

            if self.blocking:
                blocked_user = self._find_blocked_user(email)
                if blocked_user:
                    if blocked_user["blocked"]:
                        return {"success": False, "message": self.messages["user_blocked"]}
                else:
                    self.blocked.insert_one({"email": email, "blocked": False})
            if cust_length:
                length = int(cust_length)
            else:
                length = self.code_length
            verification_code = generate_secure_code(length)
            send_verification_email(self.mail_info, email, verification_code,
                                    self.mail_subject, self.mail_body)
            self.users.insert_one(
                {
                    "email": email,
                    "password": None,
                    "verification_code": verification_code,
                    "blocked": False,
                    "verified": False,
                    "custom_data": custom_data
                }
            )
            return {"success": True, "message": self.messages["verification_code_sent"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def verify_user(self, email, code, ignore_rate_limit=False):
        """
        verifies a user's email using a verification code.

        Args:
            email (str): User's email address.
            code (str): Verification code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self.users.find_one({"email": email})
            output = self._block_checker(email, user)
            if output:
                return output
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if user["verification_code"] == code:
                self.users.update_one({"email": email}, {"$set": {"verified": True,
                                                                  "verification_code": None}})
                return {"success": True, "message": self.messages["user_verified"]}
            return {"success": False, "message": self.messages["invalid_reset"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def authenticate_user(self, email, password, mfa=False,
                          cust_length=None, ignore_rate_limit=False):
        """
        authenticates a user

        Args:
            email (str): User's email address.
            password (str): User's password.
            mfa (bool): Enable multi-factor authentication.
            cust_length (int, optional): Custom length for the verification code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            output = self._block_checker(email, user)
            if output:
                return output
            if not user["verified"]:
                return {"success": False, "message": self.messages["not_verified"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if check_password(user, password):
                if mfa:
                    if cust_length:
                        length = int(cust_length)
                    else:
                        length = self.code_length
                    verification_code = generate_secure_code(length)
                    self.users.find_one_and_update(
                        {"email": email},
                        {"$set": {"verification_code": verification_code}}
                    )
                    send_verification_email(self.mail_info, email, verification_code,
                                            self.mail_subject, self.mail_body)
                return {"success": True, "message": self.messages["authentication_success"]}
            return {"success": False, "message": self.messages["invalid_creds"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def verify_mfa_code(self, email, code, ignore_rate_limit=False):
        """
        verifies a user's MFA code

        Args:
            email (str): User's email address.
            code (str): MFA code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            output = self._block_checker(email, user)
            if output:
                return output
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if user["verification_code"] == code:
                self.users.update_one({"email": email}, {"$set": {"verification_code": None}})
                return {"success": True, "message": self.messages["mfa_success"]}
            return {"success": False, "message": self.messages["invalid_mfa_code"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def delete_user(self, email, password, del_from_blocking=True, ignore_rate_limit=False):
        """
        deletes a user account

        Args:
            email (str): User's email address.
            password (str): User's password.
            del_from_blocking (bool, optional): Delete the user from the blocked database.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            blocked_user = self._find_blocked_user(email)
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if not check_password(user, password):
                return {"success": False, "message": self.messages["invalid_pass"]}
            result = self.users.delete_one({"email": email})
            if blocked_user:
                if del_from_blocking:
                    block_result = self.blocked.delete_one({"email": email})
                    if block_result.deleted_count == 0:
                        if result.deleted_count == 0:
                            return {"success": False, "message": self.messages["not_deleted_all"]}
                        return {"success": False, "message": self.messages["not_deleted_blocked"]}
                elif not blocked_user["blocked"]:
                    self.blocked.delete_one({"email": email})
            if result.deleted_count > 0:
                return {"success": True, "message": self.messages["user_deleted"]}
            return {"success": False, "message": self.messages["user_not_deleted"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def delete_user_with_verif(self, email, password, code,
                               del_from_blocking=True,
                               ignore_rate_limit=False):
        """
        deletes a user account

        Args:
            email (str): User's email address.
            password (str): User's password.
            code (str): Verification code.
            del_from_blocking (bool, optional): Delete the user from the blocked database.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self._find_user(email)
            blocked_user = self._find_blocked_user(email)
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if not check_password(user, password):
                return {"success": False, "message": self.messages["invalid_pass"]}
            if user.get("verification_code") != code:
                return {"success": False, "message": self.messages["invalid_reset"]}
            result = self.users.delete_one({"email": email})
            if blocked_user:
                if del_from_blocking:
                    block_result = self.blocked.delete_one({"email": email})
                    if block_result.deleted_count == 0:
                        if result.deleted_count == 0:
                            return {"success": False, "message": self.messages["not_deleted_all"]}
                        return {"success": False, "message": self.messages["not_deleted_blocked"]}
                elif not blocked_user["blocked"]:
                    self.blocked.delete_one({"email": email})
            if result.deleted_count > 0:
                return {"success": True, "message": self.messages["user_deleted"]}
            return {"success": False, "message": self.messages["user_not_deleted"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def generate_code(self, email, cust_length=None, ignore_rate_limit=False):
        """
        Generates a code and sends it to the user's email.

        Args:
            email (str): User's email address.
            cust_length (int, optional): Custom length for the verification code.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        if not self.mail_info:
            raise ValueError("Mail server information is required for reset codes.")
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if cust_length:
                length = int(cust_length)
            else:
                length = self.code_length
            reset_code = generate_secure_code(length)
            self.users.update_one({"email": email}, {"$set": {"verification_code": reset_code}})
            send_verification_email(self.mail_info, email, reset_code,
                                    self.mail_subject, self.mail_body)
            return {"success": True, "message": self.messages["verification_code_sent"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def verify_reset_code_and_reset_password(self, email, reset_code, new_password,
                                             ignore_rate_limit=False):
        """
        verifies a reset code and resets the user's password

        Args:
            email (str): User's email address.
            reset_code (str): Reset code.
            new_password (str): New password.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self.users.find_one({"email": email})
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if user.get("verification_code") != reset_code:
                return {"success": False, "message": self.messages["invalid_reset"]}
            hashed_password = hash_password(new_password)
            self.users.update_one(
                {"email": email}, {"$set": {"password": hashed_password, "verification_code": None}}
            )
            return {"success": True, "message": self.messages["password_reset_success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}

    def verify_reset_code_and_change_email(self, email, reset_code, new_email,
                                           password=None, ignore_rate_limit=False):
        """
        verifies a reset code and changes the user's email

        Args:
            email (str): User's email address.
            reset_code (str): Reset code.
            new_email (str): New email address.
            password (str, optional): User's password for verification if included.
            ignore_rate_limit (bool, optional): Ignore rate limiting for this action.

        Returns:
            dict: Success status and message.
        """
        try:
            user = self.users.find_one({"email": email})
            user_info = self._find_user(email)
            if not user:
                return {"success": False, "message": self.messages["user_not_found"]}
            if self._rate_limit_checker(email, ignore_rate_limit):
                return {"success": False, "message": self.messages["rate_limited"]}
            if self.users.find_one({"email": new_email}):
                return {"success": False, "message": self.messages["user_exists"]}
            if user.get("verification_code") != reset_code:
                return {"success": False, "message": self.messages["invalid_reset"]}
            if password:
                if not check_password(user_info, password):
                    return {"success": False, "message": self.messages["invalid_pass"]}

            self.users.update_one(
                {"email": email}, {"$set": {"email": new_email, "verification_code": None}}
            )
            return {"success": True, "message": self.messages["success"]}
        except Exception as error:
            return {"success": False, "message": str(error)}
