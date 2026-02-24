# 4700ftp — FTP Client

## Overview
This project implements a basic FTP client that communicates directly with an FTP server using raw socket connections. It supports essential operations such as listing directories, creating and removing directories, transferring files, and moving files between local and remote paths. The client uses both a control channel for commands and a data channel for file transfers, following the FTP protocol specification.

## Features
- Connect/login via USER and PASS  
- Directory operations: ls, mkdir, rm, rmdir  
- File upload/download via STOR and RETR  
- File movement (mv) and copying (cp)  
- Passive mode (PASV) data channel handling  
- Binary transfer mode (TYPE I), stream mode (MODE S), file structure (STRU F)

## High-Level Approach
I built a command-line parser first, then implemented control-channel setup and login. After validating responses, I added directory operations (MKD, RMD). Next, I implemented PASV for data transfer and added LIST, STOR, RETR, and DELE. Each feature was tested step-by-step using the provided course FTP server.

## Challenges
- Correctly parsing PASV responses into an IP/port  
- Handling multi-line FTP responses  
- Ensuring the client waits for server closure on downloads  
- Avoiding race conditions by always reading the welcome banner first

## Testing
I tested each command against the course FTP server:
- Verified directory creation/deletion  
- Uploaded and downloaded small test files  
- Confirmed correct behavior using a standard FTP client (ftp / FileZilla) as reference  
- Ensured the client runs cleanly on CCIS Linux machines

## How to Run
