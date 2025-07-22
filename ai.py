from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, ImageContentItem, TextContentItem, ImageUrl
from azure.core.credentials import AzureKeyCredential
import json
import os
import concurrent.futures


token = os.getenv("GITHUB_TOKEN")
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

def extract_set_results(image_url):
    prompt = "The image contains a table with 5 columns. Extract the set results from the image. The numbers are in the format 'X:Y' where X is the first number and Y is the second number. The number are between 0 and 31, where one of the numbers is often 11."

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    response = client.complete(
        messages=[
            SystemMessage("You are a programme that extracts the set results (numbers, divided by :) in a 5 column format from an image. Return the text in JSON format with nested arrays for each row and its columns."),
            UserMessage([
            TextContentItem(text=prompt), 
            ImageContentItem(image_url=ImageUrl(url=image_url))
            ]),
        ],
        temperature=0.25,
        top_p=1,
        model=model
    )
    result = response.choices[0].message.content
    if result.startswith("```json"):
        result = result[8:-3].strip()
    try:
        json_result = json.loads(result)
        return json_result
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON"}

def extract_final_results(image_url):
    prompt = "The image contains a table with 2 columns. Extract the final results from the image. The numbers are in the format 'X:Y' where X is the first number and Y is the second number. The numbers in the first column are between 0 and 3, the numbers in the second column are between 0 and 1."

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )

    response = client.complete(
        messages=[
            SystemMessage("You are a programme that extracts the final results (numbers, divided by :) in a 2 column format from an image. Return the text in JSON format with nested arrays for each row and its columns."),
            UserMessage([
                TextContentItem(text=prompt),
                ImageContentItem(image_url=ImageUrl(url=image_url))
            ]),
        ],
        temperature=0.25,
        top_p=1,
        model=model
    )
    result = response.choices[0].message.content
    if result.startswith("```json"):
        result = result[8:-3].strip()
    try:
        json_result = json.loads(result)
        return json_result
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON"}

def validate_results(set_results, final_results):
        calculated_final_results = []
        
        invalid_rows = []

        for result_index, result_array in enumerate(set_results):
            home_score = 0
            away_score = 0
            for i, result in enumerate(result_array):
                if result == ":":
                    continue
                split_result = result.split(":")
                if len(split_result) == 2:
                    h = int(split_result[0])
                    a = int(split_result[1])
                    if h > a:
                        home_score += 1
                    elif a > h:
                        away_score += 1
            calculated_final_results.append([f"{home_score}:{away_score}", "1:0" if home_score > away_score else "0:1"])

        print(calculated_final_results, final_results)
        for index, (calculated, actual) in enumerate(zip(calculated_final_results, final_results)):
            if calculated != actual:
                invalid_rows.append(index)
                print(f"Invalid row {index} detected: calculated {calculated} != actual {actual}")
        
        for result_index, result_array in enumerate(set_results):
            for result in result_array:
                if result == ":":
                    continue
                split_result = result.split(":")
                if len(split_result) == 2:
                    h = int(split_result[0])
                    a = int(split_result[1])
                    if h > a and h > 11 and h - a != 2:
                        print(f"Invalid row {result_index} with result {result} detected: {h} > {a} and {h} > 11 and {h} - {a} != 2")
                        invalid_rows.append(result_index)
                    if a > h and a > 11 and a - h != 2:
                        print(f"Invalid row {result_index} with result {result} detected: {a} > {h} and {a} > 11 and {a} - {h} != 2")
                        invalid_rows.append(result_index)
                    if h == a:
                        print(f"Invalid row {result_index} with result {result} detected: {h} == {a}")
                        invalid_rows.append(result_index)
        print(invalid_rows)
        invalid_rows = list(set(invalid_rows))
        return invalid_rows

def get_results(set_results_url, final_results_url):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        set_results_future = executor.submit(extract_set_results, set_results_url)
        final_results_future = executor.submit(extract_final_results, final_results_url)

        set_results = set_results_future.result()
        final_results = final_results_future.result()

    if "error" in set_results or "error" in final_results:
        return {"error": "Failed to extract results from the images"}

    invalid_rows = validate_results(set_results, final_results)

    return {
        "set_results": set_results,
        "final_results": final_results,
        "invalid_rows": invalid_rows
    }

if __name__ == "__main__":
    results = get_results("https://s3.voelkerlabs.de/data/set_results.jpg", "https://s3.voelkerlabs.de/data/final_results.jpg")
    print(json.dumps(results, indent=2))