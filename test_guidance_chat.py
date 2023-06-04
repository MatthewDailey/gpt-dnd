import guidance
import sys

guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")


prompt = guidance("""
{{#system~}}
  {{sys}}
{{~/system}}

{{~#each message_and_response}}
  {{#user~}}
    {{this.message}}
  {{~/user}}
  {{#assistant~}}
    {{this.response}}
  {{~/assistant}}
{{~/each}}

{{~#geneach 'conversation' stop=False}}
  {{#user~}}
    {{set 'this.input' (await 'input')}}
  {{~/user}}

  {{#assistant~}}
    {{gen 'response'}}
  {{~/assistant}}
{{~/geneach}}
""")

message_and_response = []

while True:
    user_input = sys.stdin.readline()
    p = prompt(
        sys="You are a helpful assistant",
        message_and_response=message_and_response,
        input=user_input,
    )
    print(p)
    print(p["response"])
    message_and_response.append(
        {
            "message": user_input,
            "response": p["response"],
        }
    )
