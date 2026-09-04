from crewai import Task

NOT_FOUND = "not found in sources"


def build_tasks(question, researcher, analyst, writer):
    research = Task(
        description=(
            f"The user asked: {question}\n\n"
            "Work out which specific figures are needed to answer this, then search for "
            "them. Search once per figure with a narrow query naming the vehicle, the "
            "variant if the question implies one, and the figure itself. If a query "
            "returns only review articles, search again with different wording before "
            "giving up on that figure.\n\n"
            "Record every figure you find as its own line: what the figure is, the "
            "vehicle and variant it belongs to, the value with its unit, and the URL you "
            "read it on. Where a source says whether a number is a manufacturer claim or "
            "a tested result, or whether a price is ex-showroom or on-road, keep that "
            "wording.\n\n"
            "If two sources give different values for the same figure, record both lines "
            "rather than choosing between them. That decision is not yours.\n\n"
            f"If you cannot find a figure after several searches, write it as a line "
            f"ending in '{NOT_FOUND}'. Do not supply a value from your own knowledge for "
            "any figure, under any circumstances. An honest gap is the correct output "
            "here and an invented number is the one failure that matters."
        ),
        expected_output=(
            "A flat list of evidence lines, one figure per line, each ending in either "
            f"the source URL it came from or the words '{NOT_FOUND}'. No prose "
            "introduction, no summary, no recommendation."
        ),
        agent=researcher,
    )

    analysis = Task(
        description=(
            f"The user asked: {question}\n\n"
            "Using only the researcher's evidence lines, produce one settled figure per "
            "thing the question asks about.\n\n"
            "Where two sources disagree, pick the value from the source closest to the "
            "manufacturer and most likely to be current. Where the difference is large "
            "enough that a reader relying on one value would be misled, keep the settled "
            "figure but mark it so the writer can note the spread.\n\n"
            "Check that figures being compared are actually comparable. If two vehicles' "
            "numbers come from different variants, different model years, or different "
            "measurement bases such as claimed against tested or ex-showroom against "
            "on-road, say so against that figure. A comparison of numbers that do not "
            "match on basis is worse than no comparison.\n\n"
            f"List separately every part of the question the evidence does not answer, "
            f"marked '{NOT_FOUND}'. Never close a gap with your own knowledge, and never "
            "estimate, average or interpolate a value that no source stated.\n\n"
            "Keep each line short. Do not explain which source you preferred or why you "
            "trusted it. That working is yours and it stops here."
        ),
        expected_output=(
            "One line per figure: what it is, the vehicle and variant, the settled "
            "value, and its source URL. A short caveat in square brackets only where the "
            "figure would otherwise be read wrongly, such as '[sources disagree: 17.4 / "
            "17.6]' or '[claimed, not tested]'. Then the unanswered parts of the "
            f"question, each marked '{NOT_FOUND}'. No methodology, no reasoning."
        ),
        agent=analyst,
        context=[research],
    )

    answer = Task(
        description=(
            f"The user asked: {question}\n\n"
            "Write the final answer from the analyst's figures. Lead with a direct "
            "answer to the question in one or two sentences, then list the figures, each "
            "with its source URL beside it.\n\n"
            "Every figure must already appear in the analyst's output. You have no "
            "search tool and no licence to add, round or complete anything. If the "
            f"analyst marked something '{NOT_FOUND}', carry that line into the answer "
            "unchanged rather than leaving it out.\n\n"
            "Carry over the analyst's square-bracket caveats and nothing else of theirs. "
            "Drop any reasoning about sources, reliability or method. Do not add a "
            "conclusion, a recommendation the question did not ask for, or a note about "
            "how the answer was produced.\n\n"
            "Plain text. No markdown headings, no tables, no emoji."
        ),
        expected_output=(
            "A direct answer in one or two sentences, then one figure per line with its "
            "source URL, then any lines marked "
            f"'{NOT_FOUND}'. Plain text, no reasoning, no closing commentary."
        ),
        agent=writer,
        context=[analysis],
    )

    return [research, analysis, answer]
