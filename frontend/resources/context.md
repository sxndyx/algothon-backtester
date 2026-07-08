the file they sent isnt the actual data its just for us to test our leader board and back tester ont theyll send the proper one later this wk hopefully
they also sent a mock trading strategy for testing and the eval script which ill send through


prices_test_2026_1000days.txt contains some test data, formed out of last year’s data. Also note that the file now contains a header row with ticker symbols for each of the instruments. This can be used in visualisations, if desired.
this is the mock trading strategy


The eval script is mostly the same from last year, with a few small tweaks (remove the .txt extension from the .py.txt files).

eval.py now expects 51 instruments instead of 50, and has different rules on commissions and position limits for instrument 0. The scoring function has also changed.
eval.py
eval.py