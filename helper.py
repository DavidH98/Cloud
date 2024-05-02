import datetime
import io
import mimetypes
import os
import magic

def format_file_data(file_data):
    formatted_data = []

    for file_tuple in file_data:
        file_name, file_size_in_bytes, file_date, file_id = file_tuple

        # Convert file size to KB, MB, or GB
        size_in_kb = file_size_in_bytes / 1024.0
        size_in_mb = size_in_kb / 1024.0
        size_in_gb = size_in_mb / 1024.0

        if size_in_gb >= 1:
            formatted_size = f"{size_in_gb:.2f}GB"
        elif size_in_mb >= 1:
            formatted_size = f"{size_in_mb:.2f}MB"
        elif size_in_kb >= 1:
            formatted_size = f"{size_in_kb:.2f}KB"
        else:
            formatted_size = f"{file_size_in_bytes}B"

        formatted_file_name = file_name
        formatted_datetime = file_date.strftime("%Y-%#m-%#d, %H:%M")

        # Create a dictionary with formatted data
        formatted_dict = {
            'name': formatted_file_name,
            'size': formatted_size,
            'date': formatted_datetime,
            'file_id': file_id,
            'category': categorize_file(formatted_file_name)
        }

        formatted_data.append(formatted_dict)

    return formatted_data

def categorize_file(file_name):
    # Extract the file extension
    _, file_extension = os.path.splitext(file_name.lower())

    # Define lists of supported extensions for each category
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg','.jfif']
    document_extensions = ['.doc', '.docx', '.pdf', '.txt', '.ppt', '.xls', '.xlsx', '.pptx']
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv']

    # Categorize the file based on its extension
    if file_extension in image_extensions:
        return 'mdi-file-image'
    elif file_extension in document_extensions:
        return 'mdi-file-document'
    elif file_extension in video_extensions:
        return 'mdi-file-video'
    else:
        return 'mdi-file'
    
def create_file_object(file_data, file_name):
    mime = magic.Magic()
    mime_type = mime.from_buffer(file_data)

    # If MIME type is not recognized, try to determine based on file extension
    if not mime_type:
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = 'application/octet-stream'

    file_obj = io.BytesIO(file_data)

    return file_obj, mime_type

def convert_size(size_str):
    size_str = size_str.upper()
    unit_mapping = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3, 'TB': 1024 ** 4}

    try:
        size, unit = size_str[:-2], size_str[-2:]
        size = float(size)
        if unit not in unit_mapping:
            raise ValueError("Invalid unit. Supported units are B, KB, MB, GB, TB.")
        
        bytes_size = int(size * unit_mapping[unit])
        return bytes_size
    except (ValueError, IndexError):
        raise ValueError("Invalid size format. Example formats: '100B', '1KB', '3MB', '4GB'.")

def calc_storage(files):
    storage = {'image':[0,0],'document':[0,0],'video':[0,0],'other':[0,0], 'total':[0,0]}
    for file in files:
        if file['category'].replace("mdi-","") == 'file':
            storage['other'][0] += convert_size(file['size'])
            storage['other'][1] += convert_size(file['size'])
        else:
            storage[file['category'].replace("mdi-file-","")][0] += convert_size(file['size'])
            storage[file['category'].replace("mdi-file-","")][1] += convert_size(file['size'])
        storage['total'][0] += convert_size(file['size'])
        storage['total'][1] += convert_size(file['size'])
    
    for category, data in storage.items():
        size_in_kb = storage[category][0] / 1024.0
        size_in_mb = size_in_kb / 1024.0
        size_in_gb = size_in_mb / 1024.0
        formatted_size = ""

        if size_in_gb >= 1:
            formatted_size = f"{size_in_gb:.2f}GB"
        elif size_in_mb >= 1:
            formatted_size = f"{size_in_mb:.2f}MB"
        elif size_in_kb >= 1:
            formatted_size = f"{size_in_kb:.2f}KB"
        else:
            formatted_size = f"{storage[category][0]}B"
        
        storage[category][0] = formatted_size

    for category, data in storage.items():
        if category != 'total':
            percentage = (data[1] / storage['total'][1]) * 100 if storage['total'][1] > 0 else 0
            percentage = round(percentage, 2)
            storage[category][1] = percentage

    return storage