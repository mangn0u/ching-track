"""Accounts serializers — register, login, profile, password."""

# TODO Day 2: Implement the following serializers
#
# RegisterSerializer
#   Fields: email, password, password_confirm, first_name, last_name
#   Validate: passwords match, email not already in use
#   On save: create user, send verification email
#
# LoginSerializer
#   Fields: email, password
#   Validate: credentials are correct, email is verified
#   Return: {access, refresh, user}
#
# UserProfileSerializer
#   Fields: id, email, first_name, last_name, phone_number, date_joined
#   Read-only: id, email, date_joined
#
# ChangePasswordSerializer
#   Fields: old_password, new_password, new_password_confirm
#   Validate: old password correct, new passwords match
