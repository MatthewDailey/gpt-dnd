import openai
import os

openai.organization = "org-3676qVMg5QssbgHBYPtoL1DT"
openai.api_key = os.environ["PERSONAL_OPENAI_API_KEY"]

response = openai.Image.create(
    prompt=(
        "You find yourselves standing outside the gates of the Blackwood Manor, a"
        " once-grand estate that has fallen into disrepair. The noble who has purchased"
        " the estate, Lord William, has put out a call for brave adventurers to aid in"
        " the restoration process and rid the manor of its curse once and for all. As"
        " you approach the gates, you see a small group of people gathered outside."
        " They appear to be townsfolk, and they are whispering amongst themselves. One"
        " of them approaches you and says, 'Are you the adventurers Lord William sent"
        " for? Be careful, the manor is cursed. Many have gone in, but none have"
        " returned.'"
    ),
    n=1,
    size="1024x1024",
)
image_url = response["data"][0]["url"]
print(image_url)
