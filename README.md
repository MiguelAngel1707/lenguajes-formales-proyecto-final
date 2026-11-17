# Formal Languages Project: FIRST/FOLLOW, LL(1), SLR(1) and SDD evaluation

Implementation of the project *SI2002 / ST0270 / CM0081: Formal Languages*. It follows the algorithms of
Aho, Lam, Sethi and Ullman, *Compilers: Principles, Techniques, and Tools* (2nd ed., 2006/2007).

## Group members

- Simon Alejandro Vasquez Medina
- Miguelangel Calderon Figueredo
- Sebastian Urrego Ramirez

## Environment

| Component | Version |
|---|---|
| Operating system | Windows 11 Home 10.0.26200 |
| Programming language | Python 3.14.6 (only the standard library is used) |
| Report | LaTeX, compiled with MiKTeX 25.12 (pdfTeX 4.23) |

No parser generators or parsing libraries are used. FIRST/FOLLOW, the LL(1) table, the LR(0) automaton, the SLR(1) table, both parsers and the SDD evaluator are all implemented in this repository.

## Files

| File | Contents | Book reference |
|---|---|---|
| `grammar.py` | Reading of the grammar (input format of Section 2.2), class `Grammar`, class `Node` (parse-tree node) | |
| `first_follow.py` | Item 1: FIRST and FOLLOW sets | Section 4.4.2 |
| `ll1.py` | Item 2: LL(1) condition, predictive parsing table and table-driven predictive parser | Section 4.4.3 (condition), Algorithm 4.31, Algorithm 4.34 / Fig. 4.20 |
| `slr1.py` | Item 2: augmented grammar, CLOSURE, GOTO, canonical LR(0) collection, SLR table and LR parser | Section 4.6.2, Figs. 4.32 and 4.33, Algorithm 4.46, Algorithm 4.44 / Fig. 4.36 |
| `main.py` | Program for Items 1 and 2 (input/output of Section 2.2) | |
| `sdd_rules.py` | Item 3: the grammar and the SDD, stored as **data** | Section 5.1 (Fig. 5.1 format) |
| `sdd.py` | Item 3: generic SDD evaluator (parse tree, dependency graph, topological order, evaluation) | Sections 5.2.1 and 5.2.2 |
| `tests/` | Input files used for testing | |
| `tree.py` | Optional: draws the parse tree of a string with Graphviz (`tree.dot` and `tree.png` are an example of its output) | |
| `report.pdf` | The report (Item 4) | |

## How to build and run

Python needs no build step. Run every command from the root directory of the project.

### Items 1 and 2

```
python main.py < tests/example1.txt
python main.py --sets < tests/example1.txt
```

The program reads the grammar from standard input in the format of Section 2.2. First comes a line with `n`, then `n` lines such as `B -> bBc e`. It then behaves as specified:
- If the grammar is both LL(1) and SLR(1), it asks `Select a parser (T: for LL(1), B: for SLR(1), Q: quit):`.
- Otherwise it prints `Grammar is LL(1).`, `Grammar is SLR(1).` or `Grammar is neither LL(1) nor SLR(1).`

Strings are read one per line until an empty line, and the program prints `yes` or `no` for each one. A line with only `e` is the empty string. With `--sets`, the FIRST and FOLLOW sets are printed first.

You can also type the input interactively: run `python main.py` and type the grammar and the strings.

To see the tables computed by the program and a step-by-step parse, run the test blocks of the parser modules. They read a grammar and, on the next line, one string:

```
python ll1.py < tests/report_grammar.txt     # LL(1) table M and moves of the parser (as in Fig. 4.21)
python slr1.py < tests/report_grammar.txt    # LR(0) item sets, GOTO, SLR table (Fig. 4.37) and moves (Fig. 4.38)
```

### Item 3 (SDD)

The grammar and the SDD are in `sdd_rules.py`. The program reads strings, one per line, until an empty line:

```
python sdd.py < tests/sdd_strings.txt
```

For each string, the program prints one of two things:
- `no`, if the string is not in the language;
- otherwise, the annotated parse tree, the evaluation order (a topological order of the dependency graph) and the value of `S.val`.

The language is numbers with a base prefix: `b` binary, `o` octal, `d` decimal. For example, `b101` gives `S.val = 5`, `o17` gives `S.val = 15`, and `b102` gives `S.val = error`.

**Step-by-step visualizer:**

```
python sdd.py --step
```

Type a string (for example `b101`) and press Enter. The program first prints the edges of the dependency graph. Then, each time you press Enter, it evaluates one attribute and shows the tree with the values computed so far.

**Circular SDD test (Step 6):** temporarily replace the rule on line 89 of `sdd_rules.py`,

```python
((2, "acc"), [(1, "val"), (0, "base")], first_digit),   # R.acc = first_digit(D.val, N.base)
```

with the commented rule just below it,

```python
((2, "acc"), [(2, "val")], copy),                        # R.acc = R.val
```

Then run `python sdd.py < tests/sdd_strings.txt`. The program prints `Error: the SDD is circular (the dependency graph has a cycle).` and stops. Restore the original rule afterwards.

**Drawing the parse tree (optional):** `tree.py` parses one string with the LL(1) parser and writes its parse tree to `tree.dot`. The grammar must be LL(1). [Graphviz](https://graphviz.org/) turns it into an image:

```
python tree.py b101 < tests/sdd_grammar.txt
dot -Tpng tree.dot -o tree.png
```

### Report

The report is `report.pdf`, in the root directory. It was written in LaTeX and compiled with MiKTeX (pdfTeX).

## Tests

| Input file | Expected output |
|---|---|
| `tests/example1.txt` | Example 1 of the assignment: `Grammar is SLR(1).`, `yes`, `yes`, `no` |
| `tests/example2.txt` | Example 2: the parser menu, `yes`, `yes`, `no`, the menu again |
| `tests/example3.txt` | Example 3: `Grammar is neither LL(1) nor SLR(1).` |
| `tests/example2_both_parsers.txt` | Example 2 grammar with both parsers: `yes yes no yes no` (SLR), `no no` (LL) |
| `tests/ll1_not_slr1.txt` | `S -> AaAb BbBa`: `Grammar is LL(1).`, `yes yes no no` |
| `tests/epsilon.txt` | `S -> aSb e` with the empty string `e`: `yes yes yes no no` with each parser |
| `tests/start_not_first.txt` | A grammar whose first line is not the one of `S`: `yes yes no` |
| `tests/invalid_chars.txt` | Strings with characters that are not terminals: `no` (six times), then `yes` |
| `tests/report_grammar_strings.txt` | The grammar of the report: `yes yes yes yes yes no no` with each parser |
| `tests/sdd_grammar.txt` | The grammar of the SDD through `main.py`: it is both LL(1) and SLR(1) |
| `tests/sdd_strings.txt` | Input of `sdd.py`. Values: 0, 5, 15, 2026, error, no, no, no, 65535 |

## Use of generative AI tools

We used Claude Code (Anthropic, model Claude Opus 5.5) as a programming assistant. This is what it did.

1. **Implementation and debugging of the modules.**
   - It read the assignment and proposed a work plan: the deliverables, the files of the program and the book section that each function had to follow. We asked for simple code that uses only the standard library and cites the book in each function, so that every member can explain it.
   - For Item 3, it proposed two candidate grammars. We chose the numbers with a base prefix. It also proposed the nested-list grammar used in the report.
   - It wrote `ll1.py`, `slr1.py`, `main.py`, `sdd_rules.py` and `sdd.py`. It added to `grammar.py` the class `Node`, the method `only_terminals` and the end-of-input case of `read_line`. It reviewed and tested `first_follow.py`, which did not need changes.
   - It found and fixed the bugs described in Section 5 of the report: repeated `lexval` vertices in the dependency graph, the end of the LL(1) parse, characters that are not terminals, and the end of the input in the parser menu.
   - It wrote the input files in `tests/` and ran them. As an extra check that is not part of the submission, it compared both parsers with an exact membership test on 3,086 random grammars and 455,099 strings.
2. **Comparison with the book.**
   - It extracted the text of Sections 4.4.2–4.4.4, 4.6.2–4.6.4 and 5.2.1–5.2.4. With it, it checked that each function follows its algorithm or figure and that the cited numbers are correct.
   - It changed the step-by-step output to match Fig. 4.21 (LL(1)) and Fig. 4.38 (LR).
   - It checked that the expression grammar of the book gives the same LR(0) automaton, SLR table and moves as Figs. 4.31, 4.37 and 4.38.
   - It read Exercises 5.2.4–5.2.5 and Fig. 5.4 to compare our SDD with the book's (condition G3).
3. **Drafting of the report and of this README.**
   - It wrote the LaTeX source of the report and this file. The sets, tables and traces of the report are copied from the program's output, and the LR(0) automaton figure was drawn from the output of `python slr1.py`.
   - It installed MiKTeX and compiled the report.
   - It did not do the hand-worked example of Step 3, which the assignment requires us to do ourselves. It explained Sections 5.1–5.2 with the book's examples, reviewed our drawings against the output of `sdd.py`, pointed out what was missing (the `lexval` of the leaves and the edge `R3.acc -> R3.val`), and then inserted our scanned pages into the report and typed the edge list and the evaluation order from them.
4. **Study material.**
   - It made an interactive HTML guide, which is not part of the submission. For each subtask of the project, the guide relates the code to the book and runs the algorithms step by step: FIRST/FOLLOW, LL(1), LR(0)/SLR(1) and the SDD evaluator. Its results are the same as those of our program.
   - The guide also has comments on the lines of the code and a quiz with questions for the oral presentation.

## Work of the group

### Review and study of the code

The three members (Simon Alejandro Vasquez Medina, Miguelangel Calderon Figueredo and Sebastian Urrego Ramirez) reviewed and studied all the code. The goal was that each of us can explain any part of it, trace its algorithms by hand on a new grammar and change it, as the assignment asks for the oral presentation. We did it in three ways.

1. **Code next to the book.** We read each function together with the section, algorithm or figure of the book that it follows. The column "Book reference" of the table in [Files](#files) lists them, and the comment of each function cites it:
   - `first_follow.py`: the rules for FIRST and FOLLOW of Section 4.4.2.
   - `ll1.py`: the LL(1) condition of Section 4.4.3, the construction of the table (Algorithm 4.31) and the predictive parser (Algorithm 4.34, Fig. 4.20).
   - `slr1.py`: CLOSURE (Fig. 4.32), GOTO, the canonical LR(0) collection (Fig. 4.33), the SLR table (Algorithm 4.46) and the LR parser (Algorithm 4.44, Fig. 4.36).
   - `sdd_rules.py` and `sdd.py`: the format of the rules (Fig. 5.1), the dependency graph (Section 5.2.1) and the topological order (Section 5.2.2).
2. **Hand traces compared with the program.** We traced the algorithms by hand on grammars and compared our results with the output of the program:
   - the FIRST and FOLLOW sets, with `python main.py --sets`;
   - the parsing tables and the moves of the parsers, with `python ll1.py` and `python slr1.py`;
   - the dependency graph and the evaluation order, with `python sdd.py --step`.
3. **Interactive guide and quiz.** We studied with the interactive guide described in item 4 above. For each step of an algorithm, it shows the rule of the book that applies, the line of code that runs and the state of the data. Then we answered its quiz of questions for the oral presentation.

### Hand-worked example of Step 3

The group did the example of Step 3 by hand, on paper, for the string `b101`. The scanned pages are Figures 4 to 7 of the report (Section 4.3). These are the three parts and who did each one:

1. **Annotated parse tree** (Figure 4): Simon Alejandro Vasquez Medina. It shows the tree of `b101` with the values of all the attributes of each node, including the `lexval` of the leaves:
   - `base = 2` in `B`, `N` and the three `R` nodes;
   - `acc = 1, 2, 5` going down the chain of `R` nodes;
   - `val = 5` going back up to `S`.
2. **Dependency graph** (Figure 5, and the list of edges in Figure 7, right): Simon Alejandro Vasquez Medina and Miguelangel Calderon Figueredo.
   - It has one vertex for each attribute of each node: 20 vertices, the 4 `lexval` of the leaves and 16 attributes of the nonterminals.
   - It has one edge from each attribute used by a rule to the attribute the rule defines: 21 edges.
   - It is drawn on top of the parse tree, as in Fig. 5.7 of the book.
3. **Evaluation order** (Figure 7, left): Miguelangel Calderon Figueredo and Sebastian Urrego Ramirez.
   - We repeatedly took a vertex with no incoming edges, wrote it down and removed its outgoing edges (Section 5.2.2).
   - Then we checked that, in each of the 21 edges, the source comes before the target.

Afterwards we compared the three parts with the output of `python sdd.py --step`. The values of the tree, the 21 edges and the evaluation order are the same.
