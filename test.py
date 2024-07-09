from werkzeug.security import generate_password_hash, check_password_hash

print(check_password_hash("sha256$3RSIDqpinp5SB5NJ$ae651ff90488e25a7d5cb902ef709650c17dfd792e664496e1377016467b75a7", "lassword123"))