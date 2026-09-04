# Auto Research Crew

A three-agent research crew that answers vehicle questions from live web search - every
figure sourced, nothing invented.

Ask it about a car and it searches the web, reconciles what it finds, and answers with
the URL beside every number. Anything it cannot find, it says so instead of guessing.

## Why

Ask a language model for a car's mileage and it will answer from a fuzzy memory of the
internet. A wrong figure looks exactly like a right one. Telling the model not to make
things up helps a little; building it so it cannot helps more.

Only the research agent has a search tool. The other two cannot reach the internet, so
the only facts in the system are ones that came through a search result. The process is
sequential, so the writer sees the analyst's figures rather than raw search output, and
its instructions forbid adding anything the analyst did not pass forward.

Facts can only enter at step one. That is the design.

## The three agents

| Agent | Job | Search tool |
|---|---|---|
| Researcher | Finds figures, records the URL for each | yes |
| Analyst | Reconciles conflicting sources, names the gaps | no |
| Writer | Presentation only | no |

The analyst matters more than it looks. Vehicle figures are easy to compare wrongly: a
top variant against a base one, this year's model against last year's, ex-showroom
against on-road, mileage from two different test cycles. It catches those, settles on one
figure each, and says which parts of the question the evidence does not answer. Its
reasoning does not reach the final answer, deliberately.

## Output

Real output, trimmed:

```
The kerb weight of the 2017 Tata Nexon XM diesel variant is 1305 kg.
The alternator output rating was not found in sources.

Kerb weight, 2017 Tata Nexon XM diesel: 1305 kg (https://www.cardekho.com/tata/nexon-2017-2020/specs)
not found in sources
```

A square-bracket note appears only where it changes how a number should be read, such as
`[claimed, not tested]` or `[sources disagree: 17.4 / 17.6]`.

## Setup

Python 3.10 to 3.13, an OpenAI key, and a Serper key (free tier is enough).

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in `OPENAI_API_KEY` and `SERPER_API_KEY`. `.env`
is gitignored.

## Running

```
streamlit run app.py
python main.py "Compare the Tata Nexon and Maruti Brezza on price and mileage"
```

`main.py` prompts for the question if you do not pass one. The Streamlit page shows the
answer, with the researcher's evidence and the analyst's figures in expanders below it.

## Deploying

Runs on Streamlit Community Cloud unchanged. Point it at this repo with `app.py` as the
entry point, and paste the keys into Advanced settings as TOML:

```
OPENAI_API_KEY = "sk-..."
SERPER_API_KEY = "..."
```

Keep them at the root level. Streamlit exposes root-level secrets as environment
variables, which is what `crew.py` reads; secrets nested under a `[section]` are not.

Two warnings. Community Cloud caps apps near 2.7 GB of RAM and CrewAI's dependency tree
is large, so the build may fail on memory - Hugging Face Spaces has more headroom. And a
public app spends your API credits, so set a monthly limit on the OpenAI account before
sharing the URL.

## Known limitations

Nothing checks programmatically that a figure in the final answer appears in the text
that was retrieved. The writer is told not to invent figures and has no tool to look one
up, which makes it unlikely, but the guarantee is behavioural rather than enforced. The
stronger version would extract every figure and assert it appears in the researcher's
evidence, failing the run otherwise.

There is also no ranking of source quality. A figure from a parts marketplace and one
from a manufacturer spec sheet are both just sources. The researcher is instructed to
reject listing and forum pages, which caught a real case of a marketplace part being
quoted as a factory spec, but that is a prompt rule rather than a check.

Both are worth knowing before trusting a number it gives you.

## Files

```
app.py       Streamlit entry point
main.py      terminal entry point
crew.py      builds and runs the crew
agents.py    the three agents
tasks.py     the three tasks
```

Around 280 lines, most of it agent and task prompts. That is where the behaviour comes
from, so that is where the effort went. No YAML config - with three agents it would only
add a second place to look.
