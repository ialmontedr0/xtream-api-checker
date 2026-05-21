from app.utils.m3u_parser import M3UParser

parser = M3UParser()

url = "http://example.com:8080/get.php?username=test&password=1234&type=m3u"

data = parser.parse(url)

print(data)