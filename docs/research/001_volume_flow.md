# Options Volume Flow

## What does it aim to do?

The main goal is to try to track the rate of change of volume at a specific strike (call and put side both included) to potentially exmaine any unusual activity.

## Steps

* Define the “normal” rate of change of volume by using components like implied volatility, VIX, news day, and time of day (such as NY open being high volume flow)
    * How can I derive the "normal" rate of change? Must work this out before implementation
* Calculate the rate of change of volume (flow) by taking the current volume of a strike, then subtract the previous second volume from the current volume of a strike.
    * I can scale this up by using functions from NumPy instead of using pure Python loops.
* Plot the volume flow across each strike.
    * What could the 3D surface tell us if we include expiration? Could this build a different narrative?

### Cumulative Volume Flow extension

* What if a cumulative volume flow is created?
* Gather the current volume flow as defined in the steps section, but across each strike in the strike range desired.
* Build a heatmap of each strike and at each time point.
* Probably don’t build it in seconds as it would make the graph super cluttered.

## Hypothesis

* If the volume flow is not considered a normal amount, then we can expect price movement towards the specific strike of unusual volume flow, as this could indicate that a market participant knows something about the specific strike.
    * Counter: Retail could simply be paranoid and be participating at a strike to hedge against market movements.
