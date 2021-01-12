import datetime as dt

def process_shifts(path_to_shifts):
    """Reads a file containing the shifts of workers including start time, end time, break info and wage.
    Returns a dict of cost of wages for each hour in the format of:
    "10:00": 100
    """
    shifts = {}

    for i in range(9, 24):
        shifts['{}:00'.format(i)] = 0

    break_notes = []
    end_time = []
    pay_rate = []
    start_time = []
    proc_btime_notes = []
    breaktime_start = []
    breaktime_finish = []
    proc_btime_start = []
    proc_btime_finish = []

    with open(path_to_shifts, 'r') as file1:
        lines = file1.readlines()
        lines_list = lines[1:]      # remove first list of words

    for line in lines_list:
        a, b, c, d = line.split(',')
        break_notes.append(a)
        end_time.append(b)
        pay_rate.append(float(c))
        start_time.append(d[:5])

    for string in break_notes:
        proc_btime = ''
        for char in string:
            if char in '0123456789.-':
                proc_btime += char
        proc_btime_notes.append(proc_btime)

    for i in proc_btime_notes:
        x, y = i.split('-')
        breaktime_start.append(x)
        breaktime_finish.append(y)

    for i in breaktime_start:
        if '.' not in i:
            if len(i) == 1:
                proc_start_time = dt.datetime(year=2020, month=1, day=8, hour=int(i) + 12)
            else:
                proc_start_time = dt.datetime(year=2020, month=1, day=8, hour=int(i))
        else:
            x, y = i.split('.')
            if len(x) == 1:
                proc_start_time = dt.datetime(year=2020, month=1, day=8, hour=int(x) + 12, minute=int(y))
            else:
                proc_start_time = dt.datetime(year=2020, month=1, day=8, hour=int(x), minute=int(y))
        proc_btime_start.append(proc_start_time.strftime('%H:%M'))

    for i in breaktime_finish:
        if '.' not in i:
            if len(i) == 1:
                proc_finish_time = dt.datetime(year=2020, month=1, day=8, hour=int(i) + 12)
            else:
                proc_finish_time = dt.datetime(year=2020, month=1, day=8, hour=int(i))
        else:
            x, y = i.split('.')
            if len(x) == 1:
                proc_finish_time = dt.datetime(year=2020, month=1, day=8, hour=int(x) + 12, minute=int(y))
            else:
                proc_finish_time = dt.datetime(year=2020, month=1, day=8, hour=int(x), minute=int(y))
        proc_btime_finish.append(proc_finish_time.strftime('%H:%M'))

    time = 9
    for start, finish, break_start, break_finish, pay in zip(start_time, end_time, proc_btime_start, proc_btime_finish, pay_rate):
        while time < 24:
            if time < int(start[:2]):
                time += 1
            elif int(start[:2]) <= time <= int(break_start[:2]):
                if time < int(break_start[:2]):
                    shifts['{}:00'.format(time)] += pay
                    time += 1
                else:
                    if int(break_start[:2]) == int(break_finish[:2]):
                        shifts['{}:00'.format(time)] += (((int(break_start[3:]) / 60) * pay) + (((60 - int(break_finish[3:]))/60)*pay))
                        time += 1
                    else:
                        shifts['{}:00'.format(time)] += (int(break_start[3:]) / 60) * pay
                        time += 1
            # elif int(break_start[:2]) < time < int(break_finish[:2]):             not needed, happens below
            #     time += 1
            elif int(break_start[:2]) < time <= int(break_finish[:2]):
                if int(break_start[:2]) < time < int(break_finish[:2]):
                    time += 1
                else:
                    shifts['{}:00'.format(time)] += ((60 - int(break_finish[3:])) / 60) * pay
                    time += 1
            elif int(break_finish[:2]) < time < int(finish[:2]):
                shifts['{}:00'.format(time)] += pay
                time += 1
            elif time == int(finish[:2]):
                shifts['{}:00'.format(time)] += (int(finish[3:]) / 60) * pay
                time += 1
            else:
                time += 1
        else:
            time = 9

    return shifts


def process_sales(path_to_sales):
    """Reads a csv file containing transactions of a business.
    Returns a dict of total sales for each hour of trading."""
    sales = {}
    time = []
    profit = []

    for i in range(9, 24):
        sales['{}:00'.format(i)] = 0

    with open(path_to_sales, 'r') as file2:
        lines = file2.readlines()
        line_list = lines[1:]

    for line in line_list:
        x, y = line.split(',')
        time.append(float(y[:2]))
        profit.append(float(x))

    loc = 0
    for hour in range(10, 25):
        a = time.count(hour)

        if loc < len(profit):
            total = profit[loc]
        else:
            break

        if a > 1:
            for i in range(1, a):
                total += profit[loc + i]
            loc += a
            sales['{}:00'.format(hour)] = total
        elif a == 1:
            loc += 1
            sales['{}:00'.format(hour)] = total
        else:
            sales['{}:00'.format(hour)] = 0
    return sales

def compute_percentage(shifts, sales):
    """
    :param shifts:
    :type shifts: dict
    :param sales:
    :type sales: dict
    :return: A dictionary with time as key (string) with format %H:%M and
    percentage of labour cost per sales as value (float),
    If the sales are null, then return -cost instead of percentage
    For example, it should be something like :
    {
        "17:00": 20,
        "22:00": -40,
    }
    :rtype: dict
    """
    percentages = {}
    for i in range(9, 24):
        if sales['{}:00'.format(i)] == 0:
            a = - (shifts['{}:00'.format(i)])
        else:
            a = (sales['{}:00'.format(i)] / shifts['{}:00'.format(i)]) * 100
        percentages['{}:00'.format(i)] = a

    return percentages

def best_and_worst_hour(percentages):
    """
    Args:
    percentages: output of compute_percentage
    Return: list of strings, the first element should be the best hour,
    the second (and last) element should be the worst hour. Hour are
    represented by string with format %H:%M
    e.g. ["18:00", "20:00"]

    """
    costs = []
    for i in range(9, 24):
        costs.append(percentages['{}:00'.format(i)])

    best = max(costs)
    worst = min(costs)

    best_index = costs.index(best) + 9
    worst_index = costs.index(worst) + 9

    best_worst = ["{}:00".format(best_index), "{}:00".format(worst_index)]

    return best_worst

def main(path_to_shifts, path_to_sales):

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour

if __name__ == '__main__':
    # Can be used to test code
    path_to_sales = "transactions.csv"
    path_to_shifts = "work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)
    shifts = process_shifts(path_to_shifts)
    sales = process_sales(path_to_sales)
    percentages = compute_percentage(shifts, sales)
