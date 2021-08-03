# keep-to-markdown

A script to convert Google Keep notes into markdown files, for Linux, Mac, and Windows.

**Requirements**

- Python 3.x
- Google Takeout notes as Json (See [How to download your Google data](https://support.google.com/accounts/answer/3024190))

**Example**

```
> python keep-to-markdown.py -i Takeout/Keep/

arguments:
  -i PATH       Relative path to the Google Keep data folder

optional arguments:
  -h, --help    Show this help message and exit
  -t            Use subfolders for tags instead of YAML front-matter
```

The script outputs to a `notes` directory. Images will be stored in `notes/resources`.

If the `-t` flag is included, the first tag (if present) of each note will be used to create a subfolder. (e.g. `notes/code_snippets` and `notes/code_snippets/resources`)

Other data is extracted and written as YAML front-matter:

- title
- tags (if the `-t` flag isn't specified)
- text content
- task list
- web links
- images

## Example

Example of a converted markdown note:

```markdown
---
title: <Title>
date: <Date> (optional, if title is set)
tags: <tag1>;<tag2>;
---

<textContent>
Example Text ...

<listContent>
*Tasklist*:
- [ ] task1
- [x] task2

<annotations>
*Weblinks:* [link1](http//..); [link2](http://..);

<attachments>
*Attachments:* ![image](resource/image.jpg)
```

A note's title will be used for its filename. If there is no title available the created timestamp will be used.

## Future features

- [x] OS compatible
- [ ] save modified Timestamp by default
- [ ] use Google keep colors
- [ ] usability for Joplin import
