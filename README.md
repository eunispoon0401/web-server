# COMP2322 Computer Networking
Multi-Threads Server
# Project overview
This is a custom-built, multi-threaded HTTP/1.1 web server implemented in Python. It
supports concurrent client handling, persistent connections, and handles various HTTP
status codes including 200, 304, 400, 403, and 404.
#  Environment
Python Version: 3.9.13<br>
Terminal: PowerShell, Command Prompt<br>
Standard Libraries: socket, os, threading, datetime, email.utils, time
# How to run
1.  Open your terminal in the project root and execute: <code>python MultiThreadsServer.py</code>
    the console should display: Server running on http://127.0.0.1:8080
2.  Open your browser and navigate http://127.0.0.1:8080
3.  Traffic recordes in access.log
#  Function Test
All test code are shown in the test floder<br>
1.  <code>200 ok</code><br>
    Open your browser and navigate http://127.0.0.1:8080<br>
    The website will shown text and image if it is <code>200 ok</code>
2.  <code>304 Not Modified</code><br>
    Find the Last-Modified date from a previous 200 OK response in access.log and run:<br>
    <code> curl.exe -v -H "If-Modified-Since: [Date from Header]" http://127.0.0.1:8080/index.html</code>
3.  <code>400 Bad Request</code><br>
    Since standard tools like browsers always send valid requests, use this PowerShell
    script to send "garbage" text:<br><code>
    $client = New-Object System.Net.Sockets.TcpClient("127.0.0.1", 8080)
    $stream = $client.GetStream()
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.WriteLine("NOT_A_METHOD /index.html") 
    $writer.WriteLine("") # Empty line to finish request
    $writer.Flush()
    $reader = New-Object System.IO.StreamReader($stream)
    $reader.ReadToEnd()
    $client.Close()</code><br>
4.  <code>403 forbidden</code><br>
    Use curl.exe in PowerShell to bypass local path cleaning:<br>
    <code>curl.exe -v --path-as-is 'http://127.0.0.1:8080/../MultiThreadsServer.py'</code>
5.  <code>404 not found</code><br>
    Request a file that you haven't created in www directory:<br>
    <code>curl.exe -v http://127.0.0.1:8080/does_not_exist.html</code>
6.  threading test<br>
    Open a terminal and execute <code>python MultiThreadsServer.py</code><br>
    Open a new terminal and execute <code>python threads_test.py</code><br>
    10 request records will shown in <code>access.log</code>
7.  <code>Get</code> Command<br>
    Open the broswer and navigate http://127.0.0.1:8080/index.html and http://127.0.0.1:8080/test_image.jpg<br>
    The text and the image should display correctly in the browser window without corruption.
8.










    
    

    
    
    
