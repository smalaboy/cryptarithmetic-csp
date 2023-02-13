from cryptarithmetic_bt_solver import CryptArithmeticBTSolver
from cryptarithmetic_ortools_solver import CryptArithmeticOrtoolsSolver


"""
Main programs.
Provides a command line interface to test the algorithms
"""

while True:
    print()
    print('-'*15, 'OPTIONS', '-'*15)
    print('0 - Exit')
    print('1 - ortools_solver')
    print('2 - Backtrack')
    print('3 - Forward checking')
    print()

    try:
        option = int(input('Choisir: '))
    except ValueError:
        print('Wrong input')
        continue
    if option not in [0, 1, 2, 3]:
        print('Wrong option')
        continue
    if option == 0:
        break
    words = input('Enter words separated by a space. (For example: POINT ZERO ): \n').upper().split()
    answer = input('Enter answer. (For example: ENERGY): \n').upper()

    if option in [2, 3]:
        show_logs = input('Show logs ? Y or N: \n')
        if show_logs.strip().upper() in ['Y', 'YES']:
            show_logs = CryptArithmeticBTSolver.SHOW_LOGS
        else:
            show_logs = CryptArithmeticBTSolver.NO_LOGGING
        var_ordering = input('Variables order ? deg or random [default is deg]: \n').lower()
        if var_ordering.lower() == 'random':
            var_ordering = 'random'
        else:
            var_ordering = 'deg'
        algo = 'fc' if option == 3 else 'bt'
        solver = CryptArithmeticBTSolver(words=words, answer=answer)
        solver.logging_level = show_logs
        solver.solve(solver=algo, variables_ordering=var_ordering)

        solver.print_solution()
        solver.print_stats()
    elif option == 1:
        solver = CryptArithmeticOrtoolsSolver(words=words, answer=answer)
        solver.solve()
        solver.print_solution()
        solver.print_stats()
    else:
        print('Wrong option')
        continue
