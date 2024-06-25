# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 11:48:21 2024

@author: User
"""
import streamlit as st
import numpy as np

# Function to create an empty Sudoku grid
def create_empty_grid():
    return np.zeros((9, 9), dtype=int)

# Function to display the Sudoku grid
def display_grid(grid):
    for i in range(9):
        for j in range(9):
            st.write(grid[i][j], end=' ')
        st.write()

# Main function to run the Sudoku game app
def main():
    st.title('Sudoku Game App')
    st.write('Fill in the numbers to solve the Sudoku puzzle!')
    
    grid = create_empty_grid()
    
    display_grid(grid)

if __name__ == '__main__':
    main()

