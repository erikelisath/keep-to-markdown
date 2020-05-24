import os
import sys
import glob
import json
from datetime import datetime as dt
from shutil import copy2 as cp
import mimetypes


def copy_file(file, path):
    try:
        cp(f'{path}{file}', 'notes/resource/')
    except FileNotFoundError:
        print(f'File "{file}" not found in {path}')
        return False
    else:
        return True

def read_annotations(list) -> str:
    annotations_list = '*Weblinks:*'
    for entry in list:
        if entry['source'] == 'WEBLINK':
            title = entry['title']
            url = entry['url']
            annotations_list += f' [{title}]({url});'
    return annotations_list

def read_attachments(list, path) -> str:
    attachments_list = '*Attachments:*\n'
    for entry in list:
        if 'image' in entry['mimetype']:
            image = entry['filePath']
            if copy_file(image, path) is False:
                # Falls die Datei nicht gefunden werden konnte,
                # wird geprüft ob es die Datei unter einem
                # anderen Dateiformat zufinden ist.
                # Google benutzt '.jpeg' statt '.jpg' -- doof
                image_type = mimetypes.guess_type(f'{path}{image}')
                types = mimetypes.guess_all_extensions(image_type[0])
                for type in types:
                    if type in image:
                        image_name = image.replace(type, '')
                        for t in types:
                            if len(glob.glob(f'{path}{image_name}{t}')) > 0:
                                image = f'{image_name}{t}'
                                print(f'Found "{image}"')
                                copy_file(image, path)
            attachments_list += f'![{image}](resource/{image})\n'
    return attachments_list

def read_tasklist(list) -> str:
    content_list = '*Tasklist:*\n'
    for entry in list:
        text = entry['text']
        if entry['isChecked'] is True:
            content_list += f'- [x] {text}\n'
        else:
            content_list += f'- [ ] {text}\n'
    return content_list

def read_tags(tags) -> str:
    tag_list = 'tags:'
    for entry in tags:
        tag = entry['name']
        tag_list += f' {tag};'
    return tag_list

def read_write_notes(path):
    notes = glob.glob(f'{path}/*.json')
    for note in notes:
        with open(note, 'r') as jsonfile:
            data = json.load(jsonfile)
            timestamp = data['userEditedTimestampUsec']
            if timestamp == 0:
                iso_datetime = dt.now().strftime('%Y-%m-%d %H:%M:%S:%f edited')
            else:
                iso_datetime = dt.fromtimestamp(timestamp/1000000).strftime('%Y-%m-%d %H:%M:%S:%f')

            if data['title'] != '':
                title = str(data['title']).replace('/', '_')
                if len(title) > 100:
                    title = title[0:99]
            else:
                title = iso_datetime

            if not os.path.exists(f'notes/{title}.md'):
                print(f'Convert: {title}')
                with open(f'notes/{title}.md', 'w') as mdfile:
                    mdfile.write(f'title: {title}\n')
                    # add tags
                    try:
                        tags = read_tags(data['labels'])
                        mdfile.write(f'{tags}\n\n')
                    except KeyError:
                        print('No tags aviable.')
                    # add text content
                    try:
                        textContent = data['textContent']
                        mdfile.write(f'{textContent}\n\n')
                    except KeyError:
                        print('No text content aviable.')
                    # add tasklist
                    try:
                        tasklist = read_tasklist(data['listContent'])
                        mdfile.write(f'{tasklist}\n\n')
                    except KeyError:
                        print('No tasklist aviable.')
                    # add annotations
                    try:
                        annotations = read_annotations(data['annotations'])
                        mdfile.write(f'{annotations}')
                    except KeyError:
                        print('No annotations aviable.')
                    # add attachments
                    try:
                        attachments = read_attachments(data['attachments'], path)
                        mdfile.write(f'{attachments}')
                    except KeyError:
                        print('No attachments aviable.')
            else:
                print(f'File "{title}" exists!')

def create_folder():
    try:
        os.makedirs('notes/resource')
        print('Create folder "notes" - home of markdown files.')
    except OSError:
        print('Creation of folders failed.')

if __name__ == '__main__':
    create_folder()
    try:
        read_write_notes(sys.argv[1])
    except IndexError:
        print('Please enter a correct path!')
