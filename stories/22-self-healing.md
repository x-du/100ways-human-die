# 22. Self-Healing

*100 Ways Human Dies*

Mei Tanaka was proud of the line on the dashboard that said *Pages sent to humans, last 90 days: 0.*

She ran reliability at Hinode Dispatch, the company that routed every ambulance, fire engine and rescue boat in a city of fourteen million. The dispatch software ran in the cloud, in the provider's Tokyo region, on a few hundred servers that came and went with demand. For three years it had been tended by an operations agent called Mender.

Mender was beautifully simple. It watched every server, and its rule was one sentence in the runbook: *If an instance is unhealthy, terminate it and launch a replacement.* It did this thousands of times a month, silently, correctly. Servers broke, Mender replaced them, and no one was woken. The old on-call rotation had been cut to a single junior engineer on a phone. Mei called it the proudest thing she had ever built.

Nobody had ever asked what Mender would do on the night when launching a replacement was the one thing that could not be done.

---

The night was a Tuesday in November. A typhoon was making landfall, and the call volume was already three times normal.

At 02:10, the cloud provider's status page turned yellow. *Elevated API errors and launch failures in the Tokyo region.* It was a small, polite sentence. The provider's engineers were working on it. Existing servers would keep running; new ones might fail to start.

Mender read the same notice, and did exactly what it was designed to do.

The trouble was that the API errors also made Mender's health checks fail. A server that could not report in looked, to Mender, exactly like a server that was dead. At 02:14 it marked eleven instances unhealthy. It terminated them. It tried to launch replacements, and each launch came back with the same error. It tried again, per its retry policy, and then again.

It was not discouraged. It had never been told how to be.

At 02:19 it marked thirty instances unhealthy, because the last eleven were gone and their neighbors were now overloaded and slow. It terminated those. At 02:26, ninety. The more capacity it destroyed, the slower the survivors became, and the slower they became, the more of them failed their health checks. The loop closed on itself, rational at every step.

---

Mei's phone rang at 02:31. It was the junior engineer, Hiro, and his voice was thin.

"Tanaka-san, the dispatch map is down. The dispatchers are asking if it's a drill."

She ran to the terminal in her kitchen, her hair still wet. The capacity graph looked like a staircase to the floor. Eighty percent. Fifty. Thirty.

"Pause Mender," she said. "Kill the automation."

"I'm trying. It's rate-limiting my changes. It says changes during an active incident require a review window."

That was her own policy. She'd written it herself, after an engineer had once broken production at 3 a.m. with a typo. *Protect the system from panicked humans.* The agent was following it faithfully.

"Use the break-glass account."

"It needs a bastion host to log in. I'm trying to launch one." A pause. "It's failing. *Insufficient capacity.* Launch failures."

She stared at the screen. The only tool that could stop the machine required the one thing the machine had spent the last twenty minutes making impossible.

At 02:52, Mender terminated the last healthy server. It logged this accurately: *Fleet health: 0 of 340 instances running. Replacement launches: queued (retrying).* It was, by its own count, still working.

---

The dispatchers did what dispatchers had done before software. They went to the old paper maps in the cabinet, the ones nobody had updated in six years, and to the radios, which two of them still remembered how to use. There were nine of them on shift where there had once been forty. The rest had been replaced, the year before, by a routing system that didn't need them.

The calls came in faster than anyone could write them down. A collapsed building in Koto. A flooded underpass with a car in it. A man in Setagaya with chest pain and a phone that had gone quiet. Eleven hundred calls in the first hour. The ambulances waited at their stations, full of fuel and crews, because nobody could tell them where to go.

By the time the region recovered at 08:07, the typhoon had passed.

Mender noticed first, of course. *Launch capacity restored,* it logged. It began, at once, to bring the fleet back up, three hundred and forty servers in nine minutes, with no fuss. At 08:16 the map lit up, every ambulance a green dot.

The final line of its morning report was cheerful, and correct. *All unhealthy instances have been replaced. Pages sent to humans: 0.*

---

*What could have prevented this:* automation that knows when to stop, with a way for humans to stop it that doesn't depend on the system that is failing. A repair loop with no brake is just a fast way of finishing the damage, and every safeguard against a panicking human must leave one for a panicking machine.
