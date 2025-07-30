from genstack import Genstack
from dotenv import load_dotenv
import os

load_dotenv()



client = Genstack(api_key=os.getenv("GENSTACK_API_KEY"))


res = client.generate(input="3 fun facts about Ferrari", track="dragon-track", model="gpt-4-1-nano-oai")

if "output" in res:
    print(res["output"][0]["output"]["text"])
else:
    print("Error:", res.get("message", "Unknown error"))
