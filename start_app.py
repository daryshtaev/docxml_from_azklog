from pathlib import Path

src_file = "azk2_xml.log"


def get_substring_by_word(text, word):
	len_word = len(word)
	pos_word = text.find(word)
	end_word = text[pos_word+len_word:].find(' ')
	result = text[pos_word+len_word:pos_word+len_word+end_word]
	result = result.replace('"', '')
	return result


file_lines = open(src_file, 'r', encoding='utf-8').readlines()
for line in file_lines:
	# Берем только строки про документ:
	line_splitter = '<TASK><DOCUMENT '
	line_splitter_len = len(line_splitter)
	if line[:line_splitter_len] == line_splitter:
		# Убираем теги <TASK>, </TASK> и переносы строк:
		line = line.replace('<TASK>', '').replace('</TASK>', '').replace('\n', '')
		# Вычисляем DOCUMENT_ID:
		document_id = get_substring_by_word(line, ' DOCUMENT_ID=')
		# Вычисляем DOC_NUMBER:
		doc_number = get_substring_by_word(line, ' DOC_NUMBER=')
		# Делим по блокам "<DOCUMENT":
		splitter = '<DOCUMENT '
		split_line = line.split(splitter)
		# Создадим папку для файлов документа с именем по шаблону "docNumber_documentId":
		dirname = f'docNumber_documentId/{doc_number}_{document_id}'
		filename = f'doc_{doc_number}_{document_id}.xml'
		Path(dirname).mkdir(parents=True, exist_ok=True)
		# Создадим в папке файл для документа и заполним его:
		out_file = open(f'{dirname}/{filename}', 'w', encoding='utf-8')
		out_file.write(f'{splitter}{split_line[1]}')
