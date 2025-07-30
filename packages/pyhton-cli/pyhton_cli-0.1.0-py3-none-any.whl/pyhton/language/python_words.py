# first verion, contains only very simple words

KEYWORDS = {
    "def",  # function definition
    "endfunc",  # end function definition
    "return",  # return statement
    "if",  # if statement
    "elif",
    "else",
    "endif",  # end if statement
    "and",  # logical operators
    "or",
    "not",
    "True",  # boolean true
    "False",  # boolean false
    "for",
    "in",
    "endfor",
    "while",
    "endwhile",
}

BUILTINS = {
    "print",  # print function
    "range",  # range function
}

ALL_WORDS = KEYWORDS | BUILTINS
