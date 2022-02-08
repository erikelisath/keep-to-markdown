import os
import sys
import platform
import glob
import json
from datetime import datetime as dt
from shutil import copy2 as cp
import mimetypes
import argparse


def copy_file(file, path, notespath):
    try:
        cp(f'{path}{file}', os.path.join(notespath, 'resources'))
    except FileNotFoundError:
        print(f'File "{file}" not found in {path}')
        return False
    else:
        return True

# remove illegal chars for current OS
def clean_title(title) -> str:
    ostype = platform.system()
    if ostype == 'Linux':
        title = title.replace('/', '_')
    elif ostype == 'Darwin':
        title = title.replace(':', ' ')
        title = title.replace('\\', '_').replace('/', '_').replace('|', '_')
    elif ostype == 'Windows':
        title = title.replace('\\', '_').replace('/', '_').replace('|', '_')
        title = title.replace('<', '-').replace('>', '-').replace(':', ' ')
        title = title.replace('?', '').replace('"', '').replace('*', '')
        title = title.replace('\n', '')
    return title

def read_annotations(list) -> str:
    annotations_list = '*Weblinks:*'
    for entry in list:
        if entry['source'] == 'WEBLINK':
            title = entry['title']
            url = entry['url']
            annotations_list += f' [{title}]({url});'
    return annotations_list

def read_attachments(list, path, notespath, linktype) -> str:
    attachments_list = '*Attachments:*\n'
    for entry in list:
        if 'image' in entry['mimetype']:
            image = entry['filePath']
            if copy_file(image, path, notespath) is False:
                # If the file could not be found,
                # it will be checked if the file can be found
                # another file format.
                # Google used '.jpeg' instead of '.jpg'
                image_type = mimetypes.guess_type(f'{path}{image}')
                types = mimetypes.guess_all_extensions(image_type[0])
                for type in types:
                    if type in image:
                        image_name = image.replace(type, '')
                        for t in types:
                            if len(glob.glob(f'{path}{image_name}{t}')) > 0:
                                image = f'{image_name}{t}'
                                print(f'Found "{image}"')
                                copy_file(image, path, notespath)
            respath = os.path.join('resources','')
            if linktype == 'm':
                attachments_list += f'![{image}]({respath}{image})\n'
            if linktype == 'w':
                attachments_list += f'![[{image}]]\n' # for Obsidian
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

def format_tags(tags) -> str:
    tag_list = 'tags:'
    for tag in tags:
        tag_list += f' {tag};'
    return tag_list

def read_write_notes(args):
    path = args.i
    if path[-1]!='/' and path[-1]!='\\':  # path should end on a slash
        path+='/'

    conv_folders = args.t
    linktype = args.linktype
    jsonpath = os.path.join(path, '')
    notes = glob.glob(f'{jsonpath}*.json')

    for note in notes:
        with open(note, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            timestamp = data['userEditedTimestampUsec']
            tags = []
            try:
                tags = [label['name'] for label in data['labels']]
            except KeyError:
                    print('No tags available.')

            if timestamp == 0:
                iso_datetime = dt.now().strftime('%Y%m%dT%H%M%S_edited')
            else:
                iso_datetime = dt.fromtimestamp(timestamp/1000000).strftime('%Y%m%dT%H%M%S')

            # get filename by title
            if data['title'] != '':
                title = str(data['title'])
                filename = clean_title(title)
                if len(filename) > 100:
                    filename = filename[0:99]
            else:
                title = iso_datetime
                filename = title

            # create folders by tags
            if conv_folders and len(tags):
                subfolder = tags[0]
            else:
                subfolder = ''
            notespath = os.path.join('notes', subfolder, '')

            # check if filename exists
            if os.path.exists(f'{notespath}{filename}.md'):
                print(f'Existing file found: {notespath}{filename}.md')
                # increment duplicate number, if already exists
                dup_num = 1
                while(os.path.exists(f'{notespath}{filename}({dup_num}).md')):
                    print(f'File "{notespath}{filename}({dup_num}).md" exists, increment number...')
                    dup_num = dup_num+1

                filename = f'{filename}({dup_num})'
                print(f'New filename: {filename}.md')

            # create path to notes
            if not os.path.exists(notespath):
                os.makedirs(notespath)
                os.makedirs(os.path.join(notespath, 'resources'))
                print(f'Create tag and resources subfolder: {subfolder}')

            # create Markdown file
            print(f'Convert "{title}" to markdown file.')
            with open(f'{notespath}{filename}.md', 'w', encoding='utf-8') as mdfile:
                mdfile.write(f'---\n')
                mdfile.write(f'title: {title}\n')
                if (title != iso_datetime):
                    mdfile.write(f'date: {iso_datetime}\n')
                # add tags
                if(tags and not conv_folders):
                    mdfile.write(f'{format_tags(tags)}\n')
                mdfile.write(f'---\n\n')
                # add text content
                try:
                    textContent = data['textContent']
                    mdfile.write(f'{textContent}\n\n')
                except KeyError:
                    print('No text content available.')
                # add tasklist
                try:
                    tasklist = read_tasklist(data['listContent'])
                    mdfile.write(f'{tasklist}\n\n')
                except KeyError:
                    print('No tasklist available.')
                # add annotations
                try:
                    annotations = read_annotations(data['annotations'])
                    mdfile.write(f'{annotations}')
                except KeyError:
                    print('No annotations available.')
                # add attachments
                try:
                    attachments = read_attachments(data['attachments'], path, notespath, linktype)
                    mdfile.write(f'{attachments}')
                except KeyError:
                    print('No attachments available.')

def create_folder():
    try:
        workpath = os.path.join('notes', 'resources')
        if not os.path.exists(workpath):
            os.makedirs(workpath)
            print('Create folder "notes" - home of markdown files.')
    except OSError:
        print('Creation of folders failed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converting Google Keep notes to markdown files.')
    parser.add_argument('-i', metavar='PATH', required=True, help='The path to the Takeout folder.')
    parser.add_argument('-t', action='store_true', help='Use folders instead of front-matter for tags.')
    parser.add_argument('-l', '--linktype', choices=['m', 'w'], nargs='?', const='m', help='Image link type: m=Markdown, w=Wikistyle')
    args = parser.parse_args()

    create_folder()
    try:
        read_write_notes(args)
    except IndexError:
        print('Please enter a correct path!')
