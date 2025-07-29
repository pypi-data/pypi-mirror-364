import aiwand
from openai import Client
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

def main():
    doc_links = [
        "https://ceodelhi.gov.in/OnlineERMS/PERMORMANCE/P8.pdf"
    ]

    messages = [
  {
    "role": "system",
    "content": "You are AIWand, a helpful AI assistant that provides clear, accurate, and concise responses.You excel at text processing, analysis, and generation tasks."
  },
  {
    "role": "user",
    "content": "total candidates number in list"
  },
  {
    "role": "user",
    "content": [
      {
        "type": "input_file",
        "file_url": "https://ceodelhi.gov.in/OnlineERMS/PERMORMANCE/P8.pdf"
      }
    ]
  }
]
    client = Client()
    response = client.responses.create(
        model="gpt-4o",
        input=messages,
    )
    print(response.output_text)

    class Consistuency(BaseModel):
        name: str
        party: str
    class FullResponse(BaseModel):
        total_candidates: int
        consistuencies: list[Consistuency]

    response = client.responses.parse(
        model="gpt-4o",
        input=response.output_text,
        text_format=FullResponse
    )
    print(response.output_parsed)

    repsonse = aiwand.call_ai(
        user_prompt="total candidates number in list",
        document_links=doc_links,
        model="gpt-4o"
    )
    print(repsonse)

    response = aiwand.extract(
        document_links=doc_links,
        # model="gpt-4o",
        response_format=FullResponse
    )
    print(response)


if __name__ == "main":
    main()