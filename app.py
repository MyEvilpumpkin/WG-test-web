import io
import json
import math

from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('WG-test-web.html')
    elif request.method == 'POST':
        # Get the files from request
        files = request.files.getlist('text')
        files_data = []
        all_unique_words = set()
        for file in files:
            # Transform file to string
            file_data = [file.filename]
            text = io.StringIO(file.read().decode('UTF-8')).read()
            # Split string to words in lower case
            words = text.lower().split()
            # Get unique words
            unique_words = set(words)
            file_data.append(unique_words)
            all_unique_words.update(unique_words)
            # Count how many times each word occurs
            words_dict = dict.fromkeys(unique_words, 0)
            for word in words:
                words_dict[word] += 1
            words_count = len(words)

            # Computing tf
            tf_dict = {}
            for word, count in words_dict.items():
                tf_dict[word] = count / float(words_count)
            file_data.append(tf_dict)

            files_data.append(file_data)

        # Computing idf
        n = len(files_data)

        all_idf_dict = dict.fromkeys(all_unique_words, 0.0)
        for file_data in files_data:
            for word in file_data[1]:
                all_idf_dict[word] += 1
        for word, count in all_idf_dict.items():
            all_idf_dict[word] = math.log(n / float(count))

        # Preparing data structure to json converting
        json_files_data = []

        for file_data in files_data:
            json_file_data = [file_data[0], []]

            # Get idf score for words in each document
            idf_dict = {}
            for word in file_data[1]:
                idf_dict[word] = all_idf_dict[word]
            file_data.append(idf_dict)

            # Sort word in each document by idf scores
            sorted_idf_values = sorted(idf_dict.values(), reverse=True)
            sorted_idf_dict = {}

            for value in sorted_idf_values:
                for key in idf_dict.keys():
                    if idf_dict[key] == value and key not in sorted_idf_dict:
                        sorted_idf_dict[key] = idf_dict[key]
                        break

            # Writing data to prepared structure (less or equal 50 words for document)
            i = 0
            for key in sorted_idf_dict.keys():
                if i < 50:
                    json_file_data[1].append([key, '%.4f' % file_data[2][key], '%.4f' % file_data[3][key]])
                    i += 1
            json_files_data.append(json_file_data)

        # return data in json format
        return json.dumps(json_files_data)


if __name__ == '__main__':
    app.run()
