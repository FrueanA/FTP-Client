# 4700ftp

Implements an FTP client that supports listing directories, creating + deleting files and directories, and copying/moving files between the local machine and a remote FTP server.

# Files

- 4700ftp.py: main file that parses command line arguments and performs requested operation
- ftp_client.py: FTP session implementation
- ftp_url.py: Parses the FTP URL ftp://[user[:pass]@]host[:port]/path
- ftp_operations.py: Contains operations
- helpers.py: Exceptions + Errors

# High-level approach

Client opens TCP connection to the Khoury FTP server, reads the greeting, logs in with username + password, and sets binary data mode. Uses PASV to open another data connection if an operation needs to transfer data, then closes the socket after the transfer, then reads final status for success or failure.

# Challenges

My main challenge was handling the commands that use two sockets, because I was having an odd error where sockets weren't closing properly on success and error.

# Testing

I tested using the course FTP server ftp.4700.network using my assigned username and password. I tested:

- ls on the root directory and after creating directories.
- mkdir to create new directories and rmdir to remove empty ones.
- cp local to remote (upload) and remote to local (download) + checks contents
- rm to delete files.
- mv local to remote and remote to local
- Invalid arguments and executions to test exceptions
