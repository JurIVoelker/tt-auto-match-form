import requests
from ai import get_results

url = "https://tt-auto-match-form.voelkerlabs.de/api/results"
image_path = "files/input/image.jpg"

files = {
  "file": ("image.jpg", open(image_path, "rb"), "image/jpeg")
}

response = requests.post(url, files=files)
results = response.json()

image_prefix = "https://tt-auto-match-form.voelkerlabs.de/"

set_results = image_prefix + results.get("set_results")
final_results = image_prefix + results.get("final_results")

results = get_results(set_results, final_results)

print(results)

