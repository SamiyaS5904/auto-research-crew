# Auto Research Crew

A three-agent research crew that answers vehicle questions from live web search - every
figure sourced, nothing invented.

Three CrewAI agents split the work: one searches, one reconciles what came back, one
writes the answer. Every figure in the output carries the URL it came from, and anything
the search could not find is reported as `not found in sources` rather than filled in
from the model's memory.

## Why it is built this way

The problem with asking a language model about vehicle specifications is that it will
answer confidently from a fuzzy memory of the internet, and a wrong mileage or price
looks exactly like a right one. Telling the model "do not make things up" helps a
little. Structuring the system so it cannot helps more.

So the constraint is built into the pipeline rather than into a prompt:

- **Only the research agent has a search tool.** The other two agents have no way to
  reach the internet, so the only facts in the system are ones that entered through a
  search result.
- **The process is sequential.** Each task receives only the previous task's output. The
  writer never sees raw search results, only the figures the analyst passed forward.
- **The writer is a formatter.** Its instructions forbid introducing any figure that is
  not already in the analyst's output, and it has no tool with which to find one.

Facts can only enter at step one. That is the actual defence.

## The three agents

| Agent | Owns | Has search |
|---|---|---|
| Automotive Sourcing Researcher | Finding figures and recording the URL for each | yes |
| Vehicle Specification Analyst | Reconciling disagreements between sources, naming gaps | no |
| Answer Writer | Presentation only | no |

The analyst is the agent that does the least obvious work, so it is worth saying what it
is for. Vehicle figures are easy to compare wrongly: a top variant against a base
variant, this year's model against last year's, an ex-showroom price against an on-road
one, or two mileage figures measured on different test cycles. The analyst's job is to
catch those, settle on one figure per thing asked about, and say plainly which parts of
the question the evidence does not answer.

Its reasoning does not reach the final answer. That is deliberate: the output is meant to
be the figures and their sources, not an essay about how they were chosen.

## Output

The answer is a direct response, then one figure per line with its source, then anything
that could not be found. Roughly this shape:

```
The Nexon and the Brezza are closely matched on claimed mileage.

Tata Nexon, 1.2 petrol manual: 17.4 kmpl  (https://source/nexon)
Maruti Brezza, 1.5 petrol manual: 17.4 kmpl  (https://source/brezza)
Boot space, Brezza: not found in sources
```

A note in square brackets appears only where it changes how a number should be read, for
example `[sources disagree: 17.4 / 17.6]` or `[claimed, not tested]`.

## Setup

Requires Python 3.10 to 3.13 (CrewAI does not support 3.14 yet), an OpenAI API key,
and a Serper API key. Serper has a free
tier that is sufficient for this.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in both keys:

```
OPENAI_API_KEY=
SERPER_API_KEY=
```

- OpenAI keys: https://platform.openai.com/api-keys
- Serper keys: https://serper.dev

`.env` is gitignored and should stay that way.

## Running it

As a Streamlit page:

```
streamlit run app.py
```

The page shows the answer, with the researcher's raw evidence and the analyst's
reconciled figures available in expanders underneath, so the pipeline is visible rather
than hidden.

From the terminal:

```
python main.py "Compare the Tata Nexon and Maruti Brezza on price and mileage"
python main.py "What is the service interval on a Renault Duster diesel?"
```

With no argument it prompts for the question. Agent activity is printed while the crew
runs in both cases, because `verbose=True` is on.

## Deploying

The app runs on Streamlit Community Cloud without code changes. Streamlit exposes
root-level secrets as environment variables, which is what `crew.py` reads, so the same
`os.getenv` calls work locally and deployed.

1. Push the repository to GitHub.
2. Create an app at https://share.streamlit.io pointing at the repo, with `app.py` as
   the entry point.
3. In Advanced settings, set the Python version to 3.12 and paste the keys as TOML:

```
OPENAI_API_KEY = "sk-..."
SERPER_API_KEY = "..."
```

Keep both at the root level. Secrets nested under a `[section]` heading are readable
through `st.secrets` but are not set as environment variables, so they would not reach
`crew.py`.

Two things to know before relying on a deployed instance:

- **Resource limits.** Community Cloud apps are capped at roughly 2.7 GB of RAM and 2
  CPU cores. CrewAI pulls a large dependency tree, so the build may fail on memory. If it
  does, Hugging Face Spaces offers considerably more headroom on its free tier and runs
  Streamlit apps too.
- **Cost.** A public app runs on your API keys, and anyone with the link can use them.
  Set a hard monthly spend limit in your OpenAI billing before making the URL public. The
  Serper free tier is capped on its own, so it self-limits.

A deployed app also sleeps after a period of inactivity and takes a while to wake, and a
single question takes some time to answer because three agents run in sequence with
several searches between them. Worth opening the app a few minutes before you intend to
show it.

## Files

```
app.py             Streamlit entry point
main.py            terminal entry point
crew.py            builds and runs the crew
agents.py          the three agent definitions
tasks.py           the three task definitions
```

About 250 lines of Python in total, most of it the agent and task prompts. That
proportion is intentional: the prompts are where the behaviour actually comes from, and
the surrounding code is thin on purpose.

There is no YAML configuration for the agents. CrewAI supports defining them in
`agents.yaml` and `tasks.yaml`, and that is worth doing when there are many agents or
when someone who does not write Python needs to edit the prompts. With three agents it
adds a second place to look for no benefit, so the definitions live in plain Python next
to the code that uses them.

## Known limitation

The safeguards described above reduce fabrication. They do not eliminate it.

Nothing in this project programmatically checks that a number in the final answer
actually appears in the text that was retrieved. The writer is instructed not to invent
figures and has no tool with which to look one up, which makes inventing one unlikely,
but the guarantee is behavioural rather than enforced. A stronger version would extract
every figure from the final answer and assert it appears in the researcher's evidence,
failing the run if it does not.

That check is not implemented here. It is the clearest thing this project is missing, and
it is worth knowing that rather than assuming the sourcing is airtight.

## CrewAI concepts used

- **Agent** — a language model given a persistent `role`, `goal` and `backstory`, and
  optionally tools. The backstory is not decoration; it is where most of the behaviour is
  specified.
- **Task** — a unit of work with a `description` and an `expected_output`, assigned to one
  agent. `expected_output` is where output discipline is enforced, and it does more work
  here than the description does.
- **Tool** — something an agent can call. `SerperDevTool` is the only one used, and giving
  it to exactly one agent is the central design decision.
- **Process** — how tasks are ordered. `Process.sequential` runs them in order and passes
  each output forward as context. The alternative, `hierarchical`, adds a manager agent
  that delegates; that would make the chain of custody for a fact harder to follow, which
  is the opposite of what this project wants.
