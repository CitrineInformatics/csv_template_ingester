import csv
import argparse
import random

def generate_csv(rows, columns):

    for r in range(rows):
        generated_row = [''.join(random.choice('0123456789ABCDEF') for i in range(16))]

        for i in range(columns):
            generated_row.append(random.randint(0,100000))

        yield generated_row


def generate_headers(columns):

    headers = ['NAME']

    for i in range(columns):
        headers.append('PROPERTY: Sample Property {} (Unit)'.format(i))

    return headers


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--rows', help='Number of rows required')
    parser.add_argument('-c', '--columns', help='Number of columns required')

    args = parser.parse_args()

    csv_output = generate_csv(int(args.rows), int(args.columns))

    with open('test_file-{}-{}.csv'.format(args.rows, args.columns), 'w') as output_file:
        writer = csv.writer(output_file)

        writer.writerow(generate_headers(int(args.columns)))
        for row in csv_output:
            writer.writerow(row)
