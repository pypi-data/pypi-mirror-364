binary_tree = """
class TreeNode:
    def __init__(self, value):
        self.val = value
        self.left = None
        self.right = None


def array_to_tree(arr, index=0):
    if index >= len(arr) or arr[index] is None:
        return None
    root = TreeNode(arr[index])
    root.left = array_to_tree(arr, index * 2 + 1)
    root.right = array_to_tree(arr, index * 2 + 2)
    return root
"""
linked_list = """
class ListNode:
    def __init__(self, val):
        self.val = val
        self.next = None


def array_to_list(arr, i=0):
    if i >= len(arr):
        return None
    head = ListNode(arr[i])
    head.next = array_to_list(arr, i + 1)
    return head

"""
questions = {
    0: {
        "markdown": """
### Score tally
Given an array of scores e.g `[ '5', '2', 'C', 'D', '+', '+', 'C' ]`, calculate the total points where:
```
+  add the last two scores.
D  double the last score.
C  cancel the last score and remove it.
x  add the score
```
You're always guaranteed to have the last two scores for `+` and the previous score for `D`.
### Example
```
input: [ '5', '2', 'C', 'D', '+', '+', 'C' ]
output: 30
explanation:
    '5' - add 5 -> [5]
    '2' - add 2 -> [5, 2]
    'C' - cancel last score -> [5]
    'D' - double last score -> [5, 10]
    '+' - sum last two scores -> [5, 10, 15]
    '+' - sum last two scores -> [5, 10, 15, 25]
    'C' - cancel last score -> [5, 10, 15]
    return sum -> 30
```
""",
        "test_cases": """
test_cases = [
    [[["5", "2", "C", "D", "+", "+", "C"]], 30],
    [[["9", "C", "6", "D", "C", "C"]], 0],
    [[["3", "4", "9", "8"]], 24],
    [[["4", "D", "+", "C", "D"]], 28],
    [[["1", "C"]], 0],
    [[["1", "1", "+", "+", "+", "+", "+", "+", "+", "+"]], 143],
    [[["1", "D", "D", "D", "D", "D"]], 63],
]
""",
        "title": "Score tally",
        "difficulty": "Easy",
    },
    1: {
        "markdown": """
### Repeated letters
Given a string k of lower-case letters. the letters can be repeated and
exist consecutively. A substring from k is considered valld if it contains
at least three consecutive identical letters.

An example: k = "abcdddeeeeaabbbed" has three valid substrings: "ddd",
"eeee" and "bbb".

You must order the pairs by the start index in ascending order
### Example
```
Input: "abcdddeeeeaabbbcd"
Output: [[3,5], [6,9], [12,15]]
```
""",
        "test_cases": """
test_cases = [
    [["abcdddeeeeaabbbb"], [[3, 5], [6, 9], [12, 15]]],
    [["xxxcyyyyydkkkkkk"], [[0, 2], [4, 8], [10, 15]]],
    [
        ["abcdddeeeeaabbbb" * 6],
        [
            [3, 5],
            [6, 9],
            [12, 15],
            [19, 21],
            [22, 25],
            [28, 31],
            [35, 37],
            [38, 41],
            [44, 47],
            [51, 53],
            [54, 57],
            [60, 63],
            [67, 69],
            [70, 73],
            [76, 79],
            [83, 85],
            [86, 89],
            [92, 95],
        ],
    ],
    [["abcd"], []],
    [["aabbccdd"], []],
    [[""], []],
    [["abcdefffghijkl"], [[5, 7]]],
]""",
        "title": "Repeated letters",
        "difficulty": "Easy",
    },
    2: {
        "markdown": """
### Valid matching brackets
Given a string of brackets that can either be `[]`, `()` or `{}`.
Check if the brackets are valid.

There no other characters in the string apart from '[', ']', '(', ')', '{'and '}'.

### Example
```
input: "[](){}"
output: True

input: "{{}}[][](()"
output: False

input: "[[[()]]]{}"
output: True
```
""",
        "test_cases": """
test_cases = [
    [["[](){}"], True],
    [["{{}}[][](()"], False],
    [["[[[()]]]{}"], True],
    [["["], False],
    [["{}" * 50_000 + "()" * 50_000 + "[]"], True],
    [
        [
            "{{{{{{{{{{{{{{{{{{{{{{{{{{{{[[[[[[[[[[()]]]]]]]]]]}}}}}}}}}}}}}}}}}}}}}}}}}}}}"
        ],
        True,
    ],
    [["[" + "()" * 100_000 + ")"], False],
    [["[" + "()" * 100_000 + "]"], True],
]
""",
        "title": "Valid matching brackets",
        "difficulty": "Easy",
    },
    3: {
        "markdown": """
### Max sum sub array
Given an integer array nums, find a contiguous non-empty subarray within the array that has the largest sum,
and return the sum.

### Example
```
input: [-2, 0, -1]
output: 0

input: [2, 3, -2, 4]
output: 7
```
```
""",
        "test_cases": """
test_cases = [
    [[[-2, 0, -1]], 0],
    [[[2, 3, -2, 4]], 7],
    [[[-2]], -2],
    [[[i for i in range(100_000)]], 4_999_950_000],
    [[[2] * 50_000 + [-2] * 50_000], 100_000],
    [[[2, -4, 8, 6, 9, -1, 3, -4, 12]], 33],
]
""",
        "title": "Max sum sub array",
        "difficulty": "Easy",
    },
    4: {
        "markdown": """
### Max product sub array
Given an integer array nums, find a contiguous non-empty subarray within the array that has the largest product,
and return the product.

### Example
```
input: [-2, 0, -1]
output: 0

input: [2, 3, -2, 4]
output: 6
```
```
""",
        "test_cases": """
test_cases = [
    [[[-2, 0, -1]], 0],
    [[[2, 3, -2, 4]], 6],
    [[[-2, 0, -1, -3]], 3],
    [[[-2]], -2],
    [[[1 for _ in range(200_000)]], 1],
    [[[2, -4, 8, 6, 9, -1, 3, -4, 12]], 497664],
]
""",
        "title": "Max product sub array",
        "difficulty": "Easy",
    },
    5: {
        "markdown": """
### Symmetric difference
Create a function that takes two or more arrays and returns an array of their symmetric difference. The returned array must contain only unique values (no duplicates).

The mathematical term symmetric difference (△ or ⊕) of two sets is the set of elements which are in either of the two sets but not in both.

Return the elements in order of appearance from left to right.

### Example
```
input: [[1, 2, 3], [2, 3, 4]]
output: [1, 4]
```
""",
        "test_cases": """
test_cases = [
    [[[1, 2, 3], [2, 3, 4]], [1, 4]],
    [[[1, 2, 4, 4], [0, 1, 6], [0, 1]], [2, 4, 6]],
    [[[i] for i in range(6)], [0, 1, 2, 3, 4, 5]],
    [[[-1], [], [], [0], [1]], [-1, 0, 1]],
    [
        [
            [9, -4, 8, 3, 12, 0, -4, 8],
            [3, 3, 8, 6, 7, 10],
            [11, 12, 10, 13],
            [5, 15, 3],
            [11, 15, 11, 11, 6, -2],
        ],
        [9, -4, 0, 7, 13, 5, -2],
    ],
    [[[2] * 50_000 + [-2] * 50_000], [2, -2]],
    [[[i for i in range(100_000)], [i for i in range(100_000)]], []],
    [
        [[i for i in range(100_000)], [i for i in range(10, 100_000)]],
        [i for i in range(10)],
    ],
]
""",
        "title": "Symmetric difference",
        "difficulty": "Easy",
    },
    6: {
        "markdown": """
### Pairwise
Given an array `arr`, find element pairs whose sum equal the second argument `target` and return the sum of their indices.
e.g pairwise([7, 9, 11, 13, 15], 20) returns 6 and pairwise([0, 0, 0, 0, 1, 1], 1) returns 10.

Each element can only construct a single pair.

### Example
```
inputs:
    arr: [7, 9, 11, 13, 15]
    target: 20
output: 6
explanation:
    pairs 7 + 13 and 9 + 11, indices 0 + 3 and 1 + 2, total 6

inputs:
    arr: [0, 0, 0, 0, 1, 1]
    target: 1
output: 10
explanation: pairs 0 + 1 and 0 + 1, indices 0 + 4 and 1 + 5, total 10
```
""",
        "test_cases": """
test_cases = [
    [[[7, 9, 11, 13, 15], 20], 6],
    [[[0, 0, 0, 0, 1, 1], 1], 10],
    [[[-1, 6, 3, 2, 4, 1, 3, 3], 5], 15],
    [[[1, 6, 5], 6], 2],
    [[[1, 6, 5, 15, 13, 2, 11], 10], 0],
    [[[i for i in range(0, 100_000, 10)], 10], 1],
]
""",
        "title": "Pairwise",
        "difficulty": "Easy",
    },
    7: {
        "markdown": """
### Min length sub array
Given an array of positive integers nums and a positive integer target, return the minimal length of a subarray whose sum is greater than or equal to target.

If there is no such subarray, return 0 instead.

### Example
```
inputs:
    arr: [2, 3, 1, 2, 4, 3],
    target: 7
output: 2
explanation: sub array [4, 3] has sum >= 7

inputs:
    arr: [1, 3, 6, 2, 1],
    target: 4
output: 1
explanation: sub array [6] has sum >= 4
```
""",
        "test_cases": """
test_cases = [
    [[[2, 3, 1, 2, 4, 3], 7], 2],
    [[[1, 3, 6, 2, 1], 4], 1],
    [[[i for i in range(500_000)], 3_000_000], 7],
    [[[i for i in range(-10, 10)], 60], 0],
]
""",
        "title": "Min length sub array",
        "difficulty": "Medium",
    },
    8: {
        "markdown": """
### Min in rotated array
Suppose an array of length n sorted in ascending order is rotated between 1 and n times.
For example, the array nums = [0, 1, 2, 4, 5, 6, 7] becomes [4, 5, 6, 7, 0, 1, 2] if it was rotated 4 times. [0, 1, 2, 4, 5, 6, 7] if it was rotated 7 times.

Given the sorted rotated array nums of unique elements, return the minimum element of this array.
You must write an algorithm that runs in O(log n) time.
### Example
```
input: arr: [4, 5, 6, 7, 0, 1, 2]
output: 0
```
""",
        "test_cases": """
test_cases = [
    [[[4, 5, 6, 7, 0, 1, 2]], 0],
    [[[16, 23, 43, 55, -7, -4, 3, 5, 9, 15]], -7],
    [[[i for i in range(36, 1_000_000, 10)]], 36],
    [
        [
            [i for i in range(-10, 1_000_000, 10)]
            + [i for i in range(-1_000_000, -10, 10)]
        ],
        -1_000_000,
    ],
    [[[2]], 2],
]
""",
        "title": "Min in rotated array",
        "difficulty": "Medium",
    },
    9: {
        "markdown": """
### Count primes
Given a positive integer `n`, write an algorithm to return the number of prime numbers in [0, n]
### Example
```
input: 1000
output: 168
explanation:
    There are 168 prime numbers between 0 and 1000 inclusive.
```
""",
        "test_cases": """
test_cases = [
    [[100], 25],
    [[1_000], 168],
    [[10_000], 1229],
    [[100_000], 9592],
    [[2], 1],
    [[3], 2],
    [[1], 0],
    [[1_000_000], 78498],
],
""",
        "title": "Count primes",
        "difficulty": "Medium",
    },
    10: {
        "markdown": """
### Permutations
Given an array nums of distinct integers, return all the possible permutations.
You can return the permutations in any order.

Can you do it without python's itertools?

### Example
```
input: [1, 2]
output: [[1, 2], [2, 1]]
```
""",
        "test_cases": """
test_cases = [
    [[[1, 2]], [[1, 2], [2, 1]]],
    [
        [[i for i in range(1, 5)]],
        [
            [1, 2, 3, 4],
            [1, 2, 4, 3],
            [1, 3, 2, 4],
            [1, 3, 4, 2],
            [1, 4, 2, 3],
            [1, 4, 3, 2],
            [2, 1, 3, 4],
            [2, 1, 4, 3],
            [2, 3, 1, 4],
            [2, 3, 4, 1],
            [2, 4, 1, 3],
            [2, 4, 3, 1],
            [3, 1, 2, 4],
            [3, 1, 4, 2],
            [3, 2, 1, 4],
            [3, 2, 4, 1],
            [3, 4, 1, 2],
            [3, 4, 2, 1],
            [4, 1, 2, 3],
            [4, 1, 3, 2],
            [4, 2, 1, 3],
            [4, 2, 3, 1],
            [4, 3, 1, 2],
            [4, 3, 2, 1],
        ],
    ],
    [[[1]], [[1]]],
]
""",
        "title": "Permutations",
        "difficulty": "Medium",
    },
    11: {
        "markdown": """
### Combinations
Given a string and a positive integer k, return all possible combinations of characters of size k.
You can return the combinations in any order.

Are your hands tied without python's itertools 😅?

### Example
```
input:
    string: "abcd",
    k: 3
output: 'abc', 'abd', 'acd', 'bcd'
```
""",
        "test_cases": """
test_cases = [
    [["abcd", 3], ["abc", "abd", "acd", "bcd"]],
    [
        ["combinations", 2],
        [
            "co",
            "cm",
            "cb",
            "ci",
            "cn",
            "ca",
            "ct",
            "ci",
            "co",
            "cn",
            "cs",
            "om",
            "ob",
            "oi",
            "on",
            "oa",
            "ot",
            "oi",
            "oo",
            "on",
            "os",
            "mb",
            "mi",
            "mn",
            "ma",
            "mt",
            "mi",
            "mo",
            "mn",
            "ms",
            "bi",
            "bn",
            "ba",
            "bt",
            "bi",
            "bo",
            "bn",
            "bs",
            "in",
            "ia",
            "it",
            "ii",
            "io",
            "in",
            "is",
            "na",
            "nt",
            "ni",
            "no",
            "nn",
            "ns",
            "at",
            "ai",
            "ao",
            "an",
            "as",
            "ti",
            "to",
            "tn",
            "ts",
            "io",
            "in",
            "is",
            "on",
            "os",
            "ns",
        ],
    ],
    [["rat", 3], ["rat"]],
    [["rat", 1], ["r", "a", "t"]],
    [["rat", 0], []],
]
""",
        "title": "Combinations",
        "difficulty": "Medium",
    },
    12: {
        "markdown": """
### Single number
Given a non-empty array of integers `nums`, every element appears twice except for one.

Find that single one.

### Example
```
input: [4, 1, 2, 1, 2]
output: 4
```
""",
        "test_cases": """
test_cases =  [
    [[[4, 1, 2, 1, 2]], 4],
    [[[2]], 2],
    [[[i for i in range(1, 500_000)] + [i for i in range(500_000)]], 0],
]
""",
        "title": "Single number",
        "difficulty": "Easy",
    },
    13: {
        "markdown": """
### Powers of 2
Given an integer `n`, find whether it is a power of `2`.

### Example
```
input: 64
output: True

input: 20
output: False
```
""",
        "test_cases": """
test_cases = [
    [[64], True],
    [[20], False],
    [[1024], True],
    [[2], True],
    [[0], False],
    [[1267650600228229401496703205376], True],
    [[1267650600228229401496703205377], False],
    [[-64], False],
]
""",
        "title": "Powers of 2",
        "difficulty": "Easy",
    },
    14: {
        "markdown": """
### Reverse Polish Notation
Evaluate the value of an arithmetic opression in Reverse Polish Notation. Valid operators are +, -, *, and /. Each operand may be an integer or another opression.

Note that division between two integers should truncate toward zero.
It is guaranteed that the given RPN opression is always valid.
That means the expression will always evaluate to a result, and there will not be any division by zero operation.

### Example
```
input: ["2", "1", "+", "3", "*"]
output: 9
explanation: ((2 + 1) * 3) = 9

input: ["4", "13", "5", "/", "+"]
output: 6
explanation: (4 + (13 / 5)) = 6
```
""",
        "test_cases": """
test_cases = [
    [[["2", "1", "+", "3", "*"]], 9],
    [[["4", "13", "5", "/", "+"]], 6],
    [
        [["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"]],
        12,
    ],
]
""",
        "title": "Reverse polish notation",
        "difficulty": "Easy",
    },
    15: {
        "markdown": """
### Roman numerals
Convert a given integer, `n`,  to its equivalent roman numerals for 0 < `n` < 4000.

|Decimal | 1000 | 900 | 400 | 100 | 90 | 50 | 40 | 10 | 9 | 5 | 4 | 1 |
|--------|------|-----|-----|-----|----|----|----|----|---|---|---|---|
|Roman | M | CM | CD | C | XC | L | XL | X | IX | V | IV | I|


### Example
```
input: 4
output: 'IV'

input: 23
output: 'XXIII'
```
""",
        "title": "Roman numerals",
        "difficulty": "Medium",
        "test_cases": """
test_cases = [
    [[4], "IV"],
    [[23], "XXIII"],
    [[768], "DCCLXVIII"],
    [[1], "I"],
    [[3999], "MMMCMXCIX"],
    [[369], "CCCLXIX"],
    [[1318], "MCCCXVIII"],
    [[1089], "MLXXXIX"],
    [[2424], "MMCDXXIV"],
    [[999], "CMXCIX"],
]
""",
    },
    16: {
        "markdown": """
### Longest common substring (LCS)
Given two strings text1 and text2, return their longest common substring. If there is no common substring, return ''.

A substring of a string is a new string generated from the original string with adjacent characters.
For example, "rain" is a substring of "grain". A common substring of two strings is a substring that is common to both strings.

### Example
```
input:
    text1: "brain"
    text2: 'drain'
output: 'rain'
```
""",
        "title": "Longest common substring",
        "difficulty": "Medium",
        "test_cases": """
test_cases = [
    [["brain", "drain"], "rain"],
    [["math", "arithmetic"], "th"],
    [["blackmarket", "stagemarket"], "market"],
    [
        ["theoldmanoftheseaissowise", "sowisetheoldmanoftheseais"],
        "theoldmanoftheseais",
    ],
],
""",
    },
    17: {
        "markdown": """
### Happy number
Starting with any positive integer, replace the number by the sum of the squares of its digits, and repeat the process until the number equals 1 (where it will stay), or it loops endlessly in a cycle which does not include 1.

Those numbers for which this process ends in 1 are happy numbers, while those that do not end in 1 are unhappy numbers.

Implement a function that returns true if the number is happy, or false if not.
### Example
```
input: 2
output: False

input: 7
output: True
```
""",
        "title": "Happy number",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [["brain", "drain"], "rain"],
    [["math", "arithmetic"], "th"],
    [["blackmarket", "stagemarket"], "market"],
    [
        ["theoldmanoftheseaissowise", "sowisetheoldmanoftheseais"],
        "theoldmanoftheseais",
    ],
],
""",
    },
    18: {
        "markdown": """
### Trie/Prefix tree
In English, we have a concept called root, which can be followed by some other word to form another longer word - let's call this word derivative. For example, when the root "help" is followed by the word "ful", we can form a derivative "helpful".

Given a dictionary consisting of many roots and a sentence consisting of words separated by spaces, replace all the derivatives in the sentence with the root forming it. If a derivative can be replaced by more than one root, replace it with the root that has the shortest length.

Return the sentence after the replacement.

### Example
```
input:
    dictionary = ["cat", "bat", "rat"],
    sentence = "the cattle was rattled by the battery"
output: "the cat was rat by the bat"

input:
    dictionary = ["a", "b", "c"],
    sentence = "aadsfasf absbs bbab cadsfafs"
output: "a a b c"
```
""",
        "title": "Trie/Prefix tree",
        "difficulty": "Medium",
        "test_cases": """
test_cases = [
    [
        [["cat", "bat", "rat"], "the cattle was rattled by the battery"],
        "the cat was rat by the bat",
    ],
    [[["a", "b", "c"], "aadsfasf absbs bbab cadsfafs"], "a a b c"],
]
""",
    },
    19: {
        "markdown": """
### Fractional knapsack
Given a knapsack capacity and two arrays, the first one for weights and the second one for values. Add items to the knapsack to maximize the sum of the values of the items that can be added so that the sum of the weights is less than or equal to the knapsack capacity.

You are allowed to add a fraction of an item.

### Example
```
inputs:
  capacity = 50
  weights = [10, 20, 30]
  values = [60, 100, 120]
output: 240
```
""",
        "title": "Fractional knapsack",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [[50, [10, 20, 30], [60, 100, 120]], 240],
    [[60, [10, 20, 30], [60, 100, 120]], 280],
    [[5, [10, 20, 30], [60, 100, 120]], 30],
],
""",
    },
    20: {
        "markdown": """
### Subarrays with sum
Given an array and targetSum, return the total number of contigous subarrays inside the array whose sum is equal to targetSum

### Example
```
inputs:
  arr = [13, -1, 8, 12, 3, 9]
  target = 12
output: 3
explanation: [13, -1], [12] and [3, 9]
```
""",
        "title": "Subarrays with sum",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [[[13, -1, 8, 12, 3, 9], 12], 3],
    [[[13, -1, 8, 12, 3, 9], 2], 0],
    [[[13, -1, 8, 12, 3, 9], 10], 0],
    [[[13, -1, 8, 12, 3, 9, 7, 5, 9, 10], 75], 1],
    [[[13, -1, 8, 12, 3, 9] * 20_000, 12], 60_000],
    [[[13, -1, 8, 12, 3, 9, 7, 5, 9, 10] * 10_000, 24], 30_000],
],
""",
    },
    21: {
        "markdown": """
### Paths with sum
Given the root of a binary tree and an integer targetSum, return the number of paths where the sum of the values along the path equals targetSum.

The path does not need to start or end at the root or a leaf, but it must go downwards (i.e., traveling only from parent nodes to child nodes).
### Example
```
inputs:
  root = [10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]
  target = 8
output: 3
```
""",
        "test_cases": f"""
{binary_tree}
root1 = array_to_tree([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1])
root2 = array_to_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, 5, 1])
test_cases = [
        [[root1, 8], 3],
        [[root2, 22], 3],
        [[root2, 20], 1],
]
""",
        "title": "Paths with sum",
        "difficulty": "Medium",
    },
    22: {
        "markdown": """
### Remove occurence
Given two strings s and part, perform the following operation on s until all occurrences of the substring part are removed:

Find the leftmost occurrence of the substring part and remove it from s. Return s after removing all occurrences of part.

A substring is a contiguous sequence of characters in a string.
### Example
```
inputs:
  s = "axeaxae"
  part = "ax"
output: 'eae'
```
""",
        "title": "Remove occurence",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [["axeaxae", "ax"], "eae"],
    [["axxxxyyyyb", "xy"], "ab"],
    [["daa-cbaa-c-c", "a-c"], "dab"],
    [["shesellsseashellsattheseashore", "sh"], "esellsseaellsattheseaore"],
]
""",
    },
    23: {
        "markdown": """
### Spinal case
Given a string. Convert it to spinal case

Spinal case is all-lowercase-words-joined-by-dashes.

### Example
```
input: "Hello World!"
output: "hello-world"
```
""",
        "title": "Spinal case",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [["Hello World!"], "hello-world"],
    [["The Greatest of All Time."], "the-greatest-of-all-time"],
    [["yes/no"], "yes-no"],
    [["...I-am_here lookingFor  You.See!!"], "i-am-here-looking-for-you-see"],
]
""",
    },
    24: {
        "markdown": """
### 0/1 knapsack
Given a knapsack capacity and two arrays, the first one for weights and the second one for values. Add items to the knapsack to maximize the sum of the values of the items that can be added so that the sum of the weights is less than or equal to the knapsack capacity.

You can only either include or not include an item. i.e you can't add a part of it.

Return a tuple of maximum value and selected items

### Example
```
inputs:
  capacity = 50
  weights = [10, 20, 30]
  values = [60, 100, 120]

output: (220, [0, 1, 1])
```
""",
        "title": "0/1 knapsack",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [[50, [10, 20, 30], [60, 100, 120]], (220, [0, 1, 1])],
    [[60, [10, 20, 30], [60, 100, 120]], (280, [1, 1, 1])],
    [[5, [10, 20, 30], [60, 100, 120]], (0, [0, 0, 0])],
]
""",
    },
    25: {
        "markdown": """
### Equal array partitions
Given an integer array nums, return true if you can partition the array into two subsets such that the sum of the elements in both subsets is equal or false otherwise.

### Example
```
input: [1, 5, 11, 5]
output: True
explanation: [1, 5, 5] and [11]
```
""",
        "title": "Equal array partitions",
        "difficulty": "Medium",
        "test_cases": """
test_cases = [
    [[[1, 5, 11, 5]], True],
    [[[6]], False],
    [[[i for i in range(300)]], True],
    [[[1, 5, 13, 5]], False],
    [[[1, 5, 11, 5] * 100], True],
    [[[1, 5, 13, 5, 35, 92, 11, 17, 13, 53]], False],
    [[[i for i in range(1, 330, 2)]], False],
]
""",
    },
    26: {
        "markdown": """
### Fibonacci numbers
Given a positive interger `n`, return the n<sup>th</sup> fibonacci number

The first 6 fibonacci numbers are:
[0, 1, 1, 2, 3, 5]
### Example
```
input: 0
output: 0

input: 1
output: 1

input: 5
output: 5
```
""",
        "title": "Fibonacci numbers",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [[0], 0],
    [[1], 1],
    [[5], 5],
    [[10], 55],
    [[23], 28657],
    [[50], 12586269025],
    [[100], 354224848179261915075],
],
""",
    },
    27: {
        "markdown": """
### Climb stairs
You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?

### Example
```
input: 0
output: 0
explanation: no stairs, no way to get to the top

input: 1
output: 1
explanation: 1 stair, one way to get to the top

input: 2
output: 2
explanation:
  2 ways to get to the top
    - climb stair 1 then stair 2
    - climb 2 steps to stair 2
```
""",
        "title": "Climb stairs",
        "difficulty": "Easy",
        "test_cases": """
test_cases = [
    [[0], 0],
    [[1], 1],
    [[2], 2],
    [[10], 89],
    [[36], 24157817],
],
""",
    },
    28: {
        "markdown": """
### Ways to make change
There are four types of common coins in US currency:
  - quarters (25 cents)
  - dimes (10 cents)
  - nickels (5 cents)
  - pennies (1 cent)

  There are six ways to make change for 15 cents:
    - A dime and a nickel
    - A dime and 5 pennies
    - 3 nickels
    - 2 nickels and 5 pennies
    - A nickel and 10 pennies
    - 15 pennies

Implement a function to determine how many ways there are to make change for a given input, `cents`, that represents an amount of US pennies using these common coins.

### Example
```
input: 15
output: 6
```
""",
        "title": "Ways to make change",
        "difficulty": "Medium",
        "test_cases": """
test_cases = [
    [[15], 6],
    [[10], 4],
    [[5], 2],
    [[55], 60],
    [[1000], 142511],
    [[10_000], 134235101],
],
""",
    },
    29: {
        "markdown": """
### Has path sum
Given the root of a binary tree and an integer targetSum, return true if the tree has a root-to-leaf path such that adding up all the values along the path equals targetSum.

A leaf is a node with no children.

### Example
```
input:
  root = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, None, None, 1]
  target = 18
output: True
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, None, None, 1])
t2 = array_to_tree([1, 2, 3, None, 4])
test_cases = [
    [[t1, 18], True],
]
""",
        "title": "Has path sum",
        "difficulty": "Medium",
    },
    30: {
        "markdown": """
### Merge sorted linked lists
Given two sorted linked lists, head1 and head2. Merge them into one sorted linked list.

### Example
```
input:
  l1 = [2, 4, 6, 6, 12, 22]
  l2 = [3, 7, 8, 9]
output: [2, 3, 4, 6, 6, 7, 8, 9, 12, 22]
```
""",
        "test_cases": f"""
{linked_list}
l1 = array_to_list([2, 4, 6, 6, 12, 22])
l2 = array_to_list([3, 7, 8, 9])
l3 = array_to_list([2, 3, 4, 6, 6, 7, 8, 9, 12, 22])
test_cases = [
    [[l1, l2], l3],
]
""",
        "title": "Merge sorted linked lists",
        "difficulty": "Medium",
    },
    31: {
        "markdown": """
### Has node BST
Given the root of a binary search tree and a value x, check whether x is in the tree and return `True` or `False`
### Example
```
input:
  root = [9, 8, 16]
  x = 5
output: False

input:
  root = [12, 3, 20]
  x = 3
output: True
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([9, 8, 16])
t2 = array_to_tree([9, 8, 16, 4])
t3 = array_to_tree([12, 3, 20])
t4 = array_to_tree([12, 3, 20, None, 5])
test_cases = [
    [[t1, 5], False],
    [[t3, 3], True],
    [[t2, 4], True],
    [[t4, 21], False],
]
""",
        "title": "Has node BST",
        "difficulty": "Medium",
    },
    32: {
        "markdown": """
### BST min
Given the root of a binary search tree find the minimum value and return it
### Example
```
input: [12, 3, 20]
output: 3
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([9, 8, 16])
t2 = array_to_tree([9, 8, 16, 4])
t3 = array_to_tree([12, 3, 20])
t4 = array_to_tree([12, 3, 20, None, 5])
test_cases = [
    [[t3], 3],
    [[t1], 8],
    [[t2], 4],
    [[t4], 3],
]
""",
        "title": "BST min",
        "difficulty": "Medium",
    },
    33: {
        "markdown": """
### Balanced tree
Given the root of a binary search tree, return `True` if it is balanced or `False` otherwise

A balanced tree is one whose difference between maximum height and minimum height is less than 2

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: True

input: [4, None, 9, None, None, None, 12]
output: False
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
t2 = array_to_tree([4, None, 9, None, None, None, 12])
t3 = array_to_tree([12, 3, 20, None, 5])
test_cases = [
    [[t1], True],
    [[t2], False],
    [[t3], True],
]
""",
        "title": "Balanced tree",
        "difficulty": "Medium",
    },
    34: {
        "markdown": """
### Tree in-order traversal
Given the root of a binary search tree, traverse the tree in order and return the values as an array.

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: [4, 8, 9, 11, 12, 13, 16, 18]
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], [4, 8, 9, 11, 12, 13, 16, 18]],
]
""",
        "title": "Tree in-order traversal",
        "difficulty": "Medium",
    },
    35: {
        "markdown": """
### Tree pre-order traversal
Given the root of a binary search tree, traverse the tree using pre order traversal and return the values as an array.

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: [12, 8, 4, 9, 11, 16, 13, 18]
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], [12, 8, 4, 9, 11, 16, 13, 18]],
]
""",
        "title": "Tree pre-order traversal",
        "difficulty": "Medium",
    },
    36: {
        "markdown": """
### Tree post-order traversal
Given the root of a binary search tree, traverse the tree using post order traversal and return the values as an array.

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: [4, 11, 9, 8, 13, 18, 16, 12]
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], [4, 11, 9, 8, 13, 18, 16, 12]],
]
""",
        "title": "Tree post-order traversal",
        "difficulty": "Medium",
    },
    37: {
        "markdown": """
### Tree level-order traversal
Given the root of a binary search tree, traverse the tree using level order traversal and return the values as an array.

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: [12, 8, 16, 4, 9, 13, 18, 11]
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], [12, 8, 16, 4, 9, 13, 18, 11]],
]
""",
        "title": "Tree level-order traversal",
        "difficulty": "Medium",
    },
    38: {
        "markdown": """
### Tree leaves
Given the root of a binary search tree, return all the leaves as an array ordered from left to right.

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: [4, 11, 13, 18]
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], [4, 11, 13, 18]],
]
""",
        "title": "Tree leaves",
        "difficulty": "Medium",
    },
    39: {
        "markdown": """
### Sum right nodes
Given the root of a binary search tree, return the sum of all the right nodes

### Example
```
input: [12, 8, 16, 4, 9, 13, 18, 11]
output: 25
```
""",
        "test_cases": f"""
{binary_tree}
t1 = array_to_tree([12, 8, 16, 4, 9, 13, 18, 11])
test_cases = [
    [[t1], 25],
]
""",
        "title": "Sum right nodes",
        "difficulty": "Medium",
    },
    40: {
        "markdown": """
### Value in array
Given an array of values sorted in a non decreasing order, and a target `y`. Return `True` if y is in the array or `False` otherwise

### Example
```
input:
  arr = [2, 4, 8, 9, 12, 13, 16, 18]
  y = 18
output: True
```
""",
        "test_cases": """
test_cases = [
    [[[2, 4, 8, 9, 12, 13, 16, 18], 18], True],
    [[[i for i in range(5_000_000)], 45], True],
    [[[i for i in range(5_000_000)], 5_000_000], False],
]
""",
        "title": "Value in array",
        "difficulty": "Easy",
    },
    41: {
        "markdown": """
### Merge sort
Given an array of integers, use merge sort algorithm to return an array of all the integers sorted in non decreasing order.

### Example
```
input: [8, 2, 4, 9, 12, 18, 16]
output: [2, 4, 8, 9, 12, 13, 16, 18]
```
""",
        "test_cases": """
test_cases = [
    [[[8, 2, 4, 9, 12, 18, 16]], [2, 4, 8, 9, 12, 13, 16, 18]],
    [[[i for i in range(100_000, -1, -1)]], [i for i in range(100_001)]],
]
""",
        "title": "Merge sort",
        "difficulty": "Easy",
    },
    42: {
        "markdown": """
### Heap sort
Given an array of integers, use heap sort algorithm to return an array of all the integers sorted in non decreasing order.

### Example
```
input: [8, 2, 4, 9, 12, 18, 16]
output: [2, 4, 8, 9, 12, 13, 16, 18]
```
""",
        "test_cases": """
test_cases = [
    [[[8, 2, 4, 9, 12, 18, 16]], [2, 4, 8, 9, 12, 13, 16, 18]],
    [[[i for i in range(100_000, -1, -1)]], [i for i in range(100_001)]],
]
""",
        "title": "Heap sort",
        "difficulty": "Easy",
    },
    43: {
        "markdown": """
### Quick sort
Given an array of integers, use quick sort algorithm to return an array of all the integers sorted in non decreasing order.

### Example
```
input: [8, 2, 4, 9, 12, 18, 16]
output: [2, 4, 8, 9, 12, 13, 16, 18]
```
""",
        "test_cases": """
test_cases = [
    [[[8, 2, 4, 9, 12, 18, 16]], [2, 4, 8, 9, 12, 13, 16, 18]],
    [[[i for i in range(100_000, -1, -1)]], [i for i in range(100_001)]],
]
""",
        "title": "Quick sort",
        "difficulty": "Easy",
    },
    44: {
        "markdown": """
### Smaller to the right
Given an integer array nums, return an integer array counts where counts[i] is the number of smaller elements to the right of nums[i].

### Example
```
input: [5, 2, 2, 6, 1]
output: [3, 1, 1, 1, 0]

input: [-1, -1]
output: [0, 0]
```
""",
        "test_cases": """
test_cases = [
    [[[5, 2, 2, 6, 1]], [3, 1, 1, 1, 0]],
    [[[-1, -1]], [0, 0]],
    [[[8, 2, 4, 9, 12, 18, 16]], [2, 0, 0, 0, 0, 1, 0]],
    [[[i for i in range(100_000, -1, -1)]], [0 for i in range(100_001)]],
]
""",
        "title": "Smaller to the right",
        "difficulty": "Hard",
    },
}
