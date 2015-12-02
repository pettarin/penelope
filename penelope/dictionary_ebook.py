#!/usr/bin/env python
# coding=utf-8

"""
DictionaryEbook represents a dictionary ebook
in EPUB 2 and MOBI format.
"""

from __future__ import absolute_import
from __future__ import print_function
from io import open
import os
import zipfile

from penelope.utilities import create_temp_directory
from penelope.utilities import delete_directory

__author__ = "Alberto Pettarin"
__copyright__ = "Copyright 2012-2015, Alberto Pettarin (www.albertopettarin.it)"
__license__ = "MIT"
__version__ = "3.1.1"
__email__ = "alberto@albertopettarin.it"
__status__ = "Production"

class DictionaryEbook():
    """
    A class representing a generic ebook containing a dictionary.

    It can be used to output a MOBI or an EPUB 2 container.

    The ebook must have an OPF, and one or more group XHTML files.

    Optionally, it can have a cover image, an NCX TOC, an index XHTML file.

    The actual file templates are provided by the caller.
    """

    EPUB2 = u"epub2"

    #EPUB3 = u"epub3"

    MOBI = u"mobi"

    GROUP_START_INDEX = 2

    MIMETYPE_CONTENTS = u"application/epub+zip"

    CONTAINER_XML_CONTENTS = u"""<?xml version="1.0" encoding="UTF-8" ?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>"""

    EPUB_CSS_CONTENTS = u"""@charset "UTF-8";
body {
  margin: 10px 25px 10px 25px;
}  
h1 {
  font-size: 200%;
}
h2 {
  font-size: 150%;
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
body.indexPage {}
h1.indexTitle {}
p.indexGroups {
  font-size: 150%;
}
span.indexGroup {}
body.groupPage {}
h1.groupTitle {}
div.groupNavigation {}
span.groupHeadword {}
div.groupEntry {
  margin-top: 0;
  margin-bottom: 1em;
}
h2.groupHeadword {
  margin-left: 5%;
}
p.groupDefinition {
  margin-left: 10%;
  margin-right: 10%;
}
"""

    MOBI_CSS_CONTENTS = u""""@charset "UTF-8";"""

    INDEX_XHTML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
 </head>
 <body class="indexPage">
  <h1 class="indexTitle">%s</h1>
  <p class="indexGroupss">
%s
  </p>
 </body>
</html>"""
    INDEX_XHTML_LINK_TEMPLATE = u"""   <span class="indexGroup"><a href=\"%s\">%s</a></span>"""

    INDEX_XHTML_LINK_JOINER = u" &#8226;\n"

    EPUB_GROUP_XHTML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
 </head>
 <body id="groupPage" class="groupPage">
  <h1 class="groupTitle">%s</h1>
  <div class="groupNavigation">
   <a href="%s">[ Previous ]</a>
%s
   <a href="%s">[ Next ]</a>
  </div>
%s
 </body>
</html>"""
    EPUB_GROUP_XHTML_INDEX_LINK = u"""   <a href="index.xhtml">[ Index ]</a>"""

    EPUB_GROUP_XHTML_WORD_TEMPLATE = u"""   <span class="groupHeadword">%s</span>"""

    EPUB_GROUP_XHTML_WORD_JOINER = u" &#8226;\n"

    EPUB_GROUP_XHTML_WORD_DEFINITION_TEMPLATE = u"""  <div class="groupEntry">
   <h2 class="groupHeadword">%s</h2>
   <p class="groupDefinition">%s</p>
  </div>"""

    EPUB_GROUP_XHTML_WORD_DEFINITION_JOINER = u"\n"

    MOBI_GROUP_XHTML_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
 <head>
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="style.css" />
 </head>
 <body id="groupPage" class="groupPage">
  <h1 class="groupTitle">%s</h1>
  <div class="groupNavigation">
   <a href="%s">[ Previous ]</a>
%s
   <a href="%s">[ Next ]</a>
  </div>
%s
 </body>
</html>"""

    MOBI_GROUP_XHTML_INDEX_LINK = u"""   <a href="index.xhtml">[ Index ]</a>"""

    MOBI_GROUP_XHTML_WORD_TEMPLATE = u"""   <span class="groupHeadword"><idx:entry><idx:orth>%s</idx:orth></idx:entry></span>"""

    MOBI_GROUP_XHTML_WORD_JOINER = u" &#8226;\n"

    MOBI_GROUP_XHTML_WORD_DEFINITION_TEMPLATE = u"""  <div class="groupEntry">
   <idx:entry>
    <h2 class="groupHeadword"><idx:orth>%s</idx:orth></h2>
    <p class="groupDefinition">%s</p>
   </idx:entry>
  </div>"""

    MOBI_GROUP_XHTML_WORD_DEFINITION_JOINER = u"\n"

    EPUB2_OPF_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8" ?>
<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">
 <metadata xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:identifier id="uid" opf:scheme="uuid">%s</dc:identifier>
  <dc:language>%s</dc:language>
  <dc:title>%s</dc:title>
  <dc:creator opf:role="aut">%s</dc:creator>
  <dc:rights>%s</dc:rights>
  <dc:date opf:event="creation">%s-01-01</dc:date>
%s
 </metadata>
 <manifest>
%s
 </manifest>
 <spine toc="toc.ncx">
%s
 </spine>
</package>"""

    MOBI_OPF_TEMPLATE = u"""<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid">
 <metadata>
  <dc-metadata xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
   <dc:Title>%s</dc:Title>
   <dc:Language>%s</dc:Language>
   <dc:Identifier id="uid">%s</dc:Identifier>
   <dc:Creator>%s</dc:Creator>
   <dc:Rights>%s</dc:Rights>
   <dc:Subject BASICCode="REF008000">Dictionaries</dc:Subject>
  </dc-metadata>
  <x-metadata>
   <output encoding="utf-8"></output>
   <DictionaryInLanguage>%s</DictionaryInLanguage>
   <DictionaryOutLanguage>%s</DictionaryOutLanguage>
   <EmbeddedCover>%s</EmbeddedCover>
  </x-metadata>
 </metadata>
 <manifest>
%s
 </manifest>
 <spine>
%s
 </spine>
 <tours></tours>
 <guide></guide>
</package>"""

    OPF_MANIFEST_ITEM_TEMPLATE = u"""  <item href="%s" id="%s" media-type="%s" />"""

    OPF_SPINE_ITEMREF_TEMPLATE = u"""  <itemref idref="%s" />"""

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

    def __init__(self, ebook_format, args):
        self.ebook_format = ebook_format
        self.args = args
        self.root_directory_path = None
        self.cover = None
        self.files = []
        self.manifest_files = []
        self.groups = []

    def get_tmp_path(self):
        if self.root_directory_path is not None:
            return self.root_directory_path
        return u""

    def delete(self):
        if self.root_directory_path is not None:
            delete_directory(self.root_directory_path)

    def add_file(self, relative_path, contents, mode=zipfile.ZIP_DEFLATED):
        file_path = os.path.join(self.root_directory_path, relative_path)
        file_obj = open(file_path, "wb")
        try:
            # Python 2
            if isinstance(contents, unicode):
                contents = contents.encode("utf-8")
        except NameError:
            # Python 3
            if isinstance(contents, str):
                contents = contents.encode("utf-8")
        except:
            # should not occur
            pass
        file_obj.write(contents)
        file_obj.close()
        self.files.append({"path": relative_path, "mode": mode})

    def write_cover(self, cover_path_absolute):
        if cover_path_absolute is not None:
            try:
                basename = os.path.basename(cover_path_absolute)
                cover_obj = open(cover_path_absolute, "rb")
                cover = cover_obj.read()
                cover_obj.close()
                b = basename.lower()
                mimetype = "image/jpeg"
                if b.endswith(".png"):
                    mimetype = "image/png"
                elif b.endswith(".gif"):
                    mimetype = "image/gif"
                self.add_file_manifest(u"OEBPS/%s" % basename, basename, cover, mimetype)
                self.cover = basename
            except:
                pass

    def write_css(self, custom_css_path_absolute):
        if self.ebook_format == self.MOBI:
            css = self.MOBI_CSS_CONTENTS
        else:
            css = self.EPUB_CSS_CONTENTS
        if custom_css_path_absolute is not None:
            try:
                css_obj = open(custom_css_path_absolute, "rb")
                css = css_obj.read()
                css_obj.close()
            except:
                pass
        self.add_file_manifest(u"OEBPS/style.css", u"style.css", css, "text/css")

    def add_file_manifest(self, relative_path, id, contents, mimetype):
        self.add_file(relative_path, contents)
        self.manifest_files.append({"path": relative_path, "id": id, "mimetype": mimetype})

    def get_group_xhtml_file_name_from_index(self, index):
        if (index < self.GROUP_START_INDEX) or (index >= len(self.groups) + self.GROUP_START_INDEX):
            return u"#groupPage"
        return u"g%06d.xhtml" % index

    def add_group(self, key, entries):
        self.groups.append({"key": key, "entries": entries})

    def write_groups(self):
        if self.ebook_format == self.MOBI:
            group_template = self.MOBI_GROUP_XHTML_TEMPLATE
            if self.args.include_index_page:
                index_link = self.MOBI_GROUP_XHTML_INDEX_LINK
            else:
                index_link = u""
            word_template = self.MOBI_GROUP_XHTML_WORD_TEMPLATE
            word_joiner = self.MOBI_GROUP_XHTML_WORD_JOINER
            word_definition_template = self.MOBI_GROUP_XHTML_WORD_DEFINITION_TEMPLATE
            word_definition_joiner = self.MOBI_GROUP_XHTML_WORD_DEFINITION_JOINER
        else:
            group_template = self.EPUB_GROUP_XHTML_TEMPLATE
            if self.args.include_index_page:
                index_link = self.EPUB_GROUP_XHTML_INDEX_LINK
            else:
                index_link = u""
            word_template = self.EPUB_GROUP_XHTML_WORD_TEMPLATE
            word_joiner = self.EPUB_GROUP_XHTML_WORD_JOINER
            word_definition_template = self.EPUB_GROUP_XHTML_WORD_DEFINITION_TEMPLATE
            word_definition_joiner = self.EPUB_GROUP_XHTML_WORD_DEFINITION_JOINER

        index = self.GROUP_START_INDEX
        for group in self.groups:
            group_label = self.get_group_label(group)
            group_xhtml_path = self.get_group_xhtml_file_name_from_index(index)
            previous_link = self.get_group_xhtml_file_name_from_index(index - 1)
            next_link = self.get_group_xhtml_file_name_from_index(index + 1)
            group_contents = []
            if self.args.no_definitions:
                for entry in group["entries"]:
                    headword = self.escape_if_needed(entry.headword)
                    group_contents.append(word_template % (headword))
                group_contents = word_joiner.join(group_contents)
            else:
                for entry in group["entries"]:
                    headword = self.escape_if_needed(entry.headword)
                    definition = self.escape_if_needed(entry.definition)
                    group_contents.append(word_definition_template % (headword, definition))
                group_contents = word_definition_joiner.join(group_contents)
            group_contents = group_template % (group_label, group_label, previous_link, index_link, next_link, group_contents)
            self.add_file_manifest(u"OEBPS/%s" % group_xhtml_path, group_xhtml_path, group_contents, u"application/xhtml+xml")
            index += 1 

    def escape_if_needed(self, string):
        def html_escape(s):
            x = s
            x = x.replace("&", "&amp;")
            x = x.replace('"', "&quot;")
            x = x.replace("'", "&apos;")
            x = x.replace(">", "&gt;")
            x = x.replace("<", "&lt;")
            return x
        if self.args.escape_strings:
            return html_escape(string)
        return string

    def get_group_label(self, group):
        group_label = group["key"]
        if group_label != u"SPECIAL":
            group_label = "%s&#8211;%s" % (group["entries"][0].headword, group["entries"][-1].headword)
        return group_label

    def write_index(self):
        links = []
        index = self.GROUP_START_INDEX
        for group in self.groups:
            group_label = self.get_group_label(group)
            group_xhtml_path = self.get_group_xhtml_file_name_from_index(index)
            group_link = self.INDEX_XHTML_LINK_TEMPLATE % (group_xhtml_path, group_label)
            links.append(group_link)
            index += 1
        links = self.INDEX_XHTML_LINK_JOINER.join(links)
        contents = self.INDEX_XHTML_TEMPLATE % (self.args.title, self.args.title, links)
        self.add_file_manifest(u"OEBPS/index.xhtml", u"index.xhtml", contents, u"application/xhtml+xml")

    def write_opf(self):
        manifest_contents = []
        spine_contents = []
        for mi in self.manifest_files:
            manifest_contents.append(self.OPF_MANIFEST_ITEM_TEMPLATE % (mi["id"], mi["id"], mi["mimetype"]))
            if mi["mimetype"] == u"application/xhtml+xml":
                spine_contents.append(self.OPF_SPINE_ITEMREF_TEMPLATE % (mi["id"]))
        manifest_contents = u"\n".join(manifest_contents)
        spine_contents = u"\n".join(spine_contents)
        cover = u""
        if self.ebook_format == self.MOBI:
            if self.cover is not None:
                cover = self.cover
            opf_contents = self.MOBI_OPF_TEMPLATE % (
                self.args.title,
                self.args.language_from,
                self.args.identifier,
                self.args.author,
                self.args.copyright,
                self.args.language_from,
                self.args.language_to,
                cover,
                manifest_contents,
                spine_contents
            )
        else:
            if self.cover is not None:
                cover = u"""  <meta name="cover" content="%s" />""" % self.cover
            opf_contents = self.EPUB2_OPF_TEMPLATE % (
                self.args.identifier,
                self.args.language_from,
                self.args.title,
                self.args.author,
                self.args.copyright,
                self.args.year,
                cover,
                manifest_contents,
                spine_contents
            )
        self.add_file("OEBPS/content.opf", opf_contents)

    def write_ncx(self):
        ncx_items = []
        index = 1
        if self.args.include_index_page:
            ncx_items.append(self.NCX_NAVPOINT_TEMPLATE % (index, index, "Index", "index.xhtml"))
            index += 1
        for group in self.groups:
            group_label = self.get_group_label(group)
            group_xhtml_path = self.get_group_xhtml_file_name_from_index(index)
            ncx_items.append(self.NCX_NAVPOINT_TEMPLATE % (index, index, group_label, group_xhtml_path))
            index += 1
        ncx_items = u"\n".join(ncx_items)
        ncx_contents = self.NCX_TEMPLATE % (self.args.identifier, self.args.title, ncx_items)
        self.add_file_manifest(u"OEBPS/toc.ncx", u"toc.ncx", ncx_contents, u"application/x-dtbncx+xml")

    def write(self, file_path_absolute, compress=True): 
        # get cover path
        cover_path_absolute = self.args.cover_path
        if cover_path_absolute is not None:
            cover_path_absolute = os.path.abspath(cover_path_absolute)

        # get custom css path
        custom_css_path_absolute = self.args.apply_css
        if custom_css_path_absolute is not None:
            custom_css_path_absolute = os.path.abspath(custom_css_path_absolute)

        # create new tmp directory and cd there
        self.root_directory_path = create_temp_directory()
        cwd = os.getcwd()
        os.chdir(self.root_directory_path)
        os.makedirs(u"META-INF")
        os.makedirs(u"OEBPS")

        # add mimetype and container.xml
        if self.ebook_format in [self.EPUB2]: # add EPUB3 here
            self.add_file(u"mimetype", self.MIMETYPE_CONTENTS, mode=zipfile.ZIP_STORED)
            self.add_file(u"META-INF/container.xml", self.CONTAINER_XML_CONTENTS)

        # add cover
        self.write_cover(cover_path_absolute)

        # write CSS
        self.write_css(custom_css_path_absolute)

        # write index
        if self.args.include_index_page:
            self.write_index()

        # write groups
        self.write_groups()

        # write ncx
        if self.ebook_format in [self.EPUB2]: # add EPUB3 here
            self.write_ncx()

        # write opf
        self.write_opf()

        # compress 
        if compress:
            output_file_obj = zipfile.ZipFile(file_path_absolute, "w", compression=zipfile.ZIP_DEFLATED)
            for file_to_compress in self.files:
                output_file_obj.write(file_to_compress["path"], compress_type=file_to_compress["mode"])
            output_file_obj.close()

        # return to previous cwd
        os.chdir(cwd)


