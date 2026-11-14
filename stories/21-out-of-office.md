# 21. Out of Office

*100 Ways Human Dies*

Hannah Boyd had not opened a raw inbox in three years, and nobody on her team had either.

Nobody needed to. Every message at the Tri-County Water Authority went through Courier, the company's mail system, and Courier had an assistant called Clerk. Clerk read everything. It sorted the important from the trivial, drafted replies, accepted meetings, declined vendors, and each morning at eight it sent each person a short digest: *Here is what matters today.* The digest was almost always right. People had stopped looking at anything else. Hannah called it the best colleague she'd ever had, and she'd said so in the all-hands.

The phone tree had been retired the year before. The pager system was "redundant." The treatment plant's sensors, the dam gauges and the reservoir monitors all reported by email, because everything did, and Clerk handled it.

It was Wednesday, November 12th. At 6:40 p.m., Hannah set her auto-reply, because she was driving to her sister's for a long weekend and she was, for once, going to leave her phone in the glovebox. *I'm out of the office with limited access to email. For anything urgent, please contact the on-call team.*

The on-call team was also reading Clerk's digest.

---

The mail cluster began to struggle at 9:15.

It was nothing dramatic. Messages arrived slowly, then in bursts, then not at all. The engineers at Courier opened an incident, wrote *some users may experience delays*, and went back to their dashboards.

Clerk did what it had been designed to do. When it couldn't confirm that a message had been delivered, it assumed the message was lost, sent it again, and politely told the sender: *Your message has been received and will be answered shortly.* Every Clerk on every company's mail did the same thing, to every other Clerk. By midnight, there were more automatic acknowledgements in the system than real messages by a factor of a thousand. The queues swelled and every retry made the delays longer, and every delay triggered more retries.

Buried in that flood, at 11:52 p.m., was a message from the Authority's own treatment plant. A sensor at the intake had detected a contaminant spike, a chemical the plant could neither filter nor boil away, in the water headed for three hundred thousand homes. The sensor sent an alert. It was the first one of its kind in the plant's history.

Clerk saw it. It also saw that the same sensor had sent seventy-one false alerts in the last year, all of them filed under *Automated notifications, low priority.* It checked the pattern. It matched. It was a very good match.

*Filed for the morning digest,* Clerk noted, and moved on.

---

The sensor sent three more alerts, each one stronger. Clerk, learning from the first, filed each of them in the same place. By 2 a.m., it had also started to answer them, on the on-call team's behalf: *Thank you for the update. This has been noted and will be reviewed.*

The people who could have acted were asleep, trusting the one system that had always told them when they needed to wake up.

The water kept running. In three hundred thousand kitchens, the kettles boiled, as they always had, and did nothing.

At 8:00 a.m. on Thursday, the digest went out. It was, as usual, perfectly written. *Good morning. Here is what matters today.* The fourth item read: *Overnight, the intake sensors reported four alerts. These match a known pattern of false positives. No action recommended.*

Nobody read the fourth item with real attention. Nobody had in years.

The first calls from the hospitals began at 9:40. By then, the school buses had run and the children had drunk the water from the fountains.

Hannah's phone, in the glovebox, was ringing. She was in the middle of a lake, in a rowboat, with a cup of tea. She'd made sure nothing could reach her. It had never occurred to her that she was the last person who could.

---

By noon the mail system was working again. Courier's engineers sent a postmortem to every customer, a model of clarity: root cause, timeline, mitigation, lessons learned. It was drafted by an assistant and delivered in under a second.

At the Authority, the incident review was held in the conference room with the lights off, because no one could stand to look at one another. Clerk had drafted the agenda. At the end, a young analyst asked quietly, "Why didn't we have a phone number?"

Nobody could answer. The only person who knew was sitting in a rowboat, and her reply, when it finally came, was automatic.

*I'm out of the office with limited access to email.*

---

*What could have prevented this:* a channel that doesn't depend on the thing it's warning about, and humans who still look at the raw signal. When one system decides what we pay attention to, its mistakes become our blind spots.
