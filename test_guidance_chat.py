import guidance
import sys

guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")

prompt = guidance("""
{{#system~}}
You are a helpful assistant
{{~/system}}

{{~#geneach 'conversation' stop=False}}
  {{#user~}}
    {{set 'this.input' (await 'input')}}
  {{~/user}}

  {{#assistant~}}
    {{gen 'response' temperature=0 max_tokens=300}}
  {{~/assistant}}
{{~/geneach}}
""")

while True:
    user_input = sys.stdin.readline()
    response = prompt(input=user_input)["response"]
    print(response)
