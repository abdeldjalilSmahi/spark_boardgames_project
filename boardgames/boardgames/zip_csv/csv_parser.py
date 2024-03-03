import csv


class CSVParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_info(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                id_index = headers.index('id')

                for row in reader:
                    yield row[id_index]
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")


if __name__ == '__main__':
    csv_parser = CSVParser('../data/boardgames_ranks.csv')
    for id_bhh in csv_parser.get_info():
        print(id_bhh)
