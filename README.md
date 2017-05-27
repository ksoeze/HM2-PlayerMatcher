# HM2-PlayerMatcher
Simple Python script to find similar players based on Opponents Tab in Holdem Manager 2

1.) Go to Holdem Manager opponents tab. Filter for a specific game, miniumum amount of Hands (about 1k for decent results)
and exclude HU hands etc. Right Click -> Save as Report.cvs

2.) Put matcher.py in the same directory and run it in python3... ./matcher.py > results.txt

3.) View results in Texteditor. On large monitors it is possible to view it without linebreaks. Otherwise disable linebrake
for alinged/correct column view

It ranks the top x players to every player in the list with the minimum mean square-errors. Unfortunatly HM2 allows less
stats to be exported for all players than HM1. Still a good starting point when trying to find potentional cheeting players.
(BOTs playing multiple accounts, multiaccounter, potentional study groups/collution...)

But remember that these results are never enough to start making accusations...

See the source for potentional customization.
