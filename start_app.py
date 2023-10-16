from pathlib import Path
from xml.etree.ElementTree import fromstring, ElementTree
import base64

# Файл для обработки:
src_file = "azk2_xml.log"
# Папка для вывода результатов:
result_dir = "c:/tmp/100packets/docNumber_documentId/"


def get_substring_by_word(text, word, right_limiter=' '):
	len_word = len(word)
	pos_word = text.find(word)
	end_word = text[pos_word+len_word:].find(right_limiter)
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
		split_lines = line.split(splitter)
		# Убираем первый элемент из списка, потому что там просто splitter:
		split_lines.pop(0)
		# Создадим папку для файлов документа с именем по шаблону "docNumber_documentId":
		dirname = f'{result_dir}/{doc_number}_{document_id}'
		filename = f'doc_{doc_number}_{document_id}.xml'
		Path(dirname).mkdir(parents=True, exist_ok=True)
		i = 0
		attaches = []
		for sline in split_lines:
			i += 1
			if i == 1:
				# Сюда попадает XML-представление документа
				filename = f'doc_{doc_number}_{document_id}.xml'
				out_file = open(f'{dirname}/{filename}', 'w', encoding='utf-8')
				out_file.write(f'{splitter}{sline}')
			if i == 2:
				# Сюда попадает XML-представление сводной информации о вложениях документа - тут нужно извлечь имена файлов
				attach_idx = 0
				attach_filename = []
				tree = ElementTree(fromstring(f'{splitter}{sline}'))
				root = tree.getroot()
				for child in root:
					if child.tag == 'ATTACH':
						attach_idx += 1
						filename = f'{child.attrib["NAME"]}'
						filesize = f'{child.attrib["FILE_SIZE"]}'
						attach_filename = [attach_idx, filename, filesize]
						attaches.append(attach_filename)
			if i > 2:
				# Сюда попадает XML с содержимым вложения
				line = f'{splitter}{sline}'
				body = get_substring_by_word(line, '<BODY><![CDATA[', ']]></BODY></DOCUMENT>')
				data = base64.b64decode(body)
				filename = attaches[i-3][1]
				filesize = attaches[i-3][2]
				# Метод, которым получена информация о содержимом вложений несовершенен - метод возвращает первые 1024000 байта содержимого, соответственно, содержимого вложений, размер которых больше этого размера, просто нет в логе, поэтому к началу их имени файла дописываем слова "скачать_вручную_", чтобы потом попросить человека загрузить эти файлы руками в папки:
				if int(filesize) <= 1024000:
					# Если размер файла меньше или равен 1024000 байт, то с ними будет все в порядке, записываем их, как полноценные файлы:
					out_file = open(f'{dirname}/{filename}', 'wb')
					out_file.write(data)
				else:
					out_file = open(f'{dirname}/скачать_вручную_{filename}', 'w', encoding='utf-8')
					out_file.write(line)
