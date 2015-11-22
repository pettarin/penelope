#!/usr/bin/env python
# coding=utf-8

"""
Write EPUB dictionaries.

NOTE: this file needs refactoring.
"""

from io import open
import os
import zipfile

from utilities import print_debug
from utilities import print_error
from utilities import print_info
from utilities import create_temp_directory
from utilities import copy_file
from utilities import delete_directory
from utilities import rename_file

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.0.0"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

CONTAINER_TEMPLATE = u"""<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>"""

OPF_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" ?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uuid_id">
 <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="uuid_id" opf:scheme="uuid">%s</dc:identifier>
  <dc:language>%s</dc:language>
  <dc:title>%s</dc:title>
  <dc:creator opf:role="aut">%s</dc:creator>
  <dc:rights>%s</dc:rights>
  <dc:date opf:event="creation">%s-01-01</dc:date>
 </metadata>
 <manifest>
  <item href="style.css" id="css" media-type="text/css" />
  <item href="toc.ncx"   id="ncx" media-type="application/x-dtbncx+xml" />
%s
 </manifest>
 <spine toc="ncx">
%s
 </spine>
</package>"""

MANIFEST_ITEM_TEMPLATE = u"""  <item href="%s" id="%s" media-type="application/xhtml+xml" />"""

SPINE_ITEM_TEMPLATE = u"""  <itemref idref="%s" />"""

NCX_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
 <head>
  <meta name="dtb:uid" content="%s" />
  <meta name="dtb:depth" content="1" />
  <meta name="dtb:totalPageCount" content="0" />
  <meta name="dtb:maxPageNumber" content="0" />
 </head>
 <docTitle>
  <text>%s</text>
 </docTitle>
 <navMap>
%s
 </navMap>
</ncx>"""

NCX_NAVPOINT_TEMPLATE = u""" <navPoint id="n%06d" playOrder="%d">
  <navLabel>
   <text>%s</text>
  </navLabel>
  <content src="%s" />
 </navPoint>"""

CSS_TEMPLATE = u"""@charset "UTF-8";
body {
  margin: 10px 25px 10px 25px;
}  
h1 {
  font-size: 200%;
}
p {
  margin-left: 0em;
  margin-right: 0em;
  margin-top: 0em;
  margin-bottom: 0em;
  line-height: 2em;
  text-align: justify;
}
a, a:focus, a:active, a:visited {
  color: black;
  text-decoration: none;
}
/*
span {
  margin: 0px 10px 0px 10px;
  padding: 2px 2px 2px 2px;
  border: solid 1px black;
}
body.index {
  margin: 10px 50px 10px 50px;
}
body.letter {
  margin: 10px 50px 10px 50px;
}
*/
p.index {
  font-size: 150%;
}
p.letter {
  font-size: 150%;
}

div p {
  margin-left: 25px;
  margin-rigth: 25px;
}

div {
  margin-top: 10px;
  margin-bottom: 10px;
}"""

INDEX_XHTML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
 </head>
 <body class="index">
  <h1>%s</h1>
  <p class="index">
%s
  </p>
 </body>
</html>"""

INDEX_XHTML_LINK_TEMPLATE = u"""   <span><a href=\"%s\">%s</a></span>"""

GROUP_XHTML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
 </head>
 <body>
  <h1>%s</h1>
  <h3>
   <a href="%s">[ Previous ]</a>
   <a href="index.xhtml">[ Index ]</a>
   <a href="%s">[ Next ]</a>
  </h3>
%s
 </body>
</html>"""

GROUP_XHTML_WORD_TEMPLATE = u"""   <span>%s</span>"""

GROUP_XHTML_WORD_DEFINITION_TEMPLATE = u"""  <div>
   <h4>%s</h4>
   <p>%s</p>
  </div>"""

def read(dictionary, args, input_file_paths):
    print_error("Read function not implemented for EPUB dictionaries")
    return None

def write(dictionary, args, output_file_path):
    def get_prefix(headword, length):
        lowercased = headword.lower()
        if ord(lowercased[0]) < 97:
            return u"SPECIAL"
        if len(lowercased) < length:
            return lowercased
        return lowercased[0:length]

    def html_escape(s):
        x = s
        x = x.replace("&", "&amp;")
        x = x.replace('"', "&quot;")
        x = x.replace("'", "&apos;")
        x = x.replace(">", "&gt;")
        x = x.replace("<", "&lt;")
        return x

    # result to be returned
    result = None

    # create tmp directory
    cwd = os.getcwd()
    tmp_path = create_temp_directory()
    os.chdir(tmp_path)

    # get the basename
    files_to_compress = []
    base = os.path.basename(output_file_path)
    if base.endswith(".epub"):
        base = base[:-5]

    # create directories
    os.makedirs(u"META-INF")
    os.makedirs(u"OEBPS")

    # create mimetype
    file_mimetype_rel_path = u"mimetype"
    file_mimetype_obj = open(file_mimetype_rel_path, "wb")
    file_mimetype_obj.write(u"application/epub+zip")
    file_mimetype_obj.close()

    # create container.xml
    file_container_rel_path = u"META-INF/container.xml"
    file_container_obj = open(file_container_rel_path, "wb")
    file_container_obj.write(CONTAINER_TEMPLATE.encode("utf-8"))
    file_container_obj.close()
    files_to_compress.append(file_container_rel_path)

    # sort by headword, optionally ignoring case
    dictionary.sort(by_headword=True, ignore_case=args.sort_ignore_case)

    # create groups
    all_entries = []
    groups = {}
    i = 0
    for index in dictionary.entries_index_sorted:
        entry = dictionary.entries[index]
        all_entries.append(entry)
        prefix = get_prefix(entry.headword, int(args.epub_group_prefix_length))
        if not prefix in groups:
            groups[prefix] = []
        groups[prefix].append(i)
        i += 1

    # merge small groups
    merged_groups = []
    keys = sorted(groups.keys())
    accumulator_key = keys[0]
    accumulator = groups[accumulator_key]
    for key in keys[1:]:
        if (len(accumulator) >= int(args.epub_merge_group_size)) or (key[0] != accumulator_key[0]):
            merged_groups.append([accumulator_key, accumulator])
            accumulator_key = key
            accumulator = groups[accumulator_key]
        else:
            accumulator += groups[key]
    merged_groups.append([accumulator_key, accumulator])

    # create xhtml files
    manifest_items = []
    spine_items = []
    ncx_items = []

    i = 1
    file_xhtml_rel_path_base = u"index.xhtml"
    file_xhtml_rel_path = u"OEBPS/%s" % file_xhtml_rel_path_base
    file_xhtml_obj = open(file_xhtml_rel_path, "wb")
    j = 2
    group_links = []
    for group in merged_groups:
        key = group[0]
        group_links.append(INDEX_XHTML_LINK_TEMPLATE % (u"g%06d.xhtml" % (j), key))
        j += 1
    xhtml_content = INDEX_XHTML_TEMPLATE % (
        args.title,
        args.title,
        " &#8226;\n".join(group_links)
    )
    file_xhtml_obj.write(xhtml_content.encode("utf-8"))
    file_xhtml_obj.close()
    files_to_compress.append(file_xhtml_rel_path)
    manifest_items.append(MANIFEST_ITEM_TEMPLATE % (file_xhtml_rel_path_base, file_xhtml_rel_path_base))
    spine_items.append(SPINE_ITEM_TEMPLATE % (file_xhtml_rel_path_base))
    ncx_items.append(NCX_NAVPOINT_TEMPLATE % (i, i, "Table of Contents", file_xhtml_rel_path_base))

    i = 2
    for group in merged_groups:
        key = group[0]
        entry_indices = group[1]
        file_xhtml_rel_path_base = u"g%06d.xhtml" % i
        file_xhtml_rel_path = u"OEBPS/%s" % file_xhtml_rel_path_base
        file_xhtml_obj = open(file_xhtml_rel_path, "wb")
        page_title = u"%s" % (key)
        if i == 2:
            prev_path = u"#"
        else:
            prev_path = u"g%06d.xhtml" % (i - 1)
        if i + 1 < len(merged_groups) + 2:
            next_path = u"g%06d.xhtml" % (i + 1)
        else:
            next_path = u"#"
        words = []
        for entry_index in entry_indices:
            if args.epub_output_definitions:
                headword = all_entries[entry_index].headword
                if args.epub_escape_strings:
                    headword = html_escape(headword)
                definition = all_entries[entry_index].definition
                if args.epub_escape_strings:
                    definition = html_escape(definition)
                words.append(GROUP_XHTML_WORD_DEFINITION_TEMPLATE % (headword, definition))
            else:
                headword = all_entries[entry_index].headword
                if args.epub_escape_strings:
                    headword = html_escape(headword)
                words.append(GROUP_XHTML_WORD_TEMPLATE % (headword))
        if args.epub_output_definitions:
            words = u"\n".join(words)
        else:
            words = u"<p>%s</p>" % (u" &#8226;\n".join(words))
        xhtml_content = GROUP_XHTML_TEMPLATE % (
            page_title,
            page_title,
            prev_path,
            next_path,
            words
        )
        file_xhtml_obj.write(xhtml_content.encode("utf-8"))
        file_xhtml_obj.close()
        files_to_compress.append(file_xhtml_rel_path)
        manifest_items.append(MANIFEST_ITEM_TEMPLATE % (file_xhtml_rel_path_base, file_xhtml_rel_path_base))
        spine_items.append(SPINE_ITEM_TEMPLATE % (file_xhtml_rel_path_base))
        ncx_items.append(NCX_NAVPOINT_TEMPLATE % (i, i, key, file_xhtml_rel_path_base))
        i += 1

    manifest_items = "\n".join(manifest_items)
    spine_items = "\n".join(spine_items)
    ncx_items = "\n".join(ncx_items)

    # create content.opf
    file_opf_rel_path = u"OEBPS/content.opf"
    file_opf_obj = open(file_opf_rel_path, "wb")
    opf_content = OPF_TEMPLATE % (
        args.identifier,
        args.language_from,
        args.title,
        args.author,
        args.copyright,
        args.year,
        manifest_items,
        spine_items
    )
    file_opf_obj.write((opf_content).encode("utf-8"))
    file_opf_obj.close()
    files_to_compress.append(file_opf_rel_path)

    # create toc.ncx
    file_ncx_rel_path = u"OEBPS/toc.ncx"
    file_ncx_obj = open(file_ncx_rel_path, "wb")
    ncx_content = NCX_TEMPLATE % (
        args.identifier,
        args.title,
        ncx_items
    )
    file_ncx_obj.write((ncx_content).encode("utf-8"))
    file_ncx_obj.close()
    files_to_compress.append(file_ncx_rel_path)

    # create style.css
    file_css_rel_path = u"OEBPS/style.css"
    file_css_obj = open(file_css_rel_path, "wb")
    file_css_obj.write((CSS_TEMPLATE).encode("utf-8"))
    file_css_obj.close()
    files_to_compress.append(file_css_rel_path)

    # TODO copy cover
    #file_cover_rel_path = u"cover"
    #file_cover_path = os.path.join(tmp_path, file_cover_rel_path)
    #if args.cover_path is not None:
    #    if os.path.exists(args.cover_path):
    #        file_cover_rel_path = os.path.basename(args.cover_path)
    #        file_cover_path = os.path.join(tmp_path, file_cover_rel_path)
    #        copy_file(args.cover_path, file_cover_path)
    #    else:
    #        print_error("Unable to read cover file '%s'" % (args.cover_path))
    #else:
    #    print_error("No cover image file specified: generating EPUB without cover")
    #    print_error("Use --cover-path to specify a cover image file")

    # create output file
    output_file_obj = zipfile.ZipFile(output_file_path, "w", compression=zipfile.ZIP_DEFLATED)
    output_file_obj.write(file_mimetype_rel_path, compress_type=zipfile.ZIP_STORED)
    for file_to_compress in files_to_compress:
        output_file_obj.write(file_to_compress)
    output_file_obj.close()
    os.chdir(cwd)
    result = [output_file_path]

    # delete tmp directory
    if args.keep:
        print_info("Not deleting temp dir '%s'" % (tmp_path))
    else:
        delete_directory(tmp_path)
        print_debug("Deleted temp dir '%s'" % (tmp_path), args.debug)

    return result



