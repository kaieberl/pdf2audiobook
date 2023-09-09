import sys
import tty
import pandas as pd
import termios

OUTPUT_DIR = 'YOUR_OUTPUT_DIR'

label_dict = {
    'h': 'header',
    'b': 'body',
    'c': 'caption',
    'o': 'other'
}


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


# add key 'label' to each element in data
def label_data(data):
    for index, element in data.iterrows():
        # print the text in green
        try:
            print('\033[92m' + element['text'] + '\033[0m')
        except TypeError:
            continue
        print('h: header, b: body, c: caption, o: other, q: quit')
        # user does not have to press enter
        label = getch()
        if label == 'q':
            break
        try:
            data.at[index, 'label'] = label_dict[label]
        except KeyError:
            print('Invalid label')
            label = getch()
            data.at[index, 'label'] = label_dict[label]
    return data


def write_data_to_csv(data, file_path):
    data.to_csv(file_path)


if __name__ == '__main__':
    # load from csv
    df = pd.read_csv('XXXX-001-features.csv')
    df = label_data(df)
    write_data_to_csv(df, 'path/to/your_output.csv')
