import threading
import urllib.request
#test threading
def make_request():
    try:
        response = urllib.request.urlopen("http://127.0.0.1:8080/index.html")
        print(f"Status: {response.getcode()}")
    except Exception as e:
        print(f"Error: {e}")


for i in range(10):
    threading.Thread(target=make_request).start()