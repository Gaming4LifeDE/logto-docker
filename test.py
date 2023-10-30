import requests
from rich import print

class Bla(requests.Session):
    base_url: str = ""
    
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.headers.update({"AAA": "BBB"})
        
    def get(self, path, **kwargs) -> requests.Response:
        return super().get(f"{self.base_url}/{path}", **kwargs)

s = Bla("https://httpbin.org")

print(s.get("/get", json={"my_key": "my_value"}).json())