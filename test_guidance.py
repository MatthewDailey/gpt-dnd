import guidance
import re

guidance.llm = guidance.llms.OpenAI("gpt-3.5-turbo")


# a custom function we will call in the guidance program
def parse_best(prosandcons, options):
    best = int(re.findall(r"Best=(\d+)", prosandcons)[0])
    return options[best]


create_plan = guidance("""
{{#system~}}
You are an expert dungeon master for Dungeons and Dragons.
{{~/system}}

{{! generate five potential ways to accomplish a goal }}
{{#block hidden=False}}
  {{#user~}}
    I want to {{goal}}.

    Can you please generate one option for how to accomplish this?
    Please make the option very short, at most one line.
  {{~/user}}

  {{#assistant~}}
    {{gen 'options' n=5 temperature=1.0 max_tokens=500}}
  {{~/assistant}}
{{/block}}

{{! generate pros and cons for each option and select the best option }}
{{#block hidden=True}}
  {{#user~}}
    I want to {{goal}}.

    Can you please comment on the pros and cons of each of the following options, and then pick the best option?
    ---{{#each options}}
    Option {{@index}}: {{this}}{{/each}}
    ---
    Please discuss each option very briefly (one line for pros, one for cons), and end by saying Best=X, where X is the best option.
  {{~/user}}

  {{#assistant~}}
    {{gen 'prosandcons' temperature=0.0 max_tokens=500}}
  {{~/assistant}}
{{/block}}

{{#user~}}
  I want to {{goal}}.
  {{~! Create a plan }}
  Here is my plan:
  {{parse_best prosandcons options}}
  Please elaborate on this plan, and tell me how to best accomplish it.
{{~/user}}

{{#assistant~}}
  {{gen 'plan' max_tokens=500}}
{{~/assistant}}''')
""")

out = create_plan(goal="kill the dragon", parse_best=parse_best)
print(out["plan"])
