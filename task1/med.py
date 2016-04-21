#!/usr/local/bin/python
# -*- coding: utf-8 -*-

# Write a function that calculates the minimum edit distance between two strings.
# • three types of edit operations allowed: substitution, insertion, and deletion
# • cost of edit operation is 1 for all three
def med(correct, typo):
    lenC, lenT = len(correct), len(typo) #get length for creation
    mat =[[0]*(lenT+1) for mainWordComp in range(lenC+1)] #create matrix based on the main word being compared

    #label the empty string minimum edit distances
    for i in range(lenC+1):
        mat[i][0]=i
    for j in range(0,lenT+1):
        mat[0][j]=j

    #go through each matrix point
    for i in range (1,lenC+1):
        for j in range(1,lenT+1):
            # compare each subpoint to the other
            if correct[i-1]==typo[j-1]:
                mat[i][j] = mat[i-1][j-1] 
            else: #check left, bottom,
                m = min(mat[i][j-1],mat[i-1][j],mat[i-1][j-1])
                mat[i][j]= m+1

    return mat[i][j] #top-end corner

# Using the function, calculate the minimum edit distance for every word-error pair in the data file (spelling error.pairs).
one = 0
two = 0
total = 0.0

pairs = open("spelling_error.pairs", "r")
for pair in pairs:
    total += 1

    correct, typo = pair.strip().split("\t")
    me = med(correct, typo)

    if me == 1:
        one += 1
    elif me == 2:
        two += 1

# • percentage of pairs with distance of 1
print "percentage of pairs with distance of 1:", one / total
# • percentage of pairs with distance of 2
print "percentage of pairs with distance of 2:", two / total
