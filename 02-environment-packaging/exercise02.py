# 02-environment-packaging/exercise02.py
import httpx

response = httpx.get("https://api.github.com/users/octocat")
data = response.json()

print(response.status_code)
print(data["login"], data["public_repos"])
