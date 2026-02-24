from dataclasses import dataclass

# FTP URL info
@dataclass
class FtpUrl:
    user: str
    password: str
    host: str
    port: int
    path: str


# Errors when a URL cannot be parsed
class FtpUrlParseError(Exception):
    pass


def parse_ftp_url(url: str) -> FtpUrl:
    """Parse 'ftp://[USER[:PASS]@]HOST[:PORT]/PATH' into an FtpUrl."""

    if not isinstance(url, str):
        raise FtpUrlParseError("URL must be a string")

    if not url.startswith("ftp://"):
        raise FtpUrlParseError("URL must start with 'ftp://'")

    # Remove the prefix
    rest = url[len("ftp://") :]

    # Split authority + path
    slash = rest.find("/")
    if slash == -1:
        authority = rest
        raw_path = ""
    else:
        authority = rest[:slash]
        raw_path = rest[slash + 1 :]

    if not authority:
        raise FtpUrlParseError("Missing host")

    user = "anonymous"
    password = ""
    port = 21

    # Parse optional user info
    if "@" in authority:
        userinfo, hostport = authority.split("@", 1)

        if ":" in userinfo:
            user, password = userinfo.split(":", 1)
        else:
            user = userinfo

        if not user:
            raise FtpUrlParseError("Username cannot be empty")
    else:
        hostport = authority

    # Parse host and optional port
    if ":" in hostport:
        host_part, port_part = hostport.rsplit(":", 1)

        if not host_part:
            raise FtpUrlParseError("Host cannot be empty")

        try:
            port = int(port_part)
        except ValueError:
            raise FtpUrlParseError("Invalid port")

        if not (1 <= port <= 65535):
            raise FtpUrlParseError("Port out of range")

        host = host_part
    else:
        host = hostport

    if not host:
        raise FtpUrlParseError("Host cannot be empty")

    # Normalize path
    raw_path = raw_path.strip()
    if raw_path:
        path = "/" + raw_path.lstrip("/")
    else:
        path = ""

    return FtpUrl(user, password, host, port, path)
