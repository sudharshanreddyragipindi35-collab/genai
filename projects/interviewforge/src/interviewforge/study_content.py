"""Original self-contained teaching examples; these are not Amazon internal scenarios."""

CODING = """
## 1. Understand the problem
Two warehouse scans contain product IDs. Find IDs present in both scans, keeping duplicates only as many times as they appear in both.
This is an illustrative retail scenario, not an Amazon internal system.

- First scan: `[1, 2, 2, 1]`
- Second scan: `[2, 2, 3]`
- Expected result: `[2, 2]`. Ordering does not matter.
- Ask: Can inputs be empty? Do repeated IDs represent separate units?

## 2. Choose an approach
A set loses duplicate counts. A frequency map stores how many copies remain available.
Count the first scan, then consume one count for each matching ID in the second.

## 3. Dry run
Initial counts: `{1: 2, 2: 2}`.

| Step | Current ID | Available before | Action | Result |
| --- | --- | --- | --- | --- |
| 1 | 2 | 2 | Append 2, reduce count to 1 | [2] |
| 2 | 2 | 1 | Append 2, reduce count to 0 | [2, 2] |
| 3 | 3 | 0 | Skip: no matching unit | [2, 2] |

## 4. Python implementation
```python
from collections import Counter

def intersect(first, second):
    remaining = Counter(first)
    result = []
    for product_id in second:
        if remaining[product_id] > 0:
            result.append(product_id)
            remaining[product_id] -= 1
    return result

assert intersect([1, 2, 2, 1], [2, 2, 3]) == [2, 2]
assert intersect([], [2]) == []
assert intersect([2], [2, 2]) == [2]
```

## 5. Complexity and edge cases
- Time: O(n + m), where n and m are the two scan lengths.
- Extra space: O(k) for k distinct IDs in the first scan, plus the output.
- Empty scan produces no matches.
- Decrementing counts prevents duplicate overuse.
- If memory is limited and inputs are sorted, compare a two-pointer solution.

## 6. Explain it in an interview
?I need multiplicities, so I use counts rather than a set. Each accepted match consumes one available occurrence.?

**Try it yourself:** trace `[4, 9, 5, 4]` against `[9, 4, 9, 8, 4]`. Explain why a second 9 is skipped.
"""
LP = """
## 1. Start with behavior, not a memorized slogan
Amazon's Leadership Principles inform how candidates discuss decisions and past work.
For preparation, connect a genuine example to customer impact, personal responsibility, evidence, and trade-offs.

## 2. Illustrative scenario
A checkout service produces duplicate order confirmations. You notice the problem outside your assigned feature.
You investigate the customer impact, coordinate a fix, and check whether the issue returns.
This is a fictional practice scenario. Replace it with your own experience.

## 3. Build the STAR answer
| Part | What to explain | Example prompt |
| --- | --- | --- |
| Situation | Context and customer pain | Who received duplicates, and when? |
| Task | Your responsibility | What did you personally own? |
| Action | Your decisions and reasoning | How did you reproduce the bug and compare fixes? |
| Result | Evidence and learning | How did you verify the fix and prevent recurrence? |

## 4. Make your actions specific
1. Establish the impact from support reports and logs.
2. Trace duplicate events to retry behavior.
3. Compare a quick suppression patch with durable idempotency.
4. Agree on an owner and rollout plan.
5. Monitor duplicate rate after the change and add a regression test.

This example can help rehearse Ownership, Customer Obsession, Dive Deep, and high standards.
Do not force every principle into one story.

## 5. Prepare follow-up answers
- Why was this your responsibility?
- What alternative did you reject, and why?
- Where did you disagree with someone?
- What did the data fail to tell you?
- What would you change next time?

## 6. Your exercise
Write a 90-second story from a real project. Use ?I? for your actions and ?we? for team outcomes.
Include metrics only if you can support them; an honest qualitative result is better than invented numbers.
"""
CACHE = """
## 1. Define the cache contract
A cache keeps recently used values in limited memory. When full, evict the least recently used entry.
For an illustrative product-details service, a recently read product becomes most recent.

- `get(key)`: return the value, or -1 when absent.
- `put(key, value)`: insert or update and mark the key most recent.
- Assume positive capacity and integer values for this exercise.
- A read changes recency; updating an existing key must not increase cache size.

## 2. Dry run: capacity 2
| Operation | Order: oldest to newest | Return |
| --- | --- | --- |
| put(1, 10) | [1] | none |
| put(2, 20) | [1, 2] | none |
| get(1) | [2, 1] | 10 |
| put(3, 30) | [1, 3] | evict 2 |
| get(2) | [1, 3] | -1 |

## 3. Python reference
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.items = OrderedDict()

    def get(self, key):
        if key not in self.items:
            return -1
        self.items.move_to_end(key)
        return self.items[key]

    def put(self, key, value):
        self.items[key] = value
        self.items.move_to_end(key)
        if len(self.items) > self.capacity:
            self.items.popitem(last=False)
```

## 4. Explain the design
Average O(1) get/put operations and O(capacity) storage. If library structures are disallowed, implement a dictionary plus a doubly linked list.
The dictionary locates nodes; the list moves or removes a node without scanning.

## 5. LLD follow-ups
Separate storage from eviction policy when requirements demand interchangeable policies.
Discuss TTL, concurrent access, and failure behavior before adding them. This implementation is single-threaded and does not implement TTL.

**Try it:** capacity 1, repeated updates to the same key, and reading a missing key. Describe the expected order after each operation.
"""
DESIGN = """
## 1. Clarify requirements
Design a service that collects API latency metrics. This is an original rehearsal for system-design preparation.
Ask about event rate, acceptable delay, retention, regional boundaries, and whether approximate percentiles are acceptable.

## 2. State an example workload
Assume 10,000 requests/second and a 200-byte metric event: about 2 MB/second before replication and protocol overhead.
These are exercise assumptions, not Amazon production figures.

## 3. Trace one request
1. The application emits timestamp, API name, region, and duration.
2. An ingestion service validates the event and writes it to a durable queue.
3. Consumers aggregate by API and time window.
4. A metrics store retains aggregates.
5. A query API reads aggregates for dashboards and alerts.

## 4. Discuss trade-offs
| Decision | Benefit | Cost or failure case |
| --- | --- | --- |
| Durable queue | Absorbs bursts | Adds processing delay |
| Time-window aggregation | Reduces storage | Late events need a policy |
| Histogram buckets | Compact percentile estimates | Approximation error |
| Replication | Survives node loss | Additional cost and consistency choices |

## 5. Reliability questions
Define retry behavior and event IDs to limit double-counting.
Monitor queue depth and consumer lag. Decide when to shed load and how to signal incomplete data.
Do not average percentiles from independent groups; combine compatible histograms or sketches.

## 6. Rehearse
Draw the write and read paths. Explain the first bottleneck at 10 times the traffic.
For SDE II practice, defend a trade-off and explain what evidence would make you change the design.
"""
GENAI = """
## 1. Define the use case
Build a Python assistant that answers questions from an approved documentation collection.
This is optional job-specific GenAI preparation, not a universal Amazon SDE requirement.

## 2. Walk through a grounded answer
1. Ingest reviewed documents with source IDs and timestamps.
2. Split them into meaningful passages.
3. Retrieve passages matching the question.
4. Give the model only the relevant evidence and the answering policy.
5. Evaluate whether the answer is supported; abstain when evidence is missing.

## 3. Concrete example
Question: ?What is the refund window??
A retrieved policy says 30 days for a specified product category.
The assistant must preserve that category restriction; it should not generalize to all products.

## 4. Engineering trade-offs
| Concern | Design choice |
| --- | --- |
| Changing facts | Refresh retrieval data |
| Missed wording | Compare lexical and embedding retrieval |
| Invented claims | Groundedness evaluation and abstention |
| Slow answers | Cache documents and bound retrieved context |
| Unsafe document instructions | Treat document text as data |

## 5. Your exercise
Create 10 answerable and 5 unanswerable evaluation questions.
Measure retrieval recall, unsupported claims, latency, and cost before changing the model.
Explain why adding documents to RAG does not retrain model weights.
"""
MOCK = """
## 1. Set up a rehearsal
Choose an already studied coding problem. Reserve 35 minutes for coding and 15 minutes for behavioral discussion.
These are practice timings, not an official Amazon interview schedule.

## 2. Coding sequence
1. Clarify inputs and outputs.
2. Explain a direct approach.
3. Improve it and state complexity.
4. Write readable Python.
5. Dry-run normal, empty, and duplicate-heavy inputs.
6. Explain one alternative and its trade-off.

## 3. Behavioral sequence
Describe a genuine problem you owned. Cover situation, task, personal actions, outcome, and learning.
Ask the coach to challenge a weak assumption in your story.

## 4. Reflection checklist
| Dimension | Evidence to record |
| --- | --- |
| Clarity | Could you explain the invariant? |
| Correctness | Which edge case did you miss? |
| Trade-offs | Did you compare alternatives? |
| Ownership | Were your personal actions explicit? |

## 5. Next action
Record one weakness, revise the solution or story, then repeat the specific weak section.
Completion is study progress; it is not a validated hiring score.
"""
CONTENT = {"coding": CODING, "lp": LP, "lld": CACHE, "design": DESIGN, "genai": GENAI, "mock": MOCK}


def study_text(task):
    if task.problem:
        return CACHE if task.problem.slug == "lru-cache" else CODING
    for key, content in CONTENT.items():
        if f"-{key}-" in task.id:
            return content
    return "## Practice preparation\nComplete the concept lessons first. Your coach can explain any step."
