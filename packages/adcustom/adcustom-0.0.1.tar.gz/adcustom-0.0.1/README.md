# adcustom

A custom Python module developed by Amit Dutta, providing a collection of useful mathematical, string, and matrix manipulation functions.

## Installation

You can install `adcustom` using pip:

```bash
pip install adcustom

Usage
Here's how you can use the functions in the adcustom module:

---------------------------------------------------------------
import adcustom as c

# Example: Addition
result = c.add(5, 3)
print(f"5 + 3 = {result}")

# Example: Check Prime
is_prime = c.check_prime(17)
print(f"Is 17 prime? {is_prime}")

# Example: Matrix Addition
matrix1 = [[1, 2], [3, 4]]
matrix2 = [[5, 6], [7, 8]]
sum_matrix = c.matrix_addition(matrix1, matrix2)
print("Matrix Sum:\n", sum_matrix)

# Get help on the module
help_info = c.help()
print(help_info)
---------------------------------------------------------------

Available Functions : 
---------------------

check_prime(num): Checks if an integer is prime.

factorial(num): Calculates the factorial of a non-negative integer.

permudation(total, chosen): Calculates permutations.

combination(total, chosen): Calculates combinations.

string_reverse(text): Reverses a string.

matrix_addition(mat1, mat2): Adds two matrices.

matrix_multiplication(mat1, mat2): Multiplies two matrices.

matrix_transpose(mat): Transposes a matrix.

determinant_value(mat): Calculates the determinant of a square matrix (1x1, 2x2, 3x3).

mean(data_list): Calculates the mean of a list of numbers.

median(data_list): Calculates the median of a list of numbers.

mode(data_list): Calculates the mode(s) and their frequency.

help(): Provides detailed help about the module and its functions.

Developed by Amit Dutta.
Thank you for using this module!