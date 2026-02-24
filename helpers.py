# If CLI arguments are wrong
class InvalidArgumentsError(Exception):
    pass

# If FTP response/format errors or unexpected codes occur
class FtpProtocolError(Exception):
    pass

# Check if a string is an FTP URL
def is_ftp_url(value: str) -> bool:
    return value.startswith("ftp://")
