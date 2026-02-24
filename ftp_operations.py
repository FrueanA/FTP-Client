from ftp_url import parse_ftp_url
from ftp_client import FtpSession
from helpers import is_ftp_url, InvalidArgumentsError
import os


# helper for session setup
def _open_session(url_str: str, verbose: bool) -> FtpSession:
    url = parse_ftp_url(url_str)
    s = FtpSession(url, verbose=verbose)
    s.connect()
    s.login()
    s.set_binary_mode()
    return s


def cmd_ls(url_str: str, verbose: bool = False) -> None:
    s = None
    try:
        s = _open_session(url_str, verbose)
        url = parse_ftp_url(url_str)
        out = s.list_directory(url.path)
        print(out, end="")
    finally:
        if s is not None:
            try:
                s.quit()
            except Exception:
                pass


def cmd_mkdir(url_str: str, verbose: bool = False) -> None:
    s = None
    try:
        s = _open_session(url_str, verbose)
        url = parse_ftp_url(url_str)
        s.make_directory(url.path)
    finally:
        if s is not None:
            try:
                s.quit()
            except Exception:
                pass


def cmd_rm(url_str: str, verbose: bool = False) -> None:
    s = None
    try:
        s = _open_session(url_str, verbose)
        url = parse_ftp_url(url_str)
        s.delete_file(url.path)
    finally:
        if s is not None:
            try:
                s.quit()
            except Exception:
                pass


def cmd_rmdir(url_str: str, verbose: bool = False) -> None:
    s = None
    try:
        s = _open_session(url_str, verbose)
        url = parse_ftp_url(url_str)
        s.remove_directory(url.path)
    finally:
        if s is not None:
            try:
                s.quit()
            except Exception:
                pass


def cmd_cp(arg1: str, arg2: str, verbose: bool = False) -> None:
    a1_remote = is_ftp_url(arg1)
    a2_remote = is_ftp_url(arg2)

    if a1_remote == a2_remote:
        raise InvalidArgumentsError("cp requires exactly one FTP URL and one local path")

    if a1_remote:
        # remote -> local (download)
        url = parse_ftp_url(arg1)
        s = None
        try:
            s = _open_session(arg1, verbose)
            s.retrieve_file(url.path, arg2)
        finally:
            if s is not None:
                try:
                    s.quit()
                except Exception:
                    pass
    else:
        # local -> remote (upload)
        if not os.path.isfile(arg1):
            raise InvalidArgumentsError(f"Local file not found: {arg1}")

        url = parse_ftp_url(arg2)
        s = None
        try:
            s = _open_session(arg2, verbose)
            s.store_file(arg1, url.path)
        finally:
            if s is not None:
                try:
                    s.quit()
                except Exception:
                    pass


def cmd_mv(arg1: str, arg2: str, verbose: bool = False) -> None:
    # copy and delete source during mv
    a1_remote = is_ftp_url(arg1)
    a2_remote = is_ftp_url(arg2)

    if a1_remote == a2_remote:
        raise InvalidArgumentsError("mv requires exactly one FTP URL and one local path")

    if a1_remote:
        # remote -> local
        url = parse_ftp_url(arg1)
        s = None
        try:
            s = _open_session(arg1, verbose)
            s.retrieve_file(url.path, arg2)
            s.delete_file(url.path)
        finally:
            if s is not None:
                try:
                    s.quit()
                except Exception:
                    pass
    else:
        # local -> remote
        if not os.path.isfile(arg1):
            raise InvalidArgumentsError(f"Local file not found: {arg1}")

        url = parse_ftp_url(arg2)
        s = None
        try:
            s = _open_session(arg2, verbose)
            s.store_file(arg1, url.path)
        finally:
            if s is not None:
                try:
                    s.quit()
                except Exception:
                    pass

        # delete local file if mv succeeds
        os.remove(arg1)
