from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyAk3ZBxkdlVdhtgDvYjGN3qmkW6pGukb1g")
while True:
    print("hello!")
    answer = input("What do you want to ask?\n") 
    if answer.lower() == "exit":
        break
    response = client.models.generate_content(
        model="gemini-3-flash-preview", contents=answer
    )
    reply = response.textwha
    print(f"gemini says: {reply}")