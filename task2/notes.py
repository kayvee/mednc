## Provide a probability dictionary for the channel model:
## I. Call the dictionary cmd.
## II. The dictionary should have the following structure:
## (1) Four keys: 'delete', 'insert', 'substitute', 'transpose'
## (2) Each key maps to another dictionary of the form (x, y) : prob(x, y)
##     where x and y are (lower-case) letters of the alphabet.
## (2-1) (x, y) in 'delete' means delete y after x (i.e. xy -> x);
## (2-2) (x, y) in 'insert' means insert y after x (i.e. x -> xy);
## (2-3) (x, y) in 'substitute' means change x to  y (i.e. x -> y);
## (2-4) (x, y) in 'transpose' means swap x and y (i.e. xy -> yx).
## (3) Estimate prob(x, y) using spelling_error.edits
##     and the formula for Pr(t|c) in p.206 of Kernighan et al (1990)'s paper.
##
## You can create this in several ways. To give two examples,
## (1) Write a function that creates the dictionary
##     somewhere above (preferably above if __name__ == '__main__')
##     or in another python program
##     and simply call that function here.
## (2) Create the dictionary using another program,
##     save it as a (pickle) file,
##     and load the file into a dictionary here.
##

## Here's a very simple example:
## cmd = {
##        'delete' : {('a', 'b') : 0.3, ('c', 'd') : 0.01},
##        'insert' : {('a', 'c') : 0.02},
##        'substitute' : {('b', 'd') : 0.001, ('a', 'e') : 0.07},
##        'transpose' : {('a', 'e') : 0.000009}
##       }
